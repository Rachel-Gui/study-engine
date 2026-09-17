"""Static integration checks; run after engine/build.py from Prototype_Phase-01."""
import ast
import contextlib
import io
import json
from pathlib import Path
import re
import sys
import unittest
from html.parser import HTMLParser
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'engine'))
import yaml
import components
from parse import parse_episode, GLOSSARY
from render_web import slug

class Page(HTMLParser):
    def __init__(self,text):
        super().__init__(convert_charrefs=True);self.tags=[];self.text=[];self.scripts=0;self.feed(text)
    def handle_starttag(self,tag,attrs):
        self.tags.append((tag,dict(attrs)))
        if tag=='script':self.scripts+=1
    def handle_endtag(self,tag):
        if tag=='script':self.scripts-=1
    def handle_data(self,data):
        if not self.scripts:self.text.append(data)

class GenerativeBuild(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.course=yaml.safe_load((ROOT/'course.yml').read_text());GLOSSARY.update(cls.course['glossary'])
        cls.modules=[m for m in cls.course['modules'] if m['title']=='Module 1 — Generative AI']
    def test_navigation_and_all_episodes(self):
        self.assertEqual(len(self.modules),1)
        self.assertEqual(self.course['modules'][1],self.modules[0])
        self.assertEqual(len(self.modules[0]['episodes']),7)
        total=0
        for file in self.modules[0]['episodes']:
            meta,topics=parse_episode(ROOT/'content'/file)
            for topic in topics:
                page=ROOT/'site'/f'{slug(meta["episode"])}-{slug(topic["title"])}.html'
                self.assertTrue(page.is_file());self.assertIn('Module 1',page.read_text());total+=1
                for block in topic['blocks']:
                    self.assertIn(block['kind'],components.REGISTRY)
                    components.render(block,'frame')
        self.assertEqual(total,16)
    def test_local_assets_and_clean_popovers(self):
        for path in (ROOT/'site').glob('1-*.html'):
            page=Page(path.read_text());self.assertNotIn('{{',''.join(page.text))
            self.assertNotIn('}}',''.join(page.text))
            for tag,attrs in page.tags:
                if 'data-def' in attrs:
                    for bad in ('{{','**','&gt;','&lt;','&#','<span'):
                        self.assertNotIn(bad,attrs['data-def'])
                for key in ('src','href'):
                    link=attrs.get(key,'')
                    if link and not re.match(r'https?:|mailto:|#|data:',link):self.assertTrue((ROOT/'site'/urlsplit(link).path).is_file(),link)
                if tag=='img':self.assertTrue(attrs.get('alt'))
        self.assertFalse(list((ROOT/'site/assets').rglob('*.ipynb')))
        self.assertFalse(list((ROOT/'site/assets').rglob('*.pptx')))
    def test_safe_content_payload_and_static_fallback(self):
        block={'attrs':{'kind':'prompt'},'body':yaml.safe_dump(dict(title='Test < title',question='x < y?',observe='Describe',explanation='Do not use </script> as markup',disclosure='Illustration',takeaway='A > B'))}
        html=components.render({'kind':'genlab',**block})
        self.assertIn('\\u003c/script\\u003e',html)
        self.assertNotIn('Do not use </script>',html)
        self.assertIn('A &gt; B',components.render({'kind':'genlab',**block},'frame'))
    def test_python_record_and_existing_agentic_lab(self):
        for file in ('module-1/1.6-image-to-architecture.md','module-4/4.1-what-is-an-agent.md'):
            _,topics=parse_episode(ROOT/'content'/file)
            for topic in topics:
                for block in topic['blocks']:
                    if block['kind']=='pylab':
                        ns={}
                        for _,code in components._steps(block['body']):
                            with contextlib.redirect_stdout(io.StringIO()):exec(code,ns)
                        if file.startswith('module-1'):
                            self.assertEqual(ns['changed'],{'seed':(100,200)})
                            self.assertEqual(ns['experiment']['current']['seed'],200)

if __name__=='__main__':unittest.main()
