/* Read-only architecture view works locally and on the static demo. */
(async function(){
 let profile;try{const response=await fetch('architecture-profile.json');if(!response.ok)throw Error('Profile unavailable');profile=await response.json()}catch(e){console.error(e);return}
 window.aquaArchitectureProfile=profile;
 const existingTwin=C.currentTwin;C.currentTwin=function(d,c){return AquaContracts.enrich(profile,d,c,existingTwin(d,c))};
 navItems.push(['architecture','Architecture & evidence']);
 const previous=render;
 render=function(){
  if(active!=='architecture'){previous();return}
  $('#breadcrumb').textContent='Architecture & evidence';
  $('#nav').innerHTML=navItems.map(([id,label])=>`<a href="#${id}" class="${active===id?'active':''}"><span>${C.escape(label)}</span></a>`).join('');
  const age=(Date.now()-C.stamp(row().ts))/1000,stale=age<0||age>profile.synchronization.staleAfterSeconds;
  $('#page').innerHTML=heading('AQUATWIN / ARCHITECTURE PROFILE','Observation station digital representation','ISO/IEC 30188:2026 architecture viewpoints; ISO 23247 Parts 1-4 adapted as a manufacturing analogy. No conformity or certification claim.')+
   `<div class="notice"><div><strong>Historical replay · ${stale?'Stale / not operational':'Research snapshot'}</strong><p>The target is one observation station. Location, depth and calibration remain unconfirmed. Fish stock and equipment behavior are outside the implemented model.</p></div></div>`+
   frame('Target and canonical identity',`<p>Twin: <strong>${C.escape(profile.twinId)}</strong></p><p>Target: ${C.escape(profile.target.id)}</p><p>${C.escape(profile.scope)}</p><pre>${C.escape(JSON.stringify(profile.relationships,null,2))}</pre>`)+
   frame('Architecture responsibilities',Object.entries(profile.entities23247).map(([key,value])=>`<p><strong>${C.escape(key)}</strong>: ${C.escape(value)}</p>`).join(''))+
   frame('State and model boundaries',`<p>State kinds: ${profile.stateKinds.join(', ')}. Only observed state enters Ditto synchronization. Simulations remain separate.</p><p>water-scenario-1.0: research simulations only; operational prediction and actuation are disabled.</p><p>Profile ${C.escape(profile.profileVersion)} · Observation contract ${C.escape(profile.observationSchemaVersion)}</p>`)+
   frame('Remaining evidence and implementation gaps',`<ul>${profile.gaps.map(g=>`<li>${C.escape(g)}</li>`).join('')}</ul><a href="architecture-profile.json" download>Download architecture profile</a>`);
  bind();
 };
 if(data)render();
})();
