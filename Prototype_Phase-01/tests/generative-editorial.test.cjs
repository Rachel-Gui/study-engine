/* Cross-page editorial/UX regression checks. Uses test-only jsdom. */
const {JSDOM,VirtualConsole}=require('jsdom');
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {pathToFileURL}=require('node:url');
const site=path.join(__dirname,'../site');
const banned=/lecture slides|the (?:supplied )?lecture|the notebook|Task\s+(?:2|3|4|11|12|13)\b|\bColab\b|saved notebook output|original notebook|subplot|crop coordinates|embedded PNG|\.pptx|\.ipynb|Episode (?:1\.7|2\.3)|\bxx\b|\uFFFD/i;
const entry=new JSDOM(fs.readFileSync(path.join(site,'1-1-central-question.html'),'utf8'));
const topics=[...entry.window.document.querySelectorAll('nav a.tp[data-ep^="1."]')].map(a=>a.getAttribute('href'));
const modulePromise=import(pathToFileURL(path.join(__dirname,'../assets/generative/lab.mjs')));
async function open(file){
  const errors=[];const vc=new VirtualConsole();
  for(const event of ['jsdomError','error'])vc.on(event,e=>errors.push(String(e)));
  const dom=new JSDOM(fs.readFileSync(path.join(site,file),'utf8'),{url:'http://localhost/'+file,runScripts:'outside-only',virtualConsole:vc});
  const w=dom.window;w.HTMLElement.prototype.scrollIntoView=function(){};
  w.HTMLCanvasElement.prototype.getContext=()=>({createImageData:(w,h)=>({data:new Uint8ClampedArray(w*h*4)}),putImageData(){}});
  w.eval(fs.readFileSync(path.join(site,'site.js'),'utf8'));
  const root=w.document.querySelector('[data-genlab]');
  if(root){global.document=w.document;const {initialize}=await modulePromise;initialize(root);}
  return {dom,w,doc:w.document,root,errors};
}
function checkCopy(doc,file){
  const article=doc.querySelector('article').cloneNode(true);
  article.querySelectorAll('script,style').forEach(n=>n.remove());
  const attributes=[...article.querySelectorAll('[alt],[placeholder],[title]')].flatMap(n=>['alt','placeholder','title'].map(k=>n.getAttribute(k)||''));
  assert.doesNotMatch(article.textContent+' '+attributes.join(' '),banned,file);
  assert.doesNotMatch(article.textContent,/That's the one\./,file);
}

test('all 16 Module 1 topics have clean student copy and working navigation',async()=>{
  assert.equal(topics.length,16);
  for(const file of topics){
    const t=await open(file);checkCopy(t.doc,file);
    for(const a of t.doc.querySelectorAll('nav a[href],footer a[href]')){const href=a.getAttribute('href');if(!/^[a-z]+:|^#/.test(href))assert(fs.existsSync(path.join(site,href)),a.href);}
    const here=[...t.doc.querySelectorAll('nav a.tp')].find(a=>a.getAttribute('href')===file);
    t.w.markCurrent(Number(here.dataset.i));assert(here.classList.contains('on'));assert(here.classList.contains('show'));
    const nextEpisode=[...t.doc.querySelectorAll('nav a.ep')].find(a=>a.dataset.ep!==here.dataset.ep);
    nextEpisode.click();assert(nextEpisode.classList.contains('open'));
    assert.deepEqual(t.errors,[],file);t.w.close();
  }
});

test('all quizzes give explanatory feedback and native reference labels track open/closed state',async()=>{
  let quizzes=0,answers=0;
  for(const file of topics){
    const t=await open(file);
    for(const btn of t.doc.querySelectorAll('.reflect .chk')){
      const box=btn.closest('.reflect'),v=box.querySelector('.verdict');
      btn.click();assert.equal(v.textContent,'Pick an option first.');
      const options=[...box.querySelectorAll('input[type=radio]')];
      options.find(o=>o.value!==btn.dataset.correct).click();btn.click();assert.match(v.textContent,/^Not quite/);
      options.find(o=>o.value===btn.dataset.correct).click();btn.click();assert.match(v.textContent,/^Correct\. .+/);assert(btn.dataset.feedback);quizzes++;
    }
    for(const summary of t.doc.querySelectorAll('summary[data-reference-answer]')){
      const details=summary.parentElement;assert.equal(summary.textContent,'Show reference answer');
      details.open=true;await new Promise(resolve=>setTimeout(resolve,0));assert.equal(summary.textContent,'Hide reference answer');
      details.open=false;await new Promise(resolve=>setTimeout(resolve,0));assert.equal(summary.textContent,'Show reference answer');answers++;
    }
    assert.deepEqual(t.errors,[],file);t.w.close();
  }
  assert.equal(quizzes,13);assert.equal(answers,20);
});

test('revealed experiments retain conditions and images without exposing production metadata',async()=>{
  const t=await open('1-4-generation-control-lab.html');
  for(const stage of t.root.querySelectorAll('[data-experiment]')){
    assert(!stage.hidden);stage.querySelector('textarea').value='I expect a change in composition.';
    stage.querySelector('[data-reveal]').click();
    assert.equal(stage.querySelector('summary').textContent,'View experiment settings');
    const settings=stage.querySelector('details').textContent;
    assert.match(settings,/Prompt:.*Fixed:.*Changed(?: width × height)?:/s);assert.match(settings,/runwayml\/stable-diffusion-v1-5/);
    assert.match(settings,/Not recorded for this experiment/);
    const images=[...stage.querySelectorAll('[data-series] img')];assert(images.length>=2);
    for(const img of images)assert(fs.existsSync(path.join(site,img.getAttribute('src'))));
    stage.querySelector('[data-unlock]')?.click();
  }
  checkCopy(t.doc,'revealed controls');assert.deepEqual(t.errors,[]);t.w.close();
  const p=await open('1-3-architectural-prompt-builder.html');
  const prediction=p.root.querySelector('textarea');prediction.value='The surface will change.';prediction.dispatchEvent(new p.w.Event('input',{bubbles:true}));
  p.root.querySelector('[data-generate]').click();const material=p.root.querySelector('select');material.value='Concrete';material.dispatchEvent(new p.w.Event('change',{bubbles:true}));p.root.querySelector('[data-generate]').click();
  assert.match(p.root.textContent,/PREVIOUS — Timber/);assert.match(p.root.textContent,/CURRENT — Concrete/);
  assert.match(p.root.textContent,/PNDMScheduler/);assert.match(p.root.textContent,/451f4fe16113bff5a5d2269ed5ad43b0592e9a14/);
  checkCopy(p.doc,'revealed material comparison');assert.deepEqual(p.errors,[]);p.w.close();
  const pipeline=await open('1-6-translate-before-evaluating.html');assert.equal(pipeline.root.querySelector('textarea').placeholder,'e.g., orientation, dimensions, material properties...');pipeline.w.close();
});
