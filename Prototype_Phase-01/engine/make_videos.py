#!/usr/bin/env python3
"""
make_videos.py - one narrated, animated video per lesson, plus its narration script.

    python engine/make_videos.py                     every lesson, 4K
    python engine/make_videos.py --episode 2.8       one lesson
    python engine/make_videos.py --module 2          the lessons of one module
    python engine/make_videos.py --scripts           only write the narration scripts
    python engine/make_videos.py --quality 1080p     a faster render (about 3x)
    python engine/make_videos.py --engine edge       fail loudly if the voice is unavailable
    python engine/make_videos.py --force             ignore the scene cache
    python engine/make_videos.py --modules           also join each module's lessons into one file
    python engine/make_videos.py --course            also join everything into one file

Each lesson's video comes from its storyboard, content/<module>/<lesson>.video.md
(see README section 4 and engine/storyboard.py). A lesson without a storyboard
gets a plain automatic video and the script says so.

Output:
    dist/video/2-8-llms-and-structured-generation.mp4
    dist/scripts/2-8-llms-and-structured-generation.md

Scenes are cached in .cache/ by content: editing one scene re-renders one scene.
Stop it any time; running it again picks up where it left off.
"""
import argparse, os, re, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import build                                                     # noqa: E402
import render_video as rv                                        # noqa: E402

ROOT = build.ROOT


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:70] or "video"


def _lessons(course, episodes):
    """(meta, topics, mod, path) in course order."""
    rels = [rel for mod in course["modules"] for rel in mod["episodes"]]
    return [(m, t, md, os.path.join(ROOT, "content", rel)) for (m, t, md), rel in zip(episodes, rels)]


def _select(course, lessons, a):
    mods = []
    for m in course["modules"]:
        if m not in mods:
            mods.append(m)
    want = []
    for e in a.episode or []:
        hit = [x for x in lessons if x[0]["episode"] == e]
        if not hit:
            sys.exit(f"\n  No lesson numbered {e}. Lessons: " + ", ".join(x[0]["episode"] for x in lessons) + "\n")
        want += hit
    for n in a.module or []:
        hit = [m for m in mods if rv._mod_num(m) == str(n) or slug(m["title"]) == slug(str(n))]
        if not hit:
            sys.exit(f"\n  No module numbered {n}. Modules: " + ", ".join(rv._mod_num(m) or m["title"] for m in mods) + "\n")
        want += [x for x in lessons if x[2] is hit[0] and x not in want]
    if not a.episode and not a.module:
        want = list(lessons)
    return want, mods


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--episode", "-e", action="append", help="lesson number, e.g. 2.8 (repeatable)")
    ap.add_argument("--module", "-m", action="append", help="module number, e.g. 2 (repeatable)")
    ap.add_argument("--modules", action="store_true", help="also join each module's lessons into one file")
    ap.add_argument("--course", action="store_true", help="also join every lesson into one file")
    ap.add_argument("--scripts", action="store_true", help="write the narration scripts and stop")
    ap.add_argument("--quality", default="4k", choices=list(rv.QUALITY))
    ap.add_argument("--engine", default="auto", choices=["auto", "edge", "gtts", "silent"])
    ap.add_argument("--voice", default=None, help="a Microsoft neural voice name (course.yml `voice` by default)")
    ap.add_argument("--rate", default=None, help='speaking rate, e.g. "-5%%" (course.yml `voice_rate` by default)')
    ap.add_argument("--force", action="store_true", help="re-render every scene")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist"))
    a = ap.parse_args(argv)

    course, episodes = build.load_course()
    voice = a.voice or course.get("voice", "en-US-AvaMultilingualNeural")
    rate = a.rate or course.get("voice_rate", "+0%")
    lessons = _lessons(course, episodes)
    want, mods = _select(course, lessons, a)
    vdir, sdir = os.path.join(a.out, "video"), os.path.join(a.out, "scripts")
    os.makedirs(vdir, exist_ok=True); os.makedirs(sdir, exist_ok=True)
    cache = os.path.join(ROOT, ".cache")

    jobs, missing = [], []
    for i, (meta, topics, mod, path) in enumerate(lessons):
        if (meta, topics, mod, path) not in want:
            continue
        nxt = f'{lessons[i + 1][0]["episode"]} {lessons[i + 1][0].get("title", "")}' if i + 1 < len(lessons) else None
        scenes, source = rv.lesson_scenes(meta, topics, mod, course, a.quality, path, nxt, voice, rate)
        if source != "storyboard":
            missing.append(meta["episode"])
        name = slug(f'{meta["episode"]}-{meta["title"]}')
        jobs.append((name, scenes, f'{meta["episode"]} — {meta["title"]}', f'Lesson video · {rv._mod_label(mod)} · voice {voice}', source, mod))

    print(f"\n  narration scripts -> {sdir}")
    for name, scenes, title, sub, source, mod in jobs:
        est = rv.write_script(os.path.join(sdir, name + ".md"), scenes, title + " — narration script", sub, cache, source)
        print(f"      {name}.md   {len(scenes)} scenes · about {rv._mmss(est)}" + ("" if source == "storyboard" else "   (no storyboard: automatic)"))
    if missing:
        print(f"\n  !!  {len(missing)} lesson(s) have no .video.md storyboard and get the plain automatic video: "
              + ", ".join(missing))
    if a.scripts:
        print("\n  (scripts only - nothing rendered)\n"); return

    r = rv.Renderer(cache, voice=voice, engine=a.engine, force=a.force, quality=a.quality, rate=rate)
    t0 = time.time()
    made = {}
    try:
        for name, scenes, title, sub, source, mod in jobs:
            out = os.path.join(vdir, name + ".mp4")
            r.stitch(scenes, out, f"LESSON  {title}")
            made.setdefault(id(mod), []).append(out)
        if a.modules:
            for mod in mods:
                outs = made.get(id(mod), [])
                if len(outs) > 1:
                    _join(outs, os.path.join(vdir, slug(mod["title"]) + ".mp4"), cache)
        if a.course:
            outs = [o for mod in mods for o in made.get(id(mod), [])]
            if outs:
                _join(outs, os.path.join(vdir, "course.mp4"), cache)
    finally:
        r.close()
    for name, scenes, title, sub, source, mod in jobs:
        rv.write_script(os.path.join(sdir, name + ".md"), scenes, title + " — narration script", sub, cache, source)
    r.report()
    print(f"  {len(jobs)} lesson videos in {vdir}   ({(time.time() - t0) / 60:.1f} min)\n")


def _join(files, out, cache):
    import subprocess
    lst = os.path.join(cache, "join-" + rv._sid(out) + ".txt")
    with open(lst, "w", encoding="utf-8") as f:
        for p in files:
            f.write("file '%s'\n" % os.path.abspath(p).replace("\\", "/").replace("'", r"'\''"))
    r = subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst,
                        "-c", "copy", "-movflags", "+faststart", out], capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"\n  ffmpeg could not join the lessons into {out}:\n{r.stderr[-800:]}\n")
    print(f"  joined -> {out}   {os.path.getsize(out) / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
