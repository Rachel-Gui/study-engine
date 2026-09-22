/* Print preparation tests; jsdom is a test-only dependency. */
const {JSDOM}=require('jsdom');
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');

test('printing captures complete live editor values without altering screen state',()=>{
  const root=path.join(__dirname,'../site');
  const dom=new JSDOM(fs.readFileSync(path.join(root,'2-6-guided-regression-workflow.html'),'utf8'),{runScripts:'outside-only'});
  const {window}=dom,doc=window.document;
  window.eval(fs.readFileSync(path.join(root,'site.js'),'utf8'));
  const editor=doc.querySelector('textarea'),before=editor.defaultValue;
  editor.value='Edited live value\n'+Array.from({length:120},(_,i)=>'line '+i).join('\n')+'\n<script>literal text</script>\nFINAL LINE';
  editor.scrollTop=120;doc.querySelector('section').scrollTop=500;
  window.dispatchEvent(new window.Event('beforeprint'));
  const copy=editor.nextElementSibling;
  assert.equal(copy.textContent,editor.value);
  assert.equal(copy.querySelector('script'),null);
  assert.equal(editor.defaultValue,before);
  assert.equal(editor.scrollTop,120);
  assert.equal(doc.querySelector('section').scrollTop,500);
  assert(editor.classList.contains('print-source'));
  const count=doc.querySelectorAll('[data-print-value]').length;
  window.dispatchEvent(new window.Event('beforeprint'));
  assert.equal(doc.querySelectorAll('[data-print-value]').length,count);
  window.dispatchEvent(new window.Event('afterprint'));
  assert.equal(doc.querySelectorAll('[data-print-value]').length,0);
  assert(!editor.classList.contains('print-source'));
  assert(editor.value.endsWith('FINAL LINE'));
  assert.equal(editor.scrollTop,120);
});

test('print preparation preserves hidden activities and closed reference answers',()=>{
  const dom=new JSDOM('<article><div hidden><textarea>Unrevealed step</textarea></div><textarea hidden>Hidden editor</textarea><details><summary>Reference answer</summary>Answer</details></article>',{runScripts:'outside-only'});
  dom.window.eval(fs.readFileSync(path.join(__dirname,'../site/site.js'),'utf8'));
  dom.window.dispatchEvent(new dom.window.Event('beforeprint'));
  const doc=dom.window.document;
  assert(doc.querySelector('[data-print-value]').parentElement.hidden);
  assert(!doc.querySelector('textarea[hidden]').classList.contains('print-source'));
  assert(!doc.querySelector('details').open);
});

test('print styles reveal unvisited blocks without opening hidden activity stages',()=>{
  const dom=new JSDOM('<article><p class="rv">Below the viewport</p><fieldset class="rv" hidden>Future stage</fieldset><details class="rv"><summary>Reference</summary>Answer</details></article>');
  const {document}=dom.window;
  const screen=document.createElement('style');
  screen.textContent='.rv{opacity:0;transform:translateY(12px)}';document.head.append(screen);
  const block=document.querySelector('p');assert.equal(dom.window.getComputedStyle(block).opacity,'0');
  // Apply only the actual print rules as a DOM-level media-emulation check.
  const sheet=document.createElement('style');sheet.textContent=fs.readFileSync(path.join(__dirname,'../site/site.css'),'utf8');document.head.append(sheet);
  const printRules=[...sheet.sheet.cssRules].filter(rule=>rule.media?.mediaText==='print').flatMap(rule=>[...rule.cssRules]).filter(rule=>rule.selectorText).map(rule=>rule.cssText).join('\n');sheet.remove();
  assert(printRules);const print=document.createElement('style');print.textContent=printRules;document.head.append(print);
  assert.equal(dom.window.getComputedStyle(block).opacity,'1');assert.equal(dom.window.getComputedStyle(block).transform,'none');
  assert(document.querySelector('fieldset').hidden);assert(!document.querySelector('details').open);
  assert.equal(block.className,'rv');print.remove();assert.equal(dom.window.getComputedStyle(block).opacity,'0');
  dom.window.close();
});
