"""
render_video.py - narrated motion-graphics videos, one per lesson.

Each lesson video is built from its storyboard (content/<module>/<lesson>.video.md,
see storyboard.py) rather than from the web page. A storyboard is a list of
scenes - a title card, one big idea, a diagram that draws itself, animated
steps, cards, counting numbers, typed code, a chart, a "pause and predict"
quiz, a "try it on the site" callout, a recap - each with its own narration
written for students who have never met the topic.

How a scene is rendered
  1. The narration is spoken (edge-tts, which also returns word timings).
  2. The scene's stage page (stage.py) is opened in headless Chromium. Its
     elements are grouped into "beats"; the renderer places each beat at the
     start of a sentence of the narration, so the picture builds as the
     voice goes.
  3. The renderer screenshots the stage frame by frame while something is
     moving (24 fps), and once while nothing is, and hands ffmpeg the list
     with each frame's duration. ffmpeg overlays the captions and the
     progress bar (an ASS subtitle track) and encodes the scene.
  4. Scenes are cached by content under .cache/, so editing one scene of one
     storyboard re-renders one scene.

Resolution: the stage is 1280x720 CSS pixels rendered at a device scale factor
(3 for 4K); text, diagrams and code scale together.
"""
import hashlib, html, json, math, os, re, shutil, subprocess, sys, tempfile, time
import stage, storyboard
from parse import plain

W, H = stage.W, stage.H
FPS = 24
QUALITY = {"4k": 3, "1440p": 2, "1080p": 1.5, "720p": 1}
LEAD = 0.25          # seconds before beat 0
TAIL = 0.9           # seconds of picture after the voice stops
GAP = 0.5            # pause between a quiz question and its countdown, and after the reveal
WPS = 2.45           # words per second when no word timings are available
CAP_CHARS = 88
JPEG_Q = 92


# ----------------------------------------------------------------- scenes

def _sid(*parts):
    return hashlib.sha256("\x00".join(str(p) for p in parts).encode()).hexdigest()[:12]


def _mod_num(mod):
    m = re.match(r"\s*Module\s+(\d+)", mod.get("title", ""))
    return m.group(1) if m else ""


def _mod_label(mod):
    n = _mod_num(mod)
    return f'Module {n} · {mod.get("short") or mod["title"]}' if n else (mod.get("short") or mod["title"])


def lesson_scenes(meta, topics, mod, course, quality, lesson_path=None, nxt=None, voice=None, rate=None):
    """The scenes of one lesson video, each with its stage HTML and id (the id includes the voice)."""
    voice = voice or course.get("voice", "")
    rate = rate or course.get("voice_rate", "+0%")
    sb = storyboard.path_for(lesson_path) if lesson_path else None
    if sb and os.path.exists(sb):
        _, scenes = storyboard.load(sb)
        source = "storyboard"
    else:
        scenes = storyboard.auto(meta, topics, nxt)
        source = "auto"
    ins = course.get("instructor", {})
    ctx = {"episode": meta["episode"], "title": meta.get("title", ""), "module": _mod_label(mod),
           "objectives": meta.get("objectives") or [], "course": course.get("title", ""),
           "instructor": ins.get("name", "")}
    out = []
    for k, sc in enumerate(scenes, 1):
        sc = dict(sc)
        sc["figure"] = sc.get("id")                        # a diagram's figure id, before "id" becomes the scene hash
        sc["html"] = stage.scene_html(sc, ctx)
        sc["episode"], sc["lesson"], sc["n"] = meta["episode"], meta.get("title", ""), k
        sc["narration"] = str(sc.get("narration", "")).strip()
        sc["after"] = str(sc.get("after", "") or "").strip()
        sc["words"] = len(speakable(sc["narration"]).split()) + len(speakable(sc["after"]).split())
        sc["id"] = _sid("v3", quality, meta["episode"], sc["type"], sc["html"], sc["narration"], sc["after"],
                        sc.get("pause", ""), voice, rate)
        out.append(sc)
    return out, source


# ------------------------------------------------------------------ audio

def speakable(text):
    t = plain(str(text or ""))
    t = re.sub(r"\s*[—–]\s*", ", ", t)
    t = (t.replace("‘", "'").replace("’", "'").replace("“", '"').replace("”", '"')
          .replace("…", "...").replace(" ", " "))
    return re.sub(r"\s+", " ", t).strip()


def sentences(text):
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9\"'(])", speakable(text))
    return [p.strip() for p in parts if p.strip()]


def _edge(text, mp3, srt, voice, tries=4, rate="+0%"):
    last = ""
    for attempt in range(1, tries + 1):
        tmp = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8")
        tmp.write(text); tmp.close()
        try:
            cmd = [sys.executable, "-m", "edge_tts", "--voice", voice, "--file", tmp.name,
                   "--write-media", mp3, "--write-subtitles", srt]
            if rate and rate not in ("+0%", "0%", "0"):
                cmd += [f"--rate={rate}"]
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
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


def _speak(text, mp3, srt, voice, engine, label, rate="+0%"):
    """edge-tts (free, word timings) -> gTTS -> correctly-timed silence. Returns the engine used."""
    text = speakable(text)
    for p in (mp3, srt):
        if os.path.exists(p):
            os.remove(p)
    if not text:
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono",
                        "-t", "1.0", "-q:a", "9", mp3], check=True)
        return "SILENT"
    if engine in ("auto", "edge"):
        err = _edge(text, mp3, srt, voice, rate=rate)
        if err is None:
            time.sleep(0.3)
            return "edge-tts"
        if engine == "edge":
            sys.exit(f"\n  Text-to-speech failed on {label} after 4 tries.\n\n  edge-tts said:  {err}\n"
                     "\n  edge-tts uses Microsoft's free online voice service, so this is usually the\n"
                     "  network or their rate limiter. The scenes before this one are cached: wait a\n"
                     "  minute and run the same command again; it resumes where it stopped.\n"
                     "      pip install --upgrade edge-tts\n"
                     "      python engine/make_videos.py --engine gtts   (other service)\n")
    if engine in ("auto", "gtts"):
        try:
            from gtts import gTTS
            gTTS(text, lang="en").save(mp3); return "gTTS"
        except Exception:
            if engine == "gtts":
                raise
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono",
                    "-t", f"{max(2.5, len(text.split()) / WPS):.2f}", "-q:a", "9", mp3], check=True)
    return "SILENT"


def _dur(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


# ------------------------------------------------------------------ timing

def _srt_words(path):
    if not path or not os.path.exists(path):
        return []
    txt = open(path, encoding="utf-8", errors="replace").read()
    out = []
    for m in re.finditer(r"(\d+):(\d+):(\d+)[,.](\d+)\s*-->\s*(\d+):(\d+):(\d+)[,.](\d+)\s*\n(.*?)(?:\n\s*\n|\Z)", txt, re.S):
        g = m.groups()
        t0 = int(g[0]) * 3600 + int(g[1]) * 60 + int(g[2]) + int(g[3]) / 10 ** len(g[3])
        t1 = int(g[4]) * 3600 + int(g[5]) * 60 + int(g[6]) + int(g[7]) / 10 ** len(g[7])
        words = g[8].split()
        for i, w in enumerate(words):
            out.append((t0 + (t1 - t0) * i / max(1, len(words)), w))
    return out


def word_times(narration, srt, voice_dur, offset=0.0):
    words = speakable(narration).split()
    n = len(words)
    if n == 0:
        return []
    timed = _srt_words(srt)
    if timed and len(timed) >= max(3, n * 0.6):
        m = len(timed)
        return [offset + timed[min(m - 1, int(i * m / n))][0] for i in range(n)]
    lead = 0.12
    return [offset + lead + (voice_dur - lead - 0.35) * i / max(1, n) for i in range(n)]


def _caption_chunks(sw):
    """Split one sentence's words into caption-sized chunks of similar length,
    breaking at punctuation when it falls near the ideal point. No orphans."""
    text = " ".join(sw)
    if len(text) <= CAP_CHARS:
        return [sw]
    k = math.ceil(len(text) / CAP_CHARS)
    target = len(text) / k
    chunks, cur = [], []
    for idx, w in enumerate(sw):
        cur.append(w)
        n = len(" ".join(cur))
        left = len(sw) - idx - 1
        if len(chunks) < k - 1 and left >= 3:
            if n >= target or (n >= target * 0.66 and re.search(r"[,;:—]$", w)):
                chunks.append(cur); cur = []
    if cur:
        if chunks and len(" ".join(cur)) < CAP_CHARS * 0.3 and len(" ".join(chunks[-1] + cur)) <= CAP_CHARS * 1.25:
            chunks[-1] += cur
        else:
            chunks.append(cur)
    return chunks


def caption_cues(narration, times, end):
    words = speakable(narration).split()
    cues, i = [], 0
    for s in sentences(narration):
        chunks = _caption_chunks(s.split())
        for ch in chunks:
            start = times[min(i, len(times) - 1)] if times else 0
            i += len(ch)
            cues.append([start, None, " ".join(ch)])
    for k, c in enumerate(cues):
        c[1] = cues[k + 1][0] - 0.05 if k + 1 < len(cues) else end
    return [tuple(c) for c in cues]


def beat_times(n_beats, narration, times, voice_end, first=LEAD):
    """Beat 0 at `first`; the rest at sentence starts (evenly chosen) or, when
    there are more beats than sentences, evenly across the voice."""
    if n_beats <= 0:
        return []
    out = [first]
    m = n_beats - 1
    if m == 0:
        return out
    starts, i = [], 0
    for s in sentences(narration):
        if i > 0:
            starts.append(times[min(i, len(times) - 1)])
        i += len(s.split())
    starts = [t for t in starts if t > first + 0.4]
    if len(starts) >= m:
        pick = [starts[round((j + 1) * len(starts) / (m + 1)) - 1] for j in range(m)] if m < len(starts) else starts[:m]
    else:
        end = max(voice_end - 0.6, first + 0.8)
        pick = [first + (end - first) * (j + 1) / (m + 1) for j in range(m)]
    prev = first
    for t in pick:
        t = max(t, prev + 0.35)
        out.append(t); prev = t
    return out


# --------------------------------------------------------------- captions

def _ass_time(t):
    t = max(0.0, t)
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


def _ass_text(s):
    return html.unescape(s).replace("\\", "\\\\").replace("{", "(").replace("}", ")")


def write_ass(path, cues, total, card=False):
    cap_col = "&H00F2F2F2" if card else "&H00333333"
    bar_col = "&H00D3E3E8" if card else "&H00832E4B"
    lines = ["[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}", "WrapStyle: 0",
             "ScaledBorderAndShadow: yes", "", "[V4+ Styles]",
             "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, "
             "Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
             f"Style: Cap,Montserrat,23,{cap_col},&H000000FF,&H00FFFFFF,&H00000000,0,0,0,0,100,100,0,0,1,0,0,2,56,56,24,1",
             f"Style: Bar,Montserrat,20,{bar_col},&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1",
             "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
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


def _check_tools():
    missing = [t for t in ("ffmpeg", "ffprobe") if not shutil.which(t)]
    if missing:
        sys.exit("\n  Cannot render video: " + " and ".join(missing) + " not found.\n"
                 "\n  ffmpeg is a separate program, not a Python package. Install it:\n"
                 "\n      Windows   winget install Gyan.FFmpeg\n"
                 "                THEN CLOSE THIS WINDOW AND OPEN A NEW ONE.\n"
                 "      Mac       brew install ffmpeg\n"
                 "      Linux     sudo apt install ffmpeg\n"
                 "\n  Then check with:  python engine/build.py --doctor\n")


def _merge(spans):
    spans = sorted(spans)
    out = []
    for s, e in spans:
        if out and s <= out[-1][1] + 0.02:
            out[-1][1] = max(out[-1][1], e)
        else:
            out.append([s, e])
    return out


class Renderer:
    def __init__(self, cache, voice="en-US-AvaMultilingualNeural", engine="auto", force=False, quality="4k", rate="+0%"):
        _check_tools()
        self.cache, self.voice, self.engine, self.force, self.rate = cache, voice, engine, force, rate
        self.quality, self.dpr = quality, QUALITY.get(quality, 3)
        for d in ("mp3", "mp4", "ass", "meta", "frames"):
            os.makedirs(os.path.join(cache, d), exist_ok=True)
        self.built = self.cached = 0
        self.engines = set()
        self._pw = self._br = self._pg = None

    def _page(self):
        if self._pg is None:
            from playwright.sync_api import sync_playwright
            self._pw = sync_playwright().start()
            self._br = self._pw.chromium.launch()
            self._pg = self._br.new_page(viewport={"width": W, "height": H}, device_scale_factor=self.dpr)
        return self._pg

    def close(self):
        if self._br:
            self._br.close(); self._pw.stop()
            self._pw = self._br = self._pg = None

    # ---- one scene
    def render(self, sc):
        mp4 = f"mp4/{sc['id']}.mp4"
        meta = os.path.join(self.cache, "meta", sc["id"] + ".json")
        if not self.force and os.path.exists(os.path.join(self.cache, mp4)) and os.path.exists(meta):
            self.cached += 1
            return mp4, "cached ", json.load(open(meta, encoding="utf-8"))
        label = f"scene {sc['n']} of {sc['episode']} ({sc['type']})"
        C = self.cache

        # 1. voice (two parts for a quiz: the question, then the explanation after the reveal)
        mp3a, srta = f"mp3/{sc['id']}-a.mp3", f"mp3/{sc['id']}-a.srt"
        self.engines.add(_speak(sc["narration"], os.path.join(C, mp3a), os.path.join(C, srta), self.voice, self.engine, label, self.rate))
        va = max(_dur(os.path.join(C, mp3a)), 0.8)
        is_quiz = sc["type"] == "quiz"
        pause = float(sc.get("pause", 5)) if is_quiz else 0.0
        vb, mp3b, srtb = 0.0, None, None
        if is_quiz and sc["after"]:
            mp3b, srtb = f"mp3/{sc['id']}-b.mp3", f"mp3/{sc['id']}-b.srt"
            self.engines.add(_speak(sc["after"], os.path.join(C, mp3b), os.path.join(C, srtb), self.voice, self.engine, label, self.rate))
            vb = max(_dur(os.path.join(C, mp3b)), 0.8)

        # 2. the stage and its beats
        pg = self._page()
        tmp = os.path.join(C, "_stage.html")
        open(tmp, "w", encoding="utf-8").write(sc["html"])
        pg.goto("file://" + os.path.abspath(tmp))
        pg.wait_for_timeout(120)
        info = pg.evaluate("window.STAGE.prepare()")
        n_beats, spans = info["count"], {int(k): v for k, v in info["spans"].items()}
        wa = word_times(sc["narration"], os.path.join(C, srta), va)
        if is_quiz:
            n_opts = len(sc.get("options") or [])
            base = beat_times(n_opts + 1, sc["narration"], wa, va)             # question + options
            t_ring = va + GAP
            t_reveal = t_ring + 0.3 + pause + 0.25
            times = base + [t_ring, t_reveal]
            t_after = t_reveal + 0.9
            total = t_after + vb + TAIL
            wb = word_times(sc["after"], os.path.join(C, srtb), vb, offset=t_after) if mp3b else []
            cues = caption_cues(sc["narration"], wa, va + 0.3) + \
                   ([(t_ring + 0.2, t_reveal - 0.1, "Pause the video. Which one would you pick?")] if pause else []) + \
                   (caption_cues(sc["after"], wb, total - 0.3) if mp3b else [])
        else:
            times = beat_times(n_beats, sc["narration"], wa, va)
            total = max(va, (times[-1] + spans.get(n_beats - 1, 0.6)) if times else 0) + TAIL
            cues = caption_cues(sc["narration"], wa, va + 0.3)
        times = times[:n_beats] + [times[-1] if times else 0.0] * max(0, n_beats - len(times))
        pg.evaluate("t => window.STAGE.setBeats(t)", times)

        # 3. frames: 24 fps while a beat animates, one frame while nothing moves
        bursts = _merge([(times[k], times[k] + spans.get(k, 0.6) + 0.05) for k in range(n_beats)])
        plan, t = [], 0.0
        for s, e in bursts:
            s, e = max(s, 0.0), min(e, total)
            if s > t + 1e-6:
                plan.append((t, s - t))
            k = 0
            while s + k / FPS < e:
                plan.append((s + k / FPS, 1 / FPS)); k += 1
            t = s + k / FPS
        if t < total:
            plan.append((t, total - t))
        fdir = os.path.join(C, "frames", sc["id"])
        shutil.rmtree(fdir, ignore_errors=True); os.makedirs(fdir)
        lst = [f"ffconcat version 1.0"]
        for i, (tt, d) in enumerate(plan):
            pg.evaluate("t => window.STAGE.seek(t)", tt)
            fn = f"f{i:05d}.jpg"
            pg.screenshot(path=os.path.join(fdir, fn), type="jpeg", quality=JPEG_Q, animations="disabled", caret="hide")
            lst.append(f"file '{fn}'\nduration {d:.5f}")
        lst.append(f"file 'f{len(plan) - 1:05d}.jpg'")
        open(os.path.join(fdir, "list.txt"), "w", encoding="utf-8").write("\n".join(lst) + "\n")

        # 4. captions, then encode
        ass = f"ass/{sc['id']}.ass"
        write_ass(os.path.join(C, ass), cues, total, card=(sc["type"] in ("title", "next")))
        fo = max(total - 0.5, 0.1)
        vf = f"fps={FPS},format=yuv420p," + (f"ass={ass}," if _has_ass() else "") + \
             f"fade=t=in:st=0:d=0.4,fade=t=out:st={fo:.2f}:d=0.5"
        cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
               "-f", "concat", "-safe", "0", "-i", os.path.join("frames", sc["id"], "list.txt"), "-i", mp3a]
        if mp3b:
            cmd += ["-f", "lavfi", "-t", f"{t_after - va:.3f}", "-i", "anullsrc=r=24000:cl=mono", "-i", mp3b]
            afilter = "[1:a][2:a][3:a]concat=n=3:v=0:a=1,apad,afade=t=in:st=0:d=0.2,afade=t=out:st=%.2f:d=0.4[a]" % fo
            cmd += ["-filter_complex", f"[0:v]{vf}[v];{afilter}", "-map", "[v]", "-map", "[a]"]
        else:
            cmd += ["-filter_complex", f"[0:v]{vf}[v];[1:a]apad,afade=t=in:st=0:d=0.2,afade=t=out:st={fo:.2f}:d=0.4[a]",
                    "-map", "[v]", "-map", "[a]"]
        cmd += ["-t", f"{total:.3f}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-profile:v", "high",
                "-level", "5.1", "-r", str(FPS), "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-ar", "48000",
                "-movflags", "+faststart", mp4]
        r = subprocess.run(cmd, cwd=C, capture_output=True, text=True)
        shutil.rmtree(fdir, ignore_errors=True)
        if r.returncode != 0:
            sys.exit(f"\n  ffmpeg failed on {label}:\n{r.stderr[-1500:]}\n")
        m = {"duration": total, "beats": n_beats, "frames": len(plan),
             "cues": [(round(s, 2), round(e, 2), t) for s, e, t in cues]}
        json.dump(m, open(meta, "w", encoding="utf-8"))
        self.built += 1
        return mp4, "REBUILT", m

    # ---- one video
    def stitch(self, scenes, out_mp4, label):
        t0 = time.time()
        print(f"\n  {label}\n  {len(scenes)} scenes at {int(W * self.dpr)}x{int(H * self.dpr)} ({self.quality})\n  " + "-" * 64)
        parts, total = [], 0.0
        for sc in scenes:
            mp4, tag, m = self.render(sc)
            parts.append(mp4); total += m["duration"]
            print(f"  {sc['n']:02d}  {tag}  {sc['id']}  {sc['type']:<8} {m['frames']:>4} frames  {_mmss(m['duration'])}")
        lst = os.path.join(self.cache, f"concat-{_sid(out_mp4)}.txt")
        with open(lst, "w", encoding="utf-8") as f:
            for p in parts:
                f.write(f"file '{p}'\n")
        os.makedirs(os.path.dirname(os.path.abspath(out_mp4)), exist_ok=True)
        r = subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0",
                            "-i", os.path.abspath(lst), "-c", "copy", "-movflags", "+faststart", os.path.abspath(out_mp4)],
                           cwd=self.cache, capture_output=True, text=True)
        if r.returncode != 0:
            sys.exit(f"\n  ffmpeg could not join the scenes:\n{r.stderr[-1200:]}\n")
        print("  " + "-" * 64)
        print(f"  {out_mp4}   {_mmss(total)}   {os.path.getsize(out_mp4) / 1e6:.1f} MB   {time.time() - t0:.0f}s")
        return total

    def report(self):
        if "SILENT" in self.engines:
            print("\n  !!  NO SPEECH. edge-tts was unavailable, so every rebuilt scene got correctly-timed\n"
                  "      silence. Fix:  pip install edge-tts   then run the same command with  --force --engine edge\n")
        elif self.engines:
            print(f"\n  voice: {'+'.join(sorted(self.engines))} ({self.voice})")
        print(f"  {self.built} scenes rebuilt, {self.cached} from cache")


# ----------------------------------------------------------------- scripts

def _mmss(t):
    return f"{int(t // 60)}:{int(t % 60):02d}"


def _onscreen(sc):
    t = sc["type"]
    g = lambda k, d=None: sc.get(k, d)
    if t == "title":
        return ["title card with the lesson's objectives"]
    if t == "next":
        return [f"end card: {g('text')}"]
    if t == "idea":
        return [f"big statement: {str(g('text') or '').replace(' / ', ' ')}"] + ([f"then: {g('sub')}"] if g("sub") else [])
    if t in ("list", "recap"):
        return ([f"heading: {g('heading')}"] if g("heading") else []) + [f"• {x}" for x in (g("items") or [])]
    if t == "cards":
        return ([f"heading: {g('heading')}"] if g("heading") else []) + \
               [f"card: {x.get('title') if isinstance(x, dict) else x}" for x in (g("items") or [])]
    if t == "steps":
        return ([f"heading: {g('heading')}"] if g("heading") else []) + \
               ["steps: " + " → ".join((x.get("title") if isinstance(x, dict) else str(x).lstrip("*")) for x in (g("steps") or []))]
    if t == "compare":
        return [f"{(g('left') or {}).get('title')} vs {(g('right') or {}).get('title')}"] + ([f"verdict: {g('verdict')}"] if g("verdict") else [])
    if t == "number":
        return [f"{x.get('value')} — {x.get('label')}" for x in (g("items") or [])]
    if t == "code":
        return ([f"heading: {g('heading')}"] if g("heading") else []) + [f"code, {len(str(g('code') or '').splitlines())} lines typed in"] + (["output panel"] if g("output") else [])
    if t == "chart":
        return [f"{g('kind', 'bar')} chart: {', '.join(str(x) for x in (g('labels') or []))}"]
    if t == "diagram":
        return [f"diagram '{g('figure') or g('id')}' draws itself"] + [f"• {x}" for x in (g("points") or [])]
    if t == "quiz":
        return [f"question: {g('question')}"] + [f"{'ABCD'[i]}. {o}" for i, o in enumerate(g("options") or [])] + \
               [f"pause ring ({g('pause', 5)} s), then answer {'ABCD'[int(g('answer', 0))]} is highlighted"]
    if t == "site":
        return [f"laptop mock-up: {g('path') or 'the lesson page'}", f"{g('text')}"]
    return []


def write_script(path, scenes, title, sub, cache=None, source="storyboard"):
    rows, t = [], 0.0
    for sc in scenes:
        d, measured = sc["words"] / WPS + 1.4 + (float(sc.get("pause", 5)) + 1.5 if sc["type"] == "quiz" else 0), False
        if cache:
            mp = os.path.join(cache, "meta", sc["id"] + ".json")
            if os.path.exists(mp):
                d, measured = json.load(open(mp, encoding="utf-8"))["duration"], True
        rows.append((sc, t, d, measured)); t += d
    lines = [f"# {title}", "", sub, "",
             f"{len(scenes)} scenes · about {_mmss(t)} · timings {'measured' if all(r[3] for r in rows) else 'estimated at %.1f words/s' % WPS}"
             + ("" if source == "storyboard" else " · no storyboard yet: this is the automatic fallback"), "",
             "| # | Scene | Starts | Length |", "|---|---|---|---|"]
    for sc, start, d, measured in rows:
        label = str(sc.get('heading') or sc.get('text') or sc.get('question') or sc['lesson']).replace(" / ", " ")
        lines.append(f"| {sc['n']} | {sc['type']}: {label[:70]} | {_mmss(start)} | {_mmss(d)}{'' if measured else ' (est.)'} |")
    lines.append("")
    for sc, start, d, measured in rows:
        lines += [f"## Scene {sc['n']} · {sc['type']}", "", f"*{_mmss(start)} – {_mmss(start + d)} · {sc['words']} words*", "",
                  "**On screen**", ""] + [f"  - {x}" for x in _onscreen(sc)] + ["", "**Narration**", ""]
        lines += [">" + (" " + s if s else "") for s in sentences(sc["narration"])]
        if sc.get("after"):
            lines += ["", "*(after the answer is revealed)*", ""] + [">" + (" " + s if s else "") for s in sentences(sc["after"])]
        lines.append("")
    open(path, "w", encoding="utf-8").write("\n".join(lines))
    return t
