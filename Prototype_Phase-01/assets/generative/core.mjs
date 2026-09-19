/* Pure, local teaching state. No model inference, network calls or page storage. */
import examples, {notebookExperiments,materialExperiment} from './examples.mjs?v=module1-editorial-1';
export const defaults = Object.freeze({building:'Community library', material:'Timber', context:'Seattle neighborhood', lighting:'Soft overcast daylight', intent:'Contemporary', performance:'Passive daylighting', seed:100, guidance:7.5, steps:30, negative:''});
export const promptKeys = ['building','material','context','lighting','intent','performance'];
export const labels = {building:'Building type',material:'Material',context:'Context',lighting:'Lighting',intent:'Design intent',performance:'Performance hint',seed:'Seed',guidance:'Guidance',steps:'Inference steps',negative:'Negative prompt'};
export const options = {
  building:['Community library','Pavilion','Mid-rise housing'], material:['Timber','Concrete','Rammed earth'],
  context:['Seattle neighborhood','Urban plaza','Desert courtyard'], lighting:['Soft overcast daylight','Warm evening light'],
  intent:['Contemporary','Geometric terraces'], performance:['Passive daylighting','South-facing shading','Passive cooling']
};
export function prompt(s){return `${s.intent} ${s.material.toLowerCase()} ${s.building.toLowerCase()} in a ${s.context.toLowerCase()}, ${s.lighting.toLowerCase()}, with ${s.performance.toLowerCase()}.`;}
// Exact recorded domain for Task 4. Never map these pavilion outputs onto an
// arbitrary builder prompt, or fall back to a schematic for a missing material.
export const materialDefaults=Object.freeze({building:'Small pavilion',material:'Timber',context:'Public garden, surrounded by trees',lighting:'Soft afternoon light',intent:'Open structure, elegant proportions',performance:'Not specified',seed:200,guidance:7.5,steps:30,negative:'',width:512,height:512});
export const materialOptions=Object.freeze({material:Object.freeze(materialExperiment?.samples.map(s=>s.label)||[])});
export function materialPrompt(s){return materialExperiment.promptTemplate.replace('{material}',s.material.toLowerCase());}
function materialSample(s){
  if(Object.keys(materialDefaults).some(k=>k!=='material'&&s[k]!==materialDefaults[k]))throw Error('This recorded experiment holds all non-material inputs fixed.');
  const sample=materialExperiment?.samples.find(item=>item.label===s.material);
  if(!sample)throw Error('No recorded output for this material. Your saved comparison is unchanged.');
  return sample;
}
export {materialExperiment};
export function changes(a,b){return Object.keys(defaults).filter(k=>a[k]!==b[k]).map(k=>({key:k,label:labels[k],before:a[k],after:b[k]}));}
export function escapeText(value){return String(value).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
export function validate(s){
  for(const k of promptKeys) if(!options[k].includes(s[k])) throw Error('Choose one of the supplied prompt options.');
  if(!Number.isInteger(s.seed)||s.seed<0||s.seed>999999) throw Error('Use a whole-number seed between 0 and 999999.');
  if(![3,7.5,12].includes(s.guidance)||![10,25,30,50,75].includes(s.steps)) throw Error('Choose a supplied guidance and step setting.');
  if(typeof s.negative!=='string'||s.negative.length>300) throw Error('Keep the negative prompt under 300 characters.');
}
/* Stable framing for all images. Variation is deliberately authored: it is not
   evidence that a particular diffusion model produces this response. */
export function illustration(s){
  validate(s);
  const example=examples.find(item=>changes({...defaults,...item.settings},s).length===0);
  if(example){
    if(!/^assets\/generative\/[a-zA-Z0-9_./-]+$/.test(example.src)||example.src.includes('..'))throw Error('Use a local generation asset path.');
    return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 450" role="img" aria-label="${escapeText(example.alt)}"><title>${escapeText(example.provenance)}</title><image href="${escapeText(example.src)}" width="720" height="450" preserveAspectRatio="xMidYMid meet"/></svg>`;
  }
  const m=options.material.indexOf(s.material), seed=(s.seed*1664525+1013904223)>>>0;
  const shift=seed%27, roof=148-m*13-(s.intent==='Geometric terraces'?18:0), wide=s.building==='Pavilion'?340:395;
  const floors=s.building==='Mid-rise housing'?3:2, height=floors*44;
  const sky=s.lighting==='Warm evening light'?'#d1d1d1':'#eeeeee';
  const wall=['#adadad','#d3d3d3','#949494'][m], n=s.guidance===3?4:s.guidance===12?10:6;
  let svg=`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 450" role="img" aria-label="${escapeText(prompt(s))} Authored teaching illustration."><rect width="720" height="450" fill="${sky}"/><path d="M0 230L720 190V450H0Z" fill="#dedede"/><path d="M0 395L720 352M60 450L390 335M670 450L505 335" stroke="#b6b6b6" fill="none"/>`;
  if(s.context==='Seattle neighborhood') svg+='<path d="M25 334V155M56 333V200M665 333V150" stroke="#888" stroke-width="5"/><g fill="#999999"><ellipse cx="25" cy="160" rx="43" ry="82"/><ellipse cx="56" cy="210" rx="36" ry="54"/><ellipse cx="665" cy="173" rx="42" ry="90"/></g>';
  if(s.context==='Desert courtyard') svg+='<path d="M0 300Q100 225 230 297T720 275" stroke="#aaaaaa" fill="none"/><ellipse cx="574" cy="389" rx="49" ry="13" fill="#b5b5b5"/>';
  svg+=`<path d="M102 ${roof+height+53}L${wide+110} ${roof+height+53}L620 ${roof+height+6}L238 ${roof+height+6}Z" fill="#9c9c9c"/><path d="M110 ${roof}L${wide+110} ${roof}L620 ${roof-46}L240 ${roof-46}Z" fill="#f8f8f8" stroke="#333"/><path d="M110 ${roof}H${wide+110}V${roof+height+45}H110Z" fill="${wall}" stroke="#333"/><path d="M${wide+110} ${roof}L620 ${roof-46}V${roof+height}L${wide+110} ${roof+height+45}Z" fill="#727272" stroke="#333"/>`;
  for(let row=0;row<floors;row++) for(let i=0;i<n;i++){
    const x=132+i*(wide-38)/n+shift/4, y=roof+15+row*43;
    const w=(wide-65)/n-8, h=!s.negative&&i===3?39:27;
    svg+=`<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="#424242" stroke="#eee" stroke-width="1"/><path d="M${x+2} ${y+h-5}L${x+w-2} ${y+5}" stroke="#a4a4a4" opacity=".65"/>`;
  }
  if(m===0) for(let x=115;x<wide+108;x+=9) svg+=`<path d="M${x} ${roof+3}V${roof+height+40}" stroke="#444" opacity=".3"/>`;
  if(s.performance==='South-facing shading') for(let r=0;r<floors;r++)svg+=`<path d="M107 ${roof+11+r*43}H${wide+123}" stroke="#252525" stroke-width="6"/>`;
  if(s.performance==='Passive cooling') svg+=`<path d="M280 ${roof+height+45}V${roof+height-2}H328V${roof+height+45}" fill="#343434"/>`;
  const entrance=250+shift+m*35;
  svg+=`<rect x="${entrance}" y="${roof+height+3}" width="35" height="42" fill="#303030"/><path d="M${entrance-25} ${roof+height+45}h87v7h12v7h12v7H${entrance-40}" fill="#eee" stroke="#555"/>`;
  if(s.steps===10) svg+='<rect width="720" height="450" fill="#ededed" opacity=".19"/>';
  svg+='<path d="M83 360v25m-5 0h10M641 328v25m-5 0h10" stroke="#333" stroke-width="3"/><circle cx="83" cy="355" r="5" fill="#333"/><circle cx="641" cy="323" r="5" fill="#333"/></svg>';
  return svg;
}
export class Experiment {
  constructor({materialOnly=false}={}){this.materialOnly=materialOnly;this.reset();}
  reset(){this.original=null;this.previous=null;this.current=null;this.tests=0;}
  test(settings,oneChange=false){
    const sample=this.materialOnly?materialSample(settings):null;
    if(!this.materialOnly)validate(settings);
    if(this.current){const delta=changes(this.current.settings,settings);if(oneChange&&delta.length!==1)throw Error('Change exactly one variable before testing. Your saved generations are unchanged.');}
    const next=Object.freeze({settings:Object.freeze({...settings}),prompt:sample?sample.prompt:prompt(settings),svg:sample?null:illustration(settings),sample:sample?Object.freeze({...sample}):null,number:this.tests+1});
    this.previous=this.current;this.current=next;this.original??=next;this.tests++;return next;
  }
}
// Real control-lab series are intentionally separate from the schematic Prompt
// Builder domain: each task has its own recorded prompt and fixed settings.
export function controlledSeries(key){
  const experiment=notebookExperiments[key];
  if(!experiment?.samples.length)throw Error('No recorded notebook comparison for this setting.');
  return experiment.samples;
}
export function controlledExperiment(key){
  if(!notebookExperiments[key])throw Error('Unknown notebook experiment.');
  return notebookExperiments[key];
}
export function record(experiment,notes){
  return {designIntent:notes.designIntent||'',originalPrompt:experiment.original?.prompt||'',currentPrompt:experiment.current?.prompt||'',
    changedVariables:experiment.original&&experiment.current?changes(experiment.original.settings,experiment.current.settings):[],
    immediatelyPreviousPrompt:experiment.previous?.prompt||'',expectedChange:notes.expectedChange||'',observedChange:notes.observedChange||'',
    unexpectedChanges:notes.unexpectedChanges||'',architecturalLimitations:notes.architecturalLimitations||'',
    informationNeeded:notes.informationNeeded||'',nextStep:notes.nextStep||'',reflection:notes.reflection||''};
}
