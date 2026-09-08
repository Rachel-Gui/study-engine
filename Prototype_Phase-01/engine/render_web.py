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
    for f in ("site.css", "site.js"):
        shutil.copy(os.path.join(HERE, "theme", f), os.path.join(out, f))

    # The sample course opens each module and each episode with a landing page.
    # They are generated, never authored, so nobody has to keep them in sync.
    flat, seen_mod = [], None
    for meta, topics, mod in episodes:
        if mod["title"] != seen_mod:
            seen_mod = mod["title"]
            flat.append({"t": _module_page(mod, episodes), "meta": meta, "mod": mod,
                         "kind": "module",
                         "path": f"{slug(mod['title'])}.html"})
        flat.append({"t": _episode_page(meta, topics), "meta": meta, "mod": mod,
                     "kind": "episode",
                     "path": f"{slug(meta['episode'])}-index.html"})
        for t in topics:
            flat.append({"t": t, "meta": meta, "mod": mod, "kind": "topic",
                         "path": f"{slug(meta['episode'])}-{slug(t['title'])}.html"})
    for i, p in enumerate(flat):
        p["i"] = i

    nav = _nav(episodes, flat)
    for p in flat:
        io.open(os.path.join(out, p["path"]), "w", encoding="utf-8").write(
            _page(course, p, flat, nav))

    io.open(os.path.join(out, "index.html"), "w", encoding="utf-8").write(
        _redirect(flat[0]["path"]) if flat else "<p>No content.</p>")
    return flat


def _module_page(mod, episodes):
    eps = [m for m, _, md in episodes if md is mod]
    items = "".join(f'<li><strong>{html.escape(m["episode"])}</strong> &mdash; '
                    f'{html.escape(m["title"])}</li>' for m in eps)
    q = mod.get("question", "")
    return {"title": mod["title"], "narration": "", "blocks": [
        {"kind": "prose", "attrs": {}, "body": q} if q else
        {"kind": "prose", "attrs": {}, "body": ""},
        {"kind": "_raw", "attrs": {}, "body": f'<ol class="eplist">{items}</ol>'}]}


def _episode_page(meta, topics):
    items = "".join(f'<li>{html.escape(t["title"])}</li>' for t in topics)
    return {"title": f'{meta["episode"]} \u2014 {meta["title"]}', "narration": "",
            "blocks": [
                {"kind": "prose", "attrs": {}, "body": "Topics in this section:"},
                {"kind": "_raw", "attrs": {}, "body": f'<ol class="toclist">{items}</ol>'}]}


def _nav(episodes, flat):
    out = []
    for p in flat:
        if p["kind"] == "module":
            out.append(f'<a class="mod" data-i="{p["i"]}" href="{p["path"]}">'
                       f'{html.escape(p["mod"]["title"])}</a>')
        elif p["kind"] == "episode":
            out.append(f'<a class="ep" data-i="{p["i"]}" '
                       f'data-ep="{html.escape(p["meta"]["episode"])}" '
                       f'href="{p["path"]}">'
                       f'{html.escape(p["meta"]["episode"])} &mdash; '
                       f'{html.escape(p["meta"]["title"])}</a>')
        else:
            out.append(f'<a class="tp" data-i="{p["i"]}" '
                       f'data-ep="{html.escape(p["meta"]["episode"])}" '
                       f'href="{p["path"]}">'
                       f'{html.escape(p["t"]["title"])}</a>')
    return "".join(out)


def _page(course, p, flat, nav):
    t, meta = p["t"], p["meta"]
    body = "".join(components.render(b, "web") for b in t["blocks"])

    head = ""
    if p["kind"] == "episode":
        bits = [x for x in (meta.get("duration") and f'{meta["duration"]} min',
                            meta.get("level"), meta.get("kind")) if x]
        head = (f'<div class="epmeta">{html.escape(meta["episode"])} &middot; '
                f'{" &middot; ".join(html.escape(str(b)) for b in bits)}</div>')

    prev = flat[p["i"] - 1]["path"] if p["i"] > 0 else None
    nxt = flat[p["i"] + 1]["path"] if p["i"] < len(flat) - 1 else None
    ins = course["instructor"]

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(t['title'])} &middot; {html.escape(course['code'])}</title>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,300..700;1,300..500&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="site.css">
</head><body data-pyodide="{course.get('pyodide_url','')}">
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
  <section>
    <article>
      {head}
      <h2>{html.escape(t['title'])}</h2>
      {body}
    </article>
  </section>
</main>
<footer>
  {f'<a class="btn" href="{prev}">&larr;&ensp;Previous</a>' if prev else '<span class="btn off">&larr;&ensp;Previous</span>'}
  <span class="count">Topic {p['i']+1} of {len(flat)}</span>
  {f'<a class="btn" href="{nxt}">Next&ensp;&rarr;</a>' if nxt else '<span class="btn off">Next&ensp;&rarr;</span>'}
</footer>
<script src="site.js"></script>
<script>markCurrent({p['i']});</script>
</body></html>"""


def _redirect(to):
    return (f'<!doctype html><meta charset="utf-8">'
            f'<meta http-equiv="refresh" content="0;url={to}">'
            f'<a href="{to}">Start the course</a>')
