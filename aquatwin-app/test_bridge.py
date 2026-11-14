import copy,json,os,threading,unittest,urllib.request,urllib.error
from unittest.mock import patch
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import server

class MockDitto(BaseHTTPRequestHandler):
 state={};writes=[];revision=0;etag=True;conflict=False;redirect=False
 def log_message(self,*args):pass
 def reply(self,status,body):
  raw=json.dumps(body).encode();self.send_response(status);self.send_header('Content-Type','application/json')
  if self.etag:self.send_header('ETag','"'+str(type(self).revision)+'"')
  self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
 def do_GET(self):
  if self.redirect:
   self.send_response(302);self.send_header('Location','https://example.invalid/');self.end_headers();return
  if not self.headers.get('Authorization'):return self.reply(401,{})
  return self.reply(200,self.state[self.path]) if self.path in self.state else self.reply(404,{})
 def do_PUT(self):
  if self.headers.get('If-None-Match')=='*' and self.path in self.state:return self.reply(412,{})
  if self.conflict and self.headers.get('If-Match'):return self.reply(412,{})
  if self.headers.get('If-Match') and self.headers['If-Match']!='"'+str(type(self).revision)+'"':return self.reply(412,{})
  body=json.loads(self.rfile.read(int(self.headers['Content-Length'])))
  self.state[self.path]=body;type(self).revision+=1;self.writes.append((self.path,copy.deepcopy(body)));self.reply(204,{})

class BridgeTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.mock=ThreadingHTTPServer(('127.0.0.1',0),MockDitto);threading.Thread(target=cls.mock.serve_forever,daemon=True).start()
  cls.app=ThreadingHTTPServer(('127.0.0.1',0),server.Handler);threading.Thread(target=cls.app.serve_forever,daemon=True).start()
 @classmethod
 def tearDownClass(cls):
  cls.mock.shutdown();cls.mock.server_close();cls.app.shutdown();cls.app.server_close()
 def setUp(self):
  MockDitto.state={};MockDitto.writes=[];MockDitto.revision=0;MockDitto.etag=True;MockDitto.conflict=False;MockDitto.redirect=False
  self.env=patch.dict(os.environ,{'DITTO_URL':f'http://127.0.0.1:{self.mock.server_port}','DITTO_TOKEN':'test-only','DITTO_SUBJECT':'nginx:tester'},clear=True);self.env.start()
 def tearDown(self):self.env.stop()
 def test_snapshot_mapping_missing_and_no_future(self):
  row=server.snapshot(100);self.assertEqual(row['features']['conductivity']['properties']['observed']['unit'],'mS/cm')
  error=next(i for i,r in enumerate(server.DATA['rows']) if r['error'])
  for key in server.DATA['params']:
   feat=server.snapshot(error)['features'][key]['properties'];self.assertIsNone(feat['observed']['value']);self.assertEqual(feat['observed']['qualityFlag'],9)
   if feat['last_good']:self.assertLessEqual(feat['last_good']['ts'],server.DATA['rows'][error]['ts'])
 def test_invalid_cursor(self):
  for cursor in [True,-1,1333,'100',None]:
   with self.assertRaises(server.BridgeError):server.snapshot(cursor)
 def test_policy_no_actuator_permissions(self):
  policy=server.policy('nginx:test');self.assertFalse(any('message:/' in e['resources'] for e in policy['entries'].values()))
  self.assertEqual(policy['entries']['qc_ingest']['resources']['thing:/features']['grant'],['WRITE'])
 def test_external_endpoint_blocked(self):
  for url in ['http://10.7.0.27:8080','https://example.com','http://user:pass@localhost:8080']:
   with patch.dict(os.environ,{'DITTO_URL':url}):
    with self.assertRaises(server.BridgeError):server.Ditto()
 def test_unconfigured_status(self):
  with patch.dict(os.environ,{},clear=True):self.assertEqual(server.status()['state'],'not_configured')
 def test_provision_create_only(self):
  self.assertEqual(server.status()['state'],'needs_provision');self.assertTrue(server.provision()['thingCreated'])
  writes=len(MockDitto.writes);self.assertFalse(server.provision()['thingCreated']);self.assertEqual(len(MockDitto.writes),writes)
 def test_sync_verify_dedupe_and_older_guard(self):
  server.provision();result=server.sync(100);self.assertFalse(result['duplicate']);self.assertEqual(server.status()['state'],'ready')
  writes=len(MockDitto.writes);self.assertTrue(server.sync(100)['duplicate']);self.assertEqual(len(MockDitto.writes),writes)
  with self.assertRaises(server.BridgeError):server.sync(99)
 def test_preserve_other_features_attributes(self):
  server.provision();thing=MockDitto.state[server.path()];thing['attributes']['custom']='keep';thing['features']={'foreign':{'properties':{'a':1}}}
  server.sync(200);thing=MockDitto.state[server.path()];self.assertEqual(thing['attributes']['custom'],'keep');self.assertIn('foreign',thing['features'])
  self.assertTrue(server.sync(200)['duplicate'])
 def test_missing_etag_and_conflict(self):
  server.provision();MockDitto.etag=False
  with self.assertRaises(server.BridgeError):server.sync(50)
  MockDitto.etag=True;MockDitto.conflict=True
  with self.assertRaises(server.BridgeError):server.sync(50)
 def test_redirect_not_followed(self):
  MockDitto.redirect=True
  with self.assertRaises(server.BridgeError):server.Ditto().request('GET',server.path())
 def test_api_origin_and_payload_validation(self):
  base=f'http://127.0.0.1:{self.app.server_port}';opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
  with opener.open(base+'/api/health') as r:self.assertEqual(json.load(r)['bridgeVersion'],'1.1.0')
  req=urllib.request.Request(base+'/api/ditto/sync',data=b'{"cursor":100}',headers={'Origin':'https://evil.invalid','Content-Type':'application/json'})
  with self.assertRaises(urllib.error.HTTPError) as ctx:opener.open(req)
  self.assertEqual(ctx.exception.code,403)
  req=urllib.request.Request(base+'/api/ditto/sync',data=b'{"cursor":-1}',headers={'Content-Type':'application/json'})
  with self.assertRaises(urllib.error.HTTPError) as ctx:opener.open(req)
  self.assertEqual(ctx.exception.code,400)

if __name__=='__main__':unittest.main()
