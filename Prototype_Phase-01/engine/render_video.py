"""
render_video.py - the same topics, rendered as an MP4.

Every narrated topic becomes one scene, content-addressed:

    scene_id = sha256(title + narration + every block's frame() html)[:12]

Rendered PNG / MP3 / MP4 cache under .cache/ by that id, so editing one topic
re-renders one scene. Topics with no :::narration are web-only and skipped.
"""
import hashlib, html, os, re, shutil, subprocess, sys, tempfile, textwrap, time
import components
from parse import plain

W, H, FPS = 1280, 720, 10

FRAME_CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{width:__W__px;height:__H__px;background:#fff;color:#111;font-family:Montserrat,sans-serif;
 display:flex;flex-direction:column;overflow:hidden}
header{display:flex;align-items:flex-end;gap:18px;padding:24px 54px 14px;
 border-bottom:1px solid #111;flex:0 0 auto}
header .n{font-size:12.5px;font-weight:600;letter-spacing:.18em;padding-bottom:2px}
header h1{font-size:25px;font-weight:600;letter-spacing:-.014em;line-height:1.1}
header .r{margin-left:auto;text-align:right}
header .ep{font-size:10px;font-weight:700;letter-spacing:.2em}
header .sha{font:400 9.5px/1.7 'IBM Plex Mono',monospace;color:#b3b3b3}
main{flex:1;min-height:0;display:flex;flex-direction:column;justify-content:center;
 gap:16px;padding:20px 54px 8px;overflow:hidden}
.f-prose{font-size:16px;line-height:1.55;color:#3d3d3d;max-width:78ch}
.f-key{border-left:2px solid #111;background:#f7f7f6;padding:14px 18px}
.f-key .lbl{display:block;font-size:9px;font-weight:700;letter-spacing:.2em;
 text-transform:uppercase;color:#767676;margin-bottom:7px}
.f-key p{font-size:15px;line-height:1.5;color:#3d3d3d}
.f-fig{flex:1;min-height:0;display:flex;align-items:center;justify-content:center}
.f-fig svg,.f-fig img{max-width:100%;max-height:100%}
.f-code{font:400 13.5px/1.62 'IBM Plex Mono',monospace;white-space:pre-wrap;
 word-break:break-word;overflow:hidden}
.f-list{list-style:none;padding:0;font-size:15px;line-height:1.5;color:#3d3d3d}
.f-list li{padding-left:16px;position:relative;margin-bottom:6px}
.f-list li::before{content:'';position:absolute;left:0;top:.72em;width:6px;height:1px;background:#a6a6a6}
.f-cards{display:flex;gap:20px}
.f-cards>div{flex:1;border-left:2px solid #111;padding-left:14px}
.f-cards strong{display:block;font-size:14px;font-weight:600}
.f-cards span{font-size:12.5px;color:#5a5a5a;line-height:1.42}
.f-stats{display:flex;border:1px solid #e4e4e4}
.f-stats>div{flex:1;padding:14px 17px;border-right:1px solid #e4e4e4}
.f-stats>div:last-child{border-right:0}
.f-stats b{display:block;font-size:24px;font-weight:600}
.f-stats span{font-size:11.5px;color:#767676}
.f-flow{display:flex;flex-wrap:wrap;gap:9px;background:#f7f7f6;padding:13px 16px;font-size:13px}
.f-flow span:not(:last-child)::after{content:" →";color:#a6a6a6;margin-left:9px}
.f-refs{font-size:10.5px;color:#a6a6a6;text-align:right}
footer{flex:0 0 auto;height:78px;border-top:1px solid #111;padding:14px 54px;
 font-size:15px;line-height:1.42;color:#454545;overflow:hidden}
""".replace("__W__", str(W)).replace("__H__", str(H))


def scenes_from(episodes):
    out = []
    for meta, topics, _ in episodes:
        for t in topics:
            if not t.get("narration"):
                continue                       # web-only topic
            frames = "".join(components.render(b, "frame") for b in t["blocks"])
            sid = hashlib.sha256(
                "\x00".join([t["title"], t["narration"], frames]).encode()
            ).hexdigest()[:12]
            out.append({"id": sid, "title": t["title"], "episode": meta["episode"],
                        "narration": t["narration"], "frames": frames,
                        "words": len(t["narration"].split())})
    for i, s in enumerate(out, 1):
        s["n"] = i
    return out


def frame_html(sc, total):
    cap = html.escape(textwrap.shorten(plain(sc["narration"]), 230, placeholder=" ..."))
    return (f'<!doctype html><meta charset="utf-8"><style>{FRAME_CSS}</style>'
            f'<header><span class="n">{sc["n"]:02d} / {total:02d}</span>'
            f'<h1>{html.escape(sc["title"])}</h1>'
            f'<div class="r"><div class="ep">EPISODE {html.escape(sc["episode"])}</div>'
            f'<div class="sha">{sc["id"]}</div></div></header>'
            f'<main>{sc["frames"]}</main><footer>{cap}</footer>')


def speakable(text):
    """Tidy the narration for a speech engine. Line breaks are meaningless to it,
    and typographic dashes and quotes are read inconsistently."""
    t = plain(text)
    t = (t.replace("\u2014", ", ").replace("\u2013", ", ")
          .replace("\u2018", "'").replace("\u2019", "'")
          .replace("\u201c", '"').replace("\u201d", '"')
          .replace("\u2026", "...").replace("\u00a0", " "))
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
            # --file, not --text: no command-line length or encoding limits
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
                f"({sc['episode']} - {sc['title']}) after 4 tries.\n"
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


def build_video(episodes, cache, out_mp4, voice="en-GB-RyanNeural",
                engine="auto", force=False):
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

    scenes, total = scenes_from(episodes), 0
    total = len(scenes)
    if not total:
        print("  no narrated topics - nothing to render"); return
    for d in ("png", "mp3", "mp4"):
        os.makedirs(f"{cache}/{d}", exist_ok=True)

    print(f"\n  {total} narrated scenes\n  " + "-" * 64)
    t0, built, cached, engines = time.time(), 0, 0, set()

    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        pg = br.new_page(viewport={"width": W, "height": H})
        for sc in scenes:
            png, mp3 = f"{cache}/png/{sc['id']}.png", f"{cache}/mp3/{sc['id']}.mp3"
            mp4 = f"{cache}/mp4/{sc['id']}.mp4"
            if not force and all(os.path.exists(f) for f in (png, mp3, mp4)):
                cached += 1; tag = "cached "
            else:
                tmp = f"{cache}/_frame.html"
                open(tmp, "w", encoding="utf-8").write(frame_html(sc, total))
                pg.goto("file://" + os.path.abspath(tmp))
                pg.screenshot(path=png)
                engines.add(_audio(sc, mp3, voice, engine))
                subprocess.run(
                    ["ffmpeg", "-y", "-loop", "1", "-i", png, "-i", mp3,
                     "-c:v", "libx264", "-tune", "stillimage", "-preset", "veryfast",
                     "-pix_fmt", "yuv420p", "-r", str(FPS), "-c:a", "aac", "-b:a", "128k",
                     "-shortest", "-vf", f"scale={W}:{H}", mp4],
                    check=True, capture_output=True)
                built += 1; tag = "REBUILT"
            print(f"  {sc['n']:02d}  {tag}  {sc['id']}  {sc['title']}")
        br.close()

    lst = f"{cache}/concat.txt"
    with open(lst, "w", encoding="utf-8") as f:
        for sc in scenes:
            f.write("file '%s'\n" % os.path.abspath(f"{cache}/mp4/{sc['id']}.mp4")
                    .replace("\\", "/"))
    os.makedirs(os.path.dirname(out_mp4) or ".", exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lst,
                    "-c", "copy", out_mp4], check=True, capture_output=True)

    mins = sum(_dur(f"{cache}/mp4/{s['id']}.mp4") for s in scenes) / 60
    print("  " + "-" * 64)
    print(f"  {built} rebuilt, {cached} cached   {time.time()-t0:.1f}s")
    print(f"  {out_mp4}   {mins:.1f} min   {os.path.getsize(out_mp4)/1e6:.1f} MB")
    if "SILENT" in engines:
        print("\n  !!  NO SPEECH. edge-tts was unavailable, so every scene got\n"
              "      correctly-timed silence. Fix:  pip install edge-tts\n"
              "      then:  python engine/build.py --video --force --engine edge\n")
    elif engines:
        print(f"  voice: {'+'.join(sorted(engines))} ({voice})")
