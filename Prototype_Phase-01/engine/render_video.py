"""
render_video.py - the same topics, rendered as an MP4.

Every narrated topic becomes one scene, content-addressed:

    scene_id = sha256(quality + title + narration + every block's frame() html)[:12]

Rendered PNG / MP3 / MP4 cache under .cache/ by that id, so editing one topic
re-renders one scene. Topics with no :::narration are web-only and skipped.

Resolution. The frame is laid out at 1280x720 CSS pixels and rendered by
Chromium at a device scale factor - 3 for 4K (3840x2160), 1.5 for 1080p.
Scaling the *device pixel ratio* rather than the viewport is what makes the
text and diagrams enlarge with the frame; a bigger viewport would only add
empty space around the same-sized layout.
"""
import hashlib, html, os, re, shutil, subprocess, sys, tempfile, textwrap, time
import components
from parse import plain

W, H = 1280, 720                    # CSS layout size; never change this
FPS = 24
QUALITY = {"4k": 3, "1440p": 2, "1080p": 1.5, "720p": 1}   # -> device scale factor

ACCENT, GOLD = "#4b2e83", "#e8e3d3"

FRAME_CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{width:__W__px;height:__H__px;background:#fff;color:#111;font-family:Montserrat,sans-serif;
 display:flex;flex-direction:column;overflow:hidden;position:relative}
.topbar{height:5px;background:__ACCENT__;flex:0 0 auto}
header{display:flex;align-items:flex-end;gap:22px;padding:22px 56px 14px;
 border-bottom:1px solid #d9d9d9;flex:0 0 auto}
header .kick{font-size:10.5px;font-weight:700;letter-spacing:.22em;text-transform:uppercase;
 color:__ACCENT__;margin-bottom:6px}
header h1{font-size:27px;font-weight:600;letter-spacing:-.016em;line-height:1.12;color:#111}
header .r{margin-left:auto;text-align:right;flex:0 0 auto}
header .ep{font-size:10.5px;font-weight:700;letter-spacing:.2em;color:#111}
header .n{font:500 11px/1.8 'IBM Plex Mono',monospace;color:#8a8a8a;letter-spacing:.06em}
main{flex:1;min-height:0;display:flex;flex-direction:column;justify-content:center;
 gap:16px;padding:22px 56px 10px;overflow:hidden}
.f-prose{font-size:16.5px;line-height:1.55;color:#3d3d3d;max-width:78ch}
.f-key{border-left:3px solid __ACCENT__;background:#f6f4ef;padding:15px 20px}
.f-key .lbl{display:block;font-size:9.5px;font-weight:700;letter-spacing:.2em;
 text-transform:uppercase;color:__ACCENT__;margin-bottom:7px}
.f-key p{font-size:15.5px;line-height:1.5;color:#3d3d3d}
.f-fig{flex:1;min-height:0;display:flex;align-items:center;justify-content:center}
.f-fig svg,.f-fig img{max-width:100%;max-height:100%}
.f-code{font:400 13.5px/1.62 'IBM Plex Mono',monospace;white-space:pre-wrap;
 word-break:break-word;overflow:hidden;background:#f7f7f6;padding:14px 18px;
 border-left:3px solid __ACCENT__}
.f-list{list-style:none;padding:0;font-size:15.5px;line-height:1.5;color:#3d3d3d}
.f-list li{padding-left:18px;position:relative;margin-bottom:7px}
.f-list li::before{content:'';position:absolute;left:0;top:.72em;width:8px;height:2px;background:__ACCENT__}
.f-cards{display:flex;gap:22px}
.f-cards>div{flex:1;border-left:2px solid #111;padding-left:14px}
.f-cards strong{display:block;font-size:14.5px;font-weight:600}
.f-cards span{font-size:12.5px;color:#5a5a5a;line-height:1.42}
.f-stats{display:flex;border:1px solid #e4e4e4}
.f-stats>div{flex:1;padding:14px 18px;border-right:1px solid #e4e4e4}
.f-stats>div:last-child{border-right:0}
.f-stats b{display:block;font-size:26px;font-weight:600;color:__ACCENT__}
.f-stats span{font-size:11.5px;color:#767676}
.f-flow{display:flex;flex-wrap:wrap;gap:9px;background:#f7f7f6;padding:13px 16px;font-size:13px}
.f-flow span:not(:last-child)::after{content:" \\2192";color:__ACCENT__;margin-left:9px}
.f-refs{font-size:10.5px;color:#a6a6a6;text-align:right}
.tbl table{width:100%;border-collapse:collapse;font-size:13px}
.tbl th{text-align:left;font-size:9.5px;letter-spacing:.14em;text-transform:uppercase;color:__ACCENT__;
 padding:8px 12px;border-bottom:1px solid #ddd}
.tbl td{padding:7px 12px;border-bottom:1px solid #eee;color:#3d3d3d}
footer{flex:0 0 auto;min-height:84px;border-top:1px solid #d9d9d9;padding:15px 56px 18px;
 font-size:15.5px;line-height:1.45;color:#3d3d3d;overflow:hidden}
.prog{position:absolute;left:0;bottom:0;height:4px;background:#e9e9e9;width:100%}
.prog i{position:absolute;left:0;top:0;bottom:0;background:__ACCENT__;width:__PCT__%}

/* title cards */
body.card{background:__ACCENT__;color:#fff;justify-content:center;padding:0 96px}
body.card .kick{font-size:13px;font-weight:700;letter-spacing:.28em;text-transform:uppercase;
 color:__GOLD__;margin-bottom:22px}
body.card h1{font-size:54px;font-weight:600;letter-spacing:-.02em;line-height:1.08;
 color:#fff;max-width:20ch}
body.card .q{font-size:21px;line-height:1.5;color:__GOLD__;margin-top:28px;max-width:60ch;
 font-weight:400}
body.card .sub{position:absolute;left:96px;bottom:54px;font-size:12.5px;letter-spacing:.06em;
 color:rgba(255,255,255,.7)}
body.card .rule{width:64px;height:3px;background:__GOLD__;margin:26px 0 0}
""".replace("__W__", str(W)).replace("__H__", str(H)).replace("__ACCENT__", ACCENT).replace("__GOLD__", GOLD)


# ----------------------------------------------------------------- scenes

def _sid(*parts):
    return hashlib.sha256("\x00".join(parts).encode()).hexdigest()[:12]


def scenes_from(episodes, course, quality):
    """Narrated topics, with a course title card first and a module card at
    every module boundary. Cards are narrated with the module question."""
    out, seen_mod = [], None
    ins = course.get("instructor", {})
    out.append({"kind": "card", "title": course.get("title", ""),
                "kick": course.get("code", ""),
                "question": "", "sub": f'{ins.get("name", "")} · {ins.get("dept", "")}',
                "episode": "", "module": "",
                "narration": f'{course.get("title", "")}. {course.get("code", "")}. '
                             f'Course instructor, {ins.get("name", "")}.'})
    for meta, topics, mod in episodes:
        if mod["title"] != seen_mod:
            seen_mod = mod["title"]
            q = " ".join(str(mod.get("question", "")).split())
            out.append({"kind": "card", "title": mod["title"], "kick": "",
                        "question": q, "sub": "", "episode": "", "module": mod["title"],
                        "narration": f'{mod["title"]}. {q}' if q else mod["title"]})
        for t in topics:
            if not t.get("narration"):
                continue
            # a widget falls back to its diagram on video; if the topic already
            # shows that diagram as a figure, don't draw it twice
            parts, seen = [], set()
            for b in t["blocks"]:
                f = components.render(b, "frame")
                if f and f in seen:
                    continue
                seen.add(f); parts.append(f)
            frames = "".join(parts)
            out.append({"kind": "topic", "title": t["title"], "episode": meta["episode"],
                        "eptitle": meta.get("title", ""), "module": mod["title"],
                        "narration": t["narration"], "frames": frames})
    for i, s in enumerate(out, 1):
        s["n"] = i
        s["words"] = len(s["narration"].split())
        s["id"] = _sid(quality, s["kind"], s["title"], s["narration"],
                       s.get("frames", ""), s.get("question", ""))
    return out


def frame_html(sc, total):
    pct = round(100 * sc["n"] / total, 2)
    css = FRAME_CSS.replace("__PCT__", str(pct))
    if sc["kind"] == "card":
        kick = html.escape(sc["kick"] or sc["module"].split("—")[0].strip())
        title = sc["title"]
        if "—" in title and not sc["kick"]:
            kick, title = [x.strip() for x in title.split("—", 1)]
        q = f'<div class="q">{html.escape(sc["question"])}</div>' if sc["question"] else ""
        sub = f'<div class="sub">{html.escape(sc["sub"])}</div>' if sc["sub"] else ""
        return (f'<!doctype html><meta charset="utf-8"><style>{css}</style>'
                f'<body class="card"><div class="kick">{kick}</div>'
                f'<h1>{html.escape(title)}</h1><div class="rule"></div>{q}{sub}'
                f'<div class="prog"><i></i></div></body>')
    cap = html.escape(textwrap.shorten(plain(sc["narration"]), 250, placeholder=" ..."))
    kick = html.escape(sc["module"]) if sc["module"] else ""
    return (f'<!doctype html><meta charset="utf-8"><style>{css}</style>'
            f'<div class="topbar"></div>'
            f'<header><div><div class="kick">{kick}</div>'
            f'<h1>{html.escape(sc["title"])}</h1></div>'
            f'<div class="r"><div class="ep">{html.escape(sc["episode"])} &mdash; '
            f'{html.escape(sc.get("eptitle", ""))[:44]}</div>'
            f'<div class="n">{sc["n"]:02d} / {total:02d}</div></div></header>'
            f'<main>{sc["frames"]}</main><footer>{cap}</footer>'
            f'<div class="prog"><i></i></div>')


# ------------------------------------------------------------------ audio

def speakable(text):
    """Tidy the narration for a speech engine. Line breaks are meaningless to it,
    and typographic dashes and quotes are read inconsistently."""
    t = plain(text)
    t = (t.replace("—", ", ").replace("–", ", ")
          .replace("‘", "'").replace("’", "'")
          .replace("“", '"').replace("”", '"')
          .replace("…", "...").replace(" ", " "))
    return re.sub(r"\s+", " ", t).strip()


def _edge(text, mp3, voice, tries=4):
    """edge-tts talks to Microsoft's servers, which throttle a long run of rapid
    requests. Retry with backoff rather than losing the whole render at scene 19."""
    last = ""
    for attempt in range(1, tries + 1):
        tmp = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False,
                                          encoding="utf-8")
        tmp.write(text); tmp.close()
        try:
            r = subprocess.run([sys.executable, "-m", "edge_tts", "--voice", voice,
                                "--file", tmp.name, "--write-media", mp3],
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
            print(f"      tts attempt {attempt} failed ({last[:70]}); "
                  f"retrying in {wait}s")
            time.sleep(wait)
    return last


def _audio(sc, mp3, voice, engine):
    """edge-tts (free, no API key) -> gTTS -> correctly-timed silence."""
    text = speakable(sc["narration"])
    if engine in ("auto", "edge"):
        err = _edge(text, mp3, voice)
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
                f"\n  The {sc['n'] - 1} scenes before this one are cached. Wait a minute,\n"
                "  run make-video again, and it picks up exactly where it stopped.\n"
                "\n  If it keeps failing on the same scene:\n"
                "      pip install --upgrade edge-tts\n"
                "      python engine/build.py --video --engine gtts   (other service)\n")
    if engine in ("auto", "gtts"):
        try:
            from gtts import gTTS
            gTTS(text, lang="en").save(mp3); return "gTTS"
        except Exception:
            if engine == "gtts":
                raise
    subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono",
                    "-t", f"{max(3.0, sc['words'] / 2.45):.2f}", "-q:a", "9", mp3],
                   check=True, capture_output=True)
    return "SILENT"


def _dur(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", p], capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


# ------------------------------------------------------------------- video

def _encode(png, mp3, mp4, dpr):
    """One scene: the still frame over its narration, with a short fade in and
    out on both picture and sound so the cuts between scenes are soft."""
    dur = max(_dur(mp3), 1.0) + 0.6          # hold a beat after the voice stops
    w, h = int(W * dpr), int(H * dpr)
    fo = max(dur - 0.5, 0.1)
    subprocess.run(
        ["ffmpeg", "-y", "-loop", "1", "-framerate", str(FPS), "-i", png, "-i", mp3,
         "-t", f"{dur:.2f}",
         "-vf", f"scale={w}:{h}:flags=lanczos,format=yuv420p,"
                f"fade=t=in:st=0:d=0.45,fade=t=out:st={fo:.2f}:d=0.5",
         "-af", f"apad,afade=t=in:st=0:d=0.25,afade=t=out:st={fo:.2f}:d=0.4",
         "-c:v", "libx264", "-tune", "stillimage", "-preset", "veryfast", "-crf", "19",
         "-profile:v", "high", "-level", "5.1", "-r", str(FPS),
         "-c:a", "aac", "-b:a", "160k", "-ar", "48000",
         "-movflags", "+faststart", mp4],
        check=True, capture_output=True)


def build_video(episodes, course, cache, out_mp4, voice="en-GB-RyanNeural",
                engine="auto", force=False, quality="4k"):
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

    dpr = QUALITY.get(quality, 3)
    scenes = scenes_from(episodes, course, quality)
    total = len(scenes)
    if total <= 1:
        print("  no narrated topics - nothing to render"); return
    for d in ("png", "mp3", "mp4"):
        os.makedirs(f"{cache}/{d}", exist_ok=True)

    print(f"\n  {total} scenes at {int(W*dpr)}x{int(H*dpr)} ({quality})\n  " + "-" * 64)
    t0, built, cached, engines = time.time(), 0, 0, set()

    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        pg = br.new_page(viewport={"width": W, "height": H}, device_scale_factor=dpr)
        for sc in scenes:
            png, mp3 = f"{cache}/png/{sc['id']}.png", f"{cache}/mp3/{sc['id']}.mp3"
            mp4 = f"{cache}/mp4/{sc['id']}.mp4"
            if not force and all(os.path.exists(f) for f in (png, mp3, mp4)):
                cached += 1; tag = "cached "
            else:
                tmp = f"{cache}/_frame.html"
                open(tmp, "w", encoding="utf-8").write(frame_html(sc, total))
                pg.goto("file://" + os.path.abspath(tmp))
                pg.wait_for_timeout(120)           # let web fonts settle
                pg.screenshot(path=png)
                engines.add(_audio(sc, mp3, voice, engine))
                _encode(png, mp3, mp4, dpr)
                built += 1; tag = "REBUILT"
            lab = sc["title"] if sc["kind"] == "topic" else f"[{sc['title']}]"
            print(f"  {sc['n']:02d}  {tag}  {sc['id']}  {lab}")
        br.close()

    lst = f"{cache}/concat.txt"
    with open(lst, "w", encoding="utf-8") as f:
        for sc in scenes:
            f.write("file '%s'\n" % os.path.abspath(f"{cache}/mp4/{sc['id']}.mp4")
                    .replace("\\", "/"))
    os.makedirs(os.path.dirname(out_mp4) or ".", exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lst,
                    "-c", "copy", "-movflags", "+faststart", out_mp4],
                   check=True, capture_output=True)

    mins = sum(_dur(f"{cache}/mp4/{s['id']}.mp4") for s in scenes) / 60
    print("  " + "-" * 64)
    print(f"  {built} rebuilt, {cached} cached   {time.time()-t0:.1f}s")
    print(f"  {out_mp4}   {mins:.1f} min   {os.path.getsize(out_mp4)/1e6:.1f} MB   "
          f"{int(W*dpr)}x{int(H*dpr)} @ {FPS} fps")
    if "SILENT" in engines:
        print("\n  !!  NO SPEECH. edge-tts was unavailable, so every scene got\n"
              "      correctly-timed silence. Fix:  pip install edge-tts\n"
              "      then:  python engine/build.py --video --force --engine edge\n")
    elif engines:
        print(f"  voice: {'+'.join(sorted(engines))} ({voice})")
