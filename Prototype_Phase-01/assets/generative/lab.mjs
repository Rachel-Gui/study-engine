import {defaults,options,promptKeys,labels,prompt,changes,escapeText as esc,Experiment,controlledSeries,controlledExperiment,record,materialDefaults,materialOptions,materialPrompt,materialExperiment} from './core.mjs?v=controlled-task4-1';

const card=(model,label)=>`<figure class="ga-generation${label.startsWith('CURRENT')?' ga-current':''}"><figcaption><strong>${esc(model.sample?label.split(' ')[0]+' — '+model.settings.material:label)}</strong><span>Example ${model.number} · ${model.sample?'Precomputed controlled Task 4 output':'Material = '+esc(model.settings.material)}</span></figcaption>${model.sample?`<div class="ga-real-image"><img src="${esc(model.sample.src)}" width="${model.sample.width}" height="${model.sample.height}" alt="Controlled Task 4 output: ${esc(model.settings.material)} pavilion"></div>`:model.svg}<p>${esc(model.prompt)}</p></figure>`;
function compare(experiment, original=false){
  const previous=original?experiment.original:experiment.previous,current=experiment.current;
  if(!current)return '';
  const delta=previous?changes(previous.settings,current.settings):[];
  return `<div class="ga-comparison">${previous?card(previous,original?'ORIGINAL GENERATION':'PREVIOUS GENERATION'):''}${card(current,'CURRENT GENERATION')}</div>`
    +`<p class="ga-change">${previous?'Changed: '+(delta.map(d=>`${esc(d.label)} = ${esc(d.before||'(none)')} → ${esc(d.after||'(none)')}`).join('; ')||'No setting differences'):'First successful example. Test one change to create a previous generation.'}</p>`;
}
function fields(root,realMaterial){
  const initial=realMaterial?materialDefaults:defaults,choices=realMaterial?materialOptions:options,keys=realMaterial?['material']:promptKeys,format=realMaterial?materialPrompt:prompt;
  const box=root.querySelector('[data-fields]');
  box.innerHTML=keys.map(key=>`<label class="ga-field">${labels[key]}<select data-setting="${key}">${choices[key].map(v=>`<option${v===initial[key]?' selected':''}>${v}</option>`).join('')}</select></label>`).join('');
  if(realMaterial)box.insertAdjacentHTML('afterend',`<details class="exp"><summary>Fixed inputs and output provenance</summary><p>Only the material term is selectable. The pavilion, garden, wording, seed 200, guidance 7.5, 30 steps and 512 × 512 output remain fixed. Model: ${esc(materialExperiment.model)}; scheduler: ${esc(materialExperiment.scheduler)}.</p><p><a href="${esc(materialExperiment.provenance)}" target="_blank" rel="noopener">Full generation settings, pinned revision and image hashes</a></p></details>`);
  const read=()=>({...initial,...Object.fromEntries([...box.querySelectorAll('select')].map(s=>[s.dataset.setting,s.value]))});
  const update=()=>{root.querySelector('[data-prompt]').textContent=format(read());};
  box.addEventListener('change',update);update();return read;
}
function diffusion(root,cfg,status){
  const slider=root.querySelector('[data-denoise]'),canvas=root.querySelector('canvas'),ctx=canvas.getContext('2d');
  root.querySelector('[data-scene]').innerHTML=`<img src="${esc(cfg.image)}" alt="${esc(cfg.alt)}">`;
  const pixels=ctx.createImageData(canvas.width,canvas.height);let random=127;
  for(let i=0;i<pixels.data.length;i+=4){random=(Math.imul(random,1664525)+1013904223)>>>0;const v=random>>>24;pixels.data.set([v,v,v,255],i);}
  ctx.putImageData(pixels,0,0);
  root.querySelector('[data-start]').onclick=()=>{
    if(!root.querySelector('textarea').value.trim()){status('Write a prediction before exploring.');return;}
    slider.disabled=false;slider.focus();status('Move the slider and compare your prediction with the visible structure.');
  };
  slider.oninput=()=>{
    const step=Number(slider.value);canvas.style.opacity=String(1-step/30);
    root.querySelector('[data-count]').textContent=`${step} / 30`;
    root.querySelector('[data-scene]').style.filter=`blur(${(30-step)/4}px)`;
    root.querySelector('[data-explanation]').hidden=step===0;
  };
}
function controls(root,cfg,status){
  const stages=[...root.querySelectorAll('[data-experiment]')];
  stages.forEach((stage,i)=>{
    stage.querySelector('[data-reveal]').onclick=()=>{
      if(!stage.querySelector('textarea').value.trim()){status('Record your prediction first.');return;}
      const key=stage.dataset.experiment;
      const experiment=controlledExperiment(key);
      stage.querySelector('[data-series]').innerHTML='<div class="ga-comparison">'+controlledSeries(key).map(sample=>
        `<figure class="ga-generation ga-recorded" data-source-task="${experiment.task}" data-source-panel="${sample.panel}">
          <figcaption><strong>${esc(sample.label)}</strong><span>Task ${experiment.task} · saved notebook output</span></figcaption>
          <div class="ga-real-image"><img src="${esc(sample.src)}" alt="${esc(sample.alt)}" width="${sample.pixel_size[0]}" height="${sample.pixel_size[1]}" loading="lazy"></div>
          ${sample.elapsed_seconds!=null?`<p>Recorded time: ${sample.elapsed_seconds.toFixed(1)} s · this Colab run only</p>`:''}
        </figure>`).join('')+'</div>'
        +`<details class="exp"><summary>View original notebook figure and settings</summary>
          <p><a href="${esc(experiment.original)}" target="_blank" rel="noopener">Original embedded PNG · Task ${experiment.task}</a></p>
          <p><a href="assets/generative/real-experiments/provenance.json" target="_blank" rel="noopener">Full provenance, exact settings and crop coordinates</a></p>
          <p>Model declared in notebook: runwayml/stable-diffusion-v1-5. Scheduler and runtime library versions are not recorded. The source PNG limits the available image resolution.</p></details>`;
      stage.querySelectorAll('[data-series] img').forEach(img=>img.addEventListener('error',()=>status('A saved notebook image could not be loaded. Check the published assets; no schematic replacement has been substituted.')));
      stage.querySelector('[data-explanation]').hidden=false;
      if(stage.querySelector('[data-unlock]'))stage.querySelector('[data-unlock]').hidden=false;
      status(`Task ${experiment.task} outputs are precomputed from the completed notebook, not generated live. Compare the named setting within this group, then explain.`);
    };
    const next=stage.querySelector('[data-unlock]');
    if(next)next.onclick=()=>{stages[i+1].hidden=false;stages[i+1].querySelector('textarea').focus();};
  });
}
function critic(root,cfg,status){
  root.querySelector('[data-critique-reveal]').onclick=()=>{
    if(!root.querySelector('textarea').value.trim()){status('Write your initial judgment and a visible clue first.');return;}
    const selected=[...root.querySelectorAll('[data-critique]:checked')].map(n=>Number(n.value));
    if(!selected.length){status('Select at least one issue to investigate.');return;}
    const out=root.querySelector('[data-critique-output]');
    out.innerHTML=cfg.checks.map((item,i)=>`<div class="ga-review"><strong>${selected.includes(i)?'You flagged':'Also inspect'}: ${esc(item.label)}</strong><p>${esc(item.reason)}</p></div>`).join('')+`<p class="ga-change">${esc(cfg.explanation)}</p>`;
    out.hidden=false;status('These are verification questions, not a structural diagnosis from pixels.');
  };
}
function pipeline(root,cfg,status){
  const buttons=[...root.querySelectorAll('[data-pipeline-step]')];
  root.querySelector('[data-start]').onclick=()=>{
    if(!root.querySelector('textarea').value.trim()){status('Write the missing information you would need first.');return;}
    buttons[0].disabled=false;buttons[0].focus();status('Start at Prompt; each checkpoint unlocks the next.');
  };
  buttons.forEach((button,i)=>{button.onclick=()=>{
    buttons.forEach(b=>b.setAttribute('aria-pressed',String(b===button)));
    const item=cfg.stages[i];root.querySelector('[data-pipeline-output]').innerHTML=`<div class="ga-review"><strong>${esc(item.title)}</strong><p>${esc(item.explanation)}</p><p>Required information: ${esc(item.information)}</p></div>`;
    if(buttons[i+1])buttons[i+1].disabled=false;
    status(`${i+1} of ${buttons.length} · ${item.title}`);
  };});
}
function experimentLab(root,cfg,status,workflow){
  const realMaterial=cfg.real_material===true,initial=realMaterial?materialDefaults:defaults,choices=realMaterial?materialOptions:options,keys=realMaterial?['material']:promptKeys,format=realMaterial?materialPrompt:prompt;
  const experiment=new Experiment({materialOnly:realMaterial}),read=fields(root,realMaterial),notes={};let stage=0;
  const $=s=>root.querySelector(s);
  root.querySelectorAll('[data-note]').forEach(el=>el.addEventListener('input',()=>{notes[el.dataset.note]=el.value;}));
  const gen=$('[data-generate]');
  root.addEventListener('error',event=>{if(event.target.tagName==='IMG')status('A recorded image could not be loaded. Check the published assets; no schematic image has been substituted.');},true);
  function display(){
    if($('[data-comparison]'))$('[data-comparison]').innerHTML=compare(experiment);
    if($('[data-initial]'))$('[data-initial]').innerHTML=card(experiment.original,'ORIGINAL GENERATION');
    if($('[data-answer]'))$('[data-answer]').hidden=!experiment.previous;
    gen.textContent=experiment.current?'Test one prompt change':'Select initial example';
    if(workflow&&experiment.current){gen.disabled=true;root.querySelectorAll('[data-setting]').forEach(el=>el.disabled=true);}
  }
  gen.onclick=()=>{
    try{
      if(!workflow&&!notes.expectedChange?.trim())throw Error('Write what you expect to see before selecting an example.');
      experiment.test(read(),true);display();status('Example saved. '+(experiment.previous?'Compare PREVIOUS and CURRENT.':'Now change exactly one prompt field and predict its effect.'));
      if(workflow) updateChangeValues();
    }catch(error){status(error.message);}
  };
  $('[data-reset]').onclick=()=>{
    experiment.reset();Object.keys(notes).forEach(k=>delete notes[k]);
    root.querySelectorAll('[data-note]').forEach(el=>el.value='');
    root.querySelectorAll('[data-setting]').forEach(el=>{el.disabled=false;el.value=initial[el.dataset.setting];});
    $('[data-prompt]').textContent=format(initial);gen.disabled=false;gen.textContent='Select initial example';
    for(const key of ['[data-comparison]','[data-initial]','[data-record-output]'])if($(key))$(key).replaceChildren();
    if($('[data-answer]'))$('[data-answer]').hidden=true;
    stage=0;if(workflow){showStage();updateChangeValues();}status('Experiment reset. Saved generations and notes cleared.');
  };
  if(!workflow)return;
  const stages=[...root.querySelectorAll('[data-stage]')];
  function showStage(){stages.forEach((el,i)=>el.hidden=i!==stage);$('[data-back]').disabled=stage===0;$('[data-next]').hidden=stage===7;$('[data-progress]').textContent=`Stage ${stage+1} of 8 · ${cfg.stages[stage]}`;}
  function updateChangeValues(){
    const key=$('[data-change-key]').value,current=experiment.current?.settings||initial;
    $('[data-change-value]').innerHTML=choices[key].filter(v=>v!==current[key]).map(v=>`<option>${esc(v)}</option>`).join('');
  }
  $('[data-change-key]').innerHTML=keys.map(k=>`<option value="${k}"${k==='material'?' selected':''}>${labels[k]}</option>`).join('');
  $('[data-change-key]').onchange=updateChangeValues;updateChangeValues();
  $('[data-retest]').onclick=()=>{
    try{
      if(!experiment.current)throw Error('Select the initial example in Generate first.');
      if(!notes.expectedChange?.trim())throw Error('Predict the effect of this change first.');
      experiment.test({...experiment.current.settings,[$('[data-change-key]').value]:$('[data-change-value]').value},true);
      display();updateChangeValues();status('One change tested successfully. Continue to Compare, or test another change.');
    }catch(error){status(error.message);}
  };
  const required={0:['designIntent'],4:['observedChange','unexpectedChanges'],5:['architecturalLimitations'],6:['informationNeeded','nextStep']};
  $('[data-next]').onclick=()=>{
    if(required[stage]?.some(key=>!notes[key]?.trim())){status('Complete the reasoning fields in this stage before continuing.');return;}
    if(stage===2&&!experiment.current){status('Select the initial example first.');return;}
    if(stage===3&&!experiment.previous){status('Test one changed variable first.');return;}
    stage=Math.min(stage+1,7);showStage();status('Your earlier notes and generations are preserved.');
    if(stage===7)renderRecord();
  };
  $('[data-back]').onclick=()=>{stage=Math.max(stage-1,0);showStage();status('Review earlier work; your saved results are unchanged.');};
  function renderRecord(){
    if(!experiment.previous){status('Complete an initial example and one successful change first.');return null;}
    const summary=record(experiment,notes);
    const names={designIntent:'Design intent',originalPrompt:'Original prompt',currentPrompt:'Current prompt',expectedChange:'Expected change',observedChange:'Observed change',unexpectedChanges:'Unexpected changes',architecturalLimitations:'Architectural limitations',informationNeeded:'Information needed for downstream evaluation',nextStep:'Next step',reflection:'Reflection'};
    $('[data-record-output]').innerHTML=compare(experiment,true)+'<dl class="ga-record">'+Object.entries(names).map(([k,label])=>`<dt>${label}</dt><dd>${esc(summary[k]||'Not recorded yet')}</dd>`).join('')+'</dl>';
    return {...summary,original:experiment.original.settings,current:experiment.current.settings,previous:experiment.previous.settings,
      provenance:realMaterial?{source:materialExperiment.source,model:materialExperiment.model,revision:materialExperiment.revision,settings:materialExperiment.provenance,original:experiment.original.sample,previous:experiment.previous.sample,current:experiment.current.sample}: 'Authored teaching illustrations; no model inference.'};
  }
  $('[data-record]').onclick=()=>{renderRecord();status('Record updated from your saved generations and current notes.');};
  $('[data-download]').onclick=()=>{
    const data=renderRecord();if(!data)return;
    const url=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:'application/json'}));
    const link=document.createElement('a');link.href=url;link.download='generative-design-experiment.json';link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
    status('Record downloaded. Save it before leaving this page.');
  };showStage();
}
export function initialize(root){
  if(root.dataset.initialized)return;root.dataset.initialized='true';
  root.addEventListener('keydown',event=>{
    if(/INPUT|TEXTAREA|SELECT|BUTTON/.test(event.target.tagName))event.stopPropagation();
  });
  const cfg=JSON.parse(root.querySelector('[data-config]').textContent);
  const status=text=>{root.querySelector('[data-status]').textContent=text;};
  switch(root.dataset.genlab){
    case 'diffusion':diffusion(root,cfg,status);break;
    case 'controls':controls(root,cfg,status);break;
    case 'critic':critic(root,cfg,status);break;
    case 'pipeline':pipeline(root,cfg,status);break;
    case 'prompt':experimentLab(root,cfg,status,false);break;
    case 'workflow':experimentLab(root,cfg,status,true);break;
  }
}
if(typeof document!=='undefined')document.querySelectorAll('[data-genlab]').forEach(initialize);
