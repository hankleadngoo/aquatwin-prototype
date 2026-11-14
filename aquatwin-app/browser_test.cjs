const fs=require('node:fs');
const assert=require('node:assert/strict');
(async()=>{
 const pages=await (await fetch('http://127.0.0.1:9333/json')).json();
 const ws=new WebSocket(pages.find(p=>p.type==='page').webSocketDebuggerUrl);
 await new Promise((res,rej)=>{ws.onopen=res;ws.onerror=rej});
 let seq=0;const pending=new Map(),errors=[];
 ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id){const p=pending.get(m.id);if(p){pending.delete(m.id);m.error?p.reject(m.error):p.resolve(m.result)}}else if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails.text+': '+(m.params.exceptionDetails.exception?.description||''))};
 const send=(method,params={})=>new Promise((resolve,reject)=>{const id=++seq;pending.set(id,{resolve,reject});ws.send(JSON.stringify({id,method,params}))});
 const evaluate=async expression=>{const r=await send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(r.exceptionDetails.exception?.description||r.exceptionDetails.text);return r.result.value};
 const pause=ms=>new Promise(r=>setTimeout(r,ms));
 await send('Runtime.enable');await send('Page.enable');
 await send('Emulation.setDeviceMetricsOverride',{width:1440,height:1080,deviceScaleFactor:1,mobile:false});
 await send('Page.navigate',{url:'http://127.0.0.1:8765/'});
 for(let i=0;i<40;i++){if(await evaluate("typeof data!=='undefined'&&!!data&&!!document.querySelector('h1')"))break;await pause(200)}
 assert.equal(await evaluate('data.rows.length'),1333);
 const screen=await send('Page.captureScreenshot',{format:'png'});fs.writeFileSync('qa-overview.png',Buffer.from(screen.data,'base64'));
 assert.equal(await evaluate("document.querySelectorAll('#nav a').length"),6);
 const originalValues=await evaluate('JSON.stringify(row().values)');
 for(const key of ['temperature','DO','pH','conductivity','turbidity']){
  await evaluate(`location.hash='problem-${key}'`);await pause(100);
  assert(await evaluate("!!document.querySelector('#scenarioForm')"));
  await evaluate("document.querySelector('#scenarioValue').value='10';document.querySelector('#scenarioForm').requestSubmit()");
  assert(await evaluate("!!document.querySelector('#problemScenario .pill')"));
  assert.equal(await evaluate('JSON.stringify(row().values)'),originalValues);
  await evaluate("document.querySelector('#rangeLow').value='1';document.querySelector('#rangeHigh').value='20';document.querySelector('#rangeForm').requestSubmit()");
  assert.equal(await evaluate(`problemSettings['${key}'].status`),'user_trial_only');
  await evaluate("document.querySelector('#clearRange').click()");
  assert.equal(await evaluate(`problemSettings['${key}']===undefined`),true);
  assert.equal(await evaluate('document.documentElement.scrollWidth>innerWidth'),false,'problem overflow '+key);
 }
 await evaluate("location.hash='overview'");await pause(100);

 for(const name of ['twin','ditto','quality','events','insights','lab','journal','data','overview']){
  await evaluate(`location.hash='${name}'`);await pause(120);
  assert(await evaluate("!!document.querySelector('h1')"),name);
  assert.equal(await evaluate("/[\\u0102\\u0103\\u0110\\u0111\\u0128\\u0129\\u0168\\u0169\\u01a0\\u01a1\\u01af\\u01b0\\u1ea0-\\u1ef9]/u.test(document.body.innerText)"),false,'Non-English UI on '+name);
  assert.equal(await evaluate('document.documentElement.scrollWidth>innerWidth'),false,'overflow '+name);
 }
 await evaluate("location.hash='ditto'");await pause(120);await evaluate("document.querySelector('#checkDitto').click()");await pause(200);assert.equal(await evaluate("dittoStatus.state"),'not_configured');assert.equal(await evaluate("document.querySelector('#syncDitto').disabled"),true);
 await evaluate("active='overview';cursor=10;render()");assert.equal(await evaluate("C.currentTwin(data,cursor).features.DO.properties.observed.ts"),await evaluate('data.rows[10].ts'));
 await evaluate("location.hash='lab'");await pause(120);await evaluate("document.querySelector('#runScenario').click()");assert(await evaluate("document.querySelector('#scenarioResult').textContent.includes('simulated')"));
 await evaluate("location.hash='journal'");await pause(120);
 await evaluate("document.querySelector('#entryOwner').value='QA';document.querySelector('#entryNote').value='Kiểm tra prototype';document.querySelector('#journalForm').requestSubmit()");
 assert(await evaluate("journal.some(e=>e.owner==='QA')"));
 await evaluate("journal=journal.filter(e=>e.owner!=='QA');localStorage.setItem('aquatwin-journal-v1',JSON.stringify(journal))");
 await evaluate("cursor=data.rows.length-1;location.hash='overview'");await pause(120);
 await evaluate("document.querySelector('#toast').classList.remove('show')");
 await send('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:1,mobile:true});await pause(200);
 assert.equal(await evaluate('document.documentElement.scrollWidth>innerWidth'),false,'mobile overflow');
 const mobile=await send('Page.captureScreenshot',{format:'png'});fs.writeFileSync('qa-mobile.png',Buffer.from(mobile.data,'base64'));
 await evaluate("cursor=data.rows.length-1;forecastKey='DO';location.hash='forecast'");await pause(120);
 await evaluate("document.querySelector('#longForecastForm').requestSubmit()");
 assert.equal(await evaluate('forecastResult.ok'),true);assert.equal(await evaluate('forecastResult.points.length'),193);
 const snapshotBefore=await evaluate('JSON.stringify(row().values)');
 await evaluate("document.querySelector('#longForecastRate').value='-0.4';document.querySelector('#longForecastForm').requestSubmit()");
 assert.equal(await evaluate('forecastResult.ratePerDay'),-.4);assert.equal(await evaluate('JSON.stringify(row().values)'),snapshotBefore);
 await evaluate("document.querySelector('#longForecastHours').value='24';document.querySelector('#longForecastHours').dispatchEvent(new Event('change'));document.querySelector('#longForecastForm').requestSubmit()");
 assert.equal(await evaluate('forecastResult.points.length'),97);
 await evaluate("document.querySelector('#evaluateLongForecast').click()");assert((await evaluate('forecastEvaluation.metrics[24].count'))>0);
 assert.equal(await evaluate('document.documentElement.scrollWidth>innerWidth'),false,'forecast mobile overflow');
 await send('Emulation.setDeviceMetricsOverride',{width:1440,height:1080,deviceScaleFactor:1,mobile:false});await pause(150);
 const forecastShot=await send('Page.captureScreenshot',{format:'png'});fs.writeFileSync('qa-forecast.png',Buffer.from(forecastShot.data,'base64'));
 assert.deepEqual(errors,[]);console.log('PASS browser: 6 farmer navigation items, 5 problem scenarios and trial ranges, technical screens + Ditto unconfigured state, no JS exceptions, desktop/mobile overflow, replay cursor, fault sandbox, journal persistence.');
 ws.close();
})().catch(e=>{console.error(e);process.exit(1)});
