"""Read-only normalization and provisional QC. No biological alarm thresholds."""
from pathlib import Path
import csv,json,hashlib,statistics,math
from datetime import datetime

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/'data/source.csv'
PARAMS={
 'temperature':dict(label='Temperature',unit='°C',gross=[-2,45],plausible=[20,35],spike=[1,2],roc=2),
 'conductivity':dict(label='Conductivity',unit='mS/cm',gross=[0,80],plausible=[30,60],spike=[5,10],roc=7.5),
 'pH':dict(label='pH',unit='',gross=[0,14],plausible=[7,9],spike=[.3,.6],roc=.5),
 'DO':dict(label='Dissolved oxygen',unit='mg/L',gross=[0,25],plausible=[2,15],spike=[1,2],roc=2),
 'turbidity':dict(label='Turbidity',unit='NTU',gross=[0,1100],plausible=[0,100],spike=[50,200],roc=100),
}
def overall(tests):
 if tests['missing']==9:return 9
 return max([x for x in tests.values() if x in [1,3,4]],default=2)

def build():
 with SOURCE.open(encoding='utf-8-sig',newline='') as f:raw=list(csv.DictReader(f))
 raw.sort(key=lambda r:r['ts']);rows=[]
 for r in raw:
  values={k:(float(r.get('salinity' if k=='conductivity' else k)) if r.get('salinity' if k=='conductivity' else k) else None) for k in PARAMS}
  rows.append(dict(ts=r['ts'],time=datetime.fromisoformat(r['ts']).timestamp(),site=r['site'],device=r['device'],values=values,error=r['sensor_error'],qc={},id=hashlib.sha256((r['site']+r['device']+r['ts']).encode()).hexdigest()[:24]))
 # Epoch values are used only for elapsed intervals; source labels keep local clock text.
 for i,r in enumerate(rows):
  r['gapMinutes']=(r['time']-rows[i-1]['time'])/60 if i else 0
  for key,config in PARAMS.items():
   v=r['values'][key];prev=rows[i-1]['values'][key] if i else None
   nxt=rows[i+1]['values'][key] if i+1<len(rows) else None
   tests={x:2 for x in ['missing','gross_range','site_plausible','spike','rate_of_change','flat_line']}
   if v is None or r['error']:tests['missing']=9
   else:
    tests['missing']=1
    tests['gross_range']=1 if config['gross'][0]<=v<=config['gross'][1] else 4
    if key=='turbidity' and 1000<=v<=1100:tests['gross_range']=3
    tests['site_plausible']=1 if config['plausible'][0]<=v<=config['plausible'][1] else 3
    if prev is not None and 0<r['gapMinutes']<=30:
     tests['rate_of_change']=3 if abs(v-prev)/(r['gapMinutes']/60)>config['roc'] else 1
    if prev is not None and nxt is not None and 0<r['gapMinutes']<=30 and 0<(rows[i+1]['time']-r['time'])<=1800:
     delta=abs(v-(prev+nxt)/2)
     tests['spike']=4 if delta>config['spike'][1] else 3 if delta>config['spike'][0] else 1
    start=i
    while start>0 and rows[start-1]['values'][key]==v and 0<rows[start]['gapMinutes']<=30:start-=1
    hours=(r['time']-rows[start]['time'])/3600
    tests['flat_line']=4 if hours>=12 else 3 if hours>=4 else 1
   r['qc'][key]=dict(flag=overall(tests),tests=tests)
 for r in rows:del r['time']
 # No derived oxygen columns retained: legacy salinity is conductivity.
 payload=dict(meta=dict(source=SOURCE.name,sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),count=len(rows),site='NuoiBien_2',device='nuoibienvien3',timezone='UTC+07:00',timezoneSource='prototype.md section 12: confirmed against ThingsBoard',mapping='salinity -> conductivity (mS/cm), per prototype.md section 1.2',qcVersion='qc-ui-0.2-provisional',depth=None,unitId=None,calibration=None,derivedOxygen='excluded_incorrect_legacy_salinity_assumption'),params=PARAMS,rows=rows)
 (ROOT/'data/observations.json').write_text(json.dumps(payload,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
 return payload

if __name__=='__main__':
 data=build();print('Prepared',len(data['rows']),'records; conductivity mapped; legacy derived oxygen excluded.')
