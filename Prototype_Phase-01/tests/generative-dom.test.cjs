/* DOM behavior tests; jsdom is a test-only dependency, never a site dependency.
   NODE_PATH=/path/to/test/node_modules node --test tests/generative-dom.test.cjs */
const {JSDOM}=require('jsdom');
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {pathToFileURL}=require('node:url');
const site=path.join(__dirname,'../site');
const modulePromise=import(pathToFileURL(path.join(__dirname,'../assets/generative/lab.mjs')));
async function open(slug){
  const dom=new JSDOM(fs.readFileSync(path.join(site,slug),'utf8'),{url:'http://localhost/'+slug});
  dom.window.HTMLCanvasElement.prototype.getContext=()=>({createImageData:(w,h)=>({data:new Uint8ClampedArray(w*h*4)}),putImageData(){}});
  const {initialize}=await modulePromise;
  const root=dom.window.document.querySelector('[data-genlab]');
  global.document=dom.window.document;initialize(root);
  const $=s=>root.querySelector(s);
  const change=(selector,value,event='input')=>{const el=$(selector);el.value=value;el.dispatchEvent(new dom.window.Event(event,{bubbles:true}));};
  return {dom,root,$,change,click:s=>$(s).click(),status:()=>$('[data-status]').textContent};
}

test('diffusion requires prediction, enables slider and reveals explanation after interaction',async()=>{
  const t=await open('1-2-diffusion-playground.html');
  t.click('[data-start]');assert(t.$('[data-denoise]').disabled);
  t.change('textarea','Structure will emerge before fine detail.');t.click('[data-start]');assert(!t.$('[data-denoise]').disabled);
  t.change('[data-denoise]',15);assert.equal(t.$('canvas').style.opacity,'0.5');assert(!t.$('[data-explanation]').hidden);
  t.change('[data-denoise]',30);assert.equal(t.$('canvas').style.opacity,'0');assert.equal(t.$('[data-count]').textContent,'30 / 30');
});

test('prompt edits and rejected tests preserve successful comparison pair',async()=>{
  const t=await open('1-3-architectural-prompt-builder.html');t.click('[data-generate]');assert.equal(t.$('[data-comparison]').innerHTML,'');
  t.change('[data-note=expectedChange]','A timber pavilion.');t.click('[data-generate]');
  const first=t.$('[data-comparison]').innerHTML;assert(!first.includes('PREVIOUS GENERATION'));
  t.change('[data-setting=material]','Concrete','change');assert.equal(t.$('[data-comparison]').innerHTML,first);
  t.click('[data-generate]');const second=t.$('[data-comparison]').innerHTML;assert(second.includes('PREVIOUS — Timber'));assert(second.includes('CURRENT — Concrete'));assert(second.includes('Timber → Concrete'));
  assert.equal(t.root.querySelectorAll('[data-setting]').length,1);
  assert.equal(t.$('[data-comparison]').querySelectorAll('svg').length,0);
  assert.equal(t.$('[data-comparison]').querySelectorAll('img').length,2);
  assert.match(t.$('[data-prompt]').textContent,/A small pavilion in a public garden/);
  for(const image of t.$('[data-comparison]').querySelectorAll('img'))assert(fs.existsSync(path.join(site,image.getAttribute('src'))));
  assert(!t.$('[data-answer]').hidden);
  t.click('[data-generate]');assert.equal(t.$('[data-comparison]').innerHTML,second);assert.match(t.status(),/exactly one/);
  t.change('[data-setting=material]','Steel and glass','change');t.click('[data-generate]');assert.match(t.$('[data-comparison]').textContent,/PREVIOUS — Concrete/);assert.match(t.$('[data-comparison]').textContent,/CURRENT — Steel and glass/);
  t.click('[data-reset]');assert.equal(t.$('[data-comparison]').innerHTML,'');assert.equal(t.$('[data-note=expectedChange]').value,'');
});

test('real notebook experiments unlock progressively and retain earlier outputs and predictions',async()=>{
  const t=await open('1-4-generation-control-lab.html');
  const stages=[...t.root.querySelectorAll('[data-experiment]')];
  assert(stages[1].hidden);
  for(let i=0;i<stages.length;i++){
    const stage=stages[i],area=stage.querySelector('textarea');assert(!stage.hidden);
    stage.querySelector('[data-reveal]').click();assert.equal(stage.querySelector('[data-series]').innerHTML,'');
    area.value='Predict a tradeoff, not guaranteed correctness.';
    stage.querySelector('[data-reveal]').click();assert(!stage.querySelector('[data-explanation]').hidden);
    const task=[2,3,11,13,12][i],count=[4,5,2,4,3][i];
    assert.equal(stage.querySelectorAll('.ga-generation').length,count);
    assert.equal(stage.querySelectorAll('[data-series] svg').length,0);
    assert.equal(stage.querySelectorAll('[data-series] img').length,count);
    [...stage.querySelectorAll('[data-source-task]')].forEach((card,j)=>{
      assert.equal(Number(card.dataset.sourceTask),task);assert.equal(Number(card.dataset.sourcePanel),j+1);
      const img=card.querySelector('img');assert.match(img.getAttribute('src'),/real-experiments/);
      assert(fs.existsSync(path.join(site,img.getAttribute('src'))));
    });
    if(stage.querySelector('[data-unlock]'))stage.querySelector('[data-unlock]').click();
  }
  assert.equal(stages[0].querySelectorAll('.ga-generation').length,4);
});

test('critic and pipeline require observation before revealing reasoning',async()=>{
  const c=await open('1-5-architectural-ai-critic.html');c.click('[data-critique-reveal]');assert(c.$('[data-critique-output]').hidden);
  c.change('textarea','The cantilever is attractive, but its support is unclear.');c.$('[data-critique]').checked=true;c.click('[data-critique-reveal]');assert(!c.$('[data-critique-output]').hidden);assert.match(c.$('[data-critique-output]').textContent,/You flagged/);
  const p=await open('1-6-translate-before-evaluating.html');p.click('[data-start]');assert(p.$('[data-pipeline-step]').disabled);
  p.change('textarea','Dimensions and thermal properties');p.click('[data-start]');
  const buttons=[...p.root.querySelectorAll('[data-pipeline-step]')];
  buttons.forEach((button,i)=>{assert(!button.disabled);button.click();assert.equal(button.getAttribute('aria-pressed'),'true');if(i<6)assert(!buttons[i+1].disabled);});
  assert.match(p.$('[data-pipeline-output]').textContent,/uncertainty/);
});

test('eight-stage workflow retains inputs, exact one-change history and downloadable record',async()=>{
  const t=await open('1-7-one-experiment-from-intent-to-evaluation.html');
  const visible=()=>[...t.root.querySelectorAll('[data-stage]')].filter(el=>!el.hidden).map(el=>+el.dataset.stage);
  t.click('[data-next]');assert.deepEqual(visible(),[0]);
  t.change('[data-note=designIntent]','A neighborhood library');t.click('[data-next]');assert.deepEqual(visible(),[1]);
  t.click('[data-next]');t.click('[data-next]');assert.deepEqual(visible(),[2]);
  t.click('[data-generate]');t.click('[data-next]');assert.deepEqual(visible(),[3]);
  t.click('[data-retest]');assert.match(t.status(),/Predict/);
  t.change('[data-note=expectedChange]','Material only');t.click('[data-retest]');t.click('[data-next]');assert.deepEqual(visible(),[4]);
  assert.match(t.$('[data-comparison]').textContent,/Timber → Concrete/);
  t.change('[data-note=observedChange]','The roofline and openings changed.');t.change('[data-note=unexpectedChanges]','Entrance moved');t.click('[data-next]');
  t.change('[data-note=architecturalLimitations]','Need a checked circulation plan');t.click('[data-next]');
  t.change('[data-note=informationNeeded]','Geometry, assemblies, schedules and HVAC');t.change('[data-note=nextStep]','Trace then verify');t.click('[data-next]');assert.deepEqual(visible(),[7]);
  t.change('[data-note=reflection]','<img src=x onerror=alert(1)> is text, not markup');t.click('[data-record]');
  assert.match(t.$('[data-record-output]').textContent,/A neighborhood library/);assert.match(t.$('[data-record-output]').textContent,/ORIGINAL — Timber/);assert.equal(t.$('[data-record-output]').querySelectorAll('img').length,2);assert.equal(t.$('[data-record-output]').querySelectorAll('img[src=x]').length,0);
  t.click('[data-back]');t.click('[data-back]');t.click('[data-back]');t.click('[data-back]');assert.deepEqual(visible(),[3]);
  t.change('[data-change-value]','Rammed earth','change');t.click('[data-retest]');t.click('[data-next]');assert.match(t.$('[data-comparison]').textContent,/Concrete → Rammed earth/);
  t.click('[data-next]');t.click('[data-next]');t.click('[data-next]');
  let downloaded;const oldCreate=URL.createObjectURL,oldRevoke=URL.revokeObjectURL;
  URL.createObjectURL=blob=>{downloaded=blob;return 'blob:test';};URL.revokeObjectURL=()=>{};
  t.dom.window.HTMLAnchorElement.prototype.click=function(){assert.equal(this.download,'generative-design-experiment.json');};
  t.click('[data-download]');const data=JSON.parse(await downloaded.text());URL.createObjectURL=oldCreate;URL.revokeObjectURL=oldRevoke;
  assert.equal(data.original.material,'Timber');assert.equal(data.previous.material,'Concrete');assert.equal(data.current.material,'Rammed earth');assert.equal(data.designIntent,'A neighborhood library');assert.equal(data.nextStep,'Trace then verify');
  assert.equal(data.provenance.model,'runwayml/stable-diffusion-v1-5');assert.match(data.provenance.current.src,/material-rammed-earth.png$/);assert.match(data.currentPrompt,/primary material is rammed earth$/);assert.equal(data.current.seed,200);
  t.click('[data-reset]');assert.deepEqual(visible(),[0]);assert.equal(t.$('[data-record-output]').innerHTML,'');
});

test('new form keyboard events do not trigger page navigation',async()=>{
  const t=await open('1-3-architectural-prompt-builder.html');let bubbled=false;
  t.dom.window.document.addEventListener('keydown',()=>{bubbled=true;});
  t.$('select').dispatchEvent(new t.dom.window.KeyboardEvent('keydown',{key:'ArrowRight',bubbles:true}));
  assert.equal(bubbled,false);
});

test('existing Episode 2.3 observation, residual, drag, refit and reset still work',()=>{
  const html=fs.readFileSync(path.join(site,'2-3-how-linear-regression-works.html'),'utf8').replace(/<script>markCurrent\(\d+\);<\/script>/,'');
  const dom=new JSDOM(html,{runScripts:'dangerously'}),doc=dom.window.document;
  const root=doc.querySelector('[data-feedback]').closest('.wg');
  const $=s=>root.querySelector(s),svg=$('svg');
  const original=$('[data-feedback]').textContent,equation=$('[data-equation]').textContent;
  assert.match(original,/Observed y.*Predicted ŷ.*Residual/);
  assert.equal(root.querySelectorAll('.regression-residual').length,7);
  svg.setPointerCapture=()=>{};svg.hasPointerCapture=()=>false;
  svg.getScreenCTM=()=>({inverse:()=>({})});
  svg.createSVGPoint=()=>({x:0,y:0,matrixTransform(){return {x:this.x,y:this.y};}});
  const point=$('[data-point="0"]');
  const event=(type,props)=>{const e=new dom.window.Event(type,{bubbles:true,cancelable:true});Object.assign(e,props);return e;};
  point.dispatchEvent(event('pointerdown',{isPrimary:true,button:0,pointerId:1}));
  svg.dispatchEvent(event('pointermove',{pointerId:1,clientX:220,clientY:170}));
  assert.notEqual($('[data-feedback]').textContent,original);
  assert.equal($('[data-equation]').textContent,equation);
  svg.dispatchEvent(event('pointerup',{pointerId:1}));$('[data-refit]').click();assert.notEqual($('[data-equation]').textContent,equation);
  $('[data-reset]').click();assert.equal($('[data-feedback]').textContent,original);
});
