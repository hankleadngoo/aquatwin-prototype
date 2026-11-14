"""Explicit snapshot push for a configured local Ditto. Credentials via environment only.
Does not send live messages or actuator commands. No credentials stored in the app.
"""
import argparse,base64,json,os,urllib.request
from pathlib import Path

def main():
 p=argparse.ArgumentParser();p.add_argument('--snapshot',required=True);p.add_argument('--dry-run',action='store_true');args=p.parse_args()
 thing=json.loads(Path(args.snapshot).read_text(encoding='utf-8-sig'))
 if thing.get('thingId')!='aquatwin:nuoibien-2':raise ValueError('Unexpected thingId')
 if args.dry_run:print('Valid Thing snapshot; no request sent.');return
 endpoint=os.environ['DITTO_URL'].rstrip('/')
 from urllib.parse import urlsplit
 parts=urlsplit(endpoint)
 if parts.scheme not in ['http','https'] or parts.hostname not in ['localhost','127.0.0.1','::1'] or parts.username or parts.password:raise ValueError('Local loopback Ditto endpoints only')
 token=os.environ.get('DITTO_TOKEN')
 headers={'Content-Type':'application/json'}
 if token:headers['Authorization']='Bearer '+token
 else:
  credentials=os.environ['DITTO_USER']+':'+os.environ['DITTO_PASSWORD']
  headers['Authorization']='Basic '+base64.b64encode(credentials.encode()).decode()
 policy=os.environ.get('DITTO_POLICY_ID')
 if policy:thing['policyId']=policy
 req=urllib.request.Request(endpoint+'/api/2/things/'+thing['thingId'],data=json.dumps(thing).encode(),headers=headers,method='PUT')
 from server import NoRedirect
 opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),NoRedirect())
 with opener.open(req,timeout=15) as response:print('Twin snapshot accepted:',response.status)
if __name__=='__main__':main()
