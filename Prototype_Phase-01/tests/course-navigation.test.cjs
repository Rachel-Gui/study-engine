/* Checks for the restructured course; jsdom is a test-only dependency. */
const {JSDOM}=require('jsdom');
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const site=path.join(__dirname,'../site');
const script=fs.readFileSync(path.join(site,'site.js'),'utf8');
function open(file){
  return new JSDOM(fs.readFileSync(path.join(site,file),'utf8'),{
    runScripts:'outside-only',url:'http://localhost/'+file,
  });
}

test('module directory and search index point to the newly numbered course pages',()=>{
  const dom=open('modules.html');
  try{
    const d=dom.window.document;
    assert.equal(d.querySelectorAll('.mcard.mod').length,8);
    assert.equal(d.querySelectorAll('.mcard').length,10);
    assert.equal(d.querySelectorAll('.mless li a').length,42);
    for(const a of d.querySelectorAll('.mcard a'))assert(fs.existsSync(path.join(site,a.getAttribute('href'))));
    const index=JSON.parse(fs.readFileSync(path.join(site,'search.json'),'utf8'));
    assert.equal(index.length,288);assert.equal(new Set(index.map(e=>e.p)).size,288);
    for(const entry of index)assert(fs.existsSync(path.join(site,entry.p)),entry.p);
    assert(index.some(e=>e.e==='6.6'&&e.t==='Guided regression workflow'));
    assert(index.some(e=>e.e==='2.8'&&e.k==='lesson'));
    assert(index.some(e=>e.e==='3.4'&&e.k==='lesson'));
  }finally{dom.window.close();}
});

test('course search loads once, finds new lessons, supports keyboard focus, and escapes unmatched text',async()=>{
  const dom=open('modules.html');
  try{
    const w=dom.window,d=w.document,index=JSON.parse(fs.readFileSync(path.join(site,'search.json'),'utf8'));
    let fetches=0;
    w.fetch=async url=>{assert.equal(url,'search.json');fetches++;return {json:async()=>index};};
    w.eval(script);
    const q=d.querySelector('#q'),hits=d.querySelector('#hits');
    d.body.dispatchEvent(new w.KeyboardEvent('keydown',{key:'/',bubbles:true}));
    assert.equal(d.activeElement,q);
    q.value='structured generation';q.dispatchEvent(new w.Event('input',{bubbles:true}));
    await new Promise(resolve=>setImmediate(resolve));
    assert(!hits.hidden);assert(hits.querySelector('a[href="2-8-index.html"]'));
    q.dispatchEvent(new w.KeyboardEvent('keydown',{key:'ArrowDown',bubbles:true}));
    assert.equal(d.activeElement,hits.querySelector('a'));
    d.activeElement.dispatchEvent(new w.KeyboardEvent('keydown',{key:'ArrowUp',bubbles:true}));
    assert.equal(d.activeElement,q);
    q.value='<img src=x onerror=alert(1)> no_such_topic';q.dispatchEvent(new w.Event('input'));
    await new Promise(resolve=>setImmediate(resolve));
    assert.equal(hits.querySelector('img'),null);assert.match(hits.textContent,/No results/);
    q.value='';q.dispatchEvent(new w.Event('input'));await new Promise(resolve=>setImmediate(resolve));
    assert(hits.hidden);assert.equal(fetches,1);
  }finally{dom.window.close();}
});

test('continue from home uses the last visited topic in the restructured course',()=>{
  const topic=open('6-6-guided-regression-workflow.html'),home=open('index.html');
  try{
    const w=topic.window,d=w.document;
    w.HTMLElement.prototype.scrollIntoView=()=>{};w.eval(script);
    const current=d.querySelector('nav a[href="6-6-guided-regression-workflow.html"]');
    w.markCurrent(Number(current.dataset.i));
    home.window.localStorage.setItem('studyengine.last',w.localStorage.getItem('studyengine.last'));
    home.window.eval(script);home.window.markCurrent(-1);
    const resume=home.window.document.querySelector('#resume');
    assert(!resume.hidden);assert.equal(resume.getAttribute('href'),'6-6-guided-regression-workflow.html');
    assert.match(resume.textContent,/6\.6.*Guided regression workflow/);
    home.window.localStorage.removeItem('studyengine.last');
  }finally{topic.window.close();home.window.close();}
});
