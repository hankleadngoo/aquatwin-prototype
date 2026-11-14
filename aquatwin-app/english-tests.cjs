const fs=require('node:fs'),assert=require('node:assert/strict'),cp=require('node:child_process');
const C=require('./dist/core.js');
const vietnamese=/[\u0102\u0103\u0110\u0111\u0128\u0129\u0168\u0169\u01a0\u01a1\u01af\u01b0\u1ea0-\u1ef9]/u;
for(const name of fs.readdirSync('dist').filter(n=>/\.(js|html)$/.test(n))){const text=fs.readFileSync('dist/'+name,'utf8');assert(!vietnamese.test(text),'Vietnamese UI text remains in '+name)}
assert(fs.readFileSync('dist/index.html','utf8').includes('lang="en"'));
assert.equal(C.flagNames[1],'QC passed');assert.equal(C.flagNames[9],'Missing data');
const d=JSON.parse(fs.readFileSync('dist/data.json','utf8'));
assert.deepEqual(Object.values(d.params).map(p=>p.label),['Temperature','Conductivity','pH','Dissolved oxygen','Turbidity']);
assert.equal(d.rows.length,1333);
console.log('PASS English: UI and model messages have no Vietnamese diacritics, document language and parameter/QC labels are English.');
