"""
_env.py - shared set-up checks for the three double-click scripts
(WEBSITE, VIDEOS-4K, SLIDES-4K). Each check fixes what it safely can
(Python packages, the Chromium that renders frames, ffmpeg on Windows/macOS)
and otherwise says exactly what to do.
"""
import glob, hashlib, importlib.util, json, os, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WIN = sys.platform.startswith("win")
MAC = sys.platform == "darwin"

for _s in (sys.stdout, sys.stderr):                 # Windows consoles default to cp1252
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")


def say(msg=""):
    print("  " + msg if msg else "", flush=True)


def banner(title):
    say(); say("=" * 66); say(title); say("=" * 66)


def stop(msg):
    say(); say("!" * 66)
    for line in msg.strip().splitlines():
        say(line)
    say("!" * 66); say()
    sys.exit(1)


def need_python():
    if sys.version_info < (3, 9):
        stop(f"This needs Python 3.9 or newer; this is {sys.version.split()[0]}.\n"
             "Install a current Python from python.org (Lesson 1.1), then run this again.")


def need_packages(pairs):
    """pairs: [(import_name, pip_name)]. Installs whatever is missing into this Python."""
    missing = [pip for mod, pip in pairs if importlib.util.find_spec(mod) is None]
    if not missing:
        return
    say(f"Installing Python packages: {' '.join(missing)}")
    r = subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade"] + missing)
    if r.returncode != 0:
        r = subprocess.run([sys.executable, "-m", "pip", "install", "--user", "--upgrade"] + missing)
    importlib.invalidate_caches()
    still = [pip for mod, pip in pairs if importlib.util.find_spec(mod) is None]
    if still:
        stop("Could not install: " + " ".join(still) + "\n"
             f"Try by hand:  {os.path.basename(sys.executable)} -m pip install " + " ".join(still))


def need_chromium():
    """Playwright's own Chromium draws every frame and slide. Install it once if absent."""
    code = ("from playwright.sync_api import sync_playwright\n"
            "with sync_playwright() as p:\n    b = p.chromium.launch(); b.close()\n")
    if subprocess.run([sys.executable, "-c", code], capture_output=True).returncode == 0:
        return
    say("Installing the Chromium browser that draws the frames (one time, about 150 MB) ...")
    subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"])
    if subprocess.run([sys.executable, "-c", code], capture_output=True, text=True).returncode != 0:
        stop("Chromium for Playwright would not start.\n"
             f"Run by hand:  {os.path.basename(sys.executable)} -m playwright install chromium")


def _add_to_path(folder):
    os.environ["PATH"] = folder + os.pathsep + os.environ.get("PATH", "")


def _find_ffmpeg_windows():
    roots = [os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "WinGet", "Packages"),
             os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "WinGet", "Links"),
             r"C:\ffmpeg\bin", os.path.join(os.environ.get("ProgramFiles", ""), "ffmpeg", "bin"),
             os.path.join(os.environ.get("USERPROFILE", ""), "scoop", "shims"),
             r"C:\ProgramData\chocolatey\bin"]
    for r in roots:
        if not r or not os.path.isdir(r):
            continue
        hits = glob.glob(os.path.join(r, "ffmpeg.exe")) + glob.glob(os.path.join(r, "**", "ffmpeg.exe"), recursive=True)
        for h in hits:
            if os.path.exists(os.path.join(os.path.dirname(h), "ffprobe.exe")):
                return os.path.dirname(h)
    return None


def need_ffmpeg(required=True):
    """ffmpeg and ffprobe stitch and measure the video. Find them even when a fresh
    install has not reached this window's PATH yet; install them if we can."""
    if shutil.which("ffmpeg") and shutil.which("ffprobe"):
        return True
    if WIN:
        found = _find_ffmpeg_windows()
        if not found and shutil.which("winget"):
            say("Installing ffmpeg with winget (one time) ...")
            subprocess.run(["winget", "install", "-e", "--id", "Gyan.FFmpeg",
                            "--accept-source-agreements", "--accept-package-agreements"])
            found = _find_ffmpeg_windows()
        if found:
            _add_to_path(found)
    elif MAC:
        for d in ("/opt/homebrew/bin", "/usr/local/bin"):
            if os.path.exists(os.path.join(d, "ffmpeg")):
                _add_to_path(d)
        if not shutil.which("ffmpeg") and shutil.which("brew"):
            say("Installing ffmpeg with Homebrew (one time) ...")
            subprocess.run(["brew", "install", "ffmpeg"])
    if shutil.which("ffmpeg") and shutil.which("ffprobe"):
        return True
    if not required:
        return False
    stop("ffmpeg is not installed. It is a program, not a Python package.\n"
         + ("Windows:  winget install Gyan.FFmpeg     then run this script again."
            if WIN else
            "Mac:      brew install ffmpeg            (Homebrew: https://brew.sh)\n"
            "Linux:    sudo apt install ffmpeg"))


def check_fonts():
    """The frames use Montserrat and IBM Plex Mono. Without them Chromium substitutes
    other fonts and text can run long. Warn; do not stop."""
    sys.path.insert(0, os.path.join(ROOT, "engine"))
    try:
        import build                                             # engine/build.py
        fonts = build._installed_fonts()
    except Exception:
        fonts = None
    if fonts is None:
        return
    miss = [n for n, keys in (("Montserrat", ("montserrat",)), ("IBM Plex Mono", ("plexmono", "plex mono")))
            if not any(k in fonts for k in keys)]
    if miss:
        say("WARNING: font(s) not installed: " + ", ".join(miss))
        say("  The frames will fall back to other fonts. Install them from Google Fonts")
        say("  (fonts.google.com, Download family, open the .ttf, Install), then run again.")
        say()


def _engine():
    sys.path.insert(0, os.path.join(ROOT, "engine"))
    import build                                                 # engine/build.py
    return build


def _part_sources():
    """Where the other parts of a split download may be: zips named Prototype_Phase-01*.zip,
    or the folders they were unzipped into, next to this folder, a level or two up, in
    Downloads (and its subfolders, where download managers sort zips) or on the Desktop."""
    home = os.path.expanduser("~")
    up1 = os.path.dirname(ROOT); up2 = os.path.dirname(up1); up3 = os.path.dirname(up2)
    dirs = [ROOT, up1, up2, up3, os.path.join(home, "Desktop"), os.path.join(home, "Downloads")]
    dl = os.path.join(home, "Downloads")
    if os.path.isdir(dl):
        try:
            dirs += [os.path.join(dl, d) for d in os.listdir(dl) if os.path.isdir(os.path.join(dl, d))]
        except OSError:
            pass
    me = os.path.normcase(os.path.abspath(ROOT))
    zips, roots, seen = [], [], set()
    for d in dirs:
        d = os.path.abspath(d)
        if d in seen or not os.path.isdir(d):
            continue
        seen.add(d)
        try:
            names = os.listdir(d)
        except OSError:
            continue
        for n in names:
            p = os.path.join(d, n)
            if not n.startswith("Prototype_Phase"):
                continue
            if n.lower().endswith(".zip") and os.path.isfile(p):
                zips.append(p)
            elif os.path.isdir(p):
                for r in (p, os.path.join(p, "Prototype_Phase 01")):
                    rn = os.path.normcase(os.path.abspath(r))
                    if rn != me and not me.startswith(rn + os.sep) and os.path.isdir(os.path.join(r, "assets")):
                        roots.append(r)
    return zips, roots


def need_assets():
    """Every picture the lessons use must be in this folder. A download that came in parts
    (Prototype_Phase-01-part1, -part2, -part3) and was unzipped into separate folders is the
    usual cause: copy the missing files in from the other parts, never overwriting anything.
    A part is used only if it holds at least one of the missing pictures; from it, every
    file under assets/ that this folder lacks is copied, so the folder ends up complete."""
    import zipfile
    try:
        build = _engine()
    except Exception:
        return
    missing = build.missing_assets()
    if not missing:
        restore_recorded()
        return
    say(f"{len(missing)} picture(s) are not in this folder yet. Looking for the other parts of the download ...")
    want = set(missing)
    zips, roots = _part_sources()
    roots.sort(key=lambda r: "part" not in r.lower())            # the parts themselves first
    zips.sort(key=lambda z: "part" not in os.path.basename(z).lower())
    got = 0

    def put(rel, write):
        nonlocal got
        dst = os.path.join(ROOT, *rel.split("/"))
        if not os.path.exists(dst):
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            write(dst)
            got += 1
        want.discard(rel)

    for r in roots:                                              # folders a part was unzipped into
        files = []
        for dirpath, _, names in os.walk(os.path.join(r, "assets")):
            files += [os.path.relpath(os.path.join(dirpath, n), r).replace(os.sep, "/") for n in names]
        if not want.intersection(files):
            continue
        for rel in files:
            src = os.path.join(r, *rel.split("/"))
            put(rel, lambda dst, src=src: shutil.copy2(src, dst))
    for z in zips:                                               # parts still zipped
        if not want:
            break
        try:
            with zipfile.ZipFile(z) as zf:
                members = {}
                for info in zf.infolist():
                    parts = info.filename.replace("\\", "/").split("/")
                    if parts and parts[0].startswith("Prototype_Phase"):
                        parts = parts[1:]
                    if len(parts) > 1 and parts[0] == "assets" and parts[-1] and not info.is_dir():
                        members["/".join(parts)] = info
                if not want.intersection(members):
                    continue
                for rel, info in members.items():
                    def write(dst, info=info):
                        with zf.open(info) as fi, open(dst, "wb") as fo:
                            shutil.copyfileobj(fi, fo)
                    put(rel, write)
        except (OSError, zipfile.BadZipFile):
            continue
    if got:
        say(f"Copied {got} file(s) into this folder's assets from the other parts of the download.")
    missing = build.missing_assets()
    if missing:
        stop(f"{len(missing)} picture(s) the lessons use are still missing, for example\n"
             f"    {missing[0]}\n"
             "Without them the website, the videos and the slides show blank pictures.\n"
             "If the course came in several zips (part1, part2, part3), put the zips, or the\n"
             "folders they were unzipped into, next to this folder or in Downloads, and run\n"
             "this again: it copies the pictures in by itself.")
    restore_recorded()


def _sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def _recorded():
    """{path relative to this folder: sha256} for every image whose exact bytes a provenance
    record lists: the course notebook's experiments, the material rerun, the denoising run."""
    rec = {}
    pairs = (("src", "png_sha256"), ("original", "original_sha256"), ("file", "png_sha256"), ("file", "sha256"))
    for prov in glob.glob(os.path.join(ROOT, "assets", "generative", "**", "provenance.json"), recursive=True):
        folder = os.path.dirname(prov)
        try:
            stack = [json.load(open(prov, encoding="utf-8"))]
        except (OSError, ValueError):
            continue
        while stack:
            o = stack.pop()
            if isinstance(o, dict):
                for pk, hk in pairs:
                    p, h = o.get(pk), o.get(hk)
                    if isinstance(p, str) and isinstance(h, str) and len(h) == 64:
                        full = (os.path.join(ROOT, *p.split("/")) if p.startswith("assets/")
                                else os.path.join(folder, *p.split("/")))
                        rec[os.path.relpath(full, ROOT).replace(os.sep, "/")] = h
                stack.extend(o.values())
            elif isinstance(o, list):
                stack.extend(o)
    return rec


def restore_recorded():
    """The experiment images are evidence: their provenance records list each file's exact
    bytes, and the tests check them. If a copy here differs (a tool that added metadata on
    the way, say), put back the original from the other parts of the download when an exact
    copy is there. Nothing else is touched."""
    import zipfile
    rec = _recorded()
    bad = {}
    for rel, h in rec.items():
        path = os.path.join(ROOT, *rel.split("/"))
        if os.path.isfile(path) and _sha(path) != h:
            bad[rel] = h
    if not bad:
        return
    zips, roots = _part_sources()
    fixed = 0
    for r in roots:
        for rel in list(bad):
            src = os.path.join(r, *rel.split("/"))
            if os.path.isfile(src) and _sha(src) == bad[rel]:
                shutil.copy2(src, os.path.join(ROOT, *rel.split("/")))
                del bad[rel]; fixed += 1
    for z in zips:
        if not bad:
            break
        try:
            with zipfile.ZipFile(z) as zf:
                for info in zf.infolist():
                    parts = info.filename.replace("\\", "/").split("/")
                    if parts and parts[0].startswith("Prototype_Phase"):
                        parts = parts[1:]
                    rel = "/".join(parts)
                    if rel in bad:
                        data = zf.read(info)
                        if hashlib.sha256(data).hexdigest() == bad[rel]:
                            with open(os.path.join(ROOT, *parts), "wb") as fo:
                                fo.write(data)
                            del bad[rel]; fixed += 1
        except (OSError, zipfile.BadZipFile):
            continue
    if fixed:
        say(f"Put back {fixed} experiment image(s) exactly as recorded, from the other parts of the download.")
    if bad:
        say(f"Note: {len(bad)} experiment image(s) differ from the bytes their provenance record lists,")
        say(f"  for example {next(iter(bad))}. They still show; restore them from the original download.")


def run(cmd, **kw):
    say("> " + " ".join(os.path.relpath(c, ROOT) if os.path.isabs(c) and c.startswith(ROOT) else c for c in cmd))
    return subprocess.run(cmd, cwd=ROOT, **kw).returncode


def selection(args, default_eps=("0.1",), default_mods=("1", "2")):
    """Turn script arguments into a choice of lessons.
    (none)       -> the course introduction and Modules 1 and 2
    all          -> every lesson
    2            -> Module 2          2.4 -> Lesson 2.4 (any mix)
    Returns (episodes, modules, everything, description)."""
    if any(a.lower() == "all" for a in args):
        return [], [], True, "every lesson"
    eps, mods = [], []
    for a in args:
        a = a.strip().lower().lstrip("m")
        if not a:
            continue
        (eps if "." in a else mods).append(a)
    if not eps and not mods:
        eps, mods = list(default_eps), list(default_mods)
    what = ", ".join([f"Lesson {e}" for e in eps] + [f"Module {m}" for m in mods])
    return eps, mods, False, what


def flags(eps, mods):
    return sum((["--episode", e] for e in eps), []) + sum((["--module", m] for m in mods), [])
