"""
export_slides.py - export the lesson videos as slides: one clean image per scene,
fully built (every card, line and diagram in place), with no captions.

    python engine/export_slides.py                          the first videos: 0.1 and Module 1
    python engine/export_slides.py --episode 0.1 --episode 2.1
    python engine/export_slides.py --module 2               every lesson of one module
    python engine/export_slides.py --all                    every lesson
    python engine/export_slides.py --quality 4k             3840x2160 (default 1080p)
    python engine/export_slides.py --no-pdf                 images only

Output, one folder per lesson:

    dist/slides/0-1-course-introduction/01-title.png
    dist/slides/0-1-course-introduction/02-idea.png
    ...
    dist/slides/0-1-course-introduction.pdf          the same slides, one per page

The slides are drawn from the storyboards (content/<module>/<lesson>.video.md) by
the same stage the videos use, so they match the videos exactly, but they are not
frames grabbed from the mp4: the captions are burned into the video, and a frame
grab would carry them. A quiz scene gives two slides, the question and the answer.

Needs only what the site build and the video render already need: pyyaml,
playwright (with Chromium) and Pillow. No voice, no ffmpeg, no internet.
"""
import argparse, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import build                      # noqa: E402
import render_video as rv         # noqa: E402

# the first videos Narjes asked for: the course introduction and Module 1
DEFAULT_EPISODES = ["0.1", "1.1", "1.2", "1.3", "1.4"]
QUALITY = {"4k": 3, "1440p": 2, "1080p": 1.5, "720p": 1}
W, H = 1280, 720

# Hide the video caption band and timed pause prompt in static slides;
# re-centre the stage in the full frame. Question/answer slides remain separate.
SLIDE_CSS = "<style>.band,.pause{display:none!important}.stage{bottom:72px!important}</style>"


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", str(s).lower()).strip("-")


def lessons_in_order(course, episodes):
    rels = [rel for mod in course["modules"] for rel in mod["episodes"]]
    return [(m, t, md, os.path.join(ROOT, "content", rel)) for (m, t, md), rel in zip(episodes, rels)]


def pick(course, lessons, a):
    if a.all:
        return lessons
    want = []
    for n in a.module or []:
        mods = [m for m in course["modules"] if rv._mod_num(m) == str(n)]
        if not mods:
            sys.exit(f"  No module numbered {n}.")
        want += [x for x in lessons if x[2] is mods[0] and x not in want]
    for e in a.episode or ([] if a.module else DEFAULT_EPISODES):
        hit = [x for x in lessons if x[0]["episode"] == e]
        if not hit:
            print(f"  (no lesson numbered {e}; skipped)")
            continue
        if hit[0] not in want:
            want.append(hit[0])
    return [x for x in lessons if x in want]         # keep course order


def shoot(pg, html, path, tmp, quiz=False, n_opts=0):
    """Load one scene, put every beat at its end state, save a PNG (two for a quiz)."""
    open(tmp, "w", encoding="utf-8").write(html.replace("</head>", SLIDE_CSS + "</head>", 1))
    pg.goto("file://" + os.path.abspath(tmp))
    pg.wait_for_load_state("load")
    pg.wait_for_timeout(250)                            # fonts and images settle
    n = pg.evaluate("window.STAGE.prepare()")["count"]
    out = []
    if quiz and n >= 2:
        # every beat at once, except the countdown ring and the reveal, which come later
        times = [0.0] * (n - 2) + [1000.0, 2000.0]
        pg.evaluate("t => window.STAGE.setBeats(t)", times)
        pg.evaluate("t => window.STAGE.seek(t)", 500.0)
        q = path.replace("-quiz.png", "a-quiz-question.png")
        pg.screenshot(path=q, animations="disabled", caret="hide"); out.append(q)
        pg.evaluate("t => window.STAGE.seek(t)", 5000.0)
        r = path.replace("-quiz.png", "b-quiz-answer.png")
        pg.screenshot(path=r, animations="disabled", caret="hide"); out.append(r)
    else:
        pg.evaluate("t => window.STAGE.setBeats(t)", [0.0] * n)
        pg.evaluate("t => window.STAGE.seek(t)", 1000.0)  # long after the last animation ends
        pg.screenshot(path=path, animations="disabled", caret="hide"); out.append(path)
    return out


def to_pdf(pngs, pdf):
    from PIL import Image, JpegImagePlugin  # noqa: F401  (the PDF writer needs the JPEG encoder registered)
    pages = [Image.open(p).convert("RGB") for p in pngs]
    if pages:
        pages[0].save(pdf, save_all=True, append_images=pages[1:], resolution=150)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--episode", action="append", help="a lesson number, e.g. 1.1 (repeatable)")
    ap.add_argument("--module", action="append", help="every lesson of a module, e.g. 2 (repeatable)")
    ap.add_argument("--all", action="store_true", help="every lesson in the course")
    ap.add_argument("--quality", choices=list(QUALITY), default="1080p")
    ap.add_argument("--no-pdf", action="store_true", help="write the images only")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "slides"))
    a = ap.parse_args(argv)

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit("  Needs playwright:  pip install playwright   then   playwright install chromium")

    course, episodes = build.load_course()
    lessons = lessons_in_order(course, episodes)
    chosen = pick(course, lessons, a)
    if not chosen:
        sys.exit("  Nothing to export.")
    os.makedirs(a.out, exist_ok=True)
    tmp = os.path.join(a.out, "_scene.html")
    dpr = QUALITY[a.quality]
    print(f"\n  Exporting slides at {int(W * dpr)}x{int(H * dpr)} into {a.out}\n")

    with sync_playwright() as p:
        br = p.chromium.launch()
        pg = br.new_page(viewport={"width": W, "height": H}, device_scale_factor=dpr)
        for meta, topics, mod, path in chosen:
            i = lessons.index((meta, topics, mod, path))
            nxt = f'{lessons[i + 1][0]["episode"]} {lessons[i + 1][0].get("title", "")}' if i + 1 < len(lessons) else None
            scenes, source = rv.lesson_scenes(meta, topics, mod, course, a.quality, path, nxt)
            name = slug(f'{meta["episode"]} {meta.get("title", "")}')
            d = os.path.join(a.out, name)
            os.makedirs(d, exist_ok=True)
            for f in os.listdir(d):                      # a re-run replaces the old slides
                if f.endswith(".png"):
                    os.remove(os.path.join(d, f))
            pngs = []
            for k, sc in enumerate(scenes, 1):
                png = os.path.join(d, f"{k:02d}-{sc['type']}.png")
                pngs += shoot(pg, sc["html"], png, tmp, quiz=(sc["type"] == "quiz"), n_opts=len(sc.get("options") or []))
            if not a.no_pdf:
                to_pdf(pngs, os.path.join(a.out, name + ".pdf"))
            note = "" if source == "storyboard" else "   (no storyboard: automatic video)"
            print(f"  {meta['episode']:>5}  {len(pngs):3d} slides  {name}{'' if a.no_pdf else '  + pdf'}{note}")
        br.close()
    os.remove(tmp)
    print(f"\n  Done. Open {a.out}\n")


if __name__ == "__main__":
    main()
