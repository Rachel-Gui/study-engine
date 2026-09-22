#!/usr/bin/env python3
"""
build.py - the only command anyone runs.

    python engine/build.py                 site only  (fast)
    python engine/build.py --video         site + MP4
    python engine/build.py --video --force ignore the scene cache
    python engine/build.py --engine edge   fail loudly if TTS is unavailable

Reads course.yml, parses every episode listed there, and hands the same topic
tree to both renderers. Content authors never open this file.
"""
import argparse, os, sys, yaml

# Windows consoles default to cp1252; topic titles contain em-dashes.
for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")

NEEDS = ["parse.py", "components.py", "figures.py",
         "render_web.py", "render_video.py"]


def _locate():
    """Find the engine modules and the project root.

    Downloading these files from a chat flattens the folders, so the layout
    on disk is not always the layout in the repo. Rather than dying with
    'No module named parse', look in the obvious places and say plainly what
    is missing if they aren't there.
    """
    here = os.path.dirname(os.path.abspath(__file__))
    up = os.path.dirname(here)
    for eng in (here, os.path.join(here, "engine"), os.path.join(up, "engine"), up):
        if all(os.path.exists(os.path.join(eng, f)) for f in NEEDS):
            for root in (os.path.dirname(eng), eng, up, here):
                if os.path.exists(os.path.join(root, "course.yml")):
                    return eng, root
            return eng, os.path.dirname(eng)

    found = sorted(f for f in os.listdir(here) if f.endswith(".py"))
    missing = [f for f in NEEDS if not os.path.exists(os.path.join(here, f))]
    sys.exit(
        "\n  The engine is incomplete.\n"
        f"\n  Looked in: {here}"
        f"\n  Found:     {', '.join(found) or '(no .py files)'}"
        f"\n  Missing:   {', '.join(missing)}\n"
        "\n  This almost always means the files were downloaded individually and\n"
        "  the folder structure was lost. The repo must look like this:\n"
        "\n      course.yml"
        "\n      content/03-deep-learning/3.1-neuron.md"
        "\n      engine/build.py  parse.py  components.py  figures.py"
        "\n                       render_web.py  render_video.py"
        "\n      engine/theme/site.css  site.js\n"
        "\n  Unzip the release archive, or clone the repo, instead of moving\n"
        "  files by hand.\n")


HERE, ROOT = _locate()
sys.path.insert(0, HERE)

import parse, render_web                                        # noqa: E402


def load_course():
    try:
        course = yaml.safe_load(open(os.path.join(ROOT, "course.yml"), encoding="utf-8"))
    except Exception as e:
        sys.exit(f"\n  course.yml could not be read:\n      {e}\n")
    for key in ("code", "title", "instructor", "modules"):
        if key not in course:
            sys.exit(f"\n  course.yml is missing `{key}:`\n")
    for key in ("name", "role", "dept", "email"):
        course["instructor"].setdefault(key, "")
    parse.GLOSSARY.update({k.lower(): v for k, v in (course.get("glossary") or {}).items()})
    episodes = []
    for mod in course["modules"]:
        for rel in mod["episodes"]:
            path = os.path.join(ROOT, "content", rel)
            if not os.path.exists(path):
                loose = os.path.join(ROOT, os.path.basename(rel))
                hint = (f"\n  It does exist at {loose} - move it to content/"
                        f"{os.path.dirname(rel)}/" if os.path.exists(loose) else "")
                sys.exit(f"\n  course.yml lists a file that is not there:"
                         f"\n      content/{rel}{hint}\n")
            try:
                meta, topics = parse.parse_episode(path)
            except Exception as e:
                sys.exit(f"\n  content/{rel} could not be read:\n      {e}\n")
            meta.setdefault("title", os.path.basename(rel))
            if not meta.get("episode"):
                sys.exit(f"\n  content/{rel} has no `episode:` in its frontmatter.\n"
                         f"  Quote it, so YAML keeps it as text:  episode: \"3.1\"\n")
            if not topics:
                sys.exit(f"\n  content/{rel} has no topics. Every topic starts with "
                         f"a `## Heading` line.\n")
            episodes.append((meta, topics, mod))
    return course, episodes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--engine", default="auto", choices=["auto", "edge", "gtts", "silent"])
    ap.add_argument("--voice", default=None)
    ap.add_argument("--quality", default="4k", choices=["4k", "1440p", "1080p", "720p"],
                    help="video resolution (default 4k = 3840x2160)")
    ap.add_argument("--out", default=os.path.join(ROOT, "site"))
    ap.add_argument("--serve", action="store_true",
                    help="serve the site on localhost and open a browser")
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--doctor", action="store_true",
                    help="check what is installed for video rendering")
    a = ap.parse_args()

    if a.doctor:
        sys.exit(doctor())

    course, episodes = load_course()
    flat = render_web.build_site(course, episodes, a.out)
    narrated = sum(1 for _, ts, _ in episodes for t in ts if t.get("narration"))

    print("\n  " + "=" * 68)
    print(f"  BUILDING   {ROOT}")
    print("  " + "=" * 68)
    seen = None
    for meta, topics, mod in episodes:
        if mod["title"] != seen:
            seen = mod["title"]
            print(f"\n  {mod['title'].upper()}")
        n = sum(1 for t in topics if t.get("narration"))
        print(f"      {meta['episode']:>4}  {meta['title'][:52]:<52}"
              f"{len(topics):>3} topics, {n} narrated")
    print("\n  " + "-" * 68)
    print(f"  {len(flat)} pages  ·  {len(episodes)} episodes  ·  "
          f"{narrated} video scenes  ·  {len(flat) - narrated} web-only")
    print(f"  written to {a.out}")
    if len(episodes) < 2:
        print("\n  !!  Only one episode. If you expected the whole course, you are\n"
              "      probably running an old copy of the folder. Check the path at\n"
              "      the top of this output.")

    if a.video:
        import render_video
        render_video.build_video(
            episodes, course, os.path.join(ROOT, ".cache"),
            os.path.join(ROOT, "dist", "course.mp4"),
            voice=a.voice or course.get("voice", "en-GB-RyanNeural"),
            engine=a.engine, force=a.force, quality=a.quality)
    if a.serve:
        serve(a.out, a.port)
    print()


def _installed_fonts():
    """Lower-cased list of font file names / family names, or None if unknown.
    Windows keeps fonts in two folders and has no fc-list; macOS has fc-list
    only with Homebrew, so look at the folders directly there too."""
    import glob, subprocess
    names = []
    if sys.platform.startswith("win"):
        dirs = [os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts"),
                os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "Windows", "Fonts")]
    elif sys.platform == "darwin":
        dirs = ["/Library/Fonts", os.path.expanduser("~/Library/Fonts"), "/System/Library/Fonts"]
    else:
        dirs = ["/usr/share/fonts", "/usr/local/share/fonts", os.path.expanduser("~/.fonts"),
                os.path.expanduser("~/.local/share/fonts")]
    for d in dirs:
        if d and os.path.isdir(d):
            names += [os.path.basename(p).lower() for p in glob.glob(os.path.join(d, "**", "*.[to]tf"), recursive=True)]
    try:
        names.append(subprocess.run(["fc-list"], capture_output=True, text=True,
                                    timeout=20).stdout.lower())
    except Exception:
        pass
    return " ".join(names) if names else None


def doctor():
    """Report exactly what is and is not ready for video rendering."""
    import importlib.util, shutil, subprocess
    print(f"\n  Checking {ROOT}\n  " + "-" * 60)
    ok = True

    def line(name, good, fix):
        nonlocal ok
        print(f"  {'OK  ' if good else 'MISSING'}  {name}")
        if not good:
            ok = False
            print(f"            fix:  {fix}")

    line("pyyaml (needed for the site)", importlib.util.find_spec("yaml"),
         "pip install pyyaml")
    line("playwright (renders video frames)", importlib.util.find_spec("playwright"),
         "pip install playwright  &&  playwright install chromium")
    line("edge-tts (the narration voice)", importlib.util.find_spec("edge_tts"),
         "pip install edge-tts")
    line("ffmpeg (stitches the video)", shutil.which("ffmpeg"),
         "Windows: winget install Gyan.FFmpeg  THEN CLOSE AND REOPEN THIS WINDOW\n"
         "                  Mac:     brew install ffmpeg\n"
         "                  Linux:   sudo apt install ffmpeg")
    line("ffprobe (measures scene length)", shutil.which("ffprobe"),
         "ships with ffmpeg - if ffmpeg is found but this is not, your PATH is stale;\n"
         "                  close and reopen the terminal")

    fonts = _installed_fonts()
    if fonts is None:
        print("  ?       fonts - could not check on this system.")
        print("            Montserrat and IBM Plex Mono must be installed for the")
        print("            video frames to look right. See README section 4.")
    else:
        line("Montserrat font", "montserrat" in fonts,
             "download the .ttf from Google Fonts and install it (README section 4)")
        line("IBM Plex Mono font", "plexmono" in fonts or "plex mono" in fonts,
             "download the .ttf from Google Fonts and install it (README section 4)")

    print("  " + "-" * 60)
    print("  Everything is ready. Run:  python engine/build.py --video --engine edge\n"
          if ok else
          "  Install what is missing above, then run this check again.\n")
    return 0 if ok else 1


def serve(directory, port):
    """The labs need http://, not file:// - Pyodide fetches WASM cross-origin
    and a file:// page has a null origin, so the fetch is blocked."""
    import functools, http.server, socketserver, threading, webbrowser
    handler = functools.partial(http.server.SimpleHTTPRequestHandler,
                                directory=directory)
    socketserver.TCPServer.allow_reuse_address = True
    while True:
        try:
            httpd = socketserver.TCPServer(("127.0.0.1", port), handler)
            break
        except OSError:
            port += 1
            if port > 8020:
                sys.exit("  no free port between 8000 and 8020")
    url = f"http://localhost:{port}/"
    print(f"\n  serving {url}   (Ctrl+C to stop)")
    threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n  stopped")


if __name__ == "__main__":
    main()
