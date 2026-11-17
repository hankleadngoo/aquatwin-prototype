/* Project-specific architecture contract. No standards-conformity claim. */
(function(root){
function enrich(profile,data,cursor,snapshot){
 const r=data.rows[cursor];
 if(r.site!==profile.siteId||r.device!==profile.deviceId)throw Error('Unregistered observation source');
 snapshot.attributes={...snapshot.attributes,targetId:profile.target.id,architectureProfile:profile.profileVersion,stateContractVersion:profile.observationSchemaVersion,stateKinds:profile.stateKinds,lifecycle:'research-prototype'};
 for(const [key,param] of Object.entries(profile.parameters)){
  const o=snapshot.features[key].properties.observed;
  if(o.unit!==param.unit)throw Error('Observation unit does not match architecture profile');
  Object.assign(o,{stateKind:'observed',eventId:r.id+':'+key,targetId:profile.target.id,phenomenonTime:r.ts+'+07:00',receivedAt:null,provenance:{inputSnapshotId:r.id,sourceSnapshotSha256:data.meta.sha256,mappingVersion:profile.mappingVersion,qcVersion:data.meta.qcVersion,receivedAtStatus:'unavailable_in_snapshot',sensorIdentityScope:'acquisition_device_not_individual_probe'}});
 }
 snapshot.features.health.properties.freshnessEndpoint='/api/state/health';return snapshot;
}
function modelGate(profile,id,purpose){const m=profile.models.find(m=>m.id===id);return {allowed:!!m&&purpose==='research-simulation'&&m.stateKind==='simulated',reason:purpose==='research-simulation'?'Research use only; independent operational validation is pending.':'Operational prediction and actuation are blocked for this model.'}}
const api={enrich,modelGate};if(typeof module!=='undefined')module.exports=api;root.AquaContracts=api;
})(typeof window==='undefined'?globalThis:window);
