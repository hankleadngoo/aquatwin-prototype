/* Research simulator, not a validated biological or actuator-response model. */
(function(root){
const core=typeof module!=='undefined'?require('./core.js'):root.AquaCore;
const version='water-scenario-1.0';
const features=ts=>{const h=Number(ts.slice(11,13))+Number(ts.slice(14,16))/60+Number(ts.slice(17,19))/3600;return [1,Math.sin(2*Math.PI*h/24),Math.cos(2*Math.PI*h/24)]};
function solve(A,b){const M=A.map((r,i)=>[...r,b[i]]);for(let i=0;i<3;i++){let best=i;for(let j=i+1;j<3;j++)if(Math.abs(M[j][i])>Math.abs(M[best][i]))best=j;[M[i],M[best]]=[M[best],M[i]];if(Math.abs(M[i][i])<1e-12)throw Error('Insufficient seasonal information');const v=M[i][i];for(let k=i;k<4;k++)M[i][k]/=v;for(let j=0;j<3;j++)if(j!==i){const q=M[j][i];for(let k=i;k<4;k++)M[j][k]-=q*M[i][k]}}return M.map(r=>r[3])}
const dot=(a,b)=>a.reduce((s,v,i)=>s+v*b[i],0);
const localTS=t=>new Date(t+7*3600000).toISOString().slice(0,23);
function fit(data,cursor,key,{allowSuspect=false}={}){
 if(!Number.isInteger(cursor)||cursor<0||cursor>=data.rows.length||!core.keys.includes(key))return {ok:false,reason:'Invalid cursor or parameter'};
 const initial=data.rows[cursor],end=core.stamp(initial.ts),start=end-7*86400000;
 if(initial.values[key]==null||initial.error)return {ok:false,reason:'The initial measurement is missing. Choose an origin with a reading.'};
 const initialQC=core.qcAt(data.rows,cursor,key,cursor).flag;
 if(initialQC!==1&&!allowSuspect)return {ok:false,reason:'The initial reading has not passed QC. Choose a QC-passed origin or explicitly accept it as a hypothetical initial condition.'};
 if(initialQC===4||initialQC===9)return {ok:false,reason:'Failed or missing initial readings cannot initialize a simulation.'};
 const samples=[];for(let i=0;i<=cursor;i++){const r=data.rows[i];if(core.stamp(r.ts)<start||r.values[key]==null||r.error||core.qcAt(data.rows,i,key,cursor).flag!==1)continue;samples.push({i,ts:r.ts,t:core.stamp(r.ts),v:r.values[key],x:features(r.ts)})}
 if(samples.length<96||(samples.at(-1).t-samples[0].t)<48*3600000)return {ok:false,reason:'At least 96 QC-passed samples spanning 48 hours within the previous seven days are required.'};
 const A=Array.from({length:3},()=>[0,0,0]),b=[0,0,0];for(const r of samples)for(let i=0;i<3;i++){b[i]+=r.x[i]*r.v;for(let j=0;j<3;j++)A[i][j]+=r.x[i]*r.x[j]};for(let i=0;i<3;i++)A[i][i]+=1e-8;
 let beta;try{beta=solve(A,b)}catch{return {ok:false,reason:'Insufficient data to estimate the daily cycle.'}}
 for(const r of samples)r.res=r.v-dot(beta,r.x);
 const pairs=[];let den=0,num=0;for(let i=1;i<samples.length;i++){const a=samples[i-1],r=samples[i],dt=(r.t-a.t)/900000;if(dt>0&&dt<=2){pairs.push([a,r,dt]);num+=a.res*r.res;den+=a.res*a.res}}
 if(pairs.length<48)return {ok:false,reason:'At least 48 sufficiently close sample pairs are required to estimate dynamics.'};
 const phi=Math.max(0,Math.min(.995,den>1e-12?num/den:0));
 let noise=pairs.map(([a,r,dt])=>(r.res-Math.pow(phi,dt)*a.res)/Math.sqrt((1-Math.pow(phi,2*dt))/(1-phi*phi)));
 const noiseMean=noise.reduce((a,b)=>a+b,0)/noise.length;noise=noise.map(v=>v-noiseMean);
 return {ok:true,version,key,cursor,sourceTime:initial.ts,sourceId:initial.id,inputQC:initialQC,initial:initial.values[key],beta,phi,noise,samples:samples.length,pairs:pairs.length,windowStart:samples[0].ts,windowEnd:initial.ts,assumptions:['Repeating 24h pattern','Residual persistence fitted on valid pairs','No weather, flow, biomass or equipment effects'],warnings:initialQC!==1?['Initialized with a suspect reading explicitly accepted as a user assumption.']:[]};
}
function rng(seed){let s=seed>>>0;return ()=>{s=(Math.imul(1664525,s)+1013904223)>>>0;return s/4294967296}}
function quantile(sorted,q){const at=(sorted.length-1)*q,i=Math.floor(at);return sorted[i]+(sorted[Math.min(i+1,sorted.length-1)]-sorted[i])*(at-i)}
function deterministic(model,hours,ratePerDay=0){const start=core.stamp(model.sourceTime),res=model.initial-dot(model.beta,features(model.sourceTime));return dot(model.beta,features(localTS(start+hours*3600000)))+Math.pow(model.phi,hours*4)*res+ratePerDay*hours/24}
function simulate(data,cursor,key,options={}){
 const hours=options.hours??48,rate=Number(options.ratePerDay??0),seed=options.seed??20261114,paths=options.paths??120;
 if(![24,48].includes(hours)||!Number.isFinite(rate)||Math.abs(rate)>1e4||!Number.isInteger(paths)||paths<10||paths>500)return {ok:false,reason:'Invalid simulation parameters.'};
 const model=fit(data,cursor,key,options);if(!model.ok)return model;
 const n=hours*4,start=core.stamp(model.sourceTime),random=rng(seed),base=Array.from({length:n+1},()=>[]),scenario=Array.from({length:n+1},()=>[]);
 const initialResidual=model.initial-dot(model.beta,features(model.sourceTime));
 for(let j=0;j<paths;j++){let residual=initialResidual;base[0].push(model.initial);scenario[0].push(model.initial);for(let i=1;i<=n;i++){residual=model.phi*residual+model.noise[Math.floor(random()*model.noise.length)];const value=dot(model.beta,features(localTS(start+i*900000)))+residual;base[i].push(value);scenario[i].push(value+rate*i/96)}}
 const points=base.map((vs,i)=>{vs.sort((a,b)=>a-b);scenario[i].sort((a,b)=>a-b);return {ts:localTS(start+i*900000),hours:i/4,base:deterministic(model,i/4),baseP10:quantile(vs,.1),baseP90:quantile(vs,.9),scenario:deterministic(model,i/4,rate),scenarioP10:quantile(scenario[i],.1),scenarioP90:quantile(scenario[i],.9)}});
 const limits=data.params[key].gross,invalid=points.some(p=>p.scenarioP10<limits[0]||p.scenarioP90>limits[1]);
 return {ok:true,stateKind:'simulated',modelVersion:version,key,sourceTime:model.sourceTime,inputSnapshotId:model.sourceId,inputQC:model.inputQC,hours,ratePerDay:rate,seed,paths,training:{samples:model.samples,pairs:model.pairs,start:model.windowStart,end:model.windowEnd},parameters:{beta:model.beta,phi:model.phi},warnings:[...model.warnings,...(invalid?['The simulation band exceeds the trial QC domain; values are not clipped to conceal this.']:[])],intervalMeaning:'P10–P90 across simulated trajectories; forecast probabilities have not been calibrated.',points};
}
function evaluate(data,key){const first=core.stamp(data.rows[0].ts),last=core.stamp(data.rows.at(-1).ts),records=[];
 for(let i=0;i<data.rows.length;i++){const origin=data.rows[i],time=core.stamp(origin.ts);if(time<first+3*86400000||time>last-24*3600000)continue;if(records.some(r=>Math.abs(core.stamp(r.sourceTime)-time)<23.5*3600000))continue;const model=fit(data,i,key);if(!model.ok)continue;const record={sourceTime:origin.ts,modelVersion:version,trainingEnd:model.windowEnd,horizons:{}};
  for(const horizon of [24,48]){const target=time+horizon*3600000;if(target>last)continue;let nearest=-1,distance=Infinity;for(let j=i+1;j<data.rows.length;j++){const d=Math.abs(core.stamp(data.rows[j].ts)-target);if(d<distance){distance=d;nearest=j}if(core.stamp(data.rows[j].ts)>target+900000)break}if(distance>600000||nearest<0)continue;const actual=data.rows[nearest];const tests={...actual.qc[key].tests,spike:2};if(actual.values[key]==null||actual.error||core.aggregate(tests)!==1)continue;const elapsed=(core.stamp(actual.ts)-time)/3600000;record.horizons[horizon]={actualTime:actual.ts,actual:actual.values[key],simulation:deterministic(model,elapsed),persistence:origin.values[key],elapsedHours:elapsed}}
  records.push(record);
 }
 const metrics={};for(const h of [24,48]){const eligible=records.map(r=>r.horizons[h]).filter(Boolean);const mae=method=>eligible.length?eligible.reduce((s,r)=>s+Math.abs(r[method]-r.actual),0)/eligible.length:null;metrics[h]={count:eligible.length,simulationMAE:mae('simulation'),persistenceMAE:mae('persistence'),eligibleOriginTimes:records.filter(r=>r.horizons[h]).map(r=>r.sourceTime)}}
 return {key,modelVersion:version,design:'Rolling daily origins; only past 7d fitted; held-out endpoints at 24/48h within 10min; QC-filtered, exploratory.',metrics,records};
}
const api={version,fit,simulate,evaluate,deterministic};if(typeof module!=='undefined')module.exports=api;root.WaterForecast=api;
})(typeof window==='undefined'?globalThis:window);
