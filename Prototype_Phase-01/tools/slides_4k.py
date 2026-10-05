#!/usr/bin/env python3
"""
slides_4k.py - export the lesson videos as 4K slides: one clean PNG per scene
(3840x2160, every element in place, no captions) and one PDF per lesson.
Double-click SLIDES-4K.bat (Windows) or SLIDES-4K.command (Mac), or run:

    python tools/slides_4k.py            Course introduction + Modules 1 and 2
    python tools/slides_4k.py all        every lesson in the course
    python tools/slides_4k.py 2          one module         (2.4 = one lesson; mix freely)
    python tools/slides_4k.py nopdf      images only (add to any of the above)

Output: dist/slides/<lesson>/NN-<scene>.png and dist/slides/<lesson>.pdf.
No voice, no ffmpeg and no internet needed.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _env import ROOT, banner, say, stop, need_python, need_packages, need_assets, need_chromium, check_fonts, run, selection, flags

def main(argv):
    nopdf = any(a.lower() in ("nopdf", "no-pdf", "--no-pdf") for a in argv)
    rest = [a for a in argv if a.lower() not in ("nopdf", "no-pdf", "--no-pdf")]
    eps, mods, everything, what = selection(rest)
    banner("AI for Architecture - 4K slides from the lesson videos")
    say(f"Folder:  {ROOT}")
    say(f"Lessons: {what}")
    need_python()
    need_packages([("yaml", "pyyaml"), ("playwright", "playwright"), ("PIL", "pillow")])
    need_assets()
    need_chromium()
    check_fonts()
    cmd = [sys.executable, os.path.join(ROOT, "engine", "export_slides.py"), "--quality", "4k"] \
          + (["--all"] if everything else flags(eps, mods)) + (["--no-pdf"] if nopdf else [])
    if run(cmd) != 0:
        stop("Slide export failed. Read the message above.")
    say()
    say(f"DONE.  Slides: {os.path.join(ROOT, 'dist', 'slides')}")
    say("       One folder of PNGs per lesson" + ("" if nopdf else ", plus one PDF per lesson") + ".")
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
