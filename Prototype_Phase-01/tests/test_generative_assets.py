"""Verify lossless extraction and the audited code-to-panel mapping; no inference."""
import ast
import hashlib
import json
from pathlib import Path
import unittest
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'assets/generative/real-experiments'


def sha(data):return hashlib.sha256(data).hexdigest()


class RecordedGenerativeAssets(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.manifest=json.loads((ASSETS/'provenance.json').read_text())
    def test_originals_and_all_panel_pixels_are_preserved(self):
        count=0
        for group in self.manifest['experiments'].values():
            original=ROOT/group['original'];self.assertEqual(sha(original.read_bytes()),group['original_sha256'])
            with Image.open(original) as image:
                self.assertEqual(list(image.size),group['original_size'])
                for sample in group['samples']:
                    file=ROOT/sample['src'];self.assertEqual(sha(file.read_bytes()),sample['png_sha256'])
                    expected=image.crop(sample['crop_box'])
                    with Image.open(file) as actual:
                        self.assertEqual(actual.mode,expected.mode)
                        self.assertEqual(actual.tobytes(),expected.tobytes())
                        self.assertEqual(list(actual.size),sample['pixel_size'])
                        self.assertEqual(sha(actual.tobytes()),sample['pixels_sha256'])
                    count+=1
        self.assertEqual(count,18)
    def test_task_and_subplot_setting_assignment(self):
        expected={'seed':(2,42,4,'seed',[100,200,300,400]),
                  'guidance':(3,45,5,'guidance',[2,5,7.5,10,15]),
                  'negative':(11,71,2,'negative',[None,'blurry, low quality, distorted, people, text']),
                  'steps':(13,77,4,'steps',[10,25,50,75])}
        for key,(task,cell,output,setting,values) in expected.items():
            group=self.manifest['experiments'][key]
            self.assertEqual((group['task'],group['source_cell'],group['source_output']),(task,cell,output))
            self.assertEqual([s['settings'][setting] for s in group['samples']],values)
            self.assertEqual([s['panel'] for s in group['samples']],list(range(1,len(values)+1)))
        resolution=self.manifest['experiments']['resolution']['samples']
        self.assertEqual([(s['settings']['width'],s['settings']['height']) for s in resolution],[(512,512),(512,768),(768,512)])
        for sample in resolution:
            width,height=sample['pixel_size'];settings=sample['settings']
            self.assertAlmostEqual(width/height,settings['width']/settings['height'],delta=.004)
    def test_manifest_is_consistent_with_saved_code_not_appearance(self):
        groups=self.manifest['experiments']
        for key,var in [('seed','seeds'),('guidance','guidance_values'),('steps','steps_list')]:
            nodes=ast.parse(groups[key]['source_code']).body
            value=next(ast.literal_eval(n.value) for n in nodes if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id==var for t in n.targets))
            self.assertEqual(value,[s['settings'][key] for s in groups[key]['samples']])
        for key,seed in [('guidance',123),('negative',123),('steps',321),('resolution',222)]:
            self.assertTrue(all(s['settings']['seed']==seed for s in groups[key]['samples']))
        self.assertIn('torch.Generator("cuda").manual_seed(123)',groups['negative']['source_code'])
        self.assertEqual(groups['negative']['source_code'].count('manual_seed(123)'),2)
        for key,group in groups.items():
            for sample in group['samples']:
                self.assertEqual(sample['settings']['prompt'],group['prompt'])
                if key!='guidance':self.assertEqual(sample['settings']['guidance'],7.5)
                if key!='steps':self.assertEqual(sample['settings']['steps'],30)
                if key!='resolution':self.assertIsNone(sample['settings']['width']);self.assertIsNone(sample['settings']['height'])
        self.assertEqual(self.manifest['task4']['seeds'],[200,201,202])
        self.assertNotIn('material',groups)
        self.assertEqual(self.manifest['model']['scheduler'],'Not recorded')

    def test_controlled_material_rerun_has_only_one_input_difference(self):
        folder=ASSETS/'material';manifest=json.loads((folder/'provenance.json').read_text())
        self.assertEqual(manifest['status'],'complete')
        self.assertEqual(manifest['same_runtime_timber_repeatability'],'pixel-identical')
        samples=manifest['samples']
        self.assertEqual([s['material'] for s in samples],['timber','concrete','steel and glass','rammed earth'])
        allowed={'material','prompt','file','png_sha256','pixels_sha256'}
        fixed=lambda s:{k:v for k,v in s.items() if k not in allowed}
        for sample in samples:
            self.assertEqual(fixed(sample),fixed(samples[0]))
            self.assertEqual(sample['prompt'],sample['prompt_template'].replace('{material}',sample['material']))
            self.assertEqual(sample['seed'],200)
            self.assertEqual(sample['fixed_explicit_call_arguments'],{'height':512,'width':512,'num_inference_steps':30,'guidance_scale':7.5})
            self.assertEqual(sha((folder/sample['file']).read_bytes()),sample['png_sha256'])
            self.assertEqual(json.loads((folder/sample['file'].replace('.png','.json')).read_text()),sample)
            with Image.open(folder/sample['file']) as image:
                self.assertEqual(image.size,(512,512))
                self.assertEqual(sha(image.tobytes()),sample['pixels_sha256'])


if __name__=='__main__':unittest.main()
