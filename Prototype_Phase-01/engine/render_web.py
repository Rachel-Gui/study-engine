"""render_web.py - writes the static site: one HTML page per topic."""
import subprocess, html, io, json, os, re, shutil
import components, figures_lit
from parse import inline

HERE = os.path.dirname(os.path.abspath(__file__))


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:60] or "topic"


def build_site(course, episodes, out):
    """episodes: [(meta, topics, module_dict), ...] in course order."""
    os.makedirs(out, exist_ok=True)
    for old in os.listdir(out):                      # stale pages from a previous
        if old.endswith(".html"):                    # numbering must not survive
            os.remove(os.path.join(out, old))
    shutil.copy(os.path.join(HERE, "theme", "site.js"), os.path.join(out, "site.js"))
    import screens
    with open(os.path.join(HERE, "theme", "site.css"), encoding="utf-8") as f:
        css = f.read()
    with open(os.path.join(out, "site.css"), "w", encoding="utf-8") as f:   # the screen mock-ups share their CSS with the video
        f.write(css + "\n/* ---- software environment mock-ups (engine/screens.py) ---- */\n" + screens.CSS + "\n")
    assets = os.path.normpath(os.path.join(HERE, "..", "assets"))
    if os.path.isdir(assets):
        shutil.copytree(assets, os.path.join(out, "assets"), dirs_exist_ok=True,
                        ignore=lambda directory, names: ["videos"] if directory == assets else [])

    videos = _publish_videos(course, episodes, out)

    # Each module and each episode opens with a generated landing page.
    flat, seen_mod, mi = [], None, -1
    for meta, topics, mod in episodes:
        if mod["title"] != seen_mod:
            seen_mod = mod["title"]; mi += 1
            flat.append({"t": _module_page(mod, episodes, videos), "meta": meta, "mod": mod,
                         "kind": "module", "mi": mi,
                         "path": f"{slug(mod['title'])}.html"})
        flat.append({"t": _episode_page(meta, topics, videos.get(meta["episode"])), "meta": meta, "mod": mod,
                     "kind": "episode", "mi": mi,
                     "path": f"{slug(meta['episode'])}-index.html"})
        for k, t in enumerate(topics, 1):
            flat.append({"t": t, "meta": meta, "mod": mod, "kind": "topic", "mi": mi,
                         "k": k, "nk": len(topics),
                         "path": f"{slug(meta['episode'])}-{slug(t['title'])}.html"})
    for i, p in enumerate(flat):
        p["i"] = i

    for p in flat:                                   # topic pages link to their lesson's video
        if p["kind"] == "topic":
            p["video"] = videos.get(str(p["meta"]["episode"]))
    nav = _nav(flat, bool(videos))
    for p in flat:
        io.open(os.path.join(out, p["path"]), "w", encoding="utf-8").write(
            _page(course, p, flat, nav))

    home = {"t": _home_page(course, flat, bool(videos)), "meta": {}, "mod": {},
            "kind": "home", "mi": -1, "i": -1, "path": "index.html"}
    mods = {"t": _modules_page(course, episodes, flat, videos), "meta": {}, "mod": {},
            "kind": "modules", "mi": -1, "i": -1, "path": "modules.html"}
    io.open(os.path.join(out, "index.html"), "w", encoding="utf-8").write(
        _page(course, home, flat, nav) if flat else "<p>No content.</p>")
    io.open(os.path.join(out, "modules.html"), "w", encoding="utf-8").write(
        _page(course, mods, flat, nav) if flat else "<p>No content.</p>")
    rd = {"t": _readings_page(course), "meta": {}, "mod": {}, "kind": "readings", "mi": -1, "i": -1, "path": "readings.html"}
    io.open(os.path.join(out, "readings.html"), "w", encoding="utf-8").write(
        _page(course, rd, flat, nav) if flat else "<p>No content.</p>")
    vp = {"t": _videos_page(course, episodes, videos), "meta": {}, "mod": {}, "kind": "videos", "mi": -1, "i": -1,
          "path": "videos.html"}
    io.open(os.path.join(out, "videos.html"), "w", encoding="utf-8").write(
        _page(course, vp, flat, nav) if flat else "<p>No content.</p>")
    io.open(os.path.join(out, "search.json"), "w", encoding="utf-8").write(
        json.dumps(_search_index(flat), ensure_ascii=False))
    open(os.path.join(out, ".nojekyll"), "w").close()     # GitHub Pages: serve as-is
    return flat


def _search_index(flat):
    """One entry per page: what the search box looks through."""
    idx = []
    for p in flat:
        if p["kind"] != "module" and _locked(p["mod"]):
            continue
        if p["kind"] == "module":
            text = " ".join(str(p["mod"].get("question", "")).split())
            if _locked(p["mod"]):
                text += " In progress. Lessons temporarily locked while this module is being finalized."
            idx.append({"t": p["mod"]["title"], "e": "", "l": "", "m": p["mod"].get("short") or p["mod"]["title"],
                        "p": p["path"], "x": text, "k": "module"})
            continue
        meta = p["meta"]
        if p["kind"] == "episode":
            text = " ".join(" ".join(str(o) for o in (meta.get("objectives") or [])).split())
            idx.append({"t": meta["title"], "e": meta["episode"], "l": meta["title"],
                        "m": p["mod"].get("short") or p["mod"]["title"], "p": p["path"], "x": text, "k": "lesson"})
            continue
        body = "".join(components.render(b, "web") for b in p["t"]["blocks"])
        body = re.sub(r"<(script|style|svg)\b.*?</\1>", " ", body, flags=re.S | re.I)
        text = html.unescape(re.sub(r"<[^>]+>", " ", body))
        text = re.sub(r"\s+", " ", text).strip()[:1600]
        idx.append({"t": p["t"]["title"], "e": meta["episode"], "l": meta["title"],
                    "m": p["mod"].get("short") or p["mod"]["title"], "p": p["path"], "x": text, "k": "topic"})
    return idx


# ------------------------------------------------------------ landing pages

def _objectives(items, label):
    items = [" ".join(str(x).split()) for x in (items or []) if str(x).strip()]
    if not items:
        return ""
    return (f'<div class="objs"><span class="lbl">{label}</span><ol>'
            + "".join(f"<li>{inline(x)}</li>" for x in items) + "</ol></div>")


def _module_num(mod):
    """'Module 3 — AI-Assisted Coding' -> '3'; anything else -> ''."""
    m = re.match(r"\s*Module\s+(\d+)", mod.get("title", ""))
    return m.group(1) if m else ""


def _locked(mod):
    return bool(mod.get("locked"))


def _status_badge(mod):
    status = str(mod.get("status", "")).strip()
    return f'<span class="status-badge">{html.escape(status)}</span>' if status else ""


def _readings_html(items, label="Selected readings", intro=""):
    """course.yml `readings:` entries (cite, title, venue, doi, why, access) as a reading list."""
    if not items:
        return ""
    lis = ""
    for r in items:
        doi = str(r.get("doi", "")).strip()
        url = r.get("url") or (f"https://doi.org/{doi}" if doi else "")
        link = f'<a href="{html.escape(url)}" target="_blank" rel="noopener">{html.escape(url.split("//")[-1])}</a>' if url else ""
        access = f'<span class="acc">{html.escape(str(r["access"]))}</span>' if r.get("access") else ""
        lis += (f'<li><span class="c">{html.escape(str(r.get("cite", "")))}</span> '
                f'<span class="t">{inline(str(r.get("title", "")))}.</span> <span class="v">{inline(str(r.get("venue", "")))}.</span> {link} {access}'
                + (f'<p>{inline(str(r["why"]))}</p>' if r.get("why") else "") + "</li>")
    return (f'<div class="readings"><div class="lbl">{html.escape(label)}</div>'
            + (f'<p class="intro">{inline(intro)}</p>' if intro else "") + f'<ol>{lis}</ol></div>')


def _module_art(mod):
    num = _module_num(mod)
    key = f"m{num}" if num else ("intro" if "Introduction" in mod.get("title", "") else "ref")
    return figures_lit.ART.get(key, "")


def _module_page(mod, episodes, videos=None):
    eps = [(m, ts) for m, ts, md in episodes if md is mod]
    cards = ""
    for m, ts in eps:
        bits = [x for x in (m.get("duration") and f'{m["duration"]} min',
                            m.get("level"), m.get("kind")) if x]
        tag = "div" if _locked(mod) else "a"
        href = "" if _locked(mod) else f' href="{slug(m["episode"])}-index.html"'
        locked_class = " locked" if _locked(mod) else ""
        cards += (f'<{tag} class="epcard{locked_class}"{href}>'
                  f'<span class="num">{html.escape(m["episode"])}</span>'
                  f'<strong>{html.escape(m["title"])}</strong>'
                  + (f'<span class="meta">Planned lesson</span>' if _locked(mod) else
                     f'<span class="meta">{" &middot; ".join(html.escape(str(b)) for b in bits)}'
                     f' &middot; {len(ts)} topics</span>')
                  + ('<span class="lock-label">Locked</span>' if _locked(mod) else '')
                  + f'</{tag}>')
    q = " ".join(str(mod.get("question", "")).split())
    blocks = []
    art = _module_art(mod)
    if art:
        blocks.append({"kind": "_raw", "attrs": {}, "body": f'<div class="mpic">{art}</div>'})
    if q and not _locked(mod):
        blocks.append({"kind": "_raw", "attrs": {}, "body": f'<p class="lede">{html.escape(q)}</p>'})
    if _locked(mod):
        blocks.append({"kind": "_raw", "attrs": {}, "body":
                       '<div class="lock-panel"><div class="lock-mark" aria-hidden="true"></div>'
                       f'<div>{_status_badge(mod)}<strong>This module is being finalized.</strong>'
                       '<p>Students can see the planned lesson titles, but the lesson pages are temporarily locked. '
                       'Individual lessons will be unlocked as the instructor progresses through the course.</p></div></div>'})
    objs = "" if _locked(mod) else _objectives(mod.get("objectives"), "By the end of this module you will be able to")
    if objs:
        blocks.append({"kind": "_raw", "attrs": {}, "body": objs})
    strip = _module_videos(mod, episodes, videos or {})
    if strip:
        blocks.append({"kind": "_raw", "attrs": {}, "body": strip})
    blocks.append({"kind": "_raw", "attrs": {},
                   "body": f'<span class="lbl sec">Lessons</span><div class="epgrid">{cards}</div>'})
    rd = "" if _locked(mod) else _readings_html(mod.get("readings"), "Selected readings",
                        "Selected papers and reviews; preprints are labelled. Start with the ones marked core; "
                        "the rest are where to go next. Subscription papers are available through UW Libraries.")
    if rd:
        blocks.append({"kind": "_raw", "attrs": {}, "body": rd})
    return {"title": mod["title"], "narration": "", "hero": True, "blocks": blocks}


def _readings_page(course):
    """readings.html - every module's selected readings on one page."""
    body = ('<p class="lede">Selected papers, reviews and surveys, module by module. Preprints are labelled. '
            'Each module page carries the same list next to its lessons; citation details and DOIs were verified in September 2026.</p>')
    for mod in course["modules"]:
        if _locked(mod):
            continue
        items = mod.get("readings")
        if not items:
            continue
        body += f'<h3 class="rdhead">{html.escape(mod["title"])}</h3>' + _readings_html(items, "Selected readings")
    return {"title": "Selected readings", "narration": "", "hero": True,
            "blocks": [{"kind": "_raw", "attrs": {}, "body": body}]}


def _video_slug(meta):
    """The file name make_videos.py gives this lesson's video (without .mp4)."""
    return re.sub(r"[^a-z0-9]+", "-", f'{meta["episode"]}-{meta.get("title", "")}'.lower()).strip("-")[:70] or "video"


def _publish_videos(course, episodes, out):
    """Copy the lesson videos into site/video/ as a 1080p web copy with a poster frame.

    course.yml decides which:   videos: embed: all            every unlocked lesson that has a video
                                videos: embed: ["0.1", "1.2"]  only these
    Committed web copies in assets/videos/ are preferred for deployment.
    Otherwise a video is looked for in dist/video/ (where make_videos.py writes it). Returns
    {episode: info} for the lessons that have one."""
    cfg = (course.get("videos") or {}).get("embed")
    if not cfg:
        return {}
    everything = (isinstance(cfg, str) and cfg.strip().lower() == "all") or \
                 (isinstance(cfg, list) and any(str(e).strip().lower() == "all" for e in cfg))
    want = {str(e).strip() for e in cfg} if isinstance(cfg, list) else set()
    src_dir = os.path.normpath(os.path.join(HERE, "..", "dist", "video"))
    web_dir = os.path.normpath(os.path.join(HERE, "..", "assets", "videos"))
    dst_dir = os.path.join(out, "video")
    ffmpeg = shutil.which("ffmpeg")
    found, missing = {}, []
    for meta, _, mod in episodes:
        ep = str(meta["episode"])
        if (not everything and ep not in want) or _locked(mod):
            continue
        name = _video_slug(meta)
        src = os.path.join(src_dir, name + ".mp4")
        web_src = os.path.join(web_dir, name + ".mp4")
        if os.path.isfile(web_src):
            os.makedirs(dst_dir, exist_ok=True)
            shutil.copy2(web_src, os.path.join(dst_dir, name + ".mp4"))
            web_poster = os.path.join(web_dir, name + ".jpg")
            if os.path.isfile(web_poster):
                shutil.copy2(web_poster, os.path.join(dst_dir, name + ".jpg"))
            src = web_src
        if not os.path.exists(src):
            missing.append(ep if everything else f"{ep} (dist/video/{name}.mp4)")
            continue
        os.makedirs(dst_dir, exist_ok=True)
        dst, poster = os.path.join(dst_dir, name + ".mp4"), os.path.join(dst_dir, name + ".jpg")
        if not os.path.exists(dst) or os.path.getmtime(dst) < os.path.getmtime(src):
            print(f"  preparing the web copy of video {ep} ...", flush=True)
            done = False
            if ffmpeg:          # a 1080p, streamable copy keeps the site small enough for GitHub Pages
                r = subprocess.run([ffmpeg, "-y", "-v", "error", "-i", src, "-vf", "scale=-2:'min(1080,ih)'",
                                    "-c:v", "libx264", "-preset", "faster", "-crf", "22", "-pix_fmt", "yuv420p",
                                    "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", dst],
                                   capture_output=True, text=True)
                done = r.returncode == 0
            if not done:
                shutil.copy2(src, dst)
            if ffmpeg:
                subprocess.run([ffmpeg, "-y", "-v", "error", "-ss", "8", "-i", dst, "-frames:v", "1",
                                "-vf", "scale=1280:-2", poster], capture_output=True)
        dur = ""
        if shutil.which("ffprobe"):
            r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", dst],
                               capture_output=True, text=True)
            try:
                sec = float(r.stdout.strip()); dur = f"{int(sec // 60)}:{int(sec % 60):02d}"
            except ValueError:
                pass
        found[ep] = {"src": f"video/{name}.mp4", "poster": f"video/{name}.jpg" if os.path.exists(poster) else "",
                     "dur": dur, "episode": ep, "title": meta.get("title", ""), "module": mod["title"],
                     "lesson": f"{slug(ep)}-index.html"}
    if missing:
        if everything:
            print("\n  No video rendered yet for: " + ", ".join(missing) +
                  "\n  (VIDEOS-4K renders them; run WEBSITE again afterwards to put them on the site.)")
        else:
            print("\n  VIDEOS NOT EMBEDDED - listed in course.yml but not rendered yet:\n    "
                  + "\n    ".join(missing) + "\n    Render them (VIDEOS-4K), then run WEBSITE again.")
    if found:
        print(f"\n  {len(found)} lesson video(s) on the site: " + ", ".join(found))
    return found


def _video_html(v, title):
    poster = f' poster="{html.escape(v["poster"])}"' if v.get("poster") else ""
    dur = f' &middot; {html.escape(v["dur"])}' if v.get("dur") else ""
    return (f'<figure class="lesson-video" id="video">'
            f'<figcaption><span class="lbl">&#9654; Lesson video</span>{html.escape(title)}{dur}'
            f'<a class="allv" href="videos.html#v-{slug(v["episode"])}">All lesson videos &rarr;</a></figcaption>'
            f'<div class="vwrap"><video controls preload="metadata" playsinline{poster}>'
            f'<source src="{html.escape(v["src"])}" type="video/mp4">'
            f'Your browser cannot play this video. <a href="{html.escape(v["src"])}">Download it</a>.</video>'
            f'<button class="vplay" type="button" aria-label="Play the lesson video"></button></div></figure>')


def _video_card(v, lesson_link=True):
    poster = f' poster="{html.escape(v["poster"])}"' if v.get("poster") else ""
    dur = f'<span class="dur">{html.escape(v["dur"])}</span>' if v.get("dur") else ""
    link = (f'<a class="open" href="{v["lesson"]}">Open the lesson &rarr;</a>' if lesson_link else "")
    return (f'<figure class="vcard" id="v-{slug(v["episode"])}"><div class="vframe vwrap">'
            f'<video controls preload="none" playsinline{poster}><source src="{html.escape(v["src"])}" type="video/mp4">'
            f'<a href="{html.escape(v["src"])}">Download the video</a></video>'
            f'<button class="vplay" type="button" aria-label="Play the video"></button></div>'
            f'<figcaption><span class="n">{html.escape(v["episode"])}</span>'
            f'<span class="t">{html.escape(v["title"])}</span>{dur}{link}</figcaption></figure>')


def _videos_page(course, episodes, videos):
    """videos.html - every lesson video, module by module, each one playable in place."""
    body, seen = "", []
    for meta, _, mod in episodes:
        if id(mod) in seen:
            continue
        seen.append(id(mod))
        vs = [videos[str(m["episode"])] for m, _, md in episodes if md is mod and str(m["episode"]) in videos]
        if not vs:
            continue
        mins = sum(int(v["dur"].split(":")[0]) * 60 + int(v["dur"].split(":")[1]) for v in vs if v.get("dur")) // 60
        body += (f'<div class="vmod"><h3 class="rdhead">{html.escape(mod["title"])}'
                 f'<span class="vmeta">{len(vs)} video{"s" if len(vs) != 1 else ""}'
                 + (f' &middot; {mins} min' if mins else "") + '</span></h3>'
                 f'<div class="vid-grid">{"".join(_video_card(v) for v in vs)}</div></div>')
    if not body:
        body = ('<p class="lede">The lesson videos appear here once they have been rendered. '
                'Each lesson page will show its video at the top as well.</p>')
    lede = ('<p class="lede">Every lesson has a narrated, animated video that walks through it. Watch one here, '
            'or open its lesson: the same video plays at the top of the lesson, next to the labs it points to.</p>')
    return {"title": "Lesson videos", "narration": "", "hero": True,
            "blocks": [{"kind": "_raw", "attrs": {}, "body": lede + body}]}


def _module_videos(mod, episodes, videos):
    """A strip of the module's lesson videos for its landing page."""
    vs = [videos[str(m["episode"])] for m, _, md in episodes if md is mod and str(m["episode"]) in videos]
    if not vs or _locked(mod):
        return ""
    tiles = "".join(
        f'<a class="vtile" href="videos.html#v-{slug(v["episode"])}">'
        + (f'<img src="{html.escape(v["poster"])}" alt="" loading="lazy">' if v.get("poster") else '<span class="noposter"></span>')
        + f'<span class="play" aria-hidden="true"></span><span class="cap"><b>{html.escape(v["episode"])}</b>'
          f'{html.escape(v["title"])}' + (f'<i>{html.escape(v["dur"])}</i>' if v.get("dur") else "") + '</span></a>'
        for v in vs)
    return f'<span class="lbl sec">Lesson videos</span><div class="vstrip">{tiles}</div>'


def _episode_page(meta, topics, video=None):
    items = "".join(
        f'<li><a href="{slug(meta["episode"])}-{slug(t["title"])}.html">{html.escape(t["title"])}</a>'
        + ('<span class="v">narrated</span>' if t.get("narration") else "") + "</li>"
        for t in topics)
    blocks = []
    if video:
        blocks.append({"kind": "_raw", "attrs": {}, "body": _video_html(video, meta.get("title", ""))})
    objs = _objectives(meta.get("objectives"), "In this lesson you will")
    if objs:
        blocks.append({"kind": "_raw", "attrs": {}, "body": objs})
    blocks.append({"kind": "_raw", "attrs": {},
                   "body": f'<span class="lbl sec">Topics</span><ol class="toclist">{items}</ol>'})
    return {"title": f'{meta["episode"]} — {meta["title"]}', "narration": "",
            "hero": True, "blocks": blocks}


# one line icon per module on the landing page (24x24 viewBox, stroke only)
_ICONS = {
    "0": '<path d="M4 6h16M4 12h16M4 18h10"/>',
    "1": '<path d="M8 6l-5 6 5 6M16 6l5 6-5 6M13 4l-2 16"/>',
    "2": '<path d="M12 3v4M12 17v4M3 12h4M17 12h4M5.6 5.6l2.8 2.8M15.6 15.6l2.8 2.8M18.4 5.6l-2.8 2.8M8.4 15.6l-2.8 2.8"/><circle cx="12" cy="12" r="3"/>',
    "3": '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M7 9l3 3-3 3M12 15h5"/>',
    "4": '<circle cx="6" cy="6" r="2.5"/><circle cx="18" cy="6" r="2.5"/><circle cx="12" cy="18" r="2.5"/><path d="M8 7.5l2.8 8M16 7.5l-2.8 8M8.5 6h7"/>',
    "5": '<path d="M3 20h18M6 17V9M11 17V5M16 17v-7M21 17v-4"/>',
    "6": '<path d="M3 20h18M3 20V4"/><circle cx="8" cy="14" r="1.3"/><circle cx="11" cy="10" r="1.3"/><circle cx="15" cy="11" r="1.3"/><circle cx="18" cy="6" r="1.3"/><path d="M5 17L20 5" stroke-dasharray="2 2"/>',
    "7": '<circle cx="5" cy="7" r="2"/><circle cx="5" cy="17" r="2"/><circle cx="12" cy="12" r="2.5"/><circle cx="19" cy="12" r="2"/><path d="M7 8l3 3M7 16l3-3M14.5 12h2.5"/>',
    "8": '<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/><path d="M10 6.5h4M6.5 10v4M17.5 10v4M10 17.5h4"/>',
    "ref": '<path d="M4 4h12l4 4v12H4z"/><path d="M8 12h8M8 16h8"/>',
}


def _icon(key):
    return (f'<svg class="mico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{_ICONS.get(key, _ICONS["ref"])}</svg>')


def _home_page(course, flat, has_videos=False):
    """The landing page: the course, one button (and the videos, once there are any)."""
    ins = course["instructor"]
    hero = (f'<div class="land-hero"><span class="eyebrow">{html.escape(course["code"])}</span>'
            f'<span class="land-title">{html.escape(course["title"])}</span>'
            f'<p class="tag">{html.escape(course.get("subtitle", ""))}</p>'
            f'<div class="land-cta"><a class="btn primary" href="modules.html">Start the course</a>'
            + ('<a class="btn ghost vids" href="videos.html"><span class="pl" aria-hidden="true"></span>Watch the lesson videos</a>'
               if has_videos else '') +
            f'<a class="btn ghost" id="resume" href="{flat[0]["path"]}" hidden>'
            f'Continue <span id="resume-t"></span></a></div>'
            f'<div class="land-who"><span class="lbl">Course instructor</span>'
            f'<b>{html.escape(ins["name"])}</b><span>{html.escape(ins["role"])} &middot; '
            f'{html.escape(ins["dept"])}</span></div></div>')
    return {"title": course["title"], "narration": "", "hero": True,
            "blocks": [{"kind": "_raw", "attrs": {}, "body": hero}]}


def _modules_page(course, episodes, flat, videos=None):
    """Every module as a block, so a student can jump straight in."""
    mods, seen = [], []
    for meta, topics, mod in episodes:
        if id(mod) not in seen:
            seen.append(id(mod)); mods.append(mod)
    cards = ""
    for mod in mods:
        eps = [(m, ts) for m, ts, md in episodes if md is mod]
        first = next(p for p in flat if p["kind"] == "module" and p["mod"] is mod)
        num = _module_num(mod)
        mins = sum(int(m.get("duration") or 0) for m, _ in eps)
        q = " ".join(str(mod.get("question", "")).split())
        short = mod.get("short") or mod["title"]
        kind = "intro" if not num and "Introduction" in mod["title"] else ("ref" if not num else "mod")
        if _locked(mod):
            lessons = "".join(f'<li><span class="locked-lesson"><span>{html.escape(m["episode"])}</span>'
                              f'{html.escape(m["title"])}<b>Locked</b></span></li>' for m, _ in eps)
        else:
            lessons = "".join(f'<li><a href="{slug(m["episode"])}-index.html"><span>{html.escape(m["episode"])}</span>'
                              f'{html.escape(m["title"])}'
                              + ('<i class="hasvid" title="Has a lesson video">video</i>' if str(m["episode"]) in (videos or {}) else '')
                              + '</a></li>' for m, _ in eps)
        cards += (f'<div class="mcard {kind}{" locked" if _locked(mod) else ""}">'
                  f'<a class="mhead" href="{first["path"]}">'
                  f'<span class="mart">{_module_art(mod)}</span>'
                  f'<span class="mnum">{_icon(num or ("0" if kind == "intro" else "ref"))}'
                  f'{("Module " + num) if num else html.escape(short)}</span>{_status_badge(mod)}'
                  f'<strong>{html.escape(short if num else mod["title"])}</strong>'
                  + (f'<span class="mq">{html.escape(q)}</span>' if q and not _locked(mod) else "")
                  + f'<span class="mmeta">{len(eps)} lesson{"s" if len(eps) != 1 else ""}'
                  + (f' &middot; ~{mins} min' if mins else "") + '</span>'
                  f'<span class="go">{"View status" if _locked(mod) else "Open"}<i>&rarr;</i></span></a>'
                  f'<details class="mless"><summary>Lessons</summary><ul>{lessons}</ul></details></div>')
    howto = ('<span class="lbl sec">How to use the Study Engine</span><div class="cards howto">'
             '<div class="card"><strong>Jump in anywhere</strong><span>Open any module below. Inside a module the contents panel on the left lists every lesson and topic, and the arrows at the bottom of each page (or the &larr; &rarr; keys) walk the course in order.</span></div>'
             '<div class="card"><strong>Run the labs</strong><span>Grey code boxes run Python in your browser: press Run step, change a number, run it again. Nothing to install.</span></div>'
             '<div class="card"><strong>Predict before you reveal</strong><span>Try / Predict cards ask you to commit to an answer first. Every option gets feedback; the wrong ones are the useful ones.</span></div>'
             '<div class="card"><strong>Search, or watch</strong><span>The search box at the top finds any topic, lab or term. Each lesson also has its own narrated, animated video.</span></div>'
             '<a class="card link" href="readings.html"><strong>Selected readings &rarr;</strong><span>Papers and reviews for each module, with DOIs and labelled preprints, on one page.</span></a>'
             + ('<a class="card link" href="videos.html"><strong>Lesson videos &rarr;</strong><span>Every narrated lesson video, module by module, playable on one page.</span></a>'
                if videos else '')
             + '</div>')
    return {"title": "Modules", "narration": "", "hero": True, "blocks": [
        {"kind": "_raw", "attrs": {}, "body": f'<p class="lede modlede">{html.escape(course.get("subtitle", ""))}</p>'},
        {"kind": "_raw", "attrs": {}, "body": f'<div class="mgrid">{cards}</div>'},
        {"kind": "_raw", "attrs": {}, "body": howto}]}


# ---------------------------------------------------------------- contents

def _nav(flat, has_videos=False):
    """Modules and lessons both collapse. The chevron toggles, the name navigates."""
    first = ['<a class="home" href="modules.html"><span class="mn">&#8962;</span>All modules</a>',
             '<a class="home rd" href="readings.html"><span class="mn">&#9782;</span>Selected readings</a>']
    if has_videos:
        first.append('<a class="home rd vd" href="videos.html"><span class="mn">&#9654;</span>Lesson videos</a>')
    out, open_m, open_e = first, False, False
    for p in flat:
        if p["kind"] == "module":
            if open_e: out.append("</div></div></div>"); open_e = False
            if open_m: out.append("</div></div></div>"); open_m = False
            num = _module_num(p["mod"])
            label = (f'<span class="mn">{num}</span>{html.escape(p["mod"].get("short") or p["mod"]["title"])}'
                     if num else html.escape(p["mod"].get("short") or p["mod"]["title"]))
            label += _status_badge(p["mod"])
            out.append(f'<div class="m" data-m="{p["mi"]}">'
                       f'<div class="mh"><a class="mod" data-i="{p["i"]}" data-m="{p["mi"]}" '
                       f'href="{p["path"]}" title="{html.escape(p["mod"]["title"])}">{label}</a>'
                       f'<button class="tg" aria-label="Expand module"></button></div>'
                       f'<div class="ml"><div class="in">')
            open_m = True
        elif p["kind"] == "episode":
            if open_e: out.append("</div></div></div>"); open_e = False
            ep = html.escape(p["meta"]["episode"])
            ep_tag = "span" if _locked(p["mod"]) else "a"
            ep_href = "" if _locked(p["mod"]) else f' href="{p["path"]}"'
            lock_class = " locked" if _locked(p["mod"]) else ""
            out.append(f'<div class="e{lock_class}" data-ep="{ep}" data-m="{p["mi"]}">'
                       f'<div class="eh"><{ep_tag} class="ep{lock_class}" data-i="{p["i"]}" data-ep="{ep}" '
                       f'data-m="{p["mi"]}"{ep_href}>'
                       f'<span class="n">{ep}</span>{html.escape(p["meta"]["title"])}</{ep_tag}>'
                       + ('' if _locked(p["mod"]) else '<button class="tg" aria-label="Expand lesson"></button>') + '</div>'
                       f'<div class="tl"><div class="in">')
            open_e = True
        else:
            if not _locked(p["mod"]):
                out.append(f'<a class="tp" data-i="{p["i"]}" '
                           f'data-ep="{html.escape(p["meta"]["episode"])}" data-m="{p["mi"]}" '
                           f'href="{p["path"]}">{html.escape(p["t"]["title"])}</a>')
    if open_e: out.append("</div></div></div>")
    if open_m: out.append("</div></div></div>")
    return "".join(out)


# -------------------------------------------------------------------- page

def _scope_svg_markers(body):
    """Scope reusable figures' arrow markers without changing interactive IDs."""
    # Process nested pictograms before their containing figure. A flat SVG regex
    # would give both levels the same marker IDs.
    stack, replacements = [], []
    for tag in re.finditer(r'<svg\b[^>]*>|</svg\s*>', body):
        if not tag[0].startswith('</'):
            stack.append((tag.start(), []))
            continue
        if not stack:
            continue
        start, children = stack.pop()
        svg = body[start:tag.end()]
        for a, b, child in reversed(children):
            svg = svg[:a - start] + child + svg[b - start:]
        for marker in re.findall(r'<marker\b[^>]*\bid="([^"]+)"', svg):
            if marker.startswith("figure-"):
                continue  # already scoped inside a nested SVG
            scoped = f"figure-{start}-{marker}"
            svg = re.sub(r'(<marker\b[^>]*\bid=")' + re.escape(marker) + r'(")',
                         lambda m: m[1] + scoped + m[2], svg)
            svg = svg.replace(f"url(#{marker})", f"url(#{scoped})")
        (stack[-1][1] if stack else replacements).append((start, tag.end(), svg))
    for start, end, svg in reversed(replacements):
        body = body[:start] + svg + body[end:]
    return body


def _page(course, p, flat, nav):
    t, meta, mod = p["t"], p["meta"], p["mod"]
    is_locked_content = p["kind"] in ("episode", "topic") and _locked(mod)
    if is_locked_content:
        body = ('<div class="lock-panel direct"><div class="lock-mark" aria-hidden="true"></div><div>'
                f'{_status_badge(mod)}<strong>This lesson is temporarily locked.</strong>'
                '<p>This content is still being finalized and will be unlocked as the instructor progresses through the course. '
                'Return to the module page to view its status and planned lessons.</p>'
                f'<a class="btn" href="{slug(mod["title"])}.html">Back to Module {_module_num(mod)}</a>'
                '</div></div>')
    else:
        body = "".join(components.render(b, "web") for b in t["blocks"])
    body = _scope_svg_markers(body)

    # breadcrumb + lesson meta strip
    head = ""
    if p["kind"] == "topic":
        vlink = (f'<a class="vlink" href="{slug(meta["episode"])}-index.html#video"><span class="pl" aria-hidden="true"></span>'
                 f'Lesson video' + (f' &middot; {html.escape(p["video"]["dur"])}' if p["video"].get("dur") else "") + '</a>'
                 if p.get("video") else "")
        head = (f'<div class="crumb"><a href="{slug(mod["title"])}.html">'
                f'{html.escape(mod["title"])}</a><span>&middot;</span>'
                f'<a href="{slug(meta["episode"])}-index.html">{html.escape(meta["episode"])} '
                f'&mdash; {html.escape(meta["title"])}</a>{vlink}'
                f'<span class="k"><span class="seg">'
                + "".join(f'<i class="{"done" if j < p["k"] else ""}{" cur" if j == p["k"] else ""}"></i>' for j in range(1, p["nk"] + 1))
                + f'</span>{p["k"]} of {p["nk"]}</span></div>')
    elif p["kind"] == "episode":
        bits = [x for x in (meta.get("duration") and f'{meta["duration"]} min',
                            meta.get("level"), meta.get("kind")) if x]
        head = (f'<div class="crumb"><a href="{slug(mod["title"])}.html">'
                f'{html.escape(mod["title"])}</a></div>'
                f'<div class="epmeta">{" &middot; ".join(html.escape(str(b)) for b in bits)}</div>')
    elif p["kind"] == "module":
        head = f'<div class="epmeta">Module</div>'
    elif p["kind"] in ("home", "modules", "readings", "videos"):
        head = ""

    all_mods = {"kind": "modules", "path": "modules.html", "t": {"title": "All modules"}, "mod": {}}
    if p["kind"] == "home":
        prev, nxt = None, None
    elif p["kind"] == "modules":
        prev, nxt = None, flat[0]
    elif p["kind"] in ("readings", "videos"):
        prev, nxt = all_mods, None
    else:
        available = [q for q in flat if q["kind"] == "module" or not _locked(q["mod"])]
        if is_locked_content:
            prev = next((q for q in flat if q["kind"] == "module" and q["mod"] is mod), all_mods)
            nxt = None
        else:
            pos = available.index(p)
            prev = available[pos - 1] if pos > 0 else all_mods
            nxt = available[pos + 1] if pos < len(available) - 1 else None
    ins = course["instructor"]
    hero = " hero" if t.get("hero") else ""

    def btn(q, arrow_left):
        if not q:
            return f'<span class="btn off">{"&larr;" if arrow_left else "&rarr;"}</span>'
        title = q["t"]["title"] if q["kind"] in ("topic", "episode", "modules") else q["mod"]["title"]
        lab = "Previous" if arrow_left else "Next"
        inner = (f'<span class="ar">&larr;</span><span class="tx"><small>{lab}</small>'
                 f'{html.escape(title)}</span>' if arrow_left else
                 f'<span class="tx"><small>{lab}</small>{html.escape(title)}</span>'
                 f'<span class="ar">&rarr;</span>')
        return f'<a class="btn {"prev" if arrow_left else "next"}" href="{q["path"]}">{inner}</a>'

    body_cls = f' class="{p["kind"]}"'
    search = ('<form class="search" role="search" autocomplete="off">'
              '<input type="search" id="q" placeholder="Search the course" aria-label="Search the course">'
              '<kbd>/</kbd><div id="hits" hidden></div></form>')

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(t['title'])} &middot; {html.escape(course['code'])}</title>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,300..700;1,300..500&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="site.css">
</head><body{body_cls} data-pyodide="{course.get('pyodide_url','')}">
<div class="readbar"><i id="readbar"></i></div>
<header>
  <div><div class="code">{html.escape(course['code'])}</div>
       <h1><a href="index.html">{html.escape(course['title'])}</a></h1></div>
  {search}
  <button id="navbtn" aria-label="Contents">Contents</button>
</header>
<main>
  <nav id="nav">{nav}
    <div class="who">
      <div class="lbl">Course instructor</div>
      <b>{html.escape(ins['name'])}</b>
      <span>{html.escape(ins['role'])}</span>
      <span>{html.escape(ins['dept'])}</span>
      <a href="mailto:{ins['email']}">{html.escape(ins['email'])}</a>
    </div>
  </nav>
  <section id="stage">
    <article class="page{hero}">
      {head}
      <h2>{html.escape(t['title'])}</h2>
      {body}
    </article>
  </section>
</main>
<footer>
  {btn(prev, True)}
  <span class="count"></span>
  {btn(nxt, False)}
</footer>
<script src="site.js"></script>
<script>markCurrent({p['i']});</script>
</body></html>"""
