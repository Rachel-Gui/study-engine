"""
stage.py - the animated scene templates the lesson videos are built from.

A storyboard (content/<module>/<lesson>.video.md) is a list of scenes. Each
scene type here turns its fields into a 1280x720 HTML "stage" whose elements
carry animation attributes:

    data-beat="k"        the reveal this element belongs to (0 = at the start)
    data-delay="0.2"     seconds after the beat starts
    data-dur="0.6"       how long its animation runs
    data-anim="rise"     rise | fade | pop | draw | growx | growy | count | type | ring

The runtime (STAGE_JS) is deterministic: seek(t) sets every element's style for
time t, so the renderer can screenshot any instant. Beat times are chosen by the
renderer from the narration's word timings and passed in with setBeats().

Diagrams (the course's SVG figures) are prepared in the browser: every stroke is
drawn with a dash-offset animation and every fill or label fades in, in document
order, grouped into a handful of beats - so an existing figure becomes a build.
"""
import base64, html, math, mimetypes, os, re

import figures, figures_lit, screens, widgets

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

W, H = 1280, 720
ACCENT, ACCENT2, SOFT, GOLD, GOLD_DEEP, INK, INK2 = "#4b2e83", "#6a4fa8", "#efeaf7", "#e8e3d3", "#b7a57a", "#111", "#3a3a3a"

CSS = ("""
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:__W__px;height:__H__px;overflow:hidden}
body{background:#fff;color:#111;font-family:Montserrat,sans-serif;position:relative}
.topbar{position:absolute;left:0;top:0;right:0;height:5px;background:__ACCENT__}
.eyebrow{position:absolute;left:72px;top:30px;font-size:11.5px;font-weight:700;letter-spacing:.22em;text-transform:uppercase;color:__ACCENT__}
.eyebrow b{color:#111;font-weight:700}
.band{position:absolute;left:0;right:0;bottom:0;height:92px;border-top:1px solid #e2e2e2;background:#fff}
.stage{position:absolute;left:72px;right:72px;top:72px;bottom:104px;display:flex;flex-direction:column;justify-content:center}
.stage>*{flex:0 0 auto}
[data-beat]{opacity:0;will-change:opacity,transform}
h1.big{font-size:44px;font-weight:600;letter-spacing:-.022em;line-height:1.12;color:#111;max-width:24ch}
h1.big .l{display:block}
h2.hd{font-size:26px;font-weight:600;letter-spacing:-.015em;line-height:1.2;color:#111;margin-bottom:22px;max-width:44ch}
h2.hd::after{content:"";display:block;width:48px;height:3px;background:__ACCENT__;margin-top:12px}
.sub{font-size:19px;line-height:1.5;color:#3a3a3a;max-width:56ch;margin-top:22px}
.small{font-size:15px;line-height:1.5;color:#5a5a5a}
.gold{color:__GOLD_DEEP__}
.acc{color:__ACCENT__}

/* idea */
.idea{display:flex;flex-direction:column;justify-content:center;height:100%;padding-left:12px;border-left:4px solid __GOLD__}
.idea h1.big{font-size:46px;max-width:none}
.idea .ico{width:64px;height:64px;color:__ACCENT__;margin-bottom:24px}

/* list & recap */
.list{display:flex;flex-direction:column;gap:14px;max-width:820px}
.li{display:flex;gap:18px;align-items:flex-start;font-size:21px;line-height:1.4;color:#222}
.li .dash{flex:0 0 26px;height:3px;background:__ACCENT__;margin-top:14px;transform-origin:left;display:block}
.li b{font-weight:600;color:#111}
.li span{color:#3a3a3a}
.li svg.ck{flex:0 0 26px;height:26px;margin-top:2px}
.li svg.ck path{stroke:__ACCENT__;stroke-width:2.6;fill:none;stroke-linecap:round;stroke-linejoin:round}

/* cards */
.cards{display:grid;grid-template-columns:repeat(var(--n,3),1fr);gap:18px;margin-top:6px}
.card{border:1px solid #dcdcdc;border-top:4px solid __ACCENT__;padding:18px 20px 20px;background:#fff;min-height:150px;
  display:flex;flex-direction:column;gap:9px;transform-origin:center}
.card b{font-size:19px;font-weight:600;line-height:1.25}
.card span{font-size:15.5px;line-height:1.45;color:#3a3a3a}
.card i{font-style:normal;font:500 11.5px 'IBM Plex Mono',monospace;color:__ACCENT__;letter-spacing:.08em}

/* steps */
.steps{display:flex;flex-wrap:wrap;align-items:center;justify-content:flex-start;gap:14px 0;margin-top:8px}
.step{display:flex;align-items:center}
.box{border:1.6px solid #111;border-radius:8px;padding:18px 22px;font-size:19px;font-weight:600;line-height:1.25;background:#fff;
  min-width:170px;max-width:250px;text-align:center;transform-origin:center}
.box.hi{background:__GOLD__;border-color:__ACCENT__}
.box small{display:block;font-size:13px;font-weight:400;color:#3a3a3a;margin-top:5px;line-height:1.35}
.arrow{width:46px;height:20px;flex:0 0 46px}
.arrow path{stroke:__ACCENT__;stroke-width:2.2;fill:none;stroke-linecap:round}
.arrow .hd{stroke:__ACCENT__;stroke-width:2.2;fill:none}
.steps.rows .step{flex:0 0 auto}

/* compare */
.cmp{display:grid;grid-template-columns:1fr 64px 1fr;gap:0;align-items:start;margin-top:4px}
.pane{border:1px solid #dcdcdc;padding:22px 24px;background:#fff;min-height:300px;border-radius:6px}
.pane.a{border-top:4px solid __ACCENT__}
.pane.b{border-top:4px solid __GOLD_DEEP__}
.pane h3{font-size:22px;font-weight:600;margin-bottom:14px;letter-spacing:-.01em}
.pane .li{font-size:17.5px;gap:14px;margin-bottom:10px}
.pane .li .dash{flex-basis:18px;margin-top:11px}
.vs{align-self:center;text-align:center;font:600 15px 'IBM Plex Mono',monospace;color:__ACCENT__;letter-spacing:.1em}
.verdict{margin-top:18px;font-size:19px;color:#111;font-weight:500;border-left:4px solid __GOLD__;padding:10px 16px;background:#faf8f3}

/* numbers */
.nums{display:grid;grid-template-columns:repeat(var(--n,3),1fr);gap:26px;margin-top:20px}
.num{border-top:2px solid #111;padding-top:18px}
.num b{display:block;font-size:64px;font-weight:600;letter-spacing:-.03em;line-height:1;color:__ACCENT__;font-variant-numeric:tabular-nums}
.num span{display:block;font-size:17px;line-height:1.4;color:#3a3a3a;margin-top:12px;max-width:26ch}

/* code */
.codewrap{display:grid;grid-template-columns:1fr;gap:16px;margin-top:4px}
.codewrap.two{grid-template-columns:1.2fr .8fr}
pre.code{font:400 16px/1.62 'IBM Plex Mono',monospace;background:#f7f7f6;border-left:4px solid __ACCENT__;padding:18px 22px;
  white-space:pre;overflow:hidden;color:#111;border-radius:0 6px 6px 0;min-height:120px}
pre.code .ln{display:block;min-height:1.62em}
pre.code .cm{color:#6a6a6a}
pre.out{font:400 16px/1.55 'IBM Plex Mono',monospace;background:#111;color:#f3f3f1;padding:18px 22px;border-radius:6px;white-space:pre-wrap;min-height:120px}
pre.out .lbl{display:block;font:700 10.5px Montserrat,sans-serif;letter-spacing:.2em;color:#9a9a9a;margin-bottom:8px}
.codenote{font-size:17px;line-height:1.5;color:#3a3a3a;margin-top:14px;max-width:60ch}

/* chart */
.chart svg{width:100%;height:auto;display:block}
.chart .ax{stroke:#8a8a8a;stroke-width:1.2}
.chart .tk{font-size:13px;fill:#3a3a3a}
.chart .lb{font-size:14px;fill:#111;font-weight:600}
.chart .bar{fill:__ACCENT__;transform-origin:bottom}
.chart .bar.g{fill:__GOLD_DEEP__}
.chart .ln{stroke:__ACCENT__;stroke-width:3;fill:none;stroke-linecap:round}
.chart .ln.g{stroke:__GOLD_DEEP__}
.chart .pt{fill:#fff;stroke:__ACCENT__;stroke-width:2.5}
.chart .val{font-size:13px;fill:__ACCENT__;font-weight:600}
.chart .leg{font-size:14px;fill:#3a3a3a}

/* diagram: the figure takes the full width; optional points sit under it as a row */
.diag{display:flex;flex-direction:column;gap:18px;justify-content:center}
.diag .fig>svg{width:100%;height:auto;max-height:430px;display:block;margin:0 auto}
.diag.two .fig>svg{max-height:340px}
.diag .pts{display:grid;grid-template-columns:repeat(var(--n,3),1fr);gap:14px}
.diag .pts .li{font-size:16.5px;line-height:1.35;border:1px solid #dcdcdc;border-radius:6px;padding:12px 14px;gap:12px}
.diag .pts .li .dash{flex-basis:16px;margin-top:10px}

/* quiz */
.quiz h2.hd{max-width:38ch}
.opts{display:flex;flex-direction:column;gap:12px;max-width:820px}
.opt{display:flex;gap:16px;align-items:center;border:1.5px solid #d6d6d6;border-radius:8px;padding:14px 18px;font-size:19px;line-height:1.35;color:#222;background:#fff;position:relative}
.opt .k{flex:0 0 32px;height:32px;border-radius:50%;border:1.5px solid #111;display:grid;place-items:center;font:600 14px 'IBM Plex Mono',monospace}
.opt .ok{position:absolute;inset:-1.5px;border:2.5px solid __ACCENT__;border-radius:8px;background:rgba(75,46,131,.06);pointer-events:none}
.opt .ok::after{content:"";position:absolute;right:16px;top:50%;width:11px;height:20px;border:solid __ACCENT__;border-width:0 3px 3px 0;transform:translateY(-60%) rotate(45deg)}
.opt .no{position:absolute;inset:0;background:rgba(255,255,255,.55);border-radius:8px;pointer-events:none}
.pause{position:absolute;right:0;top:0;width:210px;text-align:center}
.pause svg{width:120px;height:120px;display:block;margin:0 auto 10px}
.pause .bg{stroke:#e6e6e6;stroke-width:8;fill:none}
.pause .fg{stroke:__ACCENT__;stroke-width:8;fill:none;stroke-linecap:round;transform:rotate(-90deg);transform-origin:center}
.pause b{display:block;font-size:14px;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:__ACCENT__}
.pause span{display:block;font-size:14px;color:#3a3a3a;margin-top:4px}
.explain{margin-top:18px;font-size:18px;line-height:1.5;color:#111;border-left:4px solid __GOLD__;padding:12px 16px;background:#faf8f3;max-width:820px}

/* site callout */
.site{display:grid;grid-template-columns:1.1fr .9fr;gap:40px;align-items:center;height:100%}
.laptop{border:3px solid #111;border-radius:14px;padding:14px;background:#fff;position:relative}
.laptop::after{content:"";position:absolute;left:-30px;right:-30px;bottom:-16px;height:12px;background:#111;border-radius:0 0 10px 10px}
.screen{background:#f7f7f6;border-radius:6px;height:300px;padding:18px 20px;overflow:hidden}
.screen .bar{height:26px;border-radius:5px;background:#fff;border:1px solid #ddd;font:500 12.5px 'IBM Plex Mono',monospace;color:#3a3a3a;padding:5px 10px;margin-bottom:16px;white-space:nowrap;overflow:hidden}
.screen .tt{font-size:17px;font-weight:600;margin-bottom:10px}
.screen .ln{height:9px;border-radius:3px;background:#e4e4e4;margin:8px 0;width:82%}
.screen .ln.s{width:60%}
.screen .btn{display:inline-block;margin-top:10px;border:1.5px solid __ACCENT__;color:__ACCENT__;font-size:11px;font-weight:700;letter-spacing:.12em;padding:7px 12px;border-radius:3px}
.screen .btn.on{background:__ACCENT__;color:#fff}
.site .txt h2.hd{margin-bottom:16px}
.site .txt p{font-size:19px;line-height:1.5;color:#3a3a3a;max-width:30ch}
.site .txt .path{font:500 14px 'IBM Plex Mono',monospace;color:__ACCENT__;margin-top:18px;line-height:1.6}

/* gallery: illustrated or photographed tiles */
.gal{display:grid;grid-template-columns:repeat(var(--n,4),1fr);gap:16px;margin-top:6px}
.tile{border:1px solid #dcdcdc;border-radius:8px;background:#fff;overflow:hidden;transform-origin:center;display:flex;flex-direction:column}
.tile .pic{background:#fbfbfa;border-bottom:1px solid #ececec;display:grid;place-items:center;aspect-ratio:4/3;overflow:hidden}
.gal.square .tile .pic{aspect-ratio:1/1}
.tile .pic svg{width:78%;height:auto}
.tile .pic svg.full{width:100%}
.tile .pic img{width:100%;height:100%;object-fit:cover;display:block}
.tile .cap{padding:10px 12px 12px}
.tile .cap b{display:block;font-size:14.5px;font-weight:600;line-height:1.25}
.tile .cap span{display:block;font-size:12px;line-height:1.35;color:#3a3a3a;margin-top:3px}
.tile .cap i{display:block;font:500 10px 'IBM Plex Mono',monospace;color:__ACCENT__;letter-spacing:.08em;margin-bottom:4px;font-style:normal}
.gal.rows2 .tile .pic{aspect-ratio:2.3/1}
.gal.rows2 .tile .pic svg{width:36%}
.gal.rows2 .tile .cap{padding:8px 12px 10px}
.gal.rows2 .tile .cap b{font-size:14px}.gal.rows2 .tile .cap span{font-size:11.5px}
.gal.n2 .tile .cap b{font-size:18px}.gal.n2 .tile .cap span{font-size:14px}
.gal.n3 .tile .cap b{font-size:16px}.gal.n3 .tile .cap span{font-size:13px}
.galnote{font-size:15px;line-height:1.45;color:#3a3a3a;margin-top:14px;max-width:70ch}
/* square photographs keep their whole frame: size the grid so the tiles fit the frame height */
.gal.square.rows2 .tile .pic{aspect-ratio:1/1}
.gal.square.rows2{max-width:740px}
.gal.square.n2{max-width:760px}
.gal.square.n2 .tile .cap{padding:10px 14px 12px}

/* image: one real picture with its caption */
.img{display:grid;grid-template-columns:1.25fr .75fr;gap:34px;align-items:center;height:100%}
.shot{display:flex;gap:30px;align-items:center;justify-content:center}
.shot.side{justify-content:flex-start}
.shot .col{display:flex;flex-direction:column;align-items:center;gap:10px}
.shotv{position:relative;border-radius:8px;box-shadow:0 14px 40px rgba(0,0,0,.18)}
.shotv .clip{position:absolute;inset:0;overflow:hidden;border-radius:8px;border:1px solid #d6d6d6;background:#fff}
.shot .scap{font-size:14.5px;line-height:1.45;color:#4a4a4a;max-width:900px;text-align:center}
.shot .list{flex:1;min-width:0}
.shot.under{flex-direction:column;gap:12px}
.shot.under .list{flex:none;display:flex;flex-wrap:wrap;justify-content:center;gap:6px 30px;max-width:1136px}
.shot.under .leg{margin-bottom:0;font-size:16px;align-items:center}
.shot.under .leg .mnum{margin-top:0}
.shot .list .li{font-size:17px}
.mark{position:absolute;border:2px solid __ACCENT__;border-radius:6px;box-shadow:0 0 0 3px rgba(75,46,131,.16),0 0 20px rgba(75,46,131,.32)}
.mark .mnum{position:absolute;left:-36px;top:50%;transform:translateY(-50%)}
.mnum{display:inline-grid;place-items:center;width:28px;height:28px;border-radius:50%;background:__ACCENT__;color:#fff;font:700 14px Montserrat,sans-serif;box-shadow:0 3px 10px rgba(0,0,0,.25);flex:0 0 28px}
.shot .leg{display:flex;gap:12px;align-items:flex-start;font-size:17px;line-height:1.4;margin-bottom:16px;color:#222}
.shot .leg .mnum{margin-top:-2px}
.mark .mlab{position:absolute;white-space:nowrap;background:__ACCENT__;color:#fff;font:600 14px Montserrat,sans-serif;padding:6px 11px;border-radius:5px;box-shadow:0 4px 14px rgba(0,0,0,.2)}
.img .pic{border:1px solid #dcdcdc;border-radius:8px;overflow:hidden;background:#fbfbfa;max-height:470px;justify-self:center;max-width:100%}
.img .pic img{width:auto;max-width:100%;height:auto;max-height:468px;display:block}
.img .txt h2.hd{margin-bottom:16px}
.img .txt p{font-size:18px;line-height:1.5;color:#3a3a3a}
.img .txt .credit{font:500 12px 'IBM Plex Mono',monospace;color:#6a6a6a;margin-top:16px;line-height:1.5}
.img .txt .list{margin-top:16px}
.img .txt .li{font-size:16.5px}

/* screen: a software environment mock-up */
.scr{display:grid;grid-template-columns:1.35fr .65fr;gap:30px;align-items:center;height:100%}
.scr.wide{grid-template-columns:1fr}
.scr .txt h2.hd{margin-bottom:14px}
.scr .txt p{font-size:17.5px;line-height:1.5;color:#3a3a3a}
.scr .txt .list{margin-top:14px}
.scr .txt .li{font-size:16px}
.scr .mk{font-size:14px}
""" + screens.CSS + """

/* cards on purple */
body.cover{background:__ACCENT__;color:#fff}
body.cover .topbar{background:__GOLD__}
body.cover .eyebrow{color:__GOLD__}
body.cover .band{display:none}
body.cover .stage{top:40px;bottom:112px;display:flex;flex-direction:column;justify-content:center;left:96px;right:96px}
body.cover .kick{font-size:13px;font-weight:700;letter-spacing:.28em;text-transform:uppercase;color:__GOLD__;margin-bottom:22px}
body.cover h1.big{font-size:56px;color:#fff;max-width:none}
body.cover .rule{width:64px;height:3px;background:__GOLD__;margin:26px 0 0;transform-origin:left}
body.cover .objs{margin-top:30px;max-width:66ch}
body.cover .objs .lbl{font-size:11px;font-weight:700;letter-spacing:.24em;text-transform:uppercase;color:__GOLD__;margin-bottom:12px}
body.cover .objs .li{color:rgba(255,255,255,.94);font-size:18px}
body.cover .objs .li .dash{background:__GOLD__}
body.cover .li b{color:#fff}
body.cover .li span{color:rgba(255,255,255,.86)}
body.cover .who{position:absolute;left:96px;bottom:54px;font-size:13px;letter-spacing:.06em;color:rgba(255,255,255,.75)}
body.cover .sub{color:__GOLD__;font-size:22px;margin-top:24px}
""").replace("__W__", str(W)).replace("__H__", str(H)).replace("__ACCENT__", ACCENT).replace("__GOLD__", GOLD).replace("__GOLD_DEEP__", GOLD_DEEP)

STAGE_JS = r"""
window.STAGE = (function(){
  const ease = p => p <= 0 ? 0 : p >= 1 ? 1 : 1 - Math.pow(1 - p, 3);
  const lin = p => p <= 0 ? 0 : p >= 1 ? 1 : p;
  let els = [], times = [];
  function fit(){
    // safety net: content taller than the stage (a long gallery, a long title) is scaled
    // down about the stage centre instead of running into the eyebrow or the captions
    const st = document.querySelector('.stage'); if (!st) return 1;
    st.style.transform = '';
    let top = Infinity, bot = -Infinity;
    [...st.children].forEach(c => {
      const cs = getComputedStyle(c);
      if (cs.position === 'absolute' || cs.position === 'fixed' || !c.offsetHeight) return;
      top = Math.min(top, c.offsetTop - (parseFloat(cs.marginTop) || 0));
      bot = Math.max(bot, c.offsetTop + c.offsetHeight + (parseFloat(cs.marginBottom) || 0));
    });
    const need = bot - top, have = st.clientHeight;
    if (!(need > have + 2)) return 1;
    const k = Math.max(0.7, have / need);
    st.style.transformOrigin = '50% 50%';
    st.style.transform = 'scale(' + k.toFixed(4) + ')';
    return k;
  }
  function prepare(){
    const scale = fit();
    // diagrams: every drawable element becomes an animated element, grouped in document order
    document.querySelectorAll('svg[data-diagram]').forEach(svg => {
      const base = +svg.dataset.beatBase || 0, groups = +svg.dataset.groups || 8;
      const nodes = [...svg.querySelectorAll('path,line,polyline,polygon,rect,circle,ellipse,text')]
        .filter(n => !n.closest('defs') && !n.closest('marker'));
      const per = Math.max(1, Math.ceil(nodes.length / groups));
      nodes.forEach((n, i) => {
        const g = Math.floor(i / per), j = i % per;
        n.dataset.beat = base + g; n.dataset.delay = (j * (0.55 / per)).toFixed(3);
        const stroked = n.getAttribute('stroke') !== 'none' && (n.getAttribute('fill') === 'none' || n.getAttribute('fill') == null) && n.tagName !== 'text';
        if (stroked && typeof n.getTotalLength === 'function') {
          let L = 0; try { L = n.getTotalLength(); } catch(e) { L = 0; }
          if (L > 0 && isFinite(L)) {
            n.dataset.anim = 'draw'; n.dataset.len = L.toFixed(1); n.dataset.dur = Math.min(0.9, 0.35 + L / 900).toFixed(2);
            n.style.strokeDasharray = L + ' ' + L;
            const m = n.getAttribute('marker-end'); if (m) { n.dataset.marker = m; }
          } else { n.dataset.anim = 'fade'; n.dataset.dur = '0.4'; }
        } else { n.dataset.anim = 'fade'; n.dataset.dur = '0.45'; }
      });
      const G = Math.ceil(nodes.length / per);
      svg.dataset.groupCount = G;
      // elements declared relative to the diagram ("after:j") come after its groups
      document.querySelectorAll('[data-beat^="after:"]').forEach(e => {
        e.dataset.beat = base + G + (+e.dataset.beat.split(':')[1]);
      });
    });
    els = [...document.querySelectorAll('[data-beat]')].map(e => ({
      el: e, beat: +e.dataset.beat, delay: +(e.dataset.delay || 0), dur: +(e.dataset.dur || 0.6),
      anim: e.dataset.anim || 'rise'
    }));
    const count = els.length ? Math.max(...els.map(x => x.beat)) + 1 : 0;
    const spans = {};
    els.forEach(x => { spans[x.beat] = Math.max(spans[x.beat] || 0, x.delay + x.dur); });
    return { count, spans, scale };
  }
  function apply(x, t){
    const e = x.el, s = e.style, t0 = times[x.beat];
    if (t0 == null || t < t0 + x.delay) { hide(x); return; }
    const raw = (t - t0 - x.delay) / x.dur, p = ease(raw), q = lin(raw);
    switch (x.anim) {
      case 'fade':  s.opacity = p; s.transform = ''; break;
      case 'rise':  s.opacity = p; s.transform = `translateY(${((1 - p) * 18).toFixed(2)}px)`; break;
      case 'left':  s.opacity = p; s.transform = `translateX(${((1 - p) * -40).toFixed(2)}px)`; break;
      case 'right': s.opacity = p; s.transform = `translateX(${((1 - p) * 40).toFixed(2)}px)`; break;
      case 'pop':   s.opacity = Math.min(1, p * 1.6); s.transform = `scale(${(0.86 + 0.14 * p).toFixed(4)})`; break;
      case 'growx': s.opacity = 1; s.transform = `scaleX(${p.toFixed(4)})`; break;
      case 'growy': s.opacity = 1; s.transform = `scaleY(${p.toFixed(4)})`; break;
      case 'draw':  s.opacity = 1; s.strokeDashoffset = (+e.dataset.len * (1 - p)).toFixed(2);
                    if (e.dataset.marker) e.setAttribute('marker-end', p >= 0.97 ? e.dataset.marker : 'none'); break;
      case 'ring':  s.opacity = 1; s.strokeDashoffset = (+e.dataset.len * (1 - q)).toFixed(2); break;
      case 'count': { const a = +(e.dataset.from || 0), b = +e.dataset.to, d = +(e.dataset.dec || 0);
                    s.opacity = 1; e.textContent = (e.dataset.prefix || '') + (a + (b - a) * p).toFixed(d) + (e.dataset.suffix || ''); break; }
      case 'type':  { const f = e.dataset.text || ''; s.opacity = 1; e.textContent = f.slice(0, Math.round(f.length * q)); break; }
      case 'wipe':  s.opacity = 1; s.clipPath = `inset(0 ${((1 - p) * 100).toFixed(2)}% 0 0)`; break;
      default:      s.opacity = p; s.transform = '';
    }
  }
  function hide(x){
    const e = x.el, s = e.style;
    s.opacity = 0;
    if (x.anim === 'draw') { s.strokeDashoffset = e.dataset.len; if (e.dataset.marker) e.setAttribute('marker-end', 'none'); }
    if (x.anim === 'count') e.textContent = (e.dataset.prefix || '') + (+(e.dataset.from || 0)).toFixed(+(e.dataset.dec || 0)) + (e.dataset.suffix || '');
    if (x.anim === 'type') e.textContent = '';
  }
  function setBeats(t){ times = t; }
  function seek(t){ els.forEach(x => apply(x, t)); }
  return { prepare, setBeats, seek };
})();
"""


# --------------------------------------------------------------------- helpers

def _e(s):
    return html.escape(str(s if s is not None else ""))


_KEEP = ("VS Code", "Google Colab", "Claude Code", "GitHub Desktop", "GitHub Pages", "Stable Diffusion")


def _lines_of(text, max_chars=30):
    """Split a headline into 1-3 balanced lines (explicit ' / ' wins). The product names
    in _KEEP (VS Code, Google Colab, ...) are never split across lines."""
    text = str(text or "").strip()
    if " / " in text:                     # the author's breaks; a part too long for one line is split again
        return [l for p in text.split(" / ") if p.strip()
                for l in (_lines_of(p.strip(), max_chars) if len(p.strip()) > max_chars + 8 else [p.strip()])]
    glued = text
    for name in _KEEP:
        glued = glued.replace(name, name.replace(" ", "\u00a0"))
    words = [w.replace("\u00a0", " ") for w in glued.split(" ")]
    if len(text) <= max_chars or len(words) < 4:
        return [text]
    n = 2 if len(text) <= max_chars * 2 else 3
    per = math.ceil(len(words) / n)
    return [" ".join(words[i:i + per]) for i in range(0, len(words), per)]


def _fit_px(lines, base, width):
    """Largest font size (<= base) at which the longest headline line fits `width` px.
    Montserrat semibold runs about 0.5 em per character; 0.56 leaves a margin."""
    longest = max([len(l) for l in lines] or [1])
    return max(28, min(base, int(width / (0.56 * longest))))


def _item(text):
    """'term — explanation' -> (term, explanation); plain text -> ('', text)."""
    text = str(text or "")
    for sep in (" — ", " -- ", " – "):
        if sep in text:
            a, b = text.split(sep, 1)
            return a.strip(), b.strip()
    return "", text.strip()


def _li(text, beat, delay=0.0, check=False, anim="rise"):
    term, rest = _item(text)
    if check:
        mark = (f'<svg class="ck" viewBox="0 0 26 26"><path d="M4 14 L10 20 L22 6" data-beat="{beat}" data-delay="{delay + 0.15:.2f}" '
                f'data-anim="draw" data-len="30" data-dur="0.45"/></svg>')
    else:
        mark = f'<i class="dash" data-beat="{beat}" data-delay="{delay:.2f}" data-anim="growx" data-dur="0.4"></i>'
    body = (f"<b>{_e(term)}</b>&nbsp; <span>{_e(rest)}</span>" if term else f"<span>{_e(rest)}</span>")
    return (f'<div class="li">{mark}<div data-beat="{beat}" data-delay="{delay + 0.08:.2f}" '
            f'data-anim="{anim}" data-dur="0.5">{body}</div></div>')


def _arrow(beat, delay=0.0):
    return (f'<svg class="arrow" viewBox="0 0 46 20"><path d="M2 10 H38" data-beat="{beat}" data-delay="{delay:.2f}" '
            f'data-anim="draw" data-len="36" data-dur="0.35"/><path class="hd" d="M31 4 L39 10 L31 16" data-beat="{beat}" '
            f'data-delay="{delay + 0.28:.2f}" data-anim="fade" data-dur="0.15"/></svg>')


def _heading(text, beat=0):
    return f'<h2 class="hd" data-beat="{beat}" data-anim="rise" data-dur="0.55">{_e(text)}</h2>' if text else ""


def _svg_of(fig_id):
    """A course figure (or a widget's fallback figure) as an SVG string."""
    fn = figures.ALL.get(fig_id)
    if not fn and fig_id in widgets.ALL:
        fn = figures.ALL.get(widgets.ALL[fig_id][1])
    if not fn:
        return ""
    svg = fn()
    svg = re.sub(r'(<text\b[^>]*?\bopacity=")(0?\.\d+)(")',
                 lambda m: m.group(1) + (m.group(2) if float(m.group(2)) >= .78 else ".78") + m.group(3), svg)
    return svg


# -------------------------------------------------------------------- scenes
# Every builder returns (body_html, body_class, beats_declared). The beat count
# may grow in the browser for diagrams; the renderer reads the real count back.

def s_title(sc, ctx):
    objs = [o for o in (ctx.get("objectives") or []) if str(o).strip()]
    tl = _lines_of(ctx["title"], 26)
    b = [f'<div class="kick" data-beat="0" data-anim="rise">Lesson {_e(ctx["episode"])} · {_e(ctx["module"])}</div>',
         f'<h1 class="big" style="font-size:{_fit_px(tl, 56, 1040)}px">' + "".join(f'<span class="l" data-beat="0" data-delay="{0.12 + i * 0.12:.2f}" data-anim="rise" data-dur="0.6">{_e(l)}</span>'
                                       for i, l in enumerate(tl)) + '</h1>',
         f'<div class="rule" data-beat="0" data-delay="0.55" data-anim="growx" data-dur="0.5"></div>']
    beat = 1
    if objs:
        b.append('<div class="objs"><div class="lbl" data-beat="1" data-anim="fade">In this lesson</div>')
        for i, o in enumerate(objs):
            b.append(_li(o, beat + i))
        b.append("</div>")
        beat += len(objs)
    b.append(f'<div class="who" data-beat="0" data-delay="0.7" data-anim="fade">{_e(ctx.get("course", ""))} · {_e(ctx.get("instructor", ""))}</div>')
    return "".join(b), "cover", beat


def s_next(sc, ctx):
    tl = _lines_of(sc.get("text", ""), 26)
    b = [f'<div class="kick" data-beat="0" data-anim="rise">{_e(sc.get("kick", "Next lesson"))}</div>',
         f'<h1 class="big" style="font-size:{_fit_px(tl, 56, 1040)}px">' + "".join(f'<span class="l" data-beat="0" data-delay="{0.12 + i * 0.12:.2f}" data-anim="rise" data-dur="0.6">{_e(l)}</span>'
                                       for i, l in enumerate(tl)) + '</h1>',
         '<div class="rule" data-beat="0" data-delay="0.5" data-anim="growx" data-dur="0.5"></div>']
    if sc.get("sub"):
        b.append(f'<p class="sub" data-beat="1" data-anim="rise">{_e(sc["sub"])}</p>')
    b.append(f'<div class="who" data-beat="0" data-delay="0.7" data-anim="fade">{_e(ctx.get("course", ""))}</div>')
    return "".join(b), "cover", 2 if sc.get("sub") else 1


_ICONS = {
    "bulb": '<path d="M9 21h6M12 3a7 7 0 0 0-4 12.7V18h8v-2.3A7 7 0 0 0 12 3z"/>',
    "eye": '<path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
    "code": '<path d="M8 6l-5 6 5 6M16 6l5 6-5 6M13 4l-2 16"/>',
    "check": '<path d="M4 13l5 5L20 7"/>',
    "warn": '<path d="M12 3L2 21h20L12 3zM12 10v5M12 18v.5"/>',
    "spark": '<path d="M12 3v4M12 17v4M3 12h4M17 12h4M5.6 5.6l2.8 2.8M15.6 15.6l2.8 2.8M18.4 5.6l-2.8 2.8M8.4 15.6l-2.8 2.8"/>',
    "build": '<path d="M3 21h18M5 21V8l7-5 7 5v13M9 21v-6h6v6"/>',
    "data": '<path d="M3 20h18M6 17V9M11 17V5M16 17v-7M21 17v-4"/>',
    "net": '<circle cx="5" cy="7" r="2"/><circle cx="5" cy="17" r="2"/><circle cx="12" cy="12" r="2.5"/><circle cx="19" cy="12" r="2"/><path d="M7 8l3 3M7 16l3-3M14.5 12h2.5"/>',
    "loop": '<path d="M4 12a8 8 0 0 1 14-5l2 2M20 4v5h-5M20 12a8 8 0 0 1-14 5l-2-2M4 20v-5h5"/>',
    "agent": '<circle cx="6" cy="6" r="2.5"/><circle cx="18" cy="6" r="2.5"/><circle cx="12" cy="18" r="2.5"/><path d="M8 7.5l2.8 8M16 7.5l-2.8 8M8.5 6h7"/>',
    "question": '<path d="M9 9a3 3 0 1 1 4.5 2.6c-1 .6-1.5 1.2-1.5 2.4M12 17v.5"/><circle cx="12" cy="12" r="10"/>',
}


def s_idea(sc, ctx):
    lines = _lines_of(sc.get("text", ""), 34)
    b = ['<div class="idea">']
    if sc.get("icon") in _ICONS:
        b.append(f'<svg class="ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" '
                 f'stroke-linejoin="round" data-beat="0" data-anim="pop" data-dur="0.5">{_ICONS[sc["icon"]]}</svg>')
    b.append(f'<h1 class="big" style="font-size:{_fit_px(lines, 46, 1060)}px">' + "".join(f'<span class="l" data-beat="{i}" data-anim="rise" data-dur="0.6">{_e(l)}</span>'
                                          for i, l in enumerate(lines)) + '</h1>')
    beat = len(lines)
    if sc.get("sub"):
        b.append(f'<p class="sub" data-beat="{beat}" data-anim="rise" data-dur="0.6">{_e(sc["sub"])}</p>'); beat += 1
    b.append("</div>")
    return "".join(b), "", beat


def s_list(sc, ctx):
    items = sc.get("items") or []
    b = [_heading(sc.get("heading"), 0), '<div class="list">']
    for i, it in enumerate(items):
        b.append(_li(it, 1 + i))
    b.append("</div>")
    return "".join(b), "", 1 + len(items)


def s_recap(sc, ctx):
    items = sc.get("items") or []
    b = [_heading(sc.get("heading", "What to remember"), 0), '<div class="list">']
    for i, it in enumerate(items):
        b.append(_li(it, 1 + i, check=True))
    b.append("</div>")
    return "".join(b), "", 1 + len(items)


def s_cards(sc, ctx):
    items = sc.get("items") or []
    n = max(1, min(4, len(items)))
    b = [_heading(sc.get("heading"), 0), f'<div class="cards" style="--n:{n}">']
    for i, it in enumerate(items):
        if isinstance(it, dict):
            t, x, tag = it.get("title", ""), it.get("text", ""), it.get("tag", "")
        else:
            t, x = _item(it); tag = ""
            if not t:
                t, x = x, ""
        b.append(f'<div class="card" data-beat="{1 + i}" data-anim="pop" data-dur="0.5">'
                 + (f'<i>{_e(tag)}</i>' if tag else "") + f'<b>{_e(t)}</b>' + (f'<span>{_e(x)}</span>' if x else "") + '</div>')
    b.append("</div>")
    return "".join(b), "", 1 + len(items)


def s_steps(sc, ctx):
    steps = sc.get("steps") or []
    b = [_heading(sc.get("heading"), 0), '<div class="steps">']
    for i, st in enumerate(steps):
        if isinstance(st, dict):
            t, x, hi = st.get("title", ""), st.get("text", ""), bool(st.get("highlight"))
        else:
            t, x = _item(st); hi = False
            if not t:
                t, x = x, ""
        if t.startswith("*"):
            t, hi = t[1:].strip(), True
        b.append('<div class="step">' + (_arrow(1 + i) if i else "")
                 + f'<div class="box{" hi" if hi else ""}" data-beat="{1 + i}" data-delay="{0.3 if i else 0:.2f}" data-anim="pop" data-dur="0.45">{_e(t)}'
                 + (f'<small>{_e(x)}</small>' if x else "") + '</div></div>')
    b.append("</div>")
    if sc.get("note"):
        b.append(f'<p class="sub" data-beat="{1 + len(steps)}" data-anim="rise">{_e(sc["note"])}</p>')
    return "".join(b), "", 1 + len(steps) + (1 if sc.get("note") else 0)


def s_compare(sc, ctx):
    L, R = sc.get("left") or {}, sc.get("right") or {}
    b = [_heading(sc.get("heading"), 0), '<div class="cmp">']
    beat = 1
    for side, pane, anim in ((L, "a", "left"), (R, "b", "right")):
        b.append(f'<div class="pane {pane}" data-beat="{beat}" data-anim="{anim}" data-dur="0.55"><h3>{_e(side.get("title", ""))}</h3>')
        for j, pt in enumerate(side.get("points") or []):
            b.append(_li(pt, beat, 0.25 + j * 0.18))
        b.append("</div>")
        if pane == "a":
            b.append('<div class="vs" data-beat="1" data-delay="0.3" data-anim="fade">vs</div>')
        beat += 1
    b.append("</div>")
    if sc.get("verdict"):
        b.append(f'<div class="verdict" data-beat="{beat}" data-anim="rise">{_e(sc["verdict"])}</div>'); beat += 1
    return "".join(b), "", beat


def s_number(sc, ctx):
    items = sc.get("items") or []
    n = max(1, min(4, len(items)))
    b = [_heading(sc.get("heading"), 0), f'<div class="nums" style="--n:{n}">']
    for i, it in enumerate(items):
        v = str(it.get("value", "")); lab = it.get("label", "")
        m = re.match(r"^([^\d\-]*)(-?\d[\d,]*\.?\d*)(.*)$", v)
        if m and it.get("count", True):
            pre, num, suf = m.groups()
            num = num.replace(",", "")
            dec = len(num.split(".")[1]) if "." in num else 0
            b.append(f'<div class="num" data-beat="{1 + i}" data-anim="rise" data-dur="0.5"><b data-beat="{1 + i}" data-delay="0.1" '
                     f'data-anim="count" data-from="{it.get("from", 0)}" data-to="{num}" data-dec="{dec}" data-prefix="{_e(pre)}" '
                     f'data-suffix="{_e(suf)}" data-dur="1.1">{_e(v)}</b><span>{_e(lab)}</span></div>')
        else:
            b.append(f'<div class="num" data-beat="{1 + i}" data-anim="rise" data-dur="0.5"><b>{_e(v)}</b><span>{_e(lab)}</span></div>')
    b.append("</div>")
    return "".join(b), "", 1 + len(items)


def s_code(sc, ctx):
    code = str(sc.get("code", "")).rstrip("\n").split("\n")[:12]
    out = str(sc.get("output") or "").rstrip()
    out_w = max((len(x) for x in out.split("\n")), default=0)
    # the code panel gets more room when the output is narrow, and the type shrinks
    # (never below 12px) so the longest line always fits: Plex Mono is 0.6em per char
    longest = max((len(x) for x in code), default=1)
    if out:
        # split the row by what each panel needs (code gets 45-75%), then size the type to fit
        need_c, need_o = longest * 0.602 * 16 + 48, out_w * 0.602 * 16 + 48
        frac = min(0.75, max(0.45, need_c / (need_c + need_o)))
        panel_c, panel_o = 1120 * frac - 44, 1120 * (1 - frac) - 44
        fs_o = max(12.0, min(16.0, panel_o / (out_w * 0.602 + 2)))
        grid = f' style="grid-template-columns:{frac:.2f}fr {1 - frac:.2f}fr"'
    else:
        panel_c, fs_o, grid = 1136 - 44, 16.0, ""
    fs = max(12.0, min(16.0, panel_c / (longest * 0.602 + 2)))
    b = [_heading(sc.get("heading"), 0), f'<div class="codewrap{" two" if out else ""}"{grid}><pre class="code" style="font-size:{fs:.1f}px">']
    delay = 0.0
    for i, ln in enumerate(code):
        cm = ln.strip().startswith("#")
        dur = min(0.6, 0.12 + 0.011 * len(ln)) if ln.strip() else 0.05
        b.append(f'<span class="ln{" cm" if cm else ""}" data-beat="1" data-delay="{delay:.2f}" data-anim="type" data-text="{_e(ln)}" data-dur="{dur:.2f}"></span>')
        delay += dur + 0.08
    b.append("</pre>")
    beat = 2
    if sc.get("output"):
        b.append(f'<pre class="out" data-beat="{beat}" data-anim="rise" style="font-size:{fs_o:.1f}px"><span class="lbl">OUTPUT</span>{_e(out)}</pre>'); beat += 1
    b.append("</div>")
    if sc.get("note"):
        b.append(f'<p class="codenote" data-beat="{beat}" data-anim="rise">{_e(sc["note"])}</p>'); beat += 1
    return "".join(b), "", beat


def s_chart(sc, ctx):
    labels = [str(x) for x in (sc.get("labels") or [])]
    series = sc.get("series") or []
    kind = sc.get("kind", "bar")
    vals = [float(v) for s in series for v in s.get("values", [])]
    lo = min(0.0, min(vals)) if vals else 0.0
    hi = max(vals) if vals else 1.0
    if sc.get("max") is not None: hi = float(sc["max"])
    if sc.get("min") is not None: lo = float(sc["min"])
    hi = hi if hi > lo else lo + 1
    # the chart shares the stage with its heading and note: give up height for them
    ch = 430 - (60 if sc.get("heading") else 0) - (40 if sc.get("note") else 0)
    cw, ml, mb, mt, mr = 1100, 70, 50, 30, 30
    X = lambda i, n: ml + (i + 0.5) * (cw - ml - mr) / max(1, n)
    Y = lambda v: mt + (ch - mt - mb) * (1 - (v - lo) / (hi - lo))
    b = [_heading(sc.get("heading"), 0), f'<div class="chart"><svg viewBox="0 0 {cw} {ch}" xmlns="http://www.w3.org/2000/svg">']
    b.append(f'<line class="ax" x1="{ml}" y1="{Y(lo)}" x2="{cw - mr}" y2="{Y(lo)}" data-beat="0" data-anim="growx" data-dur="0.5" style="transform-origin:{ml}px {Y(lo)}px"/>')
    b.append(f'<line class="ax" x1="{ml}" y1="{mt}" x2="{ml}" y2="{Y(lo)}" data-beat="0" data-anim="fade" data-dur="0.5"/>')
    for k in range(5):
        v = lo + (hi - lo) * k / 4
        b.append(f'<text class="tk" x="{ml - 10}" y="{Y(v) + 4}" text-anchor="end" data-beat="0" data-delay="0.2" data-anim="fade">{v:g}</text>')
    n = len(labels); beat = 1
    for i, lab in enumerate(labels):
        b.append(f'<text class="tk" x="{X(i, n)}" y="{ch - mb + 22}" text-anchor="middle" data-beat="0" data-delay="0.3" data-anim="fade">{_e(lab)}</text>')
    if kind == "bar":
        ns = max(1, len(series)); bw = (cw - ml - mr) / max(1, n) * 0.7 / ns
        for si, s in enumerate(series):
            for i, v in enumerate(s.get("values", [])):
                x = X(i, n) - bw * ns / 2 + si * bw
                v = float(v)
                b.append(f'<rect class="bar{" g" if si % 2 else ""}" x="{x:.1f}" y="{Y(v):.1f}" width="{bw - 6:.1f}" height="{Y(lo) - Y(v):.1f}" '
                         f'data-beat="{beat + i}" data-delay="{si * 0.12:.2f}" data-anim="growy" data-dur="0.6" style="transform-origin:{x:.1f}px {Y(lo):.1f}px"/>')
                b.append(f'<text class="val" x="{x + (bw - 6) / 2:.1f}" y="{Y(v) - 8:.1f}" text-anchor="middle" data-beat="{beat + i}" data-delay="{0.45 + si * 0.12:.2f}" data-anim="fade">{_e(s.get("fmt", "{}").format(v) if "{" in s.get("fmt", "{}") else v)}</text>')
        beat += n
    else:
        for si, s in enumerate(series):
            pts = [(X(i, n), Y(float(v))) for i, v in enumerate(s.get("values", []))]
            d = " ".join(("M" if i == 0 else "L") + f"{x:.1f},{y:.1f}" for i, (x, y) in enumerate(pts))
            b.append(f'<path class="ln{" g" if si % 2 else ""}" d="{d}" data-beat="{beat}" data-delay="{si * 0.3:.2f}" data-anim="draw" data-len="{cw * 1.5:.0f}" data-dur="1.4"/>')
            for j, (x, y) in enumerate(pts):
                b.append(f'<circle class="pt" cx="{x:.1f}" cy="{y:.1f}" r="5" data-beat="{beat}" data-delay="{si * 0.3 + 0.2 + 1.0 * j / max(1, len(pts) - 1):.2f}" data-anim="pop" data-dur="0.3"/>')
        beat += 1
    if len(series) > 1:
        for si, s in enumerate(series):
            b.append(f'<rect x="{ml + si * 200}" y="{mt - 22}" width="14" height="14" class="bar{" g" if si % 2 else ""}" data-beat="{beat}" data-anim="fade" style="transform-origin:center"/>'
                     f'<text class="leg" x="{ml + si * 200 + 22}" y="{mt - 10}" data-beat="{beat}" data-anim="fade">{_e(s.get("name", ""))}</text>')
        beat += 1
    b.append("</svg></div>")
    if sc.get("note"):
        b.append(f'<p class="sub" data-beat="{beat}" data-anim="rise" style="margin-top:14px">{_e(sc["note"])}</p>'); beat += 1
    return "".join(b), "", beat


def s_diagram(sc, ctx):
    svg = _svg_of(str(sc.get("id", "")))
    points = sc.get("points") or []
    groups = int(sc.get("groups", 8))
    head = _heading(sc.get("heading"), 0)
    base = 1 if sc.get("heading") else 0
    svg = re.sub(r"<svg\b", f'<svg data-diagram="1" data-beat-base="{base}" data-groups="{groups}"', svg, count=1)
    b = [head, f'<div class="diag{" two" if points else ""}"><div class="fig">{svg}</div>']
    if points:
        b.append(f'<div class="pts" style="--n:{max(1, min(4, len(points)))}">')
        for j, pt in enumerate(points):
            b.append(_li(pt, 0).replace('data-beat="0"', f'data-beat="after:{j}"')
                     .replace('<div class="li">', f'<div class="li" data-beat="after:{j}" data-anim="rise" data-dur="0.5">', 1))
        b.append("</div>")
    b.append("</div>")
    return "".join(b), "", base + groups + len(points)      # nominal; the browser reports the real count


def s_quiz(sc, ctx):
    opts = [str(o) for o in (sc.get("options") or [])]
    ans = int(sc.get("answer", 0))
    n = len(opts)
    pause = float(sc.get("pause", 5))
    b = ['<div class="quiz">', _heading(sc.get("question"), 0), '<div class="opts">']
    for i, o in enumerate(opts):
        b.append(f'<div class="opt" data-beat="{1 + i}" data-anim="rise" data-dur="0.5"><span class="k">{"ABCD"[i]}</span><span>{_e(o)}</span>'
                 + (f'<span class="ok" data-beat="{n + 2}" data-anim="pop" data-dur="0.45"></span>' if i == ans else
                    f'<span class="no" data-beat="{n + 2}" data-anim="fade" data-dur="0.45"></span>') + '</div>')
    b.append("</div>")
    r = 52; L = 2 * math.pi * r
    b.append(f'<div class="pause" data-beat="{n + 1}" data-anim="fade" data-dur="0.3"><svg viewBox="0 0 120 120">'
             f'<circle class="bg" cx="60" cy="60" r="{r}"/><circle class="fg" cx="60" cy="60" r="{r}" data-beat="{n + 1}" data-delay="0.3" '
             f'data-anim="ring" data-len="{L:.1f}" data-dur="{pause:.1f}" style="stroke-dasharray:{L:.1f} {L:.1f}"/></svg>'
             f'<b>Pause &amp; predict</b><span>pick one before the answer</span></div>')
    if sc.get("explain"):
        b.append(f'<div class="explain" data-beat="{n + 2}" data-delay="0.35" data-anim="rise">{_e(sc["explain"])}</div>')
    b.append("</div>")
    return "".join(b), "", n + 3


def s_site(sc, ctx):
    path = sc.get("path") or f'{ctx["module"]} › {ctx["episode"]} {ctx["title"]}'
    b = ['<div class="site"><div class="laptop" data-beat="0" data-anim="rise" data-dur="0.6"><div class="screen">'
         f'<div class="bar" data-beat="1" data-anim="type" data-text="{_e(path)}" data-dur="1.2"></div>'
         f'<div class="tt" data-beat="2" data-anim="rise">{_e(sc.get("page", ctx["title"]))}</div>'
         '<div class="ln" data-beat="2" data-delay="0.1" data-anim="rise"></div><div class="ln s" data-beat="2" data-delay="0.18" data-anim="rise"></div>'
         '<div class="ln" data-beat="2" data-delay="0.26" data-anim="rise"></div>'
         f'<span class="btn" data-beat="3" data-anim="pop">{_e(sc.get("button", "RUN STEP"))}</span></div></div>',
         '<div class="txt">', _heading(sc.get("heading", "Now try it yourself"), 0),
         f'<p data-beat="2" data-delay="0.2" data-anim="rise">{_e(sc.get("text", ""))}</p>',
         f'<div class="path" data-beat="3" data-delay="0.2" data-anim="rise">{_e(path)}</div></div></div>']
    return "".join(b), "", 4


_MISSING = set()


def _data_uri(path):
    """A course asset (relative to the project root) as a data: URI, so the stage page is self-contained."""
    if not path:
        return ""
    full = path if os.path.isabs(path) else os.path.join(ROOT, path)
    if not os.path.exists(full):
        if path not in _MISSING:                     # say so once: a blank picture is easy to miss
            _MISSING.add(path)
            print(f"  !!  picture not found, left blank: {path}", flush=True)
        return ""
    mime = mimetypes.guess_type(full)[0] or "application/octet-stream"
    with open(full, "rb") as f:
        return f"data:{mime};base64," + base64.b64encode(f.read()).decode("ascii")


def _tile_pic(it):
    """The picture of a gallery tile: a real image, a course figure, or a module pictogram."""
    if it.get("image"):
        uri = _data_uri(it["image"])
        return f'<img src="{uri}" alt="">' if uri else ""
    if it.get("figure"):
        return _svg_of(str(it["figure"]))
    if it.get("art") and it["art"] in figures_lit.ART:
        return figures_lit.ART[it["art"]]
    return ""


def s_gallery(sc, ctx):
    """Tiles that arrive one by one: a picture (photo, figure or pictogram), a title, a caption."""
    items = [it if isinstance(it, dict) else {"title": str(it)} for it in (sc.get("items") or [])]
    n = int(sc.get("cols") or (4 if len(items) > 6 or len(items) == 4 else min(4, max(2, len(items)))))
    rows2 = " rows2" if len(items) > n else ""
    sq = " square" if str(sc.get("aspect", "")).startswith("sq") else ""
    b = [_heading(sc.get("heading"), 0), f'<div class="gal n{n}{rows2}{sq}" style="--n:{n}">']
    for i, it in enumerate(items):
        b.append(f'<div class="tile" data-beat="{1 + i}" data-anim="pop" data-dur="0.5"><div class="pic">{_tile_pic(it)}</div><div class="cap">'
                 + (f'<i>{_e(it["tag"])}</i>' if it.get("tag") else "")
                 + (f'<b>{_e(it["title"])}</b>' if it.get("title") else "")
                 + (f'<span>{_e(it["text"])}</span>' if it.get("text") else "") + "</div></div>")
    b.append("</div>")
    beat = 1 + len(items)
    if sc.get("note"):
        b.append(f'<p class="galnote" data-beat="{beat}" data-anim="rise">{_e(sc["note"])}</p>'); beat += 1
    return "".join(b), "", beat


def s_image(sc, ctx):
    """One real picture, large, with a caption, a credit line and up to three points."""
    uri = _data_uri(str(sc.get("src", "")))
    pts = sc.get("points") or []
    b = ['<div class="img">',
         f'<div class="pic" data-beat="0" data-anim="fade" data-dur="0.7"><img src="{uri}" alt=""></div>',
         '<div class="txt">', _heading(sc.get("heading"), 0)]
    if sc.get("caption"):
        b.append(f'<p data-beat="1" data-anim="rise">{_e(sc["caption"])}</p>')
    if pts:
        b.append('<div class="list">' + "".join(_li(pt, 2 + j) for j, pt in enumerate(pts)) + "</div>")
    if sc.get("credit"):
        b.append(f'<div class="credit" data-beat="0" data-delay="0.4" data-anim="fade">{_e(sc["credit"])}</div>')
    b.append("</div></div>")
    return "".join(b), "", 2 + len(pts)



def s_shot(sc, ctx):
    """A real screenshot, optionally cropped to the region that matters, with highlight
    boxes that pop in one by one (beats) as the narration reaches them.
      src: assets/...png   crop: [x, y, w, h] in % of the image   heading, caption
      marks: [{box: [x, y, w, h] in % of the (cropped) view, label: "...", at: left|right|below|above}]
             with legend: true the number badge sits left of the box; at: right|above|below|corner moves it
      points: up to three lines in a side column (optional)"""
    path = os.path.join(ROOT, str(sc.get("src", "")))
    uri = _data_uri(str(sc.get("src", "")))
    try:
        from PIL import Image
        W, H = Image.open(path).size
    except Exception:
        W, H = 16, 9
    cx, cy, cw, ch = [float(v) for v in (sc.get("crop") or [0, 0, 100, 100])]
    aspect = (W * cw) / (H * ch)
    pts = sc.get("points") or []
    legend = bool(sc.get("legend"))
    under = legend and not pts and aspect > 2.4          # a wide, short shot: full width, legend beneath
    side = (bool(pts) or legend) and not under
    if under:
        max_w, max_h = 1136, (330 if sc.get("caption") else 360)
    else:
        max_w, max_h = (790 if side else 1136), (452 if sc.get("caption") else 482)
    vw = min(max_w, max_h * aspect); vh = vw / aspect
    img = (f'<img src="{uri}" alt="" style="position:absolute;width:{10000 / cw:.3f}%;'
           f'left:{-cx * 100 / cw:.3f}%;top:{-cy * 100 / ch:.3f}%;max-width:none">')
    marks = []
    for j, m in enumerate(sc.get("marks") or []):
        x, y, w, h = [float(v) for v in m.get("box", [0, 0, 0, 0])]
        lab = m.get("label", "")
        at = m.get("at", "below")
        pos = {"below": f"left:0;top:calc(100% + 8px)", "above": f"left:0;bottom:calc(100% + 8px)",
               "right": f"left:calc(100% + 10px);top:50%;transform:translateY(-50%)",
               "left": f"right:calc(100% + 10px);top:50%;transform:translateY(-50%)"}.get(at, "")
        badge = {"right": "left:auto;right:-36px", "corner": "left:-15px;top:-15px;transform:none",
                 "above": "left:-6px;top:-34px;transform:none", "below": "left:-6px;top:calc(100% + 6px);transform:none"
                 }.get(m.get("at", "left"), "") if legend else ""
        bstyle = f' style="{badge}"' if badge else ""
        inner = (f'<span class="mnum"{bstyle}>{j + 1}</span>' if legend else
                 (f'<span class="mlab" style="{pos}">{_e(lab)}</span>' if lab else ""))
        marks.append(f'<div class="mark" data-beat="{1 + j}" data-anim="pop" data-dur="0.5" '
                     f'style="left:{x}%;top:{y}%;width:{w}%;height:{h}%">{inner}</div>')
    beat = 1 + len(marks)
    view = (f'<div class="shotv" data-beat="0" data-anim="fade" data-dur="0.6" '
            f'style="width:{vw:.0f}px;height:{vh:.0f}px"><div class="clip">{img}</div>{"".join(marks)}</div>')
    b = [_heading(sc.get("heading"), 0), f'<div class="shot{" side" if side else ""}{" under" if under else ""}"><div class="col">{view}']
    if sc.get("caption"):
        b.append(f'<p class="scap" data-beat="0" data-delay="0.3" data-anim="fade">{_e(sc["caption"])}</p>')
    b.append('</div>')
    if side or under:
        items = ""
        if legend:
            items += "".join(f'<div class="leg" data-beat="{1 + j}" data-anim="rise" data-dur="0.5">'
                             f'<span class="mnum">{j + 1}</span><span>{_e(m.get("label", ""))}</span></div>'
                             for j, m in enumerate(sc.get("marks") or []))
        items += "".join(_li(pt, beat + k) for k, pt in enumerate(pts))
        b.append(f'<div class="list">{items}</div>')
        beat += len(pts)
    b.append('</div>')
    return "".join(b), "", beat

def s_screen(sc, ctx):
    """A software environment mock-up (terminal, editor, notebook, browser, installer) that plays its steps."""
    spec = {k: v for k, v in sc.items() if k not in ("type", "narration", "heading", "text", "points", "wide")}
    spec.setdefault("kind", sc.get("kind", "terminal"))
    mock, used = screens.mock(spec, animate=True)
    pts = sc.get("points") or []
    wide = bool(sc.get("wide")) or not (sc.get("heading") or sc.get("text") or pts)
    b = [f'<div class="scr{" wide" if wide else ""}">', mock]
    beat = max(1, used)
    if not wide:
        b.append('<div class="txt">' + _heading(sc.get("heading"), 0))
        if sc.get("text"):
            b.append(f'<p data-beat="0" data-delay="0.3" data-anim="rise">{_e(sc["text"])}</p>')
        if pts:
            b.append('<div class="list">' + "".join(_li(pt, beat + j) for j, pt in enumerate(pts)) + "</div>")
            beat += len(pts)
        b.append("</div>")
    b.append("</div>")
    return "".join(b), "", beat


SCENES = {"title": s_title, "next": s_next, "idea": s_idea, "list": s_list, "recap": s_recap, "cards": s_cards,
          "steps": s_steps, "compare": s_compare, "number": s_number, "code": s_code, "chart": s_chart,
          "diagram": s_diagram, "quiz": s_quiz, "site": s_site, "gallery": s_gallery, "image": s_image, "screen": s_screen, "shot": s_shot}


def scene_html(sc, ctx):
    """The stage page for one scene. ctx: episode, title, module, objectives, course, instructor."""
    fn = SCENES.get(sc.get("type", "idea"), s_idea)
    body, cls, _ = fn(sc, ctx)
    foot = ""
    m = re.search(r'<div class="who"[^>]*>.*?</div>', body, re.S)
    if m:                                   # the cover's footer line sits outside the stage
        body, foot = body[:m.start()] + body[m.end():], m.group(0)
    eyebrow = "" if cls == "cover" else (f'<div class="eyebrow">Lesson <b>{_e(ctx["episode"])}</b> &nbsp;·&nbsp; {_e(ctx["title"])}</div>')
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head>'
            f'<body class="{cls}"><div class="topbar"></div>{eyebrow}<div class="stage">{body}</div>{foot}'
            f'<div class="band"></div><script>{STAGE_JS}</script></body></html>')
