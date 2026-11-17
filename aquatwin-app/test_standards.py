import copy
import unittest
from datetime import datetime, timezone
import standards
import server
import json
import threading
import urllib.request
import urllib.error
from http.server import ThreadingHTTPServer


class ContractTests(unittest.TestCase):
    def test_registry_shapes(self):
        self.assertIs(standards.validate_profile(standards.PROFILE),standards.PROFILE)
        for change in ['duplicate','orphan','operational']:
            p=copy.deepcopy(standards.PROFILE)
            if change=='duplicate':p['entities'].append(copy.deepcopy(p['entities'][0]))
            if change=='orphan':p['relationships'][0]['object']='unknown'
            if change=='operational':p['models'][0]['operationalUseAllowed']=True
            with self.assertRaises(ValueError):standards.validate_profile(p)

    def events(self, cursor=100):
        return standards.observations(server.DATA, cursor, server.quality)

    def test_identity_units_provenance(self):
        events = self.events()
        self.assertEqual(len(events), 5)
        self.assertEqual(len({e['id'] for e in events}), 5)
        self.assertEqual(events, self.events())
        self.assertTrue(all(e['data']['receivedAt'] is None for e in events))
        self.assertTrue(all(e['subject'] == standards.PROFILE['twinId'] for e in events))

    def test_reject_corruption(self):
        for field, value in [('stateKind','simulated'), ('unit','wrong'), ('sensorId','other'),
                             ('value',float('nan')), ('value',True), ('qualityFlag',False),
                             ('location',{'lat':1}), ('targetId','other')]:
            with self.subTest(field=field):
                e=copy.deepcopy(self.events()[0]);e['data'][field]=value
                with self.assertRaises(ValueError):standards.validate_observation(e)

    def test_missing_sensor_is_not_observation(self):
        cursor=next(i for i,r in enumerate(server.DATA['rows']) if r['error'])
        self.assertTrue(all(e['data']['value'] is None and e['data']['qualityFlag']==9 for e in self.events(cursor)))

    def test_snapshot_preserves_existing_shape(self):
        snapshot=server.snapshot(100)
        self.assertEqual(snapshot['attributes']['targetId'],standards.PROFILE['target']['id'])
        self.assertEqual(snapshot['features']['DO']['properties']['observed']['stateKind'],'observed')
        self.assertNotIn('predicted',snapshot['features']['DO']['properties'])

    def test_freshness_uses_wall_clock(self):
        t=datetime(2026,11,13,tzinfo=timezone.utc)
        self.assertFalse(standards.health('2026-11-13T06:55:00+07:00',t)['stale'])
        self.assertTrue(standards.health('2026-11-13T06:00:00+07:00',t)['stale'])
        self.assertTrue(standards.health('2026-11-13T08:00:00+07:00',t)['stale'])
        self.assertFalse(standards.health('2026-11-13T06:55:00+07:00',t)['operationalUseAllowed'])

    def test_invalid_cursors(self):
        for cursor in [-1,True,len(server.DATA['rows'])]:
            with self.assertRaises(ValueError):self.events(cursor)

    def test_http_contract_routes(self):
        app=ThreadingHTTPServer(('127.0.0.1',0),server.Handler)
        worker=threading.Thread(target=app.serve_forever,daemon=True);worker.start()
        base='http://127.0.0.1:'+str(app.server_port)
        opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
        try:
            with opener.open(base+'/api/architecture') as r:
                self.assertEqual(json.load(r)['twinId'],standards.PROFILE['twinId'])
            with opener.open(base+'/api/observations?cursor=100') as r:
                self.assertEqual(len(json.load(r)['events']),5)
            with opener.open(base+'/api/state/health') as r:
                self.assertFalse(json.load(r)['operationalUseAllowed'])
            for suffix in ['?cursor=-1','?cursor=1&cursor=2','?cursor=NaN','']:
                with self.assertRaises(urllib.error.HTTPError) as ctx:
                    opener.open(base+'/api/observations'+suffix)
                self.assertEqual(ctx.exception.code,400)
            req=urllib.request.Request(base+'/api/architecture',headers={'Origin':'https://other.invalid'})
            with self.assertRaises(urllib.error.HTTPError) as ctx:opener.open(req)
            self.assertEqual(ctx.exception.code,403)
        finally:
            app.shutdown();app.server_close();worker.join()

if __name__=='__main__':unittest.main()
