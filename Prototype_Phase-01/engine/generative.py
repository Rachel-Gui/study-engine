"""Content-configured studios. Prose/questions remain in episode Markdown YAML.
Only this directive loads its scoped assets; the global runner is untouched.
"""
import html, json, yaml
from parse import inline


def e(value):
    return html.escape(str(value), quote=True)


def area(key, label):
    return f'<label class="ga-field">{e(label)}<textarea data-note="{e(key)}" rows="3"></textarea></label>'


def question(config, key="prediction"):
    return area(key, config['question'])


def web(b):
    cfg = yaml.safe_load(b['body'])
    mode = b['attrs']['kind']
    content = ''
    if mode == 'diffusion':
        content = (question(cfg) + '<button type="button" data-start>Explore my prediction</button>'
                   '<div class="ga-diffusion"><div data-scene></div><canvas width="360" height="225" aria-hidden="true"></canvas></div>'
                   '<label class="ga-field">Denoising checkpoint <output data-count>0 / 30</output>'
                   '<input data-denoise type="range" min="0" max="30" value="0" disabled></label>'
                   f'<p>{e(cfg["pipeline"])}</p><p data-explanation hidden>{inline(cfg["explanation"])}</p>')
    elif mode in ('prompt', 'workflow'):
        stage = lambda n,title,body: f'<fieldset class="ga-stage" data-stage="{n}" {"hidden" if n else ""}><legend>{n+1:02d} · {e(title)}</legend>{body}</fieldset>'
        fields = '<div class="ga-fields" data-fields></div><p class="ga-prompt" data-prompt aria-live="polite"></p>'
        if mode == 'prompt':
            content = (fields + question(cfg, 'expectedChange') + '<div class="ga-actions"><button type="button" data-generate>Select initial example</button>'
                       '<button type="button" data-reset>Reset experiment</button></div>'
                       '<div data-comparison></div>' + area('observedChange',cfg['observe']) +
                       f'<details class="exp" data-answer hidden><summary>Show reference answer</summary><p>{inline(cfg["explanation"])}</p></details>')
        else:
            titles=cfg['stages']
            content='<p data-progress role="status">Stage 1 of 8</p>'
            content+=stage(0,titles[0],area('designIntent',cfg['define']))
            content+=stage(1,titles[1],fields)
            content+=stage(2,titles[2],f'<p>{e(cfg["generate"])}</p><button type="button" data-generate>Select initial example</button><div data-initial></div>')
            content+=stage(3,titles[3],f'<p>{e(cfg["control"])}</p><label class="ga-field">Variable to change<select data-change-key></select></label><label class="ga-field">New value<select data-change-value></select></label>'+area('expectedChange',cfg['expect'])+'<button type="button" data-retest>Test one change</button>')
            content+=stage(4,titles[4],'<div data-comparison></div>'+area('observedChange',cfg['observe'])+area('unexpectedChanges',cfg['unexpected']))
            content+=stage(5,titles[5],area('architecturalLimitations',cfg['critique']))
            content+=stage(6,titles[6],area('informationNeeded',cfg['translate'])+area('nextStep',cfg['next']))
            content+=stage(7,titles[7],area('reflection',cfg['reflect'])+'<button type="button" data-record>Update design experiment record</button><div data-record-output></div><button type="button" data-download>Download record (JSON)</button>')
            content+='<div class="ga-actions"><button type="button" data-back>Previous stage</button><button type="button" data-next>Continue</button><button type="button" data-reset>Reset workflow</button></div>'
    elif mode == 'controls':
        for i,item in enumerate(cfg['experiments']):
            content+=(f'<fieldset class="ga-stage" data-experiment="{e(item["key"])}" {"hidden" if i else ""}><legend>{e(item["title"])}</legend>'
                      +question(item,item['key'])+f'<p>{e(item["fixed"])}</p><button type="button" data-reveal>Test this prediction</button>'
                      '<div data-series></div>'+f'<p data-explanation hidden>{inline(item["explanation"])}</p>'
                      +(f'<button type="button" data-unlock hidden>Next controlled experiment</button>' if i<len(cfg['experiments'])-1 else '')+'</fieldset>')
    elif mode == 'critic':
        content=(f'<figure><img src="{e(cfg["image"])}" alt="{e(cfg["alt"])}" loading="lazy"><figcaption>{e(cfg["caption"])}</figcaption></figure>'
                 +question(cfg)+ '<div class="ga-checklist">'+''.join(f'<label><input type="checkbox" data-critique value="{i}"> {e(item["label"])}</label>' for i,item in enumerate(cfg['checks']))+'</div>'
                 +'<button type="button" data-critique-reveal>Compare with architectural review</button><div data-critique-output hidden></div>')
    elif mode == 'pipeline':
        content=question(cfg)+'<button type="button" data-start>Inspect the translation</button><ol class="ga-pipeline">'
        for i,item in enumerate(cfg['stages']):content+=f'<li><button type="button" data-pipeline-step="{i}" disabled>{i+1:02d} · {e(item["title"])}</button></li>'
        content+='</ol><div data-pipeline-output></div>'
    else:
        raise ValueError('Unknown generative studio mode: '+mode)
    payload=json.dumps(cfg,ensure_ascii=False).replace('&','\\u0026').replace('<','\\u003c').replace('>','\\u003e')
    return (f'<link rel="stylesheet" href="assets/generative/lab.css"><div class="wg ga" data-genlab="{e(mode)}">'
            f'<div class="wg-hd"><span class="k">Explore</span><strong>{e(cfg["title"])}</strong></div>'
            f'<div class="ga-body"><p class="ga-disclosure">{e(cfg["disclosure"])}</p>{content}'
            '<p class="ga-status" data-status role="status" aria-live="polite"></p></div>'
            f'<script type="application/json" data-config>{payload}</script></div>'
            '<script type="module" src="assets/generative/lab.mjs?v=controlled-task4-1"></script>')


def frame(b):
    cfg=yaml.safe_load(b['body'])
    return f'<aside class="f-key"><strong>{e(cfg["title"])}</strong><p>{e(cfg["takeaway"])}</p></aside>'
