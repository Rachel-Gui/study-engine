import test from 'node:test';
import assert from 'node:assert/strict';
import {defaults,Experiment,changes,controlledSeries,illustration,record,prompt,materialDefaults,materialOptions,materialExperiment} from '../assets/generative/core.mjs';

test('only successful single-variable tests advance previous/current; original stays fixed',()=>{
  const lab=new Experiment(),draft={...defaults};
  const first=lab.test(draft,true);assert.equal(lab.previous,null);assert.equal(lab.original,first);
  draft.material='Concrete';assert.equal(lab.current.settings.material,'Timber');
  const second=lab.test(draft,true);assert.equal(lab.previous,first);assert.equal(lab.current,second);
  assert.throws(()=>lab.test({...draft,material:'Rammed earth',context:'Urban plaza'},true),/exactly one/);
  assert.throws(()=>lab.test({...draft,seed:-2},true),/whole-number seed/);
  assert.equal(lab.current,second);assert.equal(lab.previous,first);assert.equal(lab.tests,2);
  const third=lab.test({...draft,material:'Rammed earth'},true);assert.equal(lab.previous,second);assert.equal(lab.original,first);assert.equal(lab.current,third);
});

test('real controlled sweeps vary only the named setting and never substitute schematics',()=>{
  const expected={seed:[2,4],guidance:[3,5],negative:[11,2],steps:[13,4],resolution:[12,3]};
  for(const [key,[task,count]] of Object.entries(expected)){
    const samples=controlledSeries(key);assert.equal(samples.length,count);
    const baseline=samples[0].settings;
    for(const sample of samples){
      const changed=Object.keys(baseline).filter(k=>baseline[k]!==sample.settings[k]);
      assert(changed.every(k=>key==='resolution'?['width','height'].includes(k):k===key));
      assert.equal(sample.settings.prompt,baseline.prompt);
      assert.match(sample.src,/assets\/generative\/real-experiments\/.+\.png$/);
      assert.match(sample.alt,new RegExp('Task '+task+','));
    }
  }
  assert.deepEqual(controlledSeries('guidance').map(s=>s.settings.guidance),[2,5,7.5,10,15]);
  assert.deepEqual(controlledSeries('steps').map(s=>s.settings.seed),[321,321,321,321]);
  assert.throws(()=>controlledSeries('material'),/No recorded/);
  assert.match(illustration(defaults),/Authored teaching illustration/); // Arbitrary library prompts never use pavilion outputs.
  assert.equal(illustration(defaults),illustration({...defaults}));
});

test('controlled material outputs match their exact prompt and only successful tests advance history',()=>{
  const lab=new Experiment({materialOnly:true});
  assert.deepEqual(materialOptions.material,['Timber','Concrete','Steel and glass','Rammed earth']);
  for(const material of materialOptions.material){
    const previous=lab.current,next=lab.test({...materialDefaults,material},true);
    assert.equal(next.svg,null);assert.equal(lab.previous,previous);
    assert.equal(next.prompt,materialExperiment.promptTemplate.replace('{material}',material.toLowerCase()));
    assert.equal(next.sample.seed,200);assert.equal(next.sample.width,512);assert.equal(next.sample.height,512);
    assert.match(next.sample.src,/real-experiments\/material\/material-/);
  }
  const previous=lab.previous,current=lab.current;
  assert.throws(()=>lab.test({...materialDefaults,material:'Brick'},true),/No recorded/);
  assert.throws(()=>lab.test({...materialDefaults,seed:201},true),/non-material inputs fixed/);
  assert.throws(()=>lab.test({...materialDefaults,width:768},true),/non-material inputs fixed/);
  assert.throws(()=>lab.test(current.settings,true),/exactly one/);
  assert.equal(lab.current,current);assert.equal(lab.previous,previous);
  lab.reset();assert.equal(lab.current,null);assert.equal(lab.previous,null);
});

test('records retain initial/current settings, reasoning and immediate previous; reset is local',()=>{
  const a=new Experiment(),b=new Experiment();a.test(defaults);a.test({...defaults,material:'Concrete'},true);
  const notes={designIntent:'Public reading space',expectedChange:'Material only',observedChange:'Roof also changed',unexpectedChanges:'Entrance moved',architecturalLimitations:'Check access',informationNeeded:'Dimensions and schedules',nextStep:'Trace and validate',reflection:'An image is a hypothesis'};
  const result=record(a,notes);for(const [k,v] of Object.entries(notes))assert.equal(result[k],v);
  assert.equal(result.changedVariables[0].key,'material');assert.equal(b.current,null);
  a.reset();assert.equal(a.previous,null);assert.equal(a.original,null);assert.equal(a.current,null);assert.equal(a.tests,0);
});
