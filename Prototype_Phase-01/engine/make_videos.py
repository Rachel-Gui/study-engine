#!/usr/bin/env python3
"""
make_videos.py - one narrated, animated MP4 per lesson and per module, plus the
narration scripts, without touching the site build.

    python engine/make_videos.py                    every lesson + every module, 4K
    python engine/make_videos.py --episode 2.8      one lesson
    python engine/make_videos.py --module 2         one module (and its lessons)
    python engine/make_videos.py --course           add the single full-course MP4
    python engine/make_videos.py --scripts          only write the narration scripts
    python engine/make_videos.py --quality 1080p    a fast preview render
    python engine/make_videos.py --engine edge      fail loudly if the voice is unavailable
    python engine/make_videos.py --force            ignore the scene cache

Output:
    dist/video/2-8-llms-and-structured-generation.mp4      one per lesson
    dist/video/module-2-generative-ai.mp4                  one per module
    dist/video/course.mp4                                  with --course
    dist/scripts/2-8-llms-and-structured-generation.md     the narration script
    dist/scripts/module-2-generative-ai.md                 per video

Scenes are cached in .cache/ by content, so a lesson and its module share every
scene, and editing one topic re-renders one scene. Stop it any time; running
it again picks up where it left off.
"""
import argparse, os, re, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import build                                                     # noqa: E402
import render_video as rv                                        # noqa: E402

ROOT = build.ROOT


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:70] or "video"


def _select(course, episodes, a):
    """Which lessons and which modules to render."""
    mods = []
    for m in course["modules"]:
        if m not in mods:
            mods.append(m)
    want_eps, want_mods = [], []
    if a.episode:
        for e in a.episode:
            hit = [x for x in episodes if x[0]["episode"] == e]
            if not hit:
                sys.exit(f"\n  No lesson numbered {e}. Lessons: "
                         + ", ".join(x[0]["episode"] for x in episodes) + "\n")
            want_eps += hit
    if a.module:
        for n in a.module:
            hit = [m for m in mods if rv._mod_num(m) == str(n) or slug(m["title"]) == slug(str(n))]
            if not hit:
                sys.exit(f"\n  No module numbered {n}. Modules: "
                         + ", ".join(rv._mod_num(m) or m["title"] for m in mods) + "\n")
            want_mods += hit
            want_eps += [x for x in episodes if x[2] is hit[0] and x not in want_eps]
    if not a.episode and not a.module:
        want_eps, want_mods = list(episodes), list(mods)
    return want_eps, want_mods


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--episode", "-e", action="append", help="lesson number, e.g. 2.8 (repeatable)")
    ap.add_argument("--module", "-m", action="append", help="module number, e.g. 2 (repeatable)")
    ap.add_argument("--course", action="store_true", help="also render the single full-course video")
    ap.add_argument("--no-modules", action="store_true", help="lessons only, no module videos")
    ap.add_argument("--scripts", action="store_true", help="write the narration scripts and stop")
    ap.add_argument("--quality", default="4k", choices=list(rv.QUALITY))
    ap.add_argument("--engine", default="auto", choices=["auto", "edge", "gtts", "silent"])
    ap.add_argument("--voice", default=None)
    ap.add_argument("--force", action="store_true", help="re-render every scene")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist"))
    a = ap.parse_args(argv)

    course, episodes = build.load_course()
    voice = a.voice or course.get("voice", "en-GB-RyanNeural")
    eps, mods = _select(course, episodes, a)
    vdir, sdir = os.path.join(a.out, "video"), os.path.join(a.out, "scripts")
    os.makedirs(vdir, exist_ok=True); os.makedirs(sdir, exist_ok=True)
    cache = os.path.join(ROOT, ".cache")

    # ---- scripts first: they are useful even without a render
    jobs = []
    for meta, topics, mod in eps:
        name = slug(f'{meta["episode"]}-{meta["title"]}')
        scenes = rv.episode_scenes(meta, topics, mod, a.quality)
        jobs.append(("lesson", name, scenes, f'{meta["episode"]} — {meta["title"]}',
                     f'Lesson video · {rv._mod_label(mod)} · voice {voice}'))
    if not a.no_modules:
        for mod in mods:
            name = slug(mod["title"])
            scenes = rv.module_scenes(mod, episodes, a.quality)
            if len(scenes) > 1:
                jobs.append(("module", name, scenes, mod["title"],
                             f'Module video · {len([e for e in episodes if e[2] is mod])} lessons · voice {voice}'))
    if a.course:
        jobs.append(("course", "course", rv.course_scenes(course, episodes, a.quality),
                     course["title"], f'Full course · {len(episodes)} lessons · voice {voice}'))

    print(f"\n  narration scripts -> {sdir}")
    for kind, name, scenes, title, sub in jobs:
        est = rv.write_script(os.path.join(sdir, name + ".md"), scenes, title + " — narration script", sub, cache)
        print(f"      {name}.md   {len(scenes)} scenes · about {rv._mmss(est)}")
    if a.scripts:
        print("\n  (scripts only - nothing rendered)\n"); return

    # ---- render
    r = rv.Renderer(cache, voice=voice, engine=a.engine, force=a.force, quality=a.quality)
    t0 = time.time()
    try:
        for kind, name, scenes, title, sub in jobs:
            r.stitch(scenes, os.path.join(vdir, name + ".mp4"), f"{kind.upper()}  {title}")
    finally:
        r.close()
    # scripts again, now with measured timings
    for kind, name, scenes, title, sub in jobs:
        rv.write_script(os.path.join(sdir, name + ".md"), scenes, title + " — narration script", sub, cache)
    r.report()
    print(f"  {len(jobs)} videos in {vdir}   ({(time.time() - t0) / 60:.1f} min)\n")


if __name__ == "__main__":
    main()
