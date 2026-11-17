const assert=require('node:assert/strict');
(async()=>{
 const pages=await(await fetch('http://127.0.0.1:9334/json')).json();
 const ws=new WebSocket(pages.find(p=>p.type==='page').webSocketDebuggerUrl);
 await new Promise((resolve,reject)=>{ws.onopen=resolve;ws.onerror=reject});
 let id=0;const pending=new Map(),errors=[];
 ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id){const p=pending.get(m.id);pending.delete(m.id);m.error?p.reject(m.error):p.resolve(m.result)}else if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails.exception?.description||m.params.exceptionDetails.text)};
 const send=(method,params={})=>new Promise((resolve,reject)=>{const seq=++id;pending.set(seq,{resolve,reject});ws.send(JSON.stringify({id:seq,method,params}))});
 const evaluate=async expression=>{const r=await send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(r.exceptionDetails.exception?.description||r.exceptionDetails.text);return r.result.value};
 const pause=ms=>new Promise(r=>setTimeout(r,ms));
 try{
  await send('Runtime.enable');await send('Page.enable');
  await send('Page.navigate',{url:'http://127.0.0.1:8876/'});
  for(let i=0;i<60;i++){if(await evaluate("typeof data!=='undefined'&&!!data&&!!window.aquaArchitectureProfile"))break;await pause(100)}
  assert(await evaluate("C.currentTwin(data,100).attributes.targetId==='urn:aquatwin:station:nuoibien-2'"));
  await evaluate("document.querySelector('#advancedTools').click()");
  assert(await evaluate("!!document.querySelector('#modal a[href=\"#architecture\"]')"));
  await evaluate("document.querySelector('#modal').close();location.hash='architecture'");await pause(200);
  assert(await evaluate("document.querySelector('h1').textContent.includes('Observation station')"));
  assert(await evaluate("document.querySelector('#page').textContent.includes('No conformity')"));
  assert(await evaluate("document.querySelector('#page').textContent.includes('Stale')"));
  await send('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:1,mobile:true});
  assert.equal(await evaluate('document.documentElement.scrollWidth>innerWidth'),false,'architecture mobile overflow');
  await evaluate("location.hash='overview'");await pause(150);
  assert.equal(await evaluate("document.querySelectorAll('#nav a').length"),6);
  assert.deepEqual(errors,[]);
  console.log('PASS browser: profile loading, enriched twin, tools navigation, architecture rendering, stale label, mobile layout and overview regression.');
 }finally{ws.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
