"""figures_lit.py - original diagrams grounded in the course's selected readings,
plus the course map and the module pictograms.

Every figure here is drawn from scratch in the course's visual language. Where a
diagram reorganises the *ideas* of a review paper (its categories, counts or
axes) the footer says "after <authors> (year)"; nothing is traced or copied from
a published figure. Numbers are the papers' own and are quoted with their scope.
"""
from figures_py import HEAD, _t, _m, _box, _arrow, ACC, GOLD

INK2 = "#3a3a3a"


def _lines(x, y, lines, size=11, anchor="middle", weight=400, lh=None, style=""):
    lh = lh or size * 1.32
    return "".join(_t(x, y + i * lh, ln, size, anchor, weight, style) for i, ln in enumerate(lines))


def _chip(x, y, w, text, size=11.5, fill="#fff", stroke="#111", lw=1.2, h=26, weight=500):
    return _box(x, y, w, h, lw=lw, fill=fill, stroke=stroke, rx=13) + _t(x + w / 2, y + h / 2 + size * 0.36, text, size, weight=weight)


def _foot(s, y, text, w=880):
    s += f'<line x1="60" y1="{y}" x2="{w - 60}" y2="{y}" opacity=".22"/>'
    size = 11.5 if len(text) <= 112 else (10.5 if len(text) <= 124 else 9.6)   # keep one line inside the frame
    return s + _t(w / 2, y + 22, text, size, style='opacity=".72"')


# ------------------------------------------------------------------ module art
# Small original pictograms (viewBox 0 0 120 90), one per module. Used on the
# modules page, the course map and the video's module gallery.

_ART_DEFS = ('<defs><marker id="ao" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">'
             '<path d="M0,0 L10,5 L0,10 z" fill="#111" stroke="none"/></marker>'
             '<marker id="ap" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">'
             f'<path d="M0,0 L10,5 L0,10 z" fill="{ACC}" stroke="none"/></marker></defs>')


def _art(body):
    return ('<svg viewBox="0 0 120 90" xmlns="http://www.w3.org/2000/svg" stroke="#111" fill="none" '
            'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">' + _ART_DEFS + body + "</svg>")


ART = {
    "intro": _art('<circle cx="60" cy="45" r="30"/><circle cx="60" cy="45" r="4" fill="#111"/>'
                  f'<path d="M60 15v10M60 65v10M30 45h10M80 45h10"/><path d="M72 33L64 41" stroke="{ACC}" stroke-width="3"/>'
                  f'<path d="M48 57l8-8" stroke="{ACC}" stroke-width="3"/>'),
    "m1": _art('<rect x="14" y="14" width="92" height="62" rx="6"/><path d="M14 28h92"/>'
               f'<path d="M26 44l10 8-10 8" stroke="{ACC}" stroke-width="2.4"/><path d="M42 60h22"/>'
               + _t(84, 60, "{ }", 22, weight=600, style='opacity=".8"')),
    "m2": _art("".join(f'<circle cx="{18 + (i % 4) * 9}" cy="{24 + (i // 4) * 9}" r="{1.2 + ((i * 7) % 5) * 0.55}" fill="#111" stroke="none" opacity="{0.35 + ((i * 3) % 6) * 0.1:.2f}"/>' for i in range(20))
               + f'<path d="M58 45h14" stroke="{ACC}" stroke-width="2.2" marker-end="url(#ap)"/>'
               + '<path d="M78 66V44l16-14 16 14v22z"/><path d="M89 66V54h10v12"/><path d="M100 30v-8h4v12"/>'),
    "m3": _art('<rect x="14" y="14" width="92" height="62" rx="6"/><path d="M14 28h92"/>'
               '<path d="M24 40h34M24 50h22M24 60h28"/>'
               f'<path d="M62 50h30" stroke="{ACC}" stroke-dasharray="3 3" stroke-width="2"/>'
               f'<path d="M84 64l5 5 9-10" stroke="{ACC}" stroke-width="2.6"/>'),
    "m4": _art('<circle cx="24" cy="24" r="9"/><circle cx="96" cy="24" r="9"/><circle cx="24" cy="66" r="9"/><circle cx="96" cy="66" r="9"/>'
               f'<path d="M60 31l14 14-14 14-14-14z" fill="{GOLD}" stroke="{ACC}" stroke-width="2"/>'
               '<path d="M32 30l16 12M88 30L72 42M32 60l16-12M88 60L72 48" marker-end="url(#ao)"/>'),
    "m5": _art('<path d="M16 72h70"/><rect x="22" y="48" width="9" height="24"/><rect x="35" y="32" width="9" height="40"/><rect x="48" y="40" width="9" height="32"/><rect x="61" y="56" width="9" height="16"/>'
               f'<circle cx="88" cy="34" r="12" stroke="{ACC}" stroke-width="2.4"/><path d="M97 43l9 9" stroke="{ACC}" stroke-width="3"/>'),
    "m6": _art('<path d="M16 74V18M16 74h90"/>' + "".join(f'<circle cx="{x}" cy="{y}" r="3" fill="#111" stroke="none"/>' for x, y in [(28, 62), (38, 56), (46, 58), (56, 46), (66, 42), (74, 36), (86, 30)])
               + f'<path d="M22 66L98 26" stroke="{ACC}" stroke-width="2.4"/><circle cx="92" cy="40" r="4" stroke="{ACC}" stroke-width="2" fill="#fff"/>'),
    "m7": _art("".join(f'<circle cx="22" cy="{y}" r="6"/>' for y in (24, 45, 66)) + "".join(f'<circle cx="60" cy="{y}" r="6" fill="{GOLD}"/>' for y in (18, 36, 54, 72))
               + f'<circle cx="98" cy="45" r="7" stroke="{ACC}" stroke-width="2.4"/>'
               + "".join(f'<path d="M28 {y1}L54 {y2}" opacity=".55"/>' for y1 in (24, 45, 66) for y2 in (18, 36, 54, 72))
               + "".join(f'<path d="M66 {y}L91 45" opacity=".55"/>' for y in (18, 36, 54, 72))),
    "m8": _art('<rect x="10" y="22" width="30" height="30"/><path d="M20 22v30M30 22v30M10 32h30M10 42h30"/>'
               '<circle cx="60" cy="26" r="4"/><circle cx="76" cy="40" r="4"/><circle cx="56" cy="50" r="4"/><path d="M63 29l10 8M60 46l13-4"/>'
               f'<path d="M88 60c6-14 12-14 18 0s12 14 18 0" stroke="{ACC}" stroke-width="2.4"/>'
               + _t(60, 76, "&#8706;u/&#8706;t = &#945;&#8706;&#178;u", 10, weight=600)),
    "ref": _art('<rect x="30" y="12" width="60" height="68" rx="4"/><path d="M42 30h36M42 44h36M42 58h24"/>'
                f'<path d="M36 28l3 3 5-6M36 42l3 3 5-6M36 56l3 3 5-6" stroke="{ACC}" stroke-width="2.2"/>'),
}

MODULES = [  # number, key, title, one line
    ("1", "m1", "Coding Foundations", "Python from zero"),
    ("2", "m2", "Generative AI", "generate, control, critique"),
    ("3", "m3", "AI-Assisted Coding", "vibe coding, with judgment"),
    ("4", "m4", "Agentic AI", "plan, use tools, act"),
    ("5", "m5", "Exploratory Data Analysis", "look before you model"),
    ("6", "m6", "Machine Learning", "features, targets, evaluation"),
    ("7", "m7", "Deep Learning Foundations", "neurons, learning, limits"),
    ("8", "m8", "Advanced Deep Learning", "images, graphs, time, physics"),
]


def _art_inline(key, x, y, w=120):
    """Place a pictogram inside a larger SVG (as a nested <svg>)."""
    inner = ART[key].replace('<svg viewBox="0 0 120 90" xmlns="http://www.w3.org/2000/svg"',
                             f'<svg x="{x}" y="{y}" width="{w}" height="{w * 0.75}" viewBox="0 0 120 90"')
    return inner


# ------------------------------------------------------------------ course map
def course_map():
    s = HEAD.format(w=880, h=430)
    tw, th, gx, gy = 196, 168, 12, 22
    for i, (n, key, title, sub) in enumerate(MODULES):
        r, c = divmod(i, 4)
        x, y = 30 + c * (tw + gx), 26 + r * (th + gy)
        s += _box(x, y, tw, th, fill="#fbfbfa", rx=8)
        s += f'<rect x="{x}" y="{y}" width="{tw}" height="4" fill="{ACC}" stroke="none"/>'
        s += _art_inline(key, x + tw / 2 - 45, y + 14, 90)
        s += _t(x + 14, y + 104, f"MODULE {n}", 9.5, anchor="start", weight=700, style=f'fill="{ACC}" letter-spacing="1.6"')
        s += _lines(x + 14, y + 124, [title], 12.5 if len(title) < 24 else 11.5, anchor="start", weight=600)
        s += _t(x + 14, y + 146, sub, 10.5, anchor="start", style='opacity=".68"')
    y = 26 + 2 * (th + gy) - 8
    s += f'<path d="M30 {y}v10h{4 * tw + 3 * gx}v-10" stroke="{ACC}"/>'
    s += _t(30 + (4 * tw + 3 * gx) / 2, y + 30, "Modules 1–4: building and using contemporary AI workflows · Modules 5–8: understanding data-driven AI models", 11.5, weight=500)
    return s + "</svg>"


# ------------------------------------------- generative AI: what the review shows
def genai_review_map():
    """Four questions of Jang, Roh & Lee (2025), redrawn as four lanes."""
    s = HEAD.format(w=880, h=470)
    s += _t(440, 30, "Generative AI in architectural design — what a review of 161 papers (2014–2024) shows", 14, weight=600)
    lanes = [("MODELS", 62), ("DESIGN PHASE", 160), ("DATA", 258), ("EVALUATION", 356)]
    for name, y in lanes:
        s += f'<line x1="40" y1="{y - 12}" x2="840" y2="{y - 12}" opacity=".2"/>'
        s += _t(40, y + 6, name, 9.5, anchor="start", weight=700, style=f'fill="{ACC}" letter-spacing="1.6"')
    # models lane: a timeline of families
    y = 62
    s += f'<line x1="180" y1="{y + 34}" x2="820" y2="{y + 34}" marker-end="url(#ao)"/>'
    fam = [("2017", "CNN", "first use in\narchitecture"), ("most papers", "GAN", "leads the\ncorpus"),
           ("gaining since 2021", "transformer", "reflects intent\nin real time"), ("gaining since 2021", "diffusion", "images from\nnoise")]
    for i, (yr, f, note) in enumerate(fam):
        x = 230 + i * 160
        s += f'<circle cx="{x}" cy="{y + 34}" r="5" fill="{ACC if i else "#111"}" stroke="none"/>'
        s += _t(x, y + 18, f, 12.5, weight=600)
        s += _t(x, y + 54, yr, 10, style='opacity=".65"')
        s += _lines(x, y + 68, note.split("\n"), 9.5, style='opacity=".6"')
    s += _lines(112, y + 30, ["FFNN · CNN · RNN ·", "GAN · transformer ·", "diffusion"], 10, style='opacity=".7"')
    # phase lane: bar
    y = 160
    total = 640
    s += _box(180, y + 8, total, 30, fill="#fff")
    s += f'<rect x="180" y="{y + 8}" width="{total * 0.6894:.0f}" height="30" fill="{GOLD}" stroke="none"/>'
    s += f'<rect x="180" y="{y + 8}" width="{total * 0.6894:.0f}" height="30" fill="none" stroke="{ACC}" stroke-width="1.4"/>'
    s += _t(180 + total * 0.6894 / 2, y + 28, "schematic design · 68.94 % of studies", 12.5, weight=600)
    s += _t(180 + total * 0.6894 + (total - total * 0.6894) / 2, y + 28, "later phases: underexplored", 11, style='opacity=".7"')
    s += _t(180, y + 58, "design development · construction documents · procurement · construction (AIA B101 phases)", 10, anchor="start", style='opacity=".62"')
    s += _lines(112, y + 22, ["where in the", "process?"], 10, style='opacity=".7"')
    # data lane: five types
    y = 258
    types = [("images", "52.8 % of inputs\n68.32 % of outputs", True), ("variables", "numbers, parameters", False),
             ("text", "briefs, prompts", False), ("graphs", "adjacency, topology", False), ("3D models", "meshes, voxels", False)]
    for i, (t, note, hi) in enumerate(types):
        x = 180 + i * 130
        s += _box(x, y + 2, 118, 54, fill=GOLD if hi else "#fff", stroke=ACC if hi else "#111", lw=1.4 if hi else 1.2, rx=6)
        s += _t(x + 59, y + 22, t, 12.5, weight=600)
        s += _lines(x + 59, y + 37, note.split("\n"), 8.8, style='opacity=".75"', lh=11)
    s += _t(180, y + 74, "30 distinct data contents across five types · multimodal and graph data emerging", 10, anchor="start", style='opacity=".62"')
    s += _lines(112, y + 20, ["in and", "out"], 10, style='opacity=".7"')
    # evaluation lane
    y = 356
    ev = [("comparative evaluation", 60.9), ("assessment by the authors", 34.2), ("third-party assessment", 17.4), ("machine-based assessment", None)]
    for i, (t, pct) in enumerate(ev):
        x = 180 + i * 162
        s += _box(x, y + 2, 156, 44, fill="#fff", rx=6)
        s += _t(x + 78, y + 20, t, 10, weight=600)
        s += _t(x + 78, y + 38, f"{pct} % of studies" if pct else "metrics, not judgement", 10, style=f'fill="{ACC}"' if pct else 'opacity=".7"')
    s += _t(180, y + 66, "105 different metrics in use · most evaluation is comparative or the authors' own judgement · third-party review is rare", 10, anchor="start", style='opacity=".62"')
    s += _lines(112, y + 20, ["how is", "'good' judged?"], 10, style='opacity=".7"')
    return _foot(s, 436, "Original diagram after Jang, Roh & Lee (2025), Automation in Construction 174, 106174. The percentages are the review's.") + "</svg>"


# ------------------------------------------------- human–AI collaborative design
def human_ai_collab():
    s = HEAD.format(w=880, h=400)
    s += _t(440, 30, "Human–AI collaboration in conceptual design: who does what, through which medium", 14, weight=600)
    # stage band: divergent -> convergent
    s += _box(60, 56, 760, 46, fill="#fbfbfa", rx=23)
    s += f'<path d="M80 79 L440 79" stroke="{ACC}" stroke-width="2" marker-end="url(#ap)"/>'
    s += f'<path d="M440 79 L800 79" stroke="#111" stroke-width="2" marker-end="url(#ao)"/>'
    s += _t(250, 74, "DIVERGE — widen the options", 11.5, weight=700, style=f'fill="{ACC}" letter-spacing="1"')
    s += _t(620, 74, "CONVERGE — choose and commit", 11.5, weight=700, style='letter-spacing="1"')
    s += _t(250, 94, "many variations, fast · creative expression · divergent thinking", 10, style='opacity=".7"')
    s += _t(620, 94, "evaluation · selection · verification · responsibility", 10, style='opacity=".7"')
    # roles
    s += _t(60, 136, "COLLABORATION MODE", 9.5, anchor="start", weight=700, style=f'fill="{ACC}" letter-spacing="1.6"')
    s += _box(60, 148, 340, 84, fill=GOLD, stroke=ACC, rx=6)
    s += _t(80, 170, "Generative AI", 13, anchor="start", weight=600)
    s += _lines(80, 190, ["proposes variations under a condition — a prompt,", "a sketch, a reference — and knows nothing it was not given"], 10.2, anchor="start", style='opacity=".85"')
    s += _box(480, 148, 340, 84, fill="#fff", rx=6)
    s += _t(500, 170, "Designer", 13, anchor="start", weight=600)
    s += _lines(500, 190, ["frames the question, judges plausibility against evidence,", "selects, verifies, signs — authorship and liability stay here"], 10.2, anchor="start", style='opacity=".85"')
    s += _arrow(404, 186, 476, 186, purple=True)
    s += _t(440, 178, "candidates", 9, style='opacity=".7"')
    s += f'<path d="M476 204 L404 204" marker-end="url(#ao)" stroke-dasharray="4 3"/>'
    s += _t(440, 220, "re-prompt", 9, style='opacity=".7"')
    # media
    s += _t(60, 266, "INTERACTION MEDIA", 9.5, anchor="start", weight=700, style=f'fill="{ACC}" letter-spacing="1.6"')
    media = [("text prompt", "words steer; nothing is enforced"), ("sketch / massing", "the output follows a picture"),
             ("reference image", "material, atmosphere, style"), ("structured data", "room lists, graphs — checkable")]
    for i, (m, note) in enumerate(media):
        x = 60 + i * 192
        s += _box(x, 278, 178, 56, fill="#fff", rx=6)
        s += _t(x + 89, 300, m, 12, weight=600)
        s += _t(x + 89, 320, note, 9.5, style='opacity=".72"')
    s += _t(60, 354, "The further right the medium, the more of the output can be checked — and the more the designer is committing to.", 10.5, anchor="start", style='opacity=".75"')
    return _foot(s, 368, "Original diagram. The three dimensions follow Fang et al. (2025), Design Studies 97, 101300; the responsibility line is the course's.") + "</svg>"


# ------------------------------------------------------- agentic AI framework
def agentic_framework():
    s = HEAD.format(w=880, h=430)
    s += _t(440, 28, "From perception to agency — and how agentic AI is classified in the built environment", 14, weight=600)
    stages = [("Perception AI", "interprets images,\ntext and sound"), ("Generative AI", "creates new\ncontent"),
              ("Agentic AI", "sets goals, reasons,\nuses tools, acts"), ("Physical AI", "agentic cognition\nin robots")]
    for i, (name, note) in enumerate(stages):
        x = 60 + i * 200
        hi = i == 2
        s += _box(x, 48, 170, 62, fill=GOLD if hi else "#fff", stroke=ACC if hi else "#111", lw=1.5 if hi else 1.2, rx=8)
        s += _t(x + 85, 72, name, 13, weight=600)
        s += _lines(x + 85, 88, note.split("\n"), 9.8, style='opacity=".75"', lh=12)
        if i < 3:
            s += _arrow(x + 172, 79, x + 198, 79, purple=True)
    s += _t(440, 130, "\"an autonomous entity that perceives its environment and takes actions to achieve specific objectives\" — the agent, as the review defines it", 10.5, style='opacity=".75"')
    # three classification columns
    cols = [("APPLICATIONS", ["BIM — model from natural language", "Building performance simulation", "Building management systems",
                              "Building digital twins", "Urban-scale planning"]),
            ("FUNCTIONAL ROLES (DIKW)", ["Data — collect, clean", "Information — interpret", "Knowledge — reason, explain",
                                          "Wisdom — support a decision"]),
            ("LEARNING APPROACHES", ["Prompt engineering", "Zero-shot", "Few-shot", "Fine-tuning"])]
    for i, (head, items) in enumerate(cols):
        x = 60 + i * 260
        s += _box(x, 152, 240, 214, fill="#fbfbfa", rx=8)
        s += _t(x + 16, 176, head, 9.5, anchor="start", weight=700, style=f'fill="{ACC}" letter-spacing="1.6"')
        for j, it in enumerate(items):
            y = 200 + j * 30
            if i == 1:
                s += f'<rect x="{x + 16}" y="{y - 12 - j * 3}" width="{12 + j * 8}" height="{14 + j * 3}" fill="{GOLD}" stroke="{ACC}" stroke-width="1"/>'
            s += f'<circle cx="{x + 24}" cy="{y - 3}" r="3" fill="{ACC}" stroke="none"/>' if i != 1 else ""
            s += _t(x + (34 if i != 1 else 62), y, it, 11, anchor="start")
        if i == 1:
            s += _t(x + 16, 340, "from interpreting data to supporting decisions", 9.5, anchor="start", style='opacity=".65"')
        if i == 0:
            s += _t(x + 16, 340, "five representative application areas", 9.5, anchor="start", style='opacity=".65"')
        if i == 2:
            s += _t(x + 16, 340, "chosen by task and by how much data exists", 9.5, anchor="start", style='opacity=".65"')
    s += _t(440, 388, "Agentic built environment: agents embedded across the building lifecycle to interact, collaborate and co-evolve with human stakeholders.", 10.5, weight=500)
    return _foot(s, 400, "Original diagram after Lee et al. (2025), Energy and Buildings 346, 116159: five applications · DIKW roles · four learning approaches.") + "</svg>"


# ------------------------------------------------------------------ ethics map
def ethics_map():
    s = HEAD.format(w=880, h=440)
    s += _t(440, 28, "Nine ethical issues of AI and robotics in AEC — and seven research directions", 14, weight=600)
    groups = [("ABOUT DATA", [("data transparency", 151), ("data privacy", None), ("data security", None)]),
              ("ABOUT PEOPLE", [("acceptance and trust", 140), ("job loss", 126), ("fear of surveillance", 111)]),
              ("ABOUT DECISIONS", [("liability", 124), ("reliability and safety", 116), ("decision-making conflict", None)])]
    for gi, (g, items) in enumerate(groups):
        y0 = 58 + gi * 108
        s += _t(60, y0, g, 9.5, anchor="start", weight=700, style=f'fill="{ACC}" letter-spacing="1.6"')
        for j, (name, n) in enumerate(items):
            y = y0 + 14 + j * 28
            w = 150 + (n or 40) * 1.6
            s += f'<rect x="60" y="{y}" width="{w:.0f}" height="20" fill="{GOLD if n and n >= 140 else "#f3f1ea"}" stroke="#111" stroke-width="1" rx="3"/>'
            s += _t(68, y + 14, name, 11, anchor="start", weight=600)
            s += _t(60 + w + 8, y + 14, f"{n} papers" if n else "fewer papers", 9.5, anchor="start", style='opacity=".62"')
    s += _t(60, 392, "314 AEC papers, 2017 – early 2022, Scopus · design & planning is 24 of them · only 14 treat ethics as their topic", 10, anchor="start", style='opacity=".65"')
    # directions
    s += _box(560, 50, 260, 330, fill="#fbfbfa", rx=8)
    s += _t(576, 74, "SEVEN FUTURE DIRECTIONS", 9.5, anchor="start", weight=700, style=f'fill="{ACC}" letter-spacing="1.6"')
    dirs = ["Human–robot collaboration safety", "Explainable AI", "Trust of AI and robotics", "Cybersecurity",
            "Bias and fairness in decision-making", "A responsibility framework", "AI and robotics standards"]
    for j, d in enumerate(dirs):
        y = 100 + j * 36
        s += f'<circle cx="{588}" cy="{y - 4}" r="3.2" fill="{ACC}" stroke="none"/>'
        s += _t(600, y, d, 11.5, anchor="start")
    s += _t(576, 366, "the review's recommendations, not its findings", 9.5, anchor="start", style='opacity=".62"')
    s += _arrow(520, 214, 556, 214, purple=True)
    return _foot(s, 408, "Original diagram after Liang et al. (2024), Automation in Construction 162, 105369. Counts: papers raising each issue, of 314.") + "</svg>"


# -------------------------------------------------------------- data-centric AI
def data_centric():
    s = HEAD.format(w=880, h=400)
    s += _t(440, 28, "Model-centric or data-centric: where does the effort go before a model is trusted?", 14, weight=600)
    s += _box(60, 48, 360, 78, fill="#fff", rx=8)
    s += _t(80, 72, "Model-centric", 13, anchor="start", weight=600)
    s += _lines(80, 92, ["hold the data fixed, improve the model", "— the reflex most courses teach first"], 10.5, anchor="start", style='opacity=".8"')
    s += _box(460, 48, 360, 78, fill=GOLD, stroke=ACC, rx=8)
    s += _t(480, 72, "Data-centric", 13, anchor="start", weight=600)
    s += _lines(480, 92, ["hold the model fixed, improve the data", "— quality, coverage, documentation, systematically"], 10.5, anchor="start", style='opacity=".85"')
    s += _t(440, 150, "Before modelling, five checks — each has its lesson in Modules 5 and 6:", 11.5, weight=500)
    checks = [("Provenance", "where it came from,\nwhat it was for", "datasheet"),
              ("Distributions", "shape, spread, outliers,\nunits, categories", "histogram"),
              ("Missingness", "how much, and why:\nat random, or not", "MCAR · MAR · MNAR"),
              ("Imbalance", "rare classes; compare\nto the majority baseline", "precision · recall"),
              ("Readiness & leakage", "a sample of the question?\nnothing from the future", "split by building / time")]
    for i, (t, note, tag) in enumerate(checks):
        x = 60 + i * 154
        s += _box(x, 166, 140, 118, fill="#fbfbfa", rx=8)
        s += f'<rect x="{x}" y="166" width="140" height="4" fill="{ACC}" stroke="none"/>'
        s += _t(x + 70, 194, t, 12, weight=600)
        s += _lines(x + 70, 214, note.split("\n"), 9.6, style='opacity=".78"', lh=12)
        s += _t(x + 70, 268, tag, 9.5, weight=600, style=f'fill="{ACC}"')
        if i < 4:
            s += _arrow(x + 142, 225, x + 152, 225)
    s += _t(440, 314, "Data cascades: 92 % of practitioners in one field study had seen upstream data problems surface as compounding downstream failures.", 10.5, style='opacity=".75"')
    s += _t(440, 334, "\"Without good data, even the best machine learning algorithms cannot perform well.\"", 11, weight=500)
    return _foot(s, 358, "Original diagram after Zha et al. (2025), Jakubik et al. (2024), Whang et al. (2023), Sambasivan et al. (2021), Gebru et al. (2021).") + "</svg>"


# ------------------------------------------------- ML across the design process
def ml_design_stages():
    s = HEAD.format(w=880, h=420)
    s += _t(440, 28, "Where machine learning enters the building design process", 14, weight=600)
    x0, x1, y0, y1 = 80, 800, 70, 250
    stages = ["PD", "SD", "DD", "CD", "PR", "CA", "OP"]
    names = ["pre-design", "schematic", "design dev.", "construction docs", "procurement", "construction", "operations"]
    step = (x1 - x0) / 7
    s += f'<line x1="{x0}" y1="{y1}" x2="{x1}" y2="{y1}"/>'
    for i, (st, nm) in enumerate(zip(stages, names)):
        x = x0 + step * (i + 0.5)
        s += f'<line x1="{x0 + step * i}" y1="{y1}" x2="{x0 + step * i}" y2="{y1 + 6}"/>'
        s += _t(x, y1 + 20, st, 11.5, weight=600)
        s += _t(x, y1 + 34, nm, 9.5, style='opacity=".65"')
    # curves: ability to influence (falling), cost of change (rising)
    s += f'<path d="M{x0} {y0 + 10} C {x0 + 200} {y0 + 30}, {x0 + 360} {y1 - 30}, {x1} {y1 - 6}" stroke="#111" stroke-width="1.6"/>'
    s += _t(x0 + 10, y0 + 4, "ability to influence the design", 10, anchor="start", weight=500)
    s += f'<path d="M{x0} {y1 - 6} C {x0 + 360} {y1 - 30}, {x0 + 520} {y0 + 30}, {x1} {y0 + 10}" stroke="#111" stroke-width="1.6" stroke-dasharray="6 4"/>'
    s += _t(x1 - 10, y0 + 4, "cost of a change", 10, anchor="end", weight=500)
    # effort curves
    s += f'<path d="M{x0 + 40} {y1 - 8} C {x0 + 300} {y1 - 10}, {x0 + 330} {y0 + 40}, {x0 + 420} {y0 + 40} S {x0 + 560} {y1 - 10}, {x1 - 20} {y1 - 8}" stroke="#8a8a8a" stroke-width="1.4"/>'
    s += _t(x0 + 430, y0 + 26, "traditional effort", 9.5, style='fill="#6a6a6a"')
    s += f'<path d="M{x0 + 20} {y1 - 8} C {x0 + 120} {y1 - 20}, {x0 + 130} {y0 + 70}, {x0 + 200} {y0 + 70} S {x0 + 330} {y1 - 10}, {x0 + 480} {y1 - 8} L {x1 - 20} {y1 - 8}" stroke="{ACC}" stroke-width="2.2"/>'
    s += _t(x0 + 200, y0 + 40, "ML-driven: decide earlier, with less effort", 10, weight=600, style=f'fill="{ACC}" stroke="#fff" stroke-width="4" paint-order="stroke"')
    # domains as chips placed by stage
    s += _t(60, 312, "FIVE DOMAINS IN 230 REVIEWED PAPERS, PLACED WHERE THEY MOSTLY SIT", 9.5, anchor="start", weight=700, style=f'fill="{ACC}" letter-spacing="1.6"')
    chips = [("building performance · 99", x0 + step * 0.5, 330, 200), ("design generation · 71", x0 + step * 0.9, 362, 170),
             ("design evaluation · 26", x0 + step * 2.8, 330, 160), ("structural design · 20", x0 + step * 3.0, 362, 160),
             ("BIM automation · 14", x0 + step * 4.9, 330, 150)]
    for t, x, y, w in chips:
        s += _chip(x, y, w, t, 10.5, fill=GOLD if "99" in t or "71" in t else "#fff", stroke=ACC if "99" in t or "71" in t else "#111")
    return _foot(s, 396, "Original diagram after Lystbæk (2025), Automation in Construction 178, 106379 (CC BY 4.0): stages, effort curves, five domains.") + "</svg>"


# -------------------------------------------------- physics-informed ML routes
def piml_taxonomy():
    s = HEAD.format(w=880, h=430)
    s += _t(440, 28, "Four ways physics enters a machine-learning model of a building", 14, weight=600)
    cols = [("Physics-informed INPUTS", "simulation results become features;\nmap simulated to observed data first",
             "cheap; useful when measurements are scarce", "redundant features can hurt; simulated ≠ observed", "inputs"),
            ("Physics-informed LOSS", "L = data loss + λ · physics residual\nat collocation points — the PINN route",
             "physically plausible predictions", "a soft penalty: laws only approximately satisfied", "loss"),
            ("Physics-informed ARCHITECTURE", "the network's structure encodes the physics:\ngrey-box, partially connected, neural ODEs",
             "strictly enforces the rule; better extrapolation", "the rules encoded are still simple", "arch"),
            ("Physics-informed ENSEMBLE", "a physics model plus a data model that\nlearns the residual; sub-system to urban scale",
             "high interpretability; each part explains something", "hard to say what each component contributed", "ens")]
    for i, (head, what, buys, costs, key) in enumerate(cols):
        x = 40 + i * 205
        s += _box(x, 50, 190, 300, fill="#fbfbfa", rx=8)
        s += f'<rect x="{x}" y="50" width="190" height="4" fill="{ACC}" stroke="none"/>'
        s += _lines(x + 95, 78, head.split(" ", 1)[0:1] + [head.split(" ", 1)[1]], 11.5, weight=600, lh=15)
        # tiny glyph
        gy = 118
        if key == "inputs":
            s += _box(x + 40, gy, 44, 26, fill="#fff", rx=4) + _t(x + 62, gy + 17, "sim", 10)
            s += _arrow(x + 86, gy + 13, x + 108, gy + 13, purple=True)
            s += _box(x + 110, gy, 44, 26, fill="#fff", rx=4) + _t(x + 132, gy + 17, "ML", 10)
        elif key == "loss":
            s += _box(x + 34, gy, 44, 26, fill="#fff", rx=4) + _t(x + 56, gy + 17, "ML", 10)
            s += _arrow(x + 80, gy + 13, x + 100, gy + 13)
            s += _box(x + 102, gy - 8, 60, 42, fill=GOLD, stroke=ACC, rx=4) + _t(x + 132, gy + 9, "data +", 9.5) + _t(x + 132, gy + 23, "λ·physics", 9.5, weight=600)
        elif key == "arch":
            for k in range(3):
                s += f'<circle cx="{x + 60 + k * 30}" cy="{gy + 13}" r="7" fill="{GOLD if k == 1 else "#fff"}" stroke="{ACC if k == 1 else "#111"}"/>'
            s += f'<path d="M{x + 67} {gy + 13}h16M{x + 97} {gy + 13}h16" stroke="{ACC}"/>'
            s += _t(x + 90, gy + 38, "structure = physics", 9, style='opacity=".7"')
        else:
            s += _box(x + 28, gy, 56, 26, fill="#fff", rx=4) + _t(x + 56, gy + 17, "physics", 10)
            s += _t(x + 98, gy + 18, "+", 14, weight=600)
            s += _box(x + 110, gy, 56, 26, fill=GOLD, stroke=ACC, rx=4) + _t(x + 138, gy + 17, "residual", 10)
        s += _lines(x + 95, 174, _wrap(what.replace("\n", " "), 34), 9.4, style='opacity=".82"', lh=12)
        s += _t(x + 14, 224, "BUYS", 8.5, anchor="start", weight=700, style=f'fill="{ACC}" letter-spacing="1.4"')
        s += _lines(x + 14, 240, _wrap(buys, 30), 9.6, anchor="start", lh=12.5)
        s += _t(x + 14, 280, "COSTS", 8.5, anchor="start", weight=700, style='fill="#8a6b2a" letter-spacing="1.4"')
        s += _lines(x + 14, 296, _wrap(costs, 30), 9.6, anchor="start", lh=12.5)
    s += _t(440, 376, "A pure surrogate — a fast model trained on simulator runs — is a separate thing: nearest the inputs route, valid only inside its sampled range.", 10.2, style='opacity=".75"')
    return _foot(s, 396, "Original diagram after Ma, Jiang, Hu & Chen (2025), Applied Energy 381, 125169: the review's four categories, pros and cons.") + "</svg>"


def _wrap(text, n):
    out, cur = [], ""
    for w in text.split():
        if len(cur) + len(w) + 1 > n and cur:
            out.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        out.append(cur)
    return out


# ------------------------------------------- AI-assisted coding: the loop
def code_comprehension_loop():
    s = HEAD.format(w=880, h=400)
    s += _t(440, 28, "When the assistant writes the code, the work moves to reading, checking and fixing it", 14, weight=600)
    nodes = [("Generate", "the assistant drafts code\nfrom your prompt and context", 134, 130),
             ("Comprehend", "read it; ask for an explanation —\n93 % partly right, 50 % partly wrong", 338, 130),
             ("Verify", "run it on a case you can check\nby hand; compare with expectation", 542, 130),
             ("Debug", "paste the error and the code —\ncontext lifted fixes from 11 % to 78 %", 746, 130)]
    for i, (t, note, x, y) in enumerate(nodes):
        hi = i in (1, 2)
        s += _box(x - 92, y - 34, 184, 92, fill=GOLD if hi else "#fff", stroke=ACC if hi else "#111", lw=1.5 if hi else 1.2, rx=8)
        s += _t(x, y - 8, t, 14, weight=600)
        s += _lines(x, y + 12, note.split("\n"), 9.6, style='opacity=".8"', lh=12.5)
        if i < 3:
            s += _arrow(x + 94, y + 12, x + 110, y + 12, purple=True)
    s += f'<path d="M746 166 C 746 214, 134 214, 134 166" stroke="{ACC}" stroke-dasharray="5 4" marker-end="url(#ap)" fill="none"/>'
    s += _t(440, 226, "re-prompt with what you learned — the loop, not the first answer, is the skill", 10.5, weight=500, style=f'fill="{ACC}"')
    s += _box(60, 248, 760, 78, fill="#fbfbfa", rx=8)
    s += _t(80, 272, "Integrate — only after the loop: into your tool, under your name", 12.5, anchor="start", weight=600)
    s += _lines(80, 292, ["A hybrid workflow with a human reviewer, not an assistant used on its own.",
                          "Speed gains are not learning gains; over-reliance erodes the ability to read code without help."], 10.2, anchor="start", style='opacity=".8"', lh=14)
    s += _t(60, 352, "What GenAI assistants do for comprehension in 31 studies (2022–24): explain software (21) · teach (3) · document · improve readability · visualise", 10, anchor="start", style='opacity=".68"')
    return _foot(s, 368, "Original diagram after Qiao, Shihab & Hundhausen (2026), ACM Transactions on Computing Education 26(2); figures are the review's.") + "</svg>"



# ------------------------------------------------------- AI, ML, DL: the nesting
def ai_hierarchy():
    """AI contains ML, ML contains DL; generative and agentic systems mostly sit on DL
    but are not branches at the same level: they overlap it."""
    s = HEAD.format(w=880, h=480)
    # AI
    s += _box(20, 16, 840, 392, fill="#fff", rx=14, lw=1.6)
    s += _t(44, 44, "ARTIFICIAL INTELLIGENCE", 12, anchor="start", weight=700, style='letter-spacing="1.6"')
    s += _t(44, 64, "systems that perform tasks associated with human intelligence: reasoning, planning, perception, language, decisions", 11, anchor="start", style=f'fill="{INK2}"')
    # ML
    s += _box(44, 80, 768, 302, fill="#f7f6f2", rx=12, lw=1.4)
    s += _t(68, 106, "MACHINE LEARNING", 12, anchor="start", weight=700, style='letter-spacing="1.6"')
    s += _t(68, 125, "learns patterns from data instead of being explicitly programmed", 11, anchor="start", style=f'fill="{INK2}"')
    # DL
    s += _box(68, 140, 548, 212, fill=GOLD, rx=10, lw=1.4)
    s += _t(92, 166, "DEEP LEARNING", 12, anchor="start", weight=700, style='letter-spacing="1.6"')
    s += _lines(92, 185, ["multi-layer neural networks that learn", "representations from large amounts of data:",
                          "CNNs, GNNs, transformers, diffusion models"], 11, anchor="start", style=f'fill="{INK2}"', lh=15)
    s += _t(92, 336, "Modules 7–8", 10, anchor="start", weight=600, style=f'fill="{ACC}"')
    # generative and agentic: overlap DL, not contained by it, not beside it
    s += _box(418, 154, 330, 88, fill="#fff", stroke=ACC, rx=9, lw=1.8)
    s += _t(434, 178, "Generative AI", 14, anchor="start", weight=700)
    s += _lines(434, 197, ["creates text, images, code, geometry and", "other design representations"], 10.8, anchor="start", style=f'fill="{INK2}"', lh=14)
    s += _t(434, 233, "mostly deep models: diffusion, LLMs · Module 2", 9.8, anchor="start", weight=600, style=f'fill="{ACC}"')
    s += _box(418, 254, 424, 88, fill="#fff", stroke=ACC, rx=9, lw=1.8)
    s += _t(434, 278, "Agentic AI", 14, anchor="start", weight=700)
    s += _lines(434, 297, ["pursues goals: plans, uses tools, acts, responds to feedback,", "with human oversight where needed"], 10.8, anchor="start", style=f'fill="{INK2}"', lh=14)
    s += _t(434, 333, "an LLM plus tools, memory and control code · Module 4", 9.8, anchor="start", weight=600, style=f'fill="{ACC}"')
    # what lies outside each inner set
    s += _t(68, 372, "also machine learning, not deep: linear regression, decision trees, clustering · Modules 5–6", 10, anchor="start", style=f'fill="{INK2}"')
    s += _t(44, 399, "also AI, not learned: rules, search, symbolic planning", 10, anchor="start", style=f'fill="{INK2}"')
    s += _t(440, 434, "Overlapping areas, not parallel branches: many generative and agentic systems are built on deep-learning models.", 12, weight=600)
    return _foot(s, 448, "Original diagram. Nesting after standard usage, e.g. LeCun, Bengio & Hinton (2015), Nature 521; agentic AI after Lee et al. (2025).") + "</svg>"


# ------------------------------------------ small role pictures for the intro
def _full(svg):
    return svg.replace("<svg ", '<svg class="full" ', 1)


def role_agent():
    """An agent working on a design goal: plan, call a tool, act, read the feedback."""
    s = HEAD.format(w=400, h=300)
    s += _box(110, 14, 180, 38, fill=GOLD, stroke=ACC, rx=8, lw=1.6)
    s += _t(200, 30, "GOAL", 10, weight=700, style=f'fill="{ACC}" letter-spacing="1.4"')
    s += _t(200, 45, "daylight on every desk", 12.5, weight=600)
    nodes = [(200, 96, "plan"), (318, 170, "use a tool"), (200, 244, "act"), (82, 170, "feedback")]
    for x, y, t in nodes:
        s += _box(x - 58, y - 18, 116, 36, fill="#fff", rx=18, lw=1.5)
        s += _t(x, y + 5, t, 14, weight=600)
    s += _arrow(200, 52, 200, 76, purple=True)
    s += f'<path d="M246 108 Q300 120 312 150" marker-end="url(#ap)" stroke="{ACC}"/>'
    s += f'<path d="M312 190 Q300 222 250 238" marker-end="url(#ap)" stroke="{ACC}"/>'
    s += f'<path d="M150 238 Q100 222 88 190" marker-end="url(#ap)" stroke="{ACC}"/>'
    s += f'<path d="M88 150 Q100 120 154 108" marker-end="url(#ap)" stroke="{ACC}"/>'
    s += _t(318, 206, "daylight simulation", 10.5, style=f'fill="{INK2}"')
    s += _t(200, 280, "revise the facade", 10.5, style=f'fill="{INK2}"')
    # the designer, overseeing
    s += '<circle cx="200" cy="158" r="9" fill="#fff"/>'
    s += '<path d="M184 188 Q200 168 216 188" fill="#fff"/>'
    s += _t(200, 206, "designer", 10.5, weight=600)
    s += _t(200, 220, "approves", 10.5, style=f'fill="{INK2}"')
    return _full(s + "</svg>")


def role_learn():
    """Schematic prediction plot: illustrative random points, not model results."""
    s = HEAD.format(w=400, h=300)
    x0, y0, x1, y1 = 66, 250, 372, 26
    s += f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y0}"/><line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y1}"/>'
    s += f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y1}" stroke="#9a9a9a" stroke-dasharray="5 4"/>'
    import random
    rnd = random.Random(7)
    for i in range(46):
        v = rnd.uniform(0.06, 0.94)
        e = rnd.gauss(0, 0.045)
        cx = x0 + v * (x1 - x0); cy = y0 - min(max(v + e, 0.02), 0.98) * (y0 - y1)
        s += f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="4.2" fill="{ACC if v > 0.62 else "#fff"}" stroke="{ACC}" stroke-width="1.3"/>'
    s += _t((x0 + x1) / 2, 280, "heating load (illustrative)", 12, weight=500)
    s += f'<text x="26" y="{(y0 + y1) / 2}" font-size="12" font-weight="500" text-anchor="middle" font-family="Montserrat, sans-serif" fill="#111" stroke="none" transform="rotate(-90 26 {(y0 + y1) / 2})">predicted</text>'
    s += _box(82, 34, 150, 44, fill="#fff", rx=6, lw=1.2)
    s += _t(92, 52, "Schematic example", 11, anchor="start", weight=600)
    s += f'<circle cx="98" cy="66" r="4" fill="{ACC}" stroke="{ACC}"/>'
    s += _t(108, 70, "high-load example", 10.5, anchor="start", style=f'fill="{INK2}"')
    return _full(s + "</svg>")

ALL = {"course_map": course_map, "genai_review_map": genai_review_map, "human_ai_collab": human_ai_collab,
       "agentic_framework": agentic_framework, "ethics_map": ethics_map, "data_centric": data_centric,
       "ml_design_stages": ml_design_stages, "piml_taxonomy": piml_taxonomy, "code_comprehension_loop": code_comprehension_loop,
       "ai_hierarchy": ai_hierarchy, "role_agent": role_agent, "role_learn": role_learn}
