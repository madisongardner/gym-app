export function validateExport(data){
 if(!Array.isArray(data)||!data.length)throw Error('Choose an RP JSON export containing training blocks.');
 const ids=new Set();
 for(const b of data){if(!b||b.id==null||!Array.isArray(b.weeks)||ids.has(b.id))throw Error('Invalid or duplicate block.');ids.add(b.id);
 for(const w of b.weeks){if(!Array.isArray(w.days))throw Error('Invalid week.');for(const d of w.days){if(!Array.isArray(d.exercises))throw Error('Invalid workout.');for(const e of d.exercises){if(typeof e.name!=='string'||!Array.isArray(e.sets))throw Error('Invalid exercise.');for(const s of e.sets){if(!s||typeof s.status!=='string')throw Error('Invalid set.');}}}}}
 return data;
}
export function blankSession(day,block){return {id:crypto.randomUUID(),createdAt:new Date().toISOString(),name:day.label||'Workout',block:block.name||'Imported plan',unit:block.unit||'lb',exercises:day.exercises.map(e=>({id:crypto.randomUUID(),name:e.name,sets:e.sets.map(s=>({weight:s.weightTarget??(s.weight>=0?s.weight:''),reps:s.repsTarget??(s.reps>=0?s.reps:''),done:false})),feedback:{}}))};}
export function mergeBlocks(old,next){const m=new Map(old.map(b=>[b.id,b]));next.forEach(b=>m.set(b.id,b));return [...m.values()];}
export function numberValue(v){if(v==='')return '';const n=Number(v);if(!Number.isFinite(n)||n<0)throw Error('Enter a nonnegative number.');return n;}
export const demo=[{id:'demo',name:'Starter · upper body',unit:'lb',weeks:[{days:[{label:'Upper body',exercises:[{name:'Dumbbell bench press',sets:[{weight:0,reps:10,status:'ready'},{weight:0,reps:10,status:'ready'}]},{name:'Cable row',sets:[{weight:0,reps:10,status:'ready'},{weight:0,reps:10,status:'ready'}]}]}]}]}];
