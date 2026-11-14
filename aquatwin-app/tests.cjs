const assert=require('node:assert/strict');
const fs=require('node:fs');
const C=require('./dist/core.js');
const data=JSON.parse(fs.readFileSync('./dist/data.json','utf8'));
assert.equal(data.rows.length,1333);
assert.equal(data.rows.filter(r=>r.error).length,3);
assert.equal(data.meta.derivedOxygen,'excluded_incorrect_legacy_salinity_assumption');
assert(data.rows.every(r=>!('salinity' in r.values)));
assert(data.rows.every((r,i)=>!i||C.stamp(r.ts)>=C.stamp(data.rows[i-1].ts)));
const cursor=100;
const t=C.currentTwin(data,cursor);
assert.equal(t.features.DO.properties.observed.ts,data.rows[cursor].ts);
assert.equal(C.qcAt(data.rows,cursor,'DO',cursor).tests.spike,2);
assert(!('predicted' in t.features.DO.properties));
for(const key of C.keys){const good=t.features[key].properties.last_good;if(good)assert(C.stamp(good.ts)<=C.stamp(data.rows[cursor].ts))}
const errorIndex=data.rows.findIndex(r=>r.error);
for(const key of C.keys){assert.equal(C.qcAt(data.rows,errorIndex,key,errorIndex).flag,9);assert.equal(C.currentTwin(data,errorIndex).features[key].properties.observed.value,null)}
assert(C.events(data,0).every(e=>e.i===0));
assert(C.events(data,errorIndex).some(e=>e.kind==='device'));
assert(C.events(data,errorIndex).some(e=>e.kind==='gap'));
const counts=C.summary(data,100);assert.equal(Object.values(counts).reduce((a,b)=>a+b,0),505);
const b=C.backtest(data,'DO');assert(b.count>0);assert(b.pairs.every(p=>p.i>=Math.floor(data.rows.length*.7)));assert(b.pairs.every(p=>p.elapsedMinutes<=30));
assert.equal(C.escape('<script>'),'&lt;script&gt;');
assert.equal(C.stamp('2026-11-12T00:00:00'),Date.parse('2026-11-11T17:00:00Z'));
console.log('PASS: source mapping, chronology, missing values, no look-ahead at replay cursor, last_good, events, QC counts, backtest split, escaping and timezone.');
