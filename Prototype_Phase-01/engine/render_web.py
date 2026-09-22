"""render_web.py - writes the static site: one HTML page per topic."""
import html, io, os, re, shutil
import components
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
    for f in ("site.css", "site.js"):
        shutil.copy(os.path.join(HERE, "theme", f), os.path.join(out, f))
    assets = os.path.normpath(os.path.join(HERE, "..", "assets"))
    if os.path.isdir(assets):
        shutil.copytree(assets, os.path.join(out, "assets"), dirs_exist_ok=True)

    # Each module and each episode opens with a generated landing page.
    flat, seen_mod, mi = [], None, -1
    for meta, topics, mod in episodes:
        if mod["title"] != seen_mod:
            seen_mod = mod["title"]; mi += 1
            flat.append({"t": _module_page(mod, episodes), "meta": meta, "mod": mod,
                         "kind": "module", "mi": mi,
                         "path": f"{slug(mod['title'])}.html"})
        flat.append({"t": _episode_page(meta, topics), "meta": meta, "mod": mod,
                     "kind": "episode", "mi": mi,
                     "path": f"{slug(meta['episode'])}-index.html"})
        for k, t in enumerate(topics, 1):
            flat.append({"t": t, "meta": meta, "mod": mod, "kind": "topic", "mi": mi,
                         "k": k, "nk": len(topics),
                         "path": f"{slug(meta['episode'])}-{slug(t['title'])}.html"})
    for i, p in enumerate(flat):
        p["i"] = i

    nav = _nav(flat)
    for p in flat:
        io.open(os.path.join(out, p["path"]), "w", encoding="utf-8").write(
            _page(course, p, flat, nav))

    io.open(os.path.join(out, "index.html"), "w", encoding="utf-8").write(
        _redirect(flat[0]["path"]) if flat else "<p>No content.</p>")
    return flat


# ------------------------------------------------------------ landing pages

def _module_page(mod, episodes):
    eps = [(m, ts) for m, ts, md in episodes if md is mod]
    cards = ""
    for m, ts in eps:
        bits = [x for x in (m.get("duration") and f'{m["duration"]} min',
                            m.get("level"), m.get("kind")) if x]
        cards += (f'<a class="epcard" href="{slug(m["episode"])}-index.html">'
                  f'<span class="num">{html.escape(m["episode"])}</span>'
                  f'<strong>{html.escape(m["title"])}</strong>'
                  f'<span class="meta">{" &middot; ".join(html.escape(str(b)) for b in bits)}'
                  f' &middot; {len(ts)} topics</span></a>')
    q = " ".join(str(mod.get("question", "")).split())
    return {"title": mod["title"], "narration": "", "hero": True,
            "blocks": ([{"kind": "_raw", "attrs": {},
                         "body": f'<p class="lede">{html.escape(q)}</p>'}] if q else [])
                      + [{"kind": "_raw", "attrs": {}, "body": f'<div class="epgrid">{cards}</div>'}]}


def _episode_page(meta, topics):
    items = "".join(
        f'<li><a href="{slug(meta["episode"])}-{slug(t["title"])}.html">{html.escape(t["title"])}</a>'
        + ('<span class="v">narrated</span>' if t.get("narration") else "") + "</li>"
        for t in topics)
    return {"title": f'{meta["episode"]} — {meta["title"]}', "narration": "",
            "hero": True, "blocks": [
                {"kind": "_raw", "attrs": {}, "body": f'<ol class="toclist">{items}</ol>'}]}


# ---------------------------------------------------------------- contents

def _nav(flat):
    """Modules and lessons both collapse. The chevron toggles, the name navigates."""
    out, open_m, open_e = [], False, False
    for p in flat:
        if p["kind"] == "module":
            if open_e: out.append("</div></div></div>"); open_e = False
            if open_m: out.append("</div></div></div>"); open_m = False
            out.append(f'<div class="m" data-m="{p["mi"]}">'
                       f'<div class="mh"><a class="mod" data-i="{p["i"]}" data-m="{p["mi"]}" '
                       f'href="{p["path"]}">{html.escape(p["mod"]["title"])}</a>'
                       f'<button class="tg" aria-label="Expand module"></button></div>'
                       f'<div class="ml"><div class="in">')
            open_m = True
        elif p["kind"] == "episode":
            if open_e: out.append("</div></div></div>"); open_e = False
            ep = html.escape(p["meta"]["episode"])
            out.append(f'<div class="e" data-ep="{ep}" data-m="{p["mi"]}">'
                       f'<div class="eh"><a class="ep" data-i="{p["i"]}" data-ep="{ep}" '
                       f'data-m="{p["mi"]}" href="{p["path"]}">'
                       f'<span class="n">{ep}</span>{html.escape(p["meta"]["title"])}</a>'
                       f'<button class="tg" aria-label="Expand lesson"></button></div>'
                       f'<div class="tl"><div class="in">')
            open_e = True
        else:
            out.append(f'<a class="tp" data-i="{p["i"]}" '
                       f'data-ep="{html.escape(p["meta"]["episode"])}" data-m="{p["mi"]}" '
                       f'href="{p["path"]}">{html.escape(p["t"]["title"])}</a>')
    if open_e: out.append("</div></div></div>")
    if open_m: out.append("</div></div></div>")
    return "".join(out)


# -------------------------------------------------------------------- page

def _page(course, p, flat, nav):
    t, meta, mod = p["t"], p["meta"], p["mod"]
    body = "".join(components.render(b, "web") for b in t["blocks"])

    # breadcrumb + lesson meta strip
    head = ""
    if p["kind"] == "topic":
        head = (f'<div class="crumb"><a href="{slug(mod["title"])}.html">'
                f'{html.escape(mod["title"])}</a><span>&middot;</span>'
                f'<a href="{slug(meta["episode"])}-index.html">{html.escape(meta["episode"])} '
                f'&mdash; {html.escape(meta["title"])}</a>'
                f'<span class="k">{p["k"]} of {p["nk"]}</span></div>')
    elif p["kind"] == "episode":
        bits = [x for x in (meta.get("duration") and f'{meta["duration"]} min',
                            meta.get("level"), meta.get("kind")) if x]
        head = (f'<div class="crumb"><a href="{slug(mod["title"])}.html">'
                f'{html.escape(mod["title"])}</a></div>'
                f'<div class="epmeta">{" &middot; ".join(html.escape(str(b)) for b in bits)}</div>')
    elif p["kind"] == "module":
        head = f'<div class="epmeta">Module</div>'

    prev = flat[p["i"] - 1] if p["i"] > 0 else None
    nxt = flat[p["i"] + 1] if p["i"] < len(flat) - 1 else None
    ins = course["instructor"]
    hero = " hero" if t.get("hero") else ""

    def btn(q, arrow_left):
        if not q:
            return f'<span class="btn off">{"&larr;" if arrow_left else "&rarr;"}</span>'
        title = q["t"]["title"] if q["kind"] == "topic" else (
            q["t"]["title"] if q["kind"] == "episode" else q["mod"]["title"])
        lab = "Previous" if arrow_left else "Next"
        inner = (f'<span class="ar">&larr;</span><span class="tx"><small>{lab}</small>'
                 f'{html.escape(title)}</span>' if arrow_left else
                 f'<span class="tx"><small>{lab}</small>{html.escape(title)}</span>'
                 f'<span class="ar">&rarr;</span>')
        return f'<a class="btn {"prev" if arrow_left else "next"}" href="{q["path"]}">{inner}</a>'

    lesson_pos = (f'<span class="pos">Topic {p["k"]} of {p["nk"]} in this lesson</span>'
                  if p["kind"] == "topic" else "")

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(t['title'])} &middot; {html.escape(course['code'])}</title>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,300..700;1,300..500&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="site.css">
</head><body data-pyodide="{course.get('pyodide_url','')}">
<div class="readbar"><i id="readbar"></i></div>
<header>
  <div><div class="code">{html.escape(course['code'])}</div>
       <h1>{html.escape(course['title'])}</h1></div>
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
  <span class="count">{lesson_pos}<span class="all">{p['i']+1} / {len(flat)}</span></span>
  {btn(nxt, False)}
</footer>
<script src="site.js"></script>
<script>markCurrent({p['i']});</script>
</body></html>"""


def _redirect(to):
    return (f'<!doctype html><meta charset="utf-8">'
            f'<meta http-equiv="refresh" content="0;url={to}">'
            f'<a href="{to}">Start the course</a>')
