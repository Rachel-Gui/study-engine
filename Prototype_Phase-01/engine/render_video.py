"""
render_video.py - narrated, animated videos from the same topics as the site.

One video per lesson, one per module, and (optionally) one for the whole course,
all assembled from the same content-addressed scenes:

    scene_id = sha256(quality + kind + episode + title + narration + frame html)[:12]

A scene is no longer one still picture. Its content is revealed step by step in
time with the narration - paragraphs, cards, list items, flow steps, code and
figures appear as the voice reaches them - with the spoken sentence shown as a
caption and a progress bar along the bottom. Long topics are paged rather than
cut off. Every state of a scene is one Chromium screenshot; ffmpeg cross-fades
between them, overlays the captions (an ASS subtitle track rendered by libass),
and encodes the scene once. Scenes are cached under .cache/ by id, so editing
one topic re-renders one scene, and a lesson video and its module video share
every scene they have in common.

Resolution. The frame is laid out at 1280x720 CSS pixels and rendered by
Chromium at a device scale factor - 3 for 4K (3840x2160), 1.5 for 1080p.
Scaling the *device pixel ratio* rather than the viewport is what makes the
text and diagrams enlarge with the frame.

Timing. With edge-tts the narration comes back with word timings, so captions
and reveals are synchronised to the voice. With any other engine (or silence)
the words are assumed to be evenly spaced, which is close enough to look right.
"""
import hashlib, html, json, math, os, re, shutil, subprocess, sys, tempfile, time
import components
from parse import plain

W, H = 1280, 720                    # CSS layout size; never change this
FPS = 24
QUALITY = {"4k": 3, "1440p": 2, "1080p": 1.5, "720p": 1}   # -> device scale factor
ACCENT, GOLD = "#4b2e83", "#e8e3d3"

XFADE = 0.45          # seconds: a reveal
XFADE_FIG = 0.9       # seconds: a figure "draws" in with a wipe
XFADE_PAGE = 0.6      # seconds: turning to the next page of a long topic
LEAD = 1.0            # seconds before the first reveal
TAIL = 0.8            # seconds of picture after the voice stops
MAX_STATES = 12       # reveals per scene, at most
WPS = 2.45            # words per second when no word timings are available
CAP_CHARS = 84        # caption line budget (characters, at 1280 wide)

FRAME_CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{width:__W__px;height:__H__px;background:#fff;color:#111;font-family:Montserrat,sans-serif;
 display:flex;flex-direction:column;overflow:hidden;position:relative}
.topbar{height:5px;background:__ACCENT__;flex:0 0 auto}
header{display:flex;align-items:flex-end;gap:22px;padding:20px 56px 13px;
 border-bottom:1px solid #d9d9d9;flex:0 0 auto}
header .kick{font-size:11px;font-weight:700;letter-spacing:.22em;text-transform:uppercase;
 color:__ACCENT__;margin-bottom:6px}
header h1{font-size:27px;font-weight:600;letter-spacing:-.016em;line-height:1.12;color:#111}
header .r{margin-left:auto;text-align:right;flex:0 0 auto}
header .ep{font-size:11px;font-weight:700;letter-spacing:.2em;color:#111;text-transform:uppercase}
header .n{font:500 11.5px/1.8 'IBM Plex Mono',monospace;color:#6b6b6b;letter-spacing:.06em}
main{flex:1;min-height:0;display:flex;flex-direction:column;justify-content:center;
 gap:16px;padding:20px 56px 10px;overflow:hidden}
main>*{flex:0 0 auto}
.f-prose{font-size:17px;line-height:1.55;color:#333;max-width:78ch}
.f-key{border-left:3px solid __ACCENT__;background:#f6f4ef;padding:15px 20px}
.f-key .lbl{display:block;font-size:10px;font-weight:700;letter-spacing:.2em;
 text-transform:uppercase;color:__ACCENT__;margin-bottom:7px}
.f-key p{font-size:16px;line-height:1.5;color:#333}
.f-fig{display:block;text-align:center}
.f-fig svg,.f-fig img{display:block;margin:0 auto;width:100%;height:auto;max-height:440px}
.f-code{font:400 13.5px/1.6 'IBM Plex Mono',monospace;white-space:pre-wrap;
 word-break:break-word;overflow:hidden;background:#f7f7f6;padding:14px 18px;
 border-left:3px solid __ACCENT__;max-height:470px}
.f-list{list-style:none;padding:0;font-size:16px;line-height:1.5;color:#333}
.f-list li{padding-left:18px;position:relative;margin-bottom:7px}
.f-list li::before{content:'';position:absolute;left:0;top:.72em;width:8px;height:2px;background:__ACCENT__}
.f-cards{display:flex;gap:22px}
.f-cards>div{flex:1;border-left:2px solid #111;padding-left:14px}
.f-cards strong{display:block;font-size:15px;font-weight:600;margin-bottom:3px}
.f-cards span{font-size:13px;color:#4a4a4a;line-height:1.42}
.f-stats{display:flex;border:1px solid #e4e4e4}
.f-stats>div{flex:1;padding:14px 18px;border-right:1px solid #e4e4e4}
.f-stats>div:last-child{border-right:0}
.f-stats b{display:block;font-size:26px;font-weight:600;color:__ACCENT__}
.f-stats span{font-size:12px;color:#5c5c5c}
.f-flow{display:flex;flex-wrap:wrap;gap:9px;background:#f7f7f6;padding:13px 16px;font-size:13.5px;
 border-left:3px solid __ACCENT__}
.f-flow span:not(:last-child)::after{content:" \\2192";color:__ACCENT__;margin-left:9px}
.f-refs{font-size:11px;color:#8a8a8a;text-align:right}
.tbl table{width:100%;border-collapse:collapse;font-size:13.5px}
.tbl th{text-align:left;font-size:10px;letter-spacing:.14em;text-transform:uppercase;color:__ACCENT__;
 padding:8px 12px;border-bottom:1px solid #ddd}
.tbl td{padding:7px 12px;border-bottom:1px solid #eee;color:#333}
footer{flex:0 0 auto;height:92px;border-top:1px solid #d9d9d9}
/* reveal units start invisible; the renderer switches them on state by state */
.u{opacity:0;transition:none}
.u.on{opacity:1}

/* title cards */
body.card{background:__ACCENT__;color:#fff}
body.card main{justify-content:center;padding:0 96px 40px;gap:0}
body.card .kick{font-size:13px;font-weight:700;letter-spacing:.28em;text-transform:uppercase;
 color:__GOLD__;margin-bottom:22px}
body.card h1{font-size:52px;font-weight:600;letter-spacing:-.02em;line-height:1.08;
 color:#fff;max-width:22ch}
body.card .q{font-size:21px;line-height:1.5;color:__GOLD__;margin-top:26px;max-width:60ch;font-weight:400}
body.card .rule{width:64px;height:3px;background:__GOLD__;margin:26px 0 0}
body.card .objs{margin-top:28px;margin-bottom:12px}
body.card .objs .lbl{font-size:11px;font-weight:700;letter-spacing:.24em;text-transform:uppercase;color:__GOLD__}
body.card .objs-list{max-width:66ch}
body.card .objs-list li{list-style:none;font-size:17px;line-height:1.45;color:rgba(255,255,255,.92);
 padding-left:26px;position:relative;margin-bottom:9px}
body.card .objs-list li::before{content:attr(data-n);position:absolute;left:0;top:2px;font:600 11px 'IBM Plex Mono',monospace;color:__GOLD__}
body.card .sub{position:absolute;left:96px;bottom:54px;font-size:12.5px;letter-spacing:.06em;color:rgba(255,255,255,.72)}
body.card footer{border:0;height:0}
""".replace("__W__", str(W)).replace("__H__", str(H)).replace("__ACCENT__", ACCENT).replace("__GOLD__", GOLD)

# Runs inside the frame page: paginates long content and exposes setState(n).
FRAME_JS = """
window.__se = (function(){
  const main = document.querySelector('main');
  const blocks = [...main.children];
  const subsOf = b => {
    for (const c of ['f-cards','f-stats','f-flow','f-list','objs-list']) if (b.classList.contains(c)) return [...b.children];
    if (b.classList.contains('tbl')) return [...b.querySelectorAll('tr')].filter(r => !r.querySelector('th'));
    return [];
  };
  const cs = getComputedStyle(main);
  const avail = main.clientHeight - parseFloat(cs.paddingTop) - parseFloat(cs.paddingBottom), gap = 16;
  const pages = [[]]; let used = 0;
  for (const b of blocks){
    const h = b.offsetHeight + gap;
    if (used + h > avail && pages[pages.length - 1].length){ pages.push([]); used = 0; }
    pages[pages.length - 1].push(b); used += h;
  }
  const items = [];
  pages.forEach((pg, p) => pg.forEach(b => {
    b.dataset.page = p;
    const ss = subsOf(b);
    const kind = b.classList.contains('f-fig') ? 'fig' : b.classList.contains('f-code') ? 'code' : 'text';
    if (ss.length > 1){ b.classList.add('host'); ss.forEach(s => { s.classList.add('u'); items.push({page: p, el: s, kind}); }); }
    else { b.classList.add('u'); items.push({page: p, el: b, kind}); }
  }));
  const setState = n => {
    const page = items[n].page;
    blocks.forEach(b => b.style.display = (+b.dataset.page === page) ? '' : 'none');
    items.forEach((it, i) => it.el.classList.toggle('on', it.page === page && i <= n));
  };
  return { count: items.length, pages: items.map(i => i.page), kinds: items.map(i => i.kind), setState };
})();
"""


# ----------------------------------------------------------------- scenes

def _sid(*parts):
    return hashlib.sha256("\x00".join(str(p) for p in parts).encode()).hexdigest()[:12]


def _mod_num(mod):
    m = re.match(r"\s*Module\s+(\d+)", mod.get("title", ""))
    return m.group(1) if m else ""


def _mod_label(mod):
    n = _mod_num(mod)
    return f'Module {n} · {mod.get("short") or mod["title"]}' if n else (mod.get("short") or mod["title"])


def _finish(scenes, quality):
    for s in scenes:
        s["words"] = len(speakable(s["narration"]).split())
        s["id"] = _sid("v2", quality, s["kind"], s.get("episode", ""), s["title"],
                       s["narration"], s.get("frames", ""), s.get("question", ""),
                       s.get("kick", ""), s.get("objectives", ""), s.get("pos", ""))
    return scenes


def _screen(blocks):
    """One line per block that appears on video, for the narration script."""
    out = []
    for b in blocks:
        k, a, body = b["kind"], b["attrs"], b["body"]
        text = " ".join(plain(body).split())
        if k == "prose":
            if "|" in body and "---" in body:
                out.append("table")
            elif body.lstrip().startswith("```"):
                out.append("code")
            else:
                out.append("text: " + text[:80] + ("…" if len(text) > 80 else ""))
        elif k == "keyidea":
            out.append("key idea: " + text[:90] + ("…" if len(text) > 90 else ""))
        elif k == "figure":
            out.append("figure: " + " ".join(plain(a.get("caption", a.get("id", ""))).split())[:90])
        elif k == "pylab":
            out.append(f'code lab: {a.get("title", "Python lab")} (the code, as one block)')
        elif k == "trace":
            out.append(f'step-through: {a.get("title", "")} (code and final variables)')
        elif k == "cards":
            out.append("cards: " + "; ".join(r[0] for r in _rows3(body))[:160])
        elif k == "compare":
            out.append("comparison: " + " vs ".join(r[0] for r in _rows3(body))[:120])
        elif k == "stats":
            out.append("headline figures: " + "; ".join(" ".join(r[:2]) for r in _rows3(body))[:120])
        elif k == "flow":
            out.append("flow: " + " → ".join(x.strip() for x in text.split(">"))[:160])
        elif k == "workflow":
            out.append("workflow steps: " + " → ".join(r[0] for r in _rows3(body))[:160])
        elif k == "widget":
            out.append(f'figure (interactive on the site): {a.get("id", "")}')
        elif k == "boundary":
            out.append("claim boundary: " + "; ".join(r[0] for r in _rows3(body))[:120])
        elif k == "refs":
            out.append("references")
        elif k in ("slide", "deck"):
            out.append("slide image")
        elif k == "os":
            out.append("setup commands (Windows pane)")
    return out


def _rows3(body):
    return [[c.strip() for c in line.split("|")] for line in body.split("\n") if line.strip()]


def topic_scenes(meta, topics, mod):
    """The narrated topics of one lesson, numbered k of nk within the lesson."""
    out = []
    narrated = [t for t in topics if t.get("narration")]
    for k, t in enumerate(narrated, 1):
        parts, seen = [], set()
        for b in t["blocks"]:
            f = components.render(b, "frame")
            if f and f in seen:            # a widget falls back to a figure the topic already shows
                continue
            seen.add(f); parts.append(f)
        out.append({"kind": "topic", "title": t["title"], "episode": meta["episode"],
                    "eptitle": meta.get("title", ""), "module": _mod_label(mod),
                    "narration": t["narration"], "frames": "".join(parts),
                    "pos": f"{k} of {len(narrated)}", "screen": _screen(t["blocks"])})
    return out


def episode_card(meta, mod):
    objs = [" ".join(str(x).split()) for x in (meta.get("objectives") or []) if str(x).strip()]
    spoken = (" In this lesson you will: " + " ".join(o.rstrip(".") + "." for o in objs)) if objs else ""
    return {"kind": "card", "title": meta.get("title", ""), "kick": f'Lesson {meta["episode"]}',
            "question": "", "objectives": "\n".join(objs), "sub": _mod_label(mod),
            "episode": meta["episode"], "module": _mod_label(mod),
            "narration": f'Lesson {meta["episode"]}. {meta.get("title", "")}.{spoken}'}


def module_card(mod):
    q = " ".join(str(mod.get("question", "")).split())
    n = _mod_num(mod)
    title = mod.get("short") or mod["title"]
    return {"kind": "card", "title": title if n else mod["title"], "kick": f"Module {n}" if n else "",
            "question": q, "objectives": "", "sub": "", "episode": "", "module": _mod_label(mod),
            "narration": f'{mod["title"]}. {q}' if q else mod["title"]}


def course_card(course):
    ins = course.get("instructor", {})
    return {"kind": "card", "title": course.get("title", ""), "kick": course.get("code", ""),
            "question": course.get("subtitle", ""), "objectives": "",
            "sub": f'{ins.get("name", "")} · {ins.get("dept", "")}', "episode": "", "module": "",
            "narration": f'{course.get("title", "")}. {course.get("code", "")}. '
                         f'Course instructor, {ins.get("name", "")}.'}


def episode_scenes(meta, topics, mod, quality):
    return _finish([episode_card(meta, mod)] + topic_scenes(meta, topics, mod), quality)


def module_scenes(mod, episodes, quality):
    out = [module_card(mod)]
    for meta, topics, md in episodes:
        if md is mod:
            out.append(episode_card(meta, mod)); out += topic_scenes(meta, topics, mod)
    return _finish(out, quality)


def course_scenes(course, episodes, quality):
    out, seen = [course_card(course)], None
    for meta, topics, mod in episodes:
        if mod is not seen:
            seen = mod; out.append(module_card(mod))
        out.append(episode_card(meta, mod)); out += topic_scenes(meta, topics, mod)
    return _finish(out, quality)


# ------------------------------------------------------------------ frames

def frame_html(sc):
    css = FRAME_CSS
    if sc["kind"] == "card":
        kick = html.escape(sc.get("kick", ""))
        q = f'<div class="q">{html.escape(sc["question"])}</div>' if sc.get("question") else ""
        objs = ""
        if sc.get("objectives"):
            lis = "".join(f'<li data-n="{i:02d}">{html.escape(o)}</li>'
                          for i, o in enumerate(sc["objectives"].split("\n"), 1))
            objs = (f'<div class="objs"><div class="lbl">In this lesson you will</div></div>'
                    f'<ul class="objs-list">{lis}</ul>')
        sub = f'<div class="sub">{html.escape(sc["sub"])}</div>' if sc.get("sub") else ""
        return (f'<!doctype html><meta charset="utf-8"><style>{css}</style>'
                f'<body class="card"><main>'
                f'<div><div class="kick">{kick}</div><h1>{html.escape(sc["title"])}</h1>'
                f'<div class="rule"></div></div>{q}{objs}</main>{sub}<footer></footer>'
                f'<script>{FRAME_JS}</script></body>')
    return (f'<!doctype html><meta charset="utf-8"><style>{css}</style>'
            f'<body><div class="topbar"></div>'
            f'<header><div><div class="kick">{html.escape(sc["module"])}</div>'
            f'<h1>{html.escape(sc["title"])}</h1></div>'
            f'<div class="r"><div class="ep">Lesson {html.escape(sc["episode"])}</div>'
            f'<div class="n">{html.escape(sc.get("pos", ""))}</div></div></header>'
            f'<main>{sc["frames"]}</main><footer></footer>'
            f'<script>{FRAME_JS}</script></body>')


# ------------------------------------------------------------------ audio

def speakable(text):
    """Tidy the narration for a speech engine. Line breaks are meaningless to it,
    and typographic dashes and quotes are read inconsistently."""
    t = plain(text)
    t = re.sub(r"\s*[—–]\s*", ", ", t)
    t = (t.replace("‘", "'").replace("’", "'")
          .replace("“", '"').replace("”", '"')
          .replace("…", "...").replace(" ", " "))
    return re.sub(r"\s+", " ", t).strip()


def sentences(text):
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\"'(])", speakable(text))
    return [p.strip() for p in parts if p.strip()]


def _edge(text, mp3, srt, voice, tries=4):
    """edge-tts talks to Microsoft's servers, which throttle a long run of rapid
    requests. Retry with backoff rather than losing the whole render at scene 19."""
    last = ""
    for attempt in range(1, tries + 1):
        tmp = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8")
        tmp.write(text); tmp.close()
        try:
            r = subprocess.run([sys.executable, "-m", "edge_tts", "--voice", voice,
                                "--file", tmp.name, "--write-media", mp3,
                                "--write-subtitles", srt],
                               capture_output=True, text=True, timeout=180)
            if r.returncode == 0 and os.path.exists(mp3) and os.path.getsize(mp3) > 1024:
                return None
            last = (r.stderr or r.stdout or "").strip().splitlines()
            last = last[-1] if last else f"exit status {r.returncode}"
        except Exception as e:
            last = str(e)
        finally:
            try:
                os.unlink(tmp.name)
            except OSError:
                pass
        if attempt < tries:
            wait = 3 * attempt
            print(f"      tts attempt {attempt} failed ({last[:70]}); retrying in {wait}s")
            time.sleep(wait)
    return last


def _audio(sc, mp3, srt, voice, engine):
    """edge-tts (free, no API key, word timings) -> gTTS -> correctly-timed silence."""
    text = speakable(sc["narration"])
    for p in (mp3, srt):
        if os.path.exists(p):
            os.remove(p)
    if engine in ("auto", "edge"):
        err = _edge(text, mp3, srt, voice)
        if err is None:
            time.sleep(0.4)          # be gentle with the free endpoint
            return "edge-tts"
        if engine == "edge":
            sys.exit(
                f"\n  Text-to-speech failed on scene {sc['n']:02d} "
                f"({sc['episode'] or 'card'} - {sc['title']}) after 4 tries.\n"
                f"\n  edge-tts said:  {err}\n"
                "\n  edge-tts uses Microsoft's free online voice service, so this is\n"
                "  usually the network or their rate limiter, not your setup.\n"
                f"\n  The scenes before this one are cached. Wait a minute, run the\n"
                "  same command again, and it picks up exactly where it stopped.\n"
                "\n  If it keeps failing on the same scene:\n"
                "      pip install --upgrade edge-tts\n"
                "      python engine/make_videos.py --engine gtts   (other service)\n")
    if engine in ("auto", "gtts"):
        try:
            from gtts import gTTS
            gTTS(text, lang="en").save(mp3); return "gTTS"
        except Exception:
            if engine == "gtts":
                raise
    subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono",
                    "-t", f"{max(3.0, sc['words'] / WPS):.2f}", "-q:a", "9", mp3],
                   check=True, capture_output=True)
    return "SILENT"


def _dur(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", p], capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


# ------------------------------------------------------------------ timing

def _srt_words(path):
    """Word start times from an edge-tts subtitle file: (time, word) in order.
    Cues carry several words each; words are spread evenly inside their cue."""
    if not path or not os.path.exists(path):
        return []
    txt = open(path, encoding="utf-8", errors="replace").read()
    out = []
    for m in re.finditer(r"(\d+):(\d+):(\d+)[,.](\d+)\s*-->\s*(\d+):(\d+):(\d+)[,.](\d+)\s*\n(.*?)(?:\n\s*\n|\Z)",
                         txt, re.S):
        h1, m1, s1, ms1, h2, m2, s2, ms2 = (int(x) for x in m.groups()[:8])
        t0 = h1 * 3600 + m1 * 60 + s1 + ms1 / (1000 if len(m.group(4)) == 3 else 10 ** len(m.group(4)))
        t1 = h2 * 3600 + m2 * 60 + s2 + ms2 / (1000 if len(m.group(8)) == 3 else 10 ** len(m.group(8)))
        words = m.group(9).split()
        for i, w in enumerate(words):
            out.append((t0 + (t1 - t0) * i / max(1, len(words)), w))
    return out


def word_times(narration, srt, voice_dur):
    """A start time for every word of the narration, in seconds."""
    words = speakable(narration).split()
    n = len(words)
    timed = _srt_words(srt)
    if timed and len(timed) >= max(3, n * 0.6):
        m = len(timed)
        return [timed[min(m - 1, int(i * m / n))][0] for i in range(n)]
    lead = 0.15
    return [lead + (voice_dur - lead - 0.4) * i / max(1, n) for i in range(n)]


def caption_cues(narration, times, voice_dur):
    """(start, end, text) captions: sentences, split at clauses when long."""
    words = speakable(narration).split()
    cues, i = [], 0
    for s in sentences(narration):
        sw = s.split()
        chunks, cur = [], []
        for w in sw:
            cur.append(w)
            joined = " ".join(cur)
            if len(joined) > CAP_CHARS * 0.72 and re.search(r"[,;:]$", w) and len(sw) - len(cur) > 3:
                chunks.append(cur); cur = []
            elif len(joined) > CAP_CHARS and len(cur) > 3:
                chunks.append(cur[:-1]); cur = [w]
        if cur:
            chunks.append(cur)
        for ch in chunks:
            start = times[min(i, len(times) - 1)] if times else 0
            i += len(ch)
            cues.append([start, None, " ".join(ch)])
    for k, c in enumerate(cues):
        c[1] = cues[k + 1][0] - 0.05 if k + 1 < len(cues) else voice_dur + 0.4
    return [tuple(c) for c in cues]


def reveal_times(n_states, narration, times, voice_dur):
    """When each reveal happens: at sentence starts when there are enough
    sentences, evenly across the voice otherwise. State 0 is at t = 0."""
    m = n_states - 1
    if m <= 0:
        return []
    starts, i = [], 0
    for s in sentences(narration):
        if i > 0:
            starts.append(times[min(i, len(times) - 1)])
        i += len(s.split())
    starts = [t for t in starts if t >= LEAD]
    if len(starts) >= m:
        pick = [starts[round((j + 1) * len(starts) / (m + 1)) - 1] if m < len(starts) else starts[j]
                for j in range(m)]
    else:
        end = max(voice_dur - 1.0, LEAD + 0.2)
        pick = [LEAD + (end - LEAD) * (j + 1) / (m + 1) for j in range(m)]
    # keep every reveal at least a transition apart, and inside the scene
    out, prev = [], 0.0
    for t in pick:
        t = max(t, prev + XFADE_FIG + 0.15, LEAD if not out else t)
        out.append(t); prev = t
    limit = voice_dur + TAIL - 0.6
    if out and out[-1] > limit and out[-1] > LEAD:
        k = (limit - LEAD) / (out[-1] - LEAD)
        out = [LEAD + (t - LEAD) * max(k, 0.0) for t in out]
    return out


# --------------------------------------------------------------- captions

def _ass_time(t):
    t = max(0.0, t)
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


def _ass_text(s):
    return html.unescape(s).replace("\\", "\\\\").replace("{", "(").replace("}", ")")


def write_ass(path, cues, total, card=False):
    """Captions in the footer band, a progress bar along the bottom."""
    cap_col = "&H00F2F2F2" if card else "&H00333333"
    bar_col = "&H00D3E3E8" if card else "&H00832E4B"     # ASS is &HAABBGGRR
    lines = [
        "[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}", "WrapStyle: 0",
        "ScaledBorderAndShadow: yes", "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, "
        "Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
        "Alignment, MarginL, MarginR, MarginV, Encoding",
        f"Style: Cap,Montserrat,23,{cap_col},&H000000FF,&H00FFFFFF,&H00000000,0,0,0,0,100,100,0,0,1,0,0,2,56,56,24,1",
        f"Style: Bar,Montserrat,20,{bar_col},&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1",
        "", "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    for s, e, text in cues:
        lines.append(f"Dialogue: 0,{_ass_time(s)},{_ass_time(e)},Cap,,0,0,0,,{{\\fad(120,120)}}{_ass_text(text)}")
    ms = int(total * 1000)
    lines.append(f"Dialogue: 1,0:00:00.00,{_ass_time(total + 1)},Bar,,0,0,0,,"
                 f"{{\\an7\\pos(0,{H - 4})\\fscx0\\t(0,{ms},\\fscx100)\\p1}}m 0 0 l {W} 0 l {W} 4 l 0 4{{\\p0}}")
    open(path, "w", encoding="utf-8").write("\n".join(lines) + "\n")


# ------------------------------------------------------------------- video

_HAS_ASS = None


def _has_ass():
    global _HAS_ASS
    if _HAS_ASS is None:
        r = subprocess.run(["ffmpeg", "-hide_banner", "-filters"], capture_output=True, text=True)
        _HAS_ASS = " ass " in r.stdout
    return _HAS_ASS


def _encode(cache, sc, states, times, kinds, mp3, ass, mp4, dpr):
    """All the states of one scene, cross-faded on the narration's clock, with
    captions and the progress bar overlaid, and a soft fade in and out."""
    voice = max(_dur(os.path.join(cache, mp3)), 1.0)
    total = voice + TAIL
    n = len(states)
    tt = [0.0] + list(times) + [total]
    trans = []
    for i in range(1, n):
        d = XFADE_FIG if kinds[i] == "fig" else (XFADE_PAGE if kinds[i] == "page" else XFADE)
        d = max(0.12, min(d, 0.85 * (tt[i] - tt[i - 1])))       # never overlap the previous reveal
        trans.append(("wipeleft" if kinds[i] == "fig" else "fade", d))
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"]
    for i, png in enumerate(states):
        if n == 1:
            length = total
        elif i == 0:
            length = tt[1]
        else:
            length = tt[i + 1] - tt[i] + trans[i - 1][1]
        # decode each still at 2 fps and let the fps filter duplicate frames: at 4K,
        # decoding a PNG 24 times a second was most of the encode time
        cmd += ["-loop", "1", "-framerate", "2", "-t", f"{length + 0.55:.3f}", "-i", png]
    cmd += ["-i", mp3]
    fg = []
    for i in range(n):
        fg.append(f"[{i}:v]settb=AVTB,fps={FPS},format=yuv420p[s{i}]")
    cur = "[s0]"
    for i in range(1, n):
        name, d = trans[i - 1]
        fg.append(f"{cur}[s{i}]xfade=transition={name}:duration={d:.2f}:offset={tt[i] - d:.3f}[x{i}]")
        cur = f"[x{i}]"
    fo = max(total - 0.5, 0.1)
    post = (f"ass={ass}," if (ass and _has_ass()) else "") + \
           f"fade=t=in:st=0:d=0.45,fade=t=out:st={fo:.2f}:d=0.5"
    fg.append(f"{cur}{post}[v]")
    cmd += ["-filter_complex", ";".join(fg), "-map", "[v]", "-map", f"{n}:a",
            "-af", f"apad,afade=t=in:st=0:d=0.25,afade=t=out:st={fo:.2f}:d=0.4",
            "-t", f"{total:.3f}",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "19",
            "-profile:v", "high", "-level", "5.1", "-r", str(FPS), "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "160k", "-ar", "48000",
            "-movflags", "+faststart", mp4]
    r = subprocess.run(cmd, cwd=cache, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"\n  ffmpeg failed on scene {sc['n']:02d} ({sc['title']}):\n{r.stderr[-1500:]}\n")
    return total


def _check_tools():
    missing = [t for t in ("ffmpeg", "ffprobe") if not shutil.which(t)]
    if missing:
        sys.exit(
            "\n  Cannot render video: " + " and ".join(missing) + " not found.\n"
            "\n  ffmpeg is a separate program, not a Python package. Install it:\n"
            "\n      Windows   winget install Gyan.FFmpeg\n"
            "                THEN CLOSE THIS WINDOW AND OPEN A NEW ONE.\n"
            "                Windows only picks up a new PATH in a fresh terminal.\n"
            "      Mac       brew install ffmpeg\n"
            "      Linux     sudo apt install ffmpeg\n"
            "\n  Then check with:  python engine/build.py --doctor\n"
            "\n  The site does not need ffmpeg - run.bat still works.\n")


class Renderer:
    """Renders scenes into the cache and stitches cached scenes into videos."""

    def __init__(self, cache, voice="en-GB-RyanNeural", engine="auto", force=False, quality="4k"):
        _check_tools()
        self.cache, self.voice, self.engine, self.force = cache, voice, engine, force
        self.quality, self.dpr = quality, QUALITY.get(quality, 3)
        for d in ("png", "mp3", "mp4", "ass", "meta"):
            os.makedirs(os.path.join(cache, d), exist_ok=True)
        self.built = self.cached = 0
        self.engines = set()
        self._pw = self._br = self._pg = None

    def _page(self):
        if self._pg is None:
            from playwright.sync_api import sync_playwright
            self._pw = sync_playwright().start()
            self._br = self._pw.chromium.launch()
            self._pg = self._br.new_page(viewport={"width": W, "height": H},
                                         device_scale_factor=self.dpr)
        return self._pg

    def close(self):
        if self._br:
            self._br.close(); self._pw.stop()
            self._pw = self._br = self._pg = None

    def meta_path(self, sc):
        return os.path.join(self.cache, "meta", sc["id"] + ".json")

    def render(self, sc):
        """One scene -> cached mp4 path (relative to the cache)."""
        mp4 = f"mp4/{sc['id']}.mp4"
        meta = self.meta_path(sc)
        if not self.force and os.path.exists(os.path.join(self.cache, mp4)) and os.path.exists(meta):
            self.cached += 1
            return mp4, "cached ", json.load(open(meta, encoding="utf-8"))
        # voice first: how long the scene runs decides how many reveals fit in it
        mp3, srt, ass = f"mp3/{sc['id']}.mp3", f"mp3/{sc['id']}.srt", f"ass/{sc['id']}.ass"
        if self.force or not os.path.exists(os.path.join(self.cache, mp3)):
            self.engines.add(_audio(sc, os.path.join(self.cache, mp3), os.path.join(self.cache, srt),
                                    self.voice, self.engine))
        voice = max(_dur(os.path.join(self.cache, mp3)), 1.0)
        budget = max(1, min(MAX_STATES, 1 + int((voice - LEAD - 0.6) / (XFADE_FIG + 0.25))))

        pg = self._page()
        tmp = os.path.join(self.cache, "_frame.html")
        open(tmp, "w", encoding="utf-8").write(frame_html(sc))
        pg.goto("file://" + os.path.abspath(tmp))
        pg.wait_for_timeout(150)                    # let web fonts settle
        info = pg.evaluate("({count: window.__se.count, pages: window.__se.pages, kinds: window.__se.kinds})")
        count, pages, kinds = info["count"], info["pages"], info["kinds"]
        # group the reveal items into at most `budget` states, page by page
        idx = []
        for p in sorted(set(pages)):
            items = [i for i, pp in enumerate(pages) if pp == p]
            target = max(1, round(budget * len(items) / max(1, count)))
            step = math.ceil(len(items) / target)
            idx += [items[min(len(items) - 1, j + step - 1)] for j in range(0, len(items), step)]
        states, skinds = [], []
        for s, i in enumerate(idx):
            pg.evaluate(f"window.__se.setState({i})")
            png = f"png/{sc['id']}-{s}.png"
            pg.screenshot(path=os.path.join(self.cache, png))
            states.append(png)
            skinds.append("page" if s and pages[i] != pages[idx[s - 1]] else kinds[i])
        wt = word_times(sc["narration"], os.path.join(self.cache, srt), voice)
        times = reveal_times(len(states), sc["narration"], wt, voice)
        cues = caption_cues(sc["narration"], wt, voice)
        write_ass(os.path.join(self.cache, ass), cues, voice + TAIL, card=(sc["kind"] == "card"))
        total = _encode(self.cache, sc, states, times, skinds, mp3, ass, mp4, self.dpr)
        m = {"duration": total, "states": len(states), "pages": len(set(pages)),
             "reveals": [round(t, 2) for t in times], "cues": [(round(s, 2), round(e, 2), t) for s, e, t in cues]}
        json.dump(m, open(meta, "w", encoding="utf-8"))
        self.built += 1
        return mp4, "REBUILT", m

    def stitch(self, scenes, out_mp4, label):
        """Render every scene of a video (cache hits are instant) and concatenate."""
        t0 = time.time()
        print(f"\n  {label}\n  {len(scenes)} scenes at {int(W * self.dpr)}x{int(H * self.dpr)} ({self.quality})\n  " + "-" * 64)
        parts, total = [], 0.0
        for i, sc in enumerate(scenes, 1):
            sc["n"] = i
            mp4, tag, m = self.render(sc)
            parts.append(mp4); total += m["duration"]
            lab = sc["title"] if sc["kind"] == "topic" else f"[{sc['title']}]"
            print(f"  {i:02d}  {tag}  {sc['id']}  {m['states']:>2} states  {lab[:56]}")
        lst = os.path.join(self.cache, f"concat-{_sid(out_mp4)}.txt")
        with open(lst, "w", encoding="utf-8") as f:
            for p in parts:
                f.write(f"file '{p}'\n")
        os.makedirs(os.path.dirname(os.path.abspath(out_mp4)), exist_ok=True)
        r = subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "concat",
                            "-safe", "0", "-i", os.path.abspath(lst), "-c", "copy",
                            "-movflags", "+faststart", os.path.abspath(out_mp4)],
                           cwd=self.cache, capture_output=True, text=True)
        if r.returncode != 0:
            sys.exit(f"\n  ffmpeg could not join the scenes:\n{r.stderr[-1200:]}\n")
        print("  " + "-" * 64)
        print(f"  {out_mp4}   {total / 60:.1f} min   {os.path.getsize(out_mp4) / 1e6:.1f} MB   "
              f"{time.time() - t0:.1f}s")
        return total

    def report(self):
        if "SILENT" in self.engines:
            print("\n  !!  NO SPEECH. edge-tts was unavailable, so every rebuilt scene got\n"
                  "      correctly-timed silence. Fix:  pip install edge-tts\n"
                  "      then run the same command again with  --force --engine edge\n")
        elif self.engines:
            print(f"\n  voice: {'+'.join(sorted(self.engines))} ({self.voice})")
        print(f"  {self.built} scenes rebuilt, {self.cached} from cache")


# ----------------------------------------------------------------- scripts

def _mmss(t):
    return f"{int(t // 60)}:{int(t % 60):02d}"


def _onscreen(sc):
    """What appears on screen in this scene, in the order it is revealed."""
    if sc["kind"] == "card":
        bits = [sc.get("kick", ""), sc["title"]]
        if sc.get("question"):
            bits.append(sc["question"])
        if sc.get("objectives"):
            bits.append("objectives: " + "; ".join(sc["objectives"].split("\n")))
        return "  - " + " · ".join(b for b in bits if b)
    items = sc.get("screen") or []
    return "\n".join(f"  - {o}" for o in items) if items else "  - (title only)"


def write_script(path, scenes, title, sub, cache=None):
    """A narration script for one video: every scene, what is on screen, the
    words, and the timing (measured if the scene is cached, estimated otherwise)."""
    t, lines = 0.0, [f"# {title}", "", sub, ""]
    est_total = 0.0
    rows = []
    for i, sc in enumerate(scenes, 1):
        d, measured = sc["words"] / WPS + LEAD + TAIL, False
        if cache:
            mp = os.path.join(cache, "meta", sc["id"] + ".json")
            if os.path.exists(mp):
                d, measured = json.load(open(mp, encoding="utf-8"))["duration"], True
        rows.append((i, sc, t, d, measured))
        t += d
    lines.append(f"{len(scenes)} scenes · about {_mmss(t)} · voice {'measured' if all(r[4] for r in rows) else 'estimated at %.1f words/s' % WPS}")
    lines.append("")
    lines.append("| # | Scene | Starts | Length |")
    lines.append("|---|---|---|---|")
    for i, sc, start, d, measured in rows:
        lab = sc["title"] if sc["kind"] == "topic" else f"Title card — {sc['title']}"
        lines.append(f"| {i} | {lab} | {_mmss(start)} | {_mmss(d)}{'' if measured else ' (est.)'} |")
    lines.append("")
    for i, sc, start, d, measured in rows:
        lab = sc["title"] if sc["kind"] == "topic" else f"Title card — {sc['title']}"
        head = f"## Scene {i} · {lab}"
        if sc["kind"] == "topic":
            head += f"  ({sc['episode']}, topic {sc.get('pos', '')})"
        lines += [head, "", f"*{_mmss(start)} – {_mmss(start + d)} · {sc['words']} words*", "",
                  "**On screen, in order of appearance**", "", _onscreen(sc), "",
                  "**Narration**", ""]
        lines += [">" + (" " + s if s else "") for s in sentences(sc["narration"])]
        lines.append("")
    open(path, "w", encoding="utf-8").write("\n".join(lines))
    return t


# ------------------------------------------------------------------- legacy

def build_video(episodes, course, cache, out_mp4, voice="en-GB-RyanNeural",
                engine="auto", force=False, quality="4k"):
    """The single full-course video (kept for `build.py --video --course`)."""
    r = Renderer(cache, voice=voice, engine=engine, force=force, quality=quality)
    try:
        r.stitch(course_scenes(course, episodes, quality), out_mp4, course.get("title", "Course"))
    finally:
        r.close()
    r.report()
