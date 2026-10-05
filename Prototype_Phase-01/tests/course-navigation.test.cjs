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
    assert.equal(d.querySelectorAll('.mless li a').length,43);
    for(const a of d.querySelectorAll('.mcard a'))assert(fs.existsSync(path.join(site,a.getAttribute('href'))));
    const index=JSON.parse(fs.readFileSync(path.join(site,'search.json'),'utf8'));
    assert.equal(index.length,304);assert.equal(new Set(index.map(e=>e.p)).size,304);
    for(const entry of index)assert(fs.existsSync(path.join(site,entry.p)),entry.p);
    assert(index.some(e=>e.e==='6.6'&&e.t==='Guided regression workflow'));
    assert(index.some(e=>e.e==='2.8'&&e.k==='lesson'));
    assert(index.some(e=>e.e==='3.4'&&e.k==='lesson'));
    assert(index.some(e=>e.e==='2.10'&&e.k==='lesson'));
    assert(d.querySelector('a[href="readings.html"]'));
    assert(fs.existsSync(path.join(site,'readings.html')));
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

test('search dismisses results, clears stale links, and does not reopen after Escape',async()=>{
  const dom=open('modules.html');
  try{
    const w=dom.window,d=w.document;
    w.fetch=async()=>({json:async()=>JSON.parse(fs.readFileSync(path.join(site,'search.json'),'utf8'))});
    w.eval(script);
    const q=d.querySelector('#q'),hits=d.querySelector('#hits');
    const tick=()=>new Promise(resolve=>setImmediate(resolve));
    q.focus();q.value='regression';q.dispatchEvent(new w.Event('input'));await tick();
    assert(hits.querySelector('a'));
    q.dispatchEvent(new w.KeyboardEvent('keydown',{key:'ArrowDown',bubbles:true}));
    d.activeElement.dispatchEvent(new w.KeyboardEvent('keydown',{key:'Escape',bubbles:true}));
    await tick();assert.equal(d.activeElement,q);assert(hits.hidden);
    q.dispatchEvent(new w.KeyboardEvent('keydown',{key:'ArrowDown',bubbles:true}));
    assert.equal(d.activeElement,q);
    q.value='energy';q.dispatchEvent(new w.Event('input'));await tick();assert(!hits.hidden);
    q.value='';q.dispatchEvent(new w.Event('input'));
    assert(hits.hidden);assert.equal(hits.querySelector('a'),null);
    q.dispatchEvent(new w.KeyboardEvent('keydown',{key:'Enter',bubbles:true}));
    await tick();assert.equal(w.location.pathname,'/modules.html');
  }finally{dom.window.close();}
});

test('dismissing search while the index loads keeps the late results hidden',async()=>{
  const dom=open('modules.html');
  try{
    const w=dom.window,d=w.document;
    let finish;
    w.fetch=()=>new Promise(resolve=>{finish=resolve;});w.eval(script);
    const q=d.querySelector('#q'),hits=d.querySelector('#hits');
    q.value='regression';q.focus();assert(!hits.hidden);
    q.dispatchEvent(new w.KeyboardEvent('keydown',{key:'Escape',bubbles:true}));
    finish({json:async()=>JSON.parse(fs.readFileSync(path.join(site,'search.json'),'utf8'))});
    await new Promise(resolve=>setImmediate(resolve));assert(hits.hidden);
  }finally{dom.window.close();}
});

test('Selected readings highlights its own sidebar link',()=>{
  const dom=open('readings.html');
  try{
    const w=dom.window,d=w.document;w.eval(script);w.markCurrent(-1);
    assert(d.querySelector('nav a[href="readings.html"]').classList.contains('on'));
    assert(!d.querySelector('nav a[href="modules.html"]').classList.contains('on'));
    assert.equal(d.querySelectorAll('nav a.on').length,1);
  }finally{dom.window.close();}
});

test('MAE has a formula and explanation, and Python buttons say Reset code',()=>{
  const index=JSON.parse(fs.readFileSync(path.join(site,'search.json'),'utf8'));
  const page=index.find(e=>e.e==='7.2'&&e.x.includes('Mean absolute error'));
  assert(page);
  const dom=open(page.p);
  try{
    const label=[...dom.window.document.querySelectorAll('strong')].find(e=>e.textContent==='Mean absolute error');
    assert(label);assert.match(label.parentElement.textContent,/∣ŷ − y∣ averaged/);
    assert.match(label.parentElement.textContent,/penalty grows linearly/);
  }finally{dom.window.close();}
  const lab=open('6-6-guided-regression-workflow.html');
  try{
    const buttons=[...lab.window.document.querySelectorAll('.pylab .rst')];
    assert.equal(buttons.length,10);assert(buttons.every(b=>b.textContent==='Reset code'));
  }finally{lab.window.close();}
});

test('inline figures have unique IDs and arrow references resolve within each SVG',()=>{
  for(const file of ['modules.html','0-1-how-the-modules-connect.html',
    '5-1-pandas-tables.html','7-2-gradient-descent-and-the-learning-rate.html',
    '8-4-surrogate-models-and-the-sampled-range.html']){
    const dom=open(file);
    try{
      const d=dom.window.document,ids=[...d.querySelectorAll('[id]')].map(e=>e.id);
      assert.equal(new Set(ids).size,ids.length,file);
      for(const svg of d.querySelectorAll('svg')){
        for(const element of svg.querySelectorAll('[marker-end],[marker-start],[marker-mid]')){
          for(const name of ['marker-start','marker-mid','marker-end']){
            const ref=element.getAttribute(name)?.match(/^url\(#(.+)\)$/);
            if(ref)assert(svg.querySelector(`[id="${ref[1]}"]`),`${file}: ${ref[1]}`);
          }
        }
      }
    }finally{dom.window.close();}
  }
});
