#!/usr/bin/env python3
"""Extract audited embedded PNGs. Never imports or executes notebook code.
Requires Pillow only for lossless panel crops; no resizing or image generation.
"""
import argparse
import base64
import hashlib
import io
import json
from pathlib import Path
from PIL import Image

SOURCE_SHA = '6f935c8115fb3ec4084c5ed1c442d7957e7a3e3287fb5fe0247010c802b8af7b'
ROOT = Path(__file__).resolve().parents[1]
# Coordinates are [left, top, right-exclusive, bottom-exclusive] in the embedded
# PNG, checked against its visible subplot edges. Panel order comes from code.
AUDIT = {
 'seed': dict(task=2, cell=42, output=4, size=[1789,473],
              boxes=[[10,32,442,463],[456,32,888,463],[903,32,1335,463],[1349,32,1781,463]],
              values=[100,200,300,400], filenames=['seed-100','seed-200','seed-300','seed-400']),
 'guidance': dict(task=3, cell=45, output=5, size=[1990,424],
                  boxes=[[10,32,393,414],[407,32,789,414],[804,32,1186,414],[1201,32,1583,414],[1598,32,1980,414]],
                  values=[2.0,5.0,7.5,10.0,15.0], filenames=['guidance-2','guidance-5','guidance-7-5','guidance-10','guidance-15']),
 'negative': dict(task=11, cell=71, output=2, size=[1041,490], folder='negative-prompt',
                  boxes=[[10,32,458,480],[584,32,1032,480]],
                  values=[None,'blurry, low quality, distorted, people, text'],filenames=['negative-off','negative-on']),
 'resolution': dict(task=12, cell=74, output=3, size=[1698,490],
                    boxes=[[10,32,458,480],[654,32,953,480],[1057,46,1689,467]],
                    values=[dict(width=512,height=512),dict(width=512,height=768),dict(width=768,height=512)],
                    filenames=['resolution-512x512','resolution-512x768','resolution-768x512']),
 'steps': dict(task=13, cell=77, output=4, size=[1959,514],
               boxes=[[10,53,461,504],[506,53,957,504],[1003,53,1454,504],[1499,53,1950,504]],
               values=[10,25,50,75],filenames=['steps-10','steps-25','steps-50','steps-75'],seconds=[3.0,7.0,13.7,18.1]),
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def literal_assignment(source, name):
    # Read string literals only; evaluating or executing notebook code is forbidden.
    import ast
    for node in ast.parse(source).body:
        if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in node.targets):
            return ast.literal_eval(node.value)
    raise ValueError('Missing recorded assignment: '+name)


def material_catalogue():
    """Keep the separately rerun Task 4 distinct from old confounded outputs."""
    folder=ROOT/'assets/generative/real-experiments/material'
    path=folder/'provenance.json'
    if not path.exists():
        return None
    data=json.loads(path.read_text())
    if data['status']!='complete':
        raise ValueError('Material run is incomplete')
    samples=[]
    for item in data['samples']:
        image=folder/item['file']
        if image.parent!=folder or digest(image.read_bytes())!=item['png_sha256']:
            raise ValueError('Material image does not match its provenance')
        samples.append({k:item[k] for k in ['material','prompt','seed','width','height','png_sha256']}
                       | {'label':item['material'].capitalize(),'src':str(image.relative_to(ROOT))})
    first=data['samples'][0]
    return {'task':4,'source':'New controlled Colab rerun, not the original confounded Task 4',
            'model':first['model'],'revision':first['model_revision'],
            'scheduler':first['scheduler_class'].split('.')[-1],
            'promptTemplate':first['prompt_template'],
            'fixed':first['fixed_explicit_call_arguments'],
            'provenance':str(path.relative_to(ROOT)),'samples':samples}


def extract(source):
    raw=source.read_bytes()
    if digest(raw)!=SOURCE_SHA:
        raise ValueError('Notebook changed; audit code, output indexes and crop boxes again before extraction.')
    nb=json.loads(raw)
    cell_source=lambda i: ''.join(nb['cells'][i]['source'])
    prompts={key:literal_assignment(cell_source(cell),name) for key,cell,name in [
        ('seed',40,'prompt'),('guidance',45,'prompt3'),('negative',71,'prompt11'),
        ('resolution',74,'prompt12'),('steps',77,'prompt13')]}
    out=ROOT/'assets/generative/real-experiments';(out/'source-figures').mkdir(parents=True,exist_ok=True)
    model={'identifier':'runwayml/stable-diffusion-v1-5','pipeline_class':'StableDiffusionPipeline',
           'source_cell':8,'declared_dtype':'torch.float16','declared_device':'cuda',
           'attention_slicing':True,'safety_checker':None,
           'text_encoder_snapshot_in_load_log':'451f4fe16113bff5a5d2269ed5ad43b0592e9a14',
           'revision_note':'No revision explicitly pinned in the load call; the text encoder snapshot is reported by the saved load log, not a separately verified revision for every model component.',
           'scheduler':'Not recorded','diffusers_version':'Not recorded','torch_version':'Not recorded',
           'runtime_hardware_note':'Notebook metadata reports a T4 GPU; exact runtime environment is not fully recorded.'}
    manifest={'source':'Completed course notebook','notebook':source.name,'notebook_sha256':digest(raw),
              'index_convention':'Zero-based notebook cell and output; one-based subplot panel',
              'method':'Decode embedded image/png; lossless rectangular crop of each full subplot image; no rerun, regeneration, rescaling or screenshot.',
              'model':model,'experiments':{},
              'task4':{'status':'Exploratory, confounded; not used as a controlled material comparison',
                       'source_cell':48,'materials':['timber','steel and glass','rammed earth'],'seeds':[200,201,202]},
              'limitations':['Some source cells have null execution_count despite saved outputs; provenance follows saved code and subplot order, not a reconstructed execution history.',
                            'The preserved resolution is the embedded Matplotlib panel resolution, not the original in-memory PIL image resolution.',
                            'Except Task 12, output width/height were not explicitly passed and are not inferred from image appearance.',
                            'Task 13 times are rounded values read from the saved figure titles for this one run, not general performance benchmarks.']}
    for key,spec in AUDIT.items():
        data=nb['cells'][spec['cell']]['outputs'][spec['output']]['data']['image/png']
        data=base64.b64decode(''.join(data) if isinstance(data,list) else data)
        image=Image.open(io.BytesIO(data));image.load()
        assert list(image.size)==spec['size']
        original=out/'source-figures'/f'task-{spec["task"]:02d}.png';original.write_bytes(data)
        base=dict(prompt=prompts[key],seed={'seed':None,'guidance':123,'negative':123,'resolution':222,'steps':321}[key],
                  guidance=7.5,steps=30,negative=None,width=None,height=None)
        group={'task':spec['task'],'changed_setting':key,'source_cell':spec['cell'],'source_output':spec['output'],
               'source_code':cell_source(spec['cell']),'execution_count':nb['cells'][spec['cell']].get('execution_count'),
               'original':str(original.relative_to(ROOT)),'original_size':list(image.size),'original_sha256':digest(data),
               'prompt':prompts[key],'prompt_source_cell':40 if key=='seed' else spec['cell'],
               'baseline_settings':base,'samples':[]}
        folder=out/spec.get('folder',key);folder.mkdir(exist_ok=True)
        for i,(box,value,name) in enumerate(zip(spec['boxes'],spec['values'],spec['filenames'])):
            panel=image.crop(box);destination=folder/(name+'.png');panel.save(destination,format='PNG',optimize=True)
            settings={**base,**(value if key=='resolution' else {key:value})}
            if key=='negative':label='Without negative prompt' if value is None else 'With negative prompt'
            elif key=='resolution':label=f'{value["width"]} × {value["height"]} (width × height)'
            elif key=='steps':label=f'{value} steps'
            else:label=f'{key.capitalize()} = {value:g}'
            sample={'panel':i+1,'label':label,'settings':settings,'src':str(destination.relative_to(ROOT)),
                    'alt':f'Task {spec["task"]}, panel {i+1}: {label}. Precomputed architectural model output from the completed notebook.',
                    'crop_box':box,'pixel_size':list(panel.size),'mode':panel.mode,
                    'png_sha256':digest(destination.read_bytes()),'pixels_sha256':digest(panel.tobytes())}
            if key=='steps':sample.update(elapsed_seconds=spec['seconds'][i],timing_source='Rounded text in the original embedded figure title')
            group['samples'].append(sample)
        manifest['experiments'][key]=group
    (out/'provenance.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    catalogue={key:{'task':g['task'],'prompt':g['prompt'],'original':g['original'],'samples':g['samples']}
               for key,g in manifest['experiments'].items()}
    (ROOT/'assets/generative/examples.mjs').write_text(
        '// Extracted from saved notebook PNGs. Generated by tools/extract_generative_notebook.py.\n'
        '// Task-specific real outputs are registered separately from generic schematic settings.\n'
        'export default [];\n\nexport const notebookExperiments = '+json.dumps(catalogue,ensure_ascii=False,indent=2)+';\n'
        +'\nexport const materialExperiment = '+json.dumps(material_catalogue(),ensure_ascii=False,indent=2)+';\n')
    print(f'Extracted {sum(len(g["samples"]) for g in catalogue.values())} lossless panels and five original PNGs to {out}')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('notebook',type=Path)
    extract(parser.parse_args().notebook)
