"""
components.py - one entry per :::directive.

Every component has TWO renderers:

    web(block)    -> HTML for the site (may be interactive)
    frame(block)  -> HTML for a 1280x720 video frame (must be static)

That pair is the whole reason one markdown file can produce both outputs.
An interactive widget degrades to a still at its default state; a component
that makes no sense on video returns "" and simply doesn't appear.

To add a component: write web() and frame(), then register it in REGISTRY.
Nothing else in the engine needs to change.
"""
import html, json, re
import figures, widgets
from parse import inline, plain, rows

# --------------------------------------------------------------------- prose


BULLET = re.compile(r"^\s*[-*]\s+(.*)$")
NUMBER = re.compile(r"^\s*\d+[.)]\s+(.*)$")


def _chunks(body):
    """Group lines into ('p'|'ul'|'ol', [lines]) runs."""
    out = []
    for line in body.split("\n"):
        if not line.strip():
            continue
        b, n = BULLET.match(line), NUMBER.match(line)
        # an indented line continues the previous list item rather than
        # starting a new paragraph
        if not b and not n and line[:1].isspace() and out and out[-1][0] in ("ul", "ol"):
            out[-1][1][-1] += " " + line.strip()
            continue
        kind, text = ("ul", b.group(1)) if b else ("ol", n.group(1)) if n else ("p", line)
        if out and out[-1][0] == kind and kind != "p":
            out[-1][1].append(text)
        elif out and out[-1][0] == "p" and kind == "p":
            out[-1][1].append(text)                # wrap continuation lines
        else:
            out.append((kind, [text]))
    return out


def prose_web(b):
    html_out = ""
    for kind, lines in _chunks(b["body"]):
        if kind == "p":
            html_out += f"<p>{inline(' '.join(lines))}</p>"
        else:
            items = "".join(f"<li>{inline(l)}</li>" for l in lines)
            html_out += f"<{kind}>{items}</{kind}>"
    return html_out


def prose_frame(b):
    out = ""
    for kind, lines in _chunks(b["body"]):
        if kind == "p":
            out += f'<p class="f-prose">{html.escape(plain(" ".join(lines)))}</p>'
        else:
            items = "".join(f"<li>{html.escape(plain(l))}</li>" for l in lines)
            out += f'<ul class="f-list">{items}</ul>'
    return out


# ------------------------------------------------------------------- keyidea


def keyidea_web(b):
    return (f'<aside class="keyidea"><span class="lbl">Key idea</span>'
            f'{prose_web(b)}</aside>')


def keyidea_frame(b):
    return (f'<aside class="f-key"><span class="lbl">Key idea</span>'
            f'<p>{html.escape(plain(b["body"]))}</p></aside>')


# -------------------------------------------------------------------- figure


def _svg(b):
    fn = figures.ALL.get(b["attrs"].get("id", ""))
    return fn() if fn else ""


def figure_web(b):
    cap = b["attrs"].get("caption", "")
    c = f'<figcaption>{inline(cap)}</figcaption>' if cap else ""
    return f'<figure class="fig">{_svg(b)}{c}</figure>'


def figure_frame(b):
    return f'<div class="f-fig">{_svg(b)}</div>'


# --------------------------------------------------------------------- pylab
# Runnable Python in the browser via Pyodide. Steps are split on "# step: Title".
# NOTE: Pyodide ships numpy/pandas/scipy/matplotlib/scikit-learn.
# TensorFlow is NOT available and cannot be installed - use sklearn or numpy here.


def _steps(body):
    parts = re.split(r"^# step:\s*(.+)$", body, flags=re.M)
    if len(parts) == 1:
        return [("Run this", body.strip())]
    return [(parts[i].strip(), parts[i + 1].strip()) for i in range(1, len(parts), 2)]


def pylab_web(b):
    steps = _steps(b["body"])
    pkgs = [p.strip() for p in b["attrs"].get("packages", "").split(",") if p.strip()]
    title = b["attrs"].get("title", "Python lab")
    editor_rows = max(4, min(16, int(b["attrs"].get("editor_rows", 16))))
    cards = ""
    for i, (name, code) in enumerate(steps, 1):
        state = "ready" if i == 1 else "locked"
        cards += (
            f'<div class="step" data-step="{i}">'
            f'<div class="hd"><span class="num">{i}</span>'
            f'<span class="nm">{html.escape(name)}</span>'
            f'<span class="state">{state}</span></div>'
            f'<textarea class="src" spellcheck="false" rows="{min(editor_rows, code.count(chr(10)) + 2)}">'
            f'{html.escape(code)}</textarea>'
            f'<div class="act"><button class="run" {"disabled" if i > 1 else ""}>Run step</button>'
            f'<button class="rst">Reset</button></div>'
            f'<div class="out" hidden></div></div>')
    return (f'<div class="pylab" data-packages=\'{json.dumps(pkgs)}\'>'
            f'<div class="bar"><span>Browser Python</span>'
            f'<strong>{html.escape(title)}</strong>'
            f'<span class="boot">Python loads when you run step 1</span></div>'
            f'{cards}</div>')


def pylab_frame(b):
    code = "\n\n".join(c for _, c in _steps(b["body"]))
    return f'<pre class="f-code">{html.escape(code[:1400])}</pre>'


# ---------------------------------------------------------------------- cards
#   Binary | Two possible classes | Review now / monitor


ICONS = {  # small line glyphs, drawn not imported
    0: '<circle cx="9" cy="12" r="5"/><circle cx="19" cy="12" r="5"/>',
    1: '<circle cx="8" cy="8" r="4"/><rect x="14" y="12" width="9" height="9"/>',
    2: '<rect x="4" y="6" width="9" height="9"/><rect x="12" y="12" width="9" height="9"/>',
    3: '<path d="M4,19 L11,12 L18,15 L24,6"/>',
}


def _icon(i):
    return (f'<svg class="ic" viewBox="0 0 28 24" fill="none" stroke="#111" '
            f'stroke-width="1.4">{ICONS.get(i % 4, "")}</svg>')


def cards_web(b):
    r = rows(b["body"], 3)
    return ('<div class="cards">' + "".join(
        f'<div class="card">{_icon(i)}<strong>{inline(a)}</strong>'
        f'<span>{inline(c)}</span><em>{inline(d)}</em></div>'
        for i, (a, c, d) in enumerate(r)) + "</div>")


def cards_frame(b):
    r = rows(b["body"], 3)
    return ('<div class="f-cards">' + "".join(
        f'<div><strong>{html.escape(plain(a))}</strong>'
        f'<span>{html.escape(plain(c))}</span></div>' for a, c, _ in r) + "</div>")


# -------------------------------------------------------------------- compare
#   False positive | Called "sufficient" - actually isn't | Ships into a home...


CMP_IC = ('<svg class="ic" viewBox="0 0 24 24" fill="none" stroke="#111" '
          'stroke-width="1.4"><circle cx="12" cy="12" r="9"/>%s</svg>')


def compare_web(b):
    marks = ['<path d="M9,9 L15,15 M15,9 L9,15"/>', '<path d="M8,12.5 L11,15.5 L16,9"/>']
    return ('<div class="compare">' + "".join(
        f'<div>{CMP_IC % marks[i % 2]}<strong>{inline(a)}</strong>'
        f'<span>{inline(c)}</span><p>{inline(d)}</p></div>'
        for i, (a, c, d) in enumerate(rows(b["body"], 3))) + "</div>")


compare_frame = lambda b: ('<div class="f-cards">' + "".join(
    f'<div><strong>{html.escape(plain(a))}</strong><span>{html.escape(plain(c))}</span></div>'
    for a, c, _ in rows(b["body"], 3)) + "</div>")


# ---------------------------------------------------------------------- stats
#   19735 | ten-minute readings


def stats_web(b):
    return ('<div class="stats">' + "".join(
        f'<div><b>{inline(a)}</b><span>{inline(c)}</span></div>'
        for a, c in rows(b["body"], 2)) + "</div>")


stats_frame = lambda b: ('<div class="f-stats">' + "".join(
    f'<div><b>{html.escape(plain(a))}</b><span>{html.escape(plain(c))}</span></div>'
    for a, c in rows(b["body"], 2)) + "</div>")


# ----------------------------------------------------------------------- flow
#   Load data > Split > Train > Evaluate      (one line, ">" separated)


def _flow(body):
    return [s.strip() for s in body.replace("\n", " ").split(">") if s.strip()]


flow_web = lambda b: ('<div class="flow">' + "".join(
    f"<span>{inline(s)}</span>" for s in _flow(b["body"])) + "</div>")
flow_frame = lambda b: ('<div class="f-flow">' + "".join(
    f"<span>{html.escape(plain(s))}</span>" for s in _flow(b["body"])) + "</div>")


# ------------------------------------------------------------------ resources
#   INTERACTIVE | Title | Source | Description | https://...


def resources_web(b):
    return ('<div class="res">' + "".join(
        f'<a class="r" href="{u}" target="_blank" rel="noopener">'
        f'<span class="k">{html.escape(k)}</span><strong>{inline(t)}</strong>'
        f'<span class="s">{inline(src)}</span><p>{inline(d)}</p></a>'
        for k, t, src, d, u in rows(b["body"], 5)) + "</div>")


resources_frame = lambda b: ""      # link cards are meaningless on video


# ----------------------------------------------------------------------- refs
#   Author (year) | Title. Journal 1, 2-3. | https://doi.org/...


def refs_web(b):
    return ('<ol class="refs">' + "".join(
        f'<li><span class="c">{inline(a)}</span><span>{inline(t)} '
        f'<a href="{u}" target="_blank" rel="noopener">{u.split("//")[-1]}</a></span></li>'
        for a, t, u in rows(b["body"], 3)) + "</ol>")


refs_frame = lambda b: ('<div class="f-refs">' + " &nbsp;·&nbsp; ".join(
    html.escape(plain(a)) for a, _, _ in rows(b["body"], 3)) + "</div>")


# -------------------------------------------------------------------- reflect
#   Question text on the first line, then one option per line prefixed with "-"


def reflect_web(b):
    """Question on line 1, then options prefixed with '-'. Mark the correct one
    with a leading '*' and the card gains a Check answer button."""
    ls = [l.strip() for l in b["body"].split("\n") if l.strip()]
    if not ls:
        return ""
    q, opts, correct = ls[0], [], -1
    for l in ls[1:]:
        if not l.startswith("-"):
            continue
        t = l[1:].strip()
        if t.startswith("*"):
            correct = len(opts); t = t[1:].strip()
        opts.append(t)
    name = f"r{abs(hash(q)) % 100000}"
    o = "".join(f'<label><input type="radio" name="{name}" value="{i}">'
                f'<span>{inline(x)}</span></label>' for i, x in enumerate(opts))
    check = (f'<button class="chk" data-correct="{correct}">Check answer</button>'
             f'<p class="verdict" hidden></p>') if correct >= 0 else ""
    return (f'<div class="reflect"><p class="q">{inline(q)}</p>{o}{check}'
            f'<textarea placeholder="Your reasoning (stays in this browser)">'
            f'</textarea></div>')


reflect_frame = lambda b: ""        # an exercise is not a video scene


# ---------------------------------------------------------------------- slide
#   :::slide{src=assets/lec9-22.png label="Lecture 9, slide 22" caption="..."}


def slide_web(b):
    a = b["attrs"]
    return (f'<figure class="slide"><figcaption class="lbl">'
            f'{html.escape(a.get("label", ""))}</figcaption>'
            f'<img src="{a.get("src", "")}" alt="{html.escape(a.get("caption", ""))}">'
            f'</figure>')


def slide_frame(b):
    return f'<div class="f-fig"><img src="{b["attrs"].get("src", "")}"></div>'


# --------------------------------------------------------------------- widget
#   :::widget{id=neuron-lab}


def widget_web(b):
    return widgets.web(b["attrs"].get("id", ""))


def widget_frame(b):
    return widgets.frame(b["attrs"].get("id", ""))


# ----------------------------------------------------------------------- deck
#   :::deck{dir=assets/lec-ann count=12 label="Lecture 9"}


def deck_web(b):
    a = b["attrs"]
    n = int(a.get("count", 0) or 0)
    d, label = a.get("dir", "").rstrip("/"), a.get("label", "Slide deck")
    if not n:
        return (f'<div class="deck empty"><div class="lbl">{html.escape(label)}</div>'
                f'<p>No slides yet. Export the deck as numbered PNGs into '
                f'<code>{html.escape(d or "assets/&lt;deck&gt;")}/</code> as '
                f'<code>01.png, 02.png, …</code>, then set '
                f'<code>count=</code> to how many there are.</p></div>')
    imgs = "".join(f'<img src="{d}/{i:02d}.png" alt="Slide {i}" '
                   f'{"" if i == 1 else "hidden"}>' for i in range(1, n + 1))
    return (f'<div class="deck" data-n="{n}"><div class="lbl">{html.escape(label)}</div>'
            f'<div class="stage">{imgs}'
            f'<button class="prev" aria-label="Previous slide">&#8249;</button>'
            f'<button class="next" aria-label="Next slide">&#8250;</button></div>'
            f'<div class="bar"><span class="cnt">Slide <b>1</b> of {n}</span>'
            f'<input type="range" min="1" max="{n}" value="1"></div></div>')


def deck_frame(b):
    d = b["attrs"].get("dir", "").rstrip("/")
    n = int(b["attrs"].get("count", 0) or 0)
    return f'<div class="f-fig"><img src="{d}/01.png"></div>' if n else ""


# ------------------------------------------------------------------- workflow
#   Frame the decision | Define the action, unit, classes and labelling guide.
#   (optional third cell = a runnable snippet revealed by the + toggle)


def workflow_web(b):
    out = ""
    for i, (title, desc, code) in enumerate(rows(b["body"], 3), 1):
        ex = (f'<details><summary>Runnable example</summary>'
              f'<pre>{html.escape(code)}</pre></details>') if code else ""
        out += (f'<div class="wf"><span class="n">{i:02d}</span>'
                f'<strong>{inline(title)}</strong><p>{inline(desc)}</p>{ex}</div>')
    return f'<div class="wfs">{out}</div>'


def workflow_frame(b):
    return ('<div class="f-flow">' + "".join(
        f'<span>{html.escape(plain(t))}</span>' for t, _, _ in rows(b["body"], 3))
        + "</div>")


# -------------------------------------------------------------------- details
#   :::details{summary="Explore the data dictionary"}


def details_web(b):
    return (f'<details class="exp"><summary>'
            f'{html.escape(b["attrs"].get("summary", "More"))}</summary>'
            f'<div>{prose_web(b)}</div></details>')


details_frame = lambda b: ""


# --------------------------------------------------------------- glossarynote


def glossarynote_web(b):
    return ('<aside class="gloss"><span class="ic">AI</span><div>'
            '<strong>Machine learning &amp; AI terms</strong>'
            '<span>Underlined terms are part of the course glossary. Hover, tap, or '
            'press Tab to see a plain-language definition.</span></div></aside>')


glossarynote_frame = lambda b: ""


# ------------------------------------------------------------------------ todo
#   :::todo  - a visible "this section still needs work" marker. Delete the
#   block when the section is done; it is meant to be impossible to miss.


def todo_web(b):
    return (f'<div class="todo"><span class="lbl">Needs work</span>'
            f'{prose_web(b)}</div>')


todo_frame = lambda b: ""


# -------------------------------------------------------------------- registry

REGISTRY = {
    "prose":     (prose_web, prose_frame),
    "_raw":      (lambda b: b["body"], lambda b: ""),
    "keyidea":   (keyidea_web, keyidea_frame),
    "figure":    (figure_web, figure_frame),
    "pylab":     (pylab_web, pylab_frame),
    "cards":     (cards_web, cards_frame),
    "compare":   (compare_web, compare_frame),
    "stats":     (stats_web, stats_frame),
    "flow":      (flow_web, flow_frame),
    "resources": (resources_web, resources_frame),
    "refs":      (refs_web, refs_frame),
    "reflect":   (reflect_web, reflect_frame),
    "slide":         (slide_web, slide_frame),
    "widget":        (widget_web, widget_frame),
    "deck":          (deck_web, deck_frame),
    "workflow":      (workflow_web, workflow_frame),
    "details":       (details_web, details_frame),
    "glossarynote":  (glossarynote_web, glossarynote_frame),
    "todo":          (todo_web, todo_frame),
}


def render(block, mode="web"):
    pair = REGISTRY.get(block["kind"])
    if not pair:
        return f'<!-- unknown component: {block["kind"]} -->'
    return pair[0 if mode == "web" else 1](block)
