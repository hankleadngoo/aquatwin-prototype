"""Local-only UI + Ditto bridge. Credentials never enter the browser."""
import argparse,base64,json,os,threading,urllib.request,urllib.error
from datetime import datetime
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parent
DATA=json.loads((ROOT/'dist/data.json').read_text(encoding='utf-8'))
THING_ID='aquatwin:nuoibien-2';POLICY_ID='aquatwin:nuoibien-2-policy';LOCK=threading.Lock()
class BridgeError(Exception):
 def __init__(self,message,status=400):self.message=message;self.status=status
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,req,fp,code,msg,headers,newurl):return None
def quality(index,key,cursor):
 tests=dict(DATA['rows'][index]['qc'][key]['tests'])
 if index==cursor:tests['spike']=2
 if tests.get('missing')==9:return 9
 return max([v for v in tests.values() if v in [1,3,4]],default=2)
def snapshot(cursor):
 if isinstance(cursor,bool) or not isinstance(cursor,int) or not 0<=cursor<len(DATA['rows']):raise BridgeError('Invalid data cursor.')
 row=DATA['rows'][cursor];features={}
 for key,config in DATA['params'].items():
  good=None
  for i in range(cursor,-1,-1):
   if quality(i,key,cursor)==1:
    r=DATA['rows'][i];good={'value':r['values'][key],'ts':r['ts']};break
  features[key]={'properties':{'observed':{'value':row['values'][key],'ts':row['ts'],'unit':config['unit'],'qualityFlag':quality(cursor,key,cursor)},'last_good':good}}
 features['health']={'properties':{'mode':'historical-replay','sourceTime':row['ts'],'deviceError':row['error'] or None,'depth_m':None,'calibration_ref':None,'unit_id':None,'spikeStatus':'pending_next_observation','qcVersion':DATA['meta']['qcVersion']}}
 return {'thingId':THING_ID,'policyId':POLICY_ID,'attributes':{'site':row['site'],'device':row['device'],'timezone':'UTC+07:00','sourceMapping':'salinity=conductivity_mS_cm'},'features':features}
def policy(subject):
 if not subject or any(c in subject for c in '\r\n'):raise BridgeError('Set DITTO_SUBJECT to the authenticated Ditto account subject.')
 return {'policyId':POLICY_ID,'entries':{
  'owner':{'subjects':{subject:{'type':'Local operator'}},'resources':{'thing:/':{'grant':['READ','WRITE'],'revoke':[]},'policy:/':{'grant':['READ','WRITE'],'revoke':[]}}},
  'qc_ingest':{'subjects':{'aquatwin:ingest':{'type':'QC MQTT source'}},'resources':{'thing:/features':{'grant':['WRITE'],'revoke':[]}}},
  'observer':{'subjects':{'aquatwin:observer':{'type':'Read-only observer'}},'resources':{'thing:/':{'grant':['READ'],'revoke':[]}}}}}
class Ditto:
 def __init__(self):
  self.url=os.environ.get('DITTO_URL','http://127.0.0.1:8080').rstrip('/');parts=urlsplit(self.url)
  if parts.scheme not in ['http','https'] or parts.hostname not in ['localhost','127.0.0.1','::1'] or parts.username or parts.password or parts.query or parts.fragment or parts.path not in ['', '/']:
   raise BridgeError('The gateway connects to loopback Ditto only; farm data is not sent to external servers.')
  self.headers={'Content-Type':'application/json','Accept':'application/json'}
  token=os.environ.get('DITTO_TOKEN');user=os.environ.get('DITTO_USER');password=os.environ.get('DITTO_PASSWORD')
  self.auth_configured=bool(token or (user and password))
  if token:self.headers['Authorization']='Bearer '+token
  elif user and password:self.headers['Authorization']='Basic '+base64.b64encode((user+':'+password).encode()).decode()
  self.opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),NoRedirect())
 def request(self,method,path,payload=None,allow_missing=False,headers=None):
  if not self.auth_configured:raise BridgeError('Set DITTO_TOKEN or DITTO_USER / DITTO_PASSWORD.',503)
  req=urllib.request.Request(self.url+path,data=json.dumps(payload).encode() if payload is not None else None,headers={**self.headers,**(headers or {})},method=method)
  try:
   with self.opener.open(req,timeout=5) as r:
    raw=r.read(2000000);return {'status':r.status,'body':json.loads(raw) if raw else None,'etag':r.headers.get('ETag')}
  except urllib.error.HTTPError as e:
   if e.code==404 and allow_missing:return {'status':404,'body':None,'etag':None}
   if e.code in [401,403]:raise BridgeError('Ditto denied access; check credentials and Policy.',502)
   if e.code in [409,412]:raise BridgeError('The Ditto state has changed; read it again before synchronizing.',409)
   raise BridgeError('Ditto returned HTTP error '+str(e.code)+'.',502)
  except (urllib.error.URLError,TimeoutError,OSError):raise BridgeError('Cannot connect to loopback Ditto; check the server and port.',503)
  except ValueError:raise BridgeError('Ditto returned invalid JSON.',502)
def path():return '/api/2/things/'+THING_ID
def status():
 try:
  client=Ditto()
  if not client.auth_configured:return {'state':'not_configured','endpoint':client.url,'configured':False,'connected':False,'message':'Ditto credentials are not configured in the gateway environment.'}
  result=client.request('GET',path(),allow_missing=True)
  return {'state':'ready' if result['status']==200 else 'needs_provision','endpoint':client.url,'configured':True,'connected':True,'thingExists':result['status']==200,'thingId':THING_ID,'sourceTime':((result.get('body') or {}).get('features',{}).get('health',{}).get('properties',{}).get('sourceTime')),'message':'Authenticated and read the Thing successfully.' if result['status']==200 else 'Ditto is reachable; the Thing does not exist yet.'}
 except BridgeError as e:return {'state':'unavailable','configured':True,'connected':False,'message':e.message}
def provision():
 client=Ditto();desired=policy(os.environ.get('DITTO_SUBJECT',''))
 result=client.request('GET','/api/2/policies/'+POLICY_ID,allow_missing=True);pc=result['status']==404
 if pc:client.request('PUT','/api/2/policies/'+POLICY_ID,desired,headers={'If-None-Match':'*'})
 result=client.request('GET',path(),allow_missing=True);tc=result['status']==404
 if tc:client.request('PUT',path(),{'thingId':THING_ID,'policyId':POLICY_ID,'attributes':{'site':DATA['meta']['site'],'device':DATA['meta']['device'],'sourceMapping':'salinity=conductivity_mS_cm'}},headers={'If-None-Match':'*'})
 return {'policyCreated':pc,'thingCreated':tc,'message':'Created missing resources; existing Policies and Things were preserved.'}
def sync(cursor):
 candidate=snapshot(cursor);client=Ditto()
 with LOCK:
  current=client.request('GET',path(),allow_missing=True)
  if current['status']==404:raise BridgeError('The Thing does not exist. Provision it first.',409)
  thing=current['body']
  if thing.get('policyId')!=POLICY_ID:raise BridgeError('The Thing uses a different Policy; administrator review is required.',409)
  previous=thing.get('features',{}).get('health',{}).get('properties',{}).get('sourceTime');incoming=candidate['features']['health']['properties']['sourceTime']
  if previous:
   try:
    if datetime.fromisoformat(previous)>datetime.fromisoformat(incoming):raise BridgeError('The snapshot is older than the Ditto state; state rollback is blocked.',409)
   except (ValueError,TypeError):raise BridgeError('The Ditto timestamp is invalid; review it before proceeding.',409)
  if all(thing.get('features',{}).get(k)==v for k,v in candidate['features'].items()):return {'duplicate':True,'sourceTime':incoming,'message':'The snapshot already exists; duplicate update skipped.'}
  if not current['etag']:raise BridgeError('Ditto did not return an ETag; version-controlled synchronization is blocked.',409)
  body={k:thing[k] for k in ['thingId','policyId','attributes','features'] if k in thing};body['features']={**thing.get('features',{}),**candidate['features']}
  client.request('PUT',path(),body,headers={'If-Match':current['etag']})
  verified=client.request('GET',path())['body']
  if any(verified.get('features',{}).get(k)!=v for k,v in candidate['features'].items()):raise BridgeError('Unable to verify the readback state.',502)
  return {'duplicate':False,'sourceTime':incoming,'message':'Synchronized and verified with GET.','thing':verified}
class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(ROOT/'dist'),**kwargs)
 def log_message(self,format,*args):pass
 def output(self,code,body):
  payload=json.dumps(body,ensure_ascii=False).encode();self.send_response(code);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(payload)));self.end_headers();self.wfile.write(payload)
 def trusted(self):
  expected={'127.0.0.1:'+str(self.server.server_port),'localhost:'+str(self.server.server_port)}
  if self.headers.get('Host','') not in expected or (self.headers.get('Origin') and self.headers['Origin'] not in {'http://'+h for h in expected}):raise BridgeError('Origin / Host not allowed.',403)
 def do_GET(self):
  if not self.path.startswith('/api/'):return super().do_GET()
  try:
   self.trusted()
   if self.path=='/api/ditto/status':return self.output(200,status())
   if self.path=='/api/ditto/thing':return self.output(200,Ditto().request('GET',path())['body'])
   if self.path=='/api/health':return self.output(200,{'app':'aquatwin','bridgeVersion':'1.1.0','rows':len(DATA['rows'])})
   raise BridgeError('API endpoint not found.',404)
  except BridgeError as e:self.output(e.status,{'error':e.message})
 def do_POST(self):
  try:
   self.trusted()
   if self.headers.get('Content-Type','').split(';')[0]!='application/json':raise BridgeError('JSON content is required.',415)
   size=int(self.headers.get('Content-Length','0'))
   if not 0<size<=2048:raise BridgeError('Invalid request size.')
   body=json.loads(self.rfile.read(size))
   if not isinstance(body,dict):raise BridgeError('JSON must be an object.')
   if self.path=='/api/ditto/provision':return self.output(200,provision())
   if self.path=='/api/ditto/sync':return self.output(200,sync(body.get('cursor')))
   raise BridgeError('API endpoint not found.',404)
  except BridgeError as e:self.output(e.status,{'error':e.message})
  except (ValueError,TypeError):self.output(400,{'error':'Invalid JSON or parameters.'})
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=8765);args=parser.parse_args()
 print(f'AquaTwin local gateway: http://127.0.0.1:{args.port}/',flush=True)
 ThreadingHTTPServer(('127.0.0.1',args.port),Handler).serve_forever()
