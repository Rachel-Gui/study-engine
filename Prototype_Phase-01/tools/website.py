#!/usr/bin/env python3
"""
website.py - build the Study Engine and open it in your browser.
Double-click WEBSITE.bat (Windows) or WEBSITE.command (Mac), or run:

    python tools/website.py              build, serve on http://localhost:8000, open the browser
    python tools/website.py preview      the same, with the locked modules opened (for checking only)
    python tools/website.py build        build only, no server

Lesson videos rendered by VIDEOS-4K (dist/video/) are put on the site automatically:
a 1080p web copy plays at the top of each lesson and on the Lesson videos page.
Stop the server with Ctrl+C, or close the window.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _env import ROOT, banner, say, need_python, need_packages, need_assets, need_ffmpeg, run

def main(argv):
    args = [a.lower() for a in argv]
    banner("AI for Architecture - build and open the website")
    say(f"Folder: {ROOT}")
    need_python()
    need_packages([("yaml", "pyyaml")])
    need_assets()
    vids = os.path.join(ROOT, "dist", "video")
    if os.path.isdir(vids) and any(f.endswith(".mp4") for f in os.listdir(vids)):
        if not need_ffmpeg(required=False):
            say("Note: ffmpeg not found, so the videos are copied to the site at full size.")
    cmd = [sys.executable, os.path.join(ROOT, "engine", "build.py")]
    if "preview" in args:
        cmd.append("--preview")
    if "build" not in args:
        cmd.append("--serve")
        say("The site opens in your browser. Leave this window open while you use it;")
        say("press Ctrl+C here (or close the window) to stop.")
    return run(cmd)

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
