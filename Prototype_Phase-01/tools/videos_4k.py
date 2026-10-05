#!/usr/bin/env python3
"""
videos_4k.py - render the narrated lesson videos in 4K, then put them on the website.
Double-click VIDEOS-4K.bat (Windows) or VIDEOS-4K.command (Mac), or run:

    python tools/videos_4k.py            Course introduction + Modules 1 and 2
    python tools/videos_4k.py all        every lesson in the course
    python tools/videos_4k.py 2          one module         (2.4 = one lesson; mix freely)
    python tools/videos_4k.py 1080p      a faster 1080p render (add to any of the above)

Output: dist/video/<lesson>.mp4 (3840x2160) and dist/scripts/<lesson>.md (narration script).
Needs the internet (the narration voice is Microsoft's online neural voice).
Stop any time; running it again resumes - every finished scene is cached in .cache/.
"""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _env import (ROOT, banner, say, stop, need_python, need_packages, need_assets, need_chromium, need_ffmpeg,
                  check_fonts, run, selection, flags)

def main(argv):
    quality = "1080p" if any(a.lower() == "1080p" for a in argv) else "4k"
    rest = [a for a in argv if a.lower() not in ("1080p", "4k")]
    eps, mods, everything, what = selection(rest)
    banner(f"AI for Architecture - narrated lesson videos, {quality.upper()}")
    say(f"Folder:  {ROOT}")
    say(f"Lessons: {what}")
    need_python()
    need_packages([("yaml", "pyyaml"), ("playwright", "playwright"), ("edge_tts", "edge-tts"), ("PIL", "pillow")])
    need_assets()
    need_chromium()
    need_ffmpeg()
    check_fonts()
    say("Rendering. A 4K lesson takes several minutes; the first run is the slowest.")
    say("Leave this window open. If it stops, run it again: it resumes where it stopped.")
    cmd = [sys.executable, os.path.join(ROOT, "engine", "make_videos.py"), "--engine", "edge",
           "--quality", quality] + ([] if everything else flags(eps, mods))
    for attempt in range(1, 5):              # the free voice service sometimes throttles long runs
        if run(cmd) == 0:
            break
        if attempt == 4:
            stop("The render stopped four times. Read the message above.\n"
                 "Everything finished so far is cached: run VIDEOS-4K again later to continue.")
        say(f"The render stopped (attempt {attempt} of 4). Waiting a minute, then resuming ...")
        time.sleep(60)
    banner("Putting the videos on the website")
    run([sys.executable, os.path.join(ROOT, "engine", "build.py")])
    say()
    say(f"DONE.  Videos (4K):        {os.path.join(ROOT, 'dist', 'video')}")
    say(f"       Narration scripts:  {os.path.join(ROOT, 'dist', 'scripts')}")
    say("       On the website:     run WEBSITE, then open 'Lesson videos' (or any lesson).")
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
