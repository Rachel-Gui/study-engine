/* DOM checks for the Python foundations; jsdom is a test-only dependency. */
const {JSDOM}=require('jsdom');
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const site=path.join(__dirname,'../site');
const script=fs.readFileSync(path.join(site,'site.js'),'utf8');

test('trace controls replay recordings and keep arrow keys within the activity',()=>{
  let count=0;
  for(const file of fs.readdirSync(site).filter(n=>/^0-[345]-.*\.html$/.test(n))){
    const html=fs.readFileSync(path.join(site,file),'utf8');
    if(!html.includes('class="trace"'))continue;
    const dom=new JSDOM(html,{runScripts:'outside-only',url:'http://localhost/'+file});
    try{
      const w=dom.window,d=w.document;w.eval(script);
      let navigation=0;
      d.querySelectorAll('footer a.btn').forEach(a=>a.addEventListener('click',e=>{e.preventDefault();navigation++;}));
      for(const trace of d.querySelectorAll('.trace')){
        count++;
        const steps=JSON.parse(trace.dataset.trace).steps;
        trace.dispatchEvent(new w.KeyboardEvent('keydown',{key:'ArrowRight',bubbles:true}));
        assert.equal(trace.querySelector('.tr-pos').textContent,`step 2 of ${steps.length}`);
        assert.equal(navigation,0,'trace keyboard input must not navigate away');
        trace.dispatchEvent(new w.KeyboardEvent('keydown',{key:'ArrowLeft',bubbles:true}));
        assert(trace.querySelector('.tr-prev').disabled);assert.equal(navigation,0);
        trace.querySelector('.tr-end').click();
        assert.equal(trace.querySelector('.tr-out pre').textContent,steps.at(-1).out);
        assert(trace.querySelector('.tr-next').disabled);
        trace.querySelector('.tr-reset').click();assert(trace.querySelector('.tr-prev').disabled);
      }
      d.body.dispatchEvent(new w.KeyboardEvent('keydown',{key:'ArrowRight',bubbles:true}));
      assert.equal(navigation,1,'ordinary page navigation remains available');
    }finally{dom.window.close();}
  }
  assert.equal(count,17);
});

test('a corrected Python step clears its previous error styling and preserves teaching-error progression',async()=>{
  const html=fs.readFileSync(path.join(site,'0-3-your-first-program.html'),'utf8');
  const dom=new JSDOM(html,{runScripts:'outside-only',url:'http://localhost/0-3-your-first-program.html'});
  try{
    const w=dom.window,d=w.document;
    let fail=true;
    w.loadPyodide=async()=>({loadPackage:async()=>{},setStdout(){},runPythonAsync:async code=>{
      if(code.includes('_out = []'))return {toJs:()=>[]};
      if(fail)throw new Error('NameError: fix the name');
      return 'corrected output';
    }});
    const append=d.head.appendChild.bind(d.head);
    d.head.appendChild=node=>{const result=append(node);if(node.tagName==='SCRIPT')queueMicrotask(()=>node.onload());return result;};
    w.eval(script);
    const steps=d.querySelectorAll('.pylab .step'),run=steps[0].querySelector('.run'),out=steps[0].querySelector('.out');
    await run.onclick();assert(out.classList.contains('has-error'));assert(!steps[1].querySelector('.run').disabled);
    fail=false;await run.onclick();assert.equal(steps[0].querySelector('.state').textContent,'done');
    assert.match(out.textContent,/corrected output/);assert(!out.classList.contains('has-error'));
  }finally{dom.window.close();}
});
