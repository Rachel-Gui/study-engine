"""figures_dl.py - line-art diagrams for Module 3 (deep learning).

Same conventions as figures.py: black on white, Montserrat, one <svg> string
per diagram with a viewBox so it scales identically on the site and in a 4K
video frame. Spirit Purple is used for at most one emphasis element per figure.
"""
import math

ACC = "#4b2e83"
_S = ('font-family="Montserrat, sans-serif" fill="#111"')
HEAD = ('<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" '
        'stroke="#111" fill="none" stroke-width="1.4" '
        'stroke-linecap="round" stroke-linejoin="round">'
        '<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" '
        'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
        '<path d="M0,0 L10,5 L0,10 z" fill="#111" stroke="none"/></marker>'
        '<marker id="ao" viewBox="0 0 10 10" refX="9" refY="5" '
        'markerWidth="5" markerHeight="5" orient="auto-start-reverse">'
        '<path d="M0,0 L10,5 L0,10 z" fill="#111" stroke="none"/></marker></defs>')


def _t(x, y, s, size=13, anchor="middle", weight=400, style=""):
    base = _S.replace(' fill="#111"', "") if "fill=" in style else _S   # first attribute wins in SVG
    return (f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" '
            f'font-weight="{weight}" {base} stroke="none" {style}>{s}</text>')


def _grid(x0, y0, n, cell, vals=None, hi=None, hi_stroke=ACC, lw=1.1):
    """n x n grid of cells; vals (0..1) darken cells; hi=(r,c,size) outlines a window."""
    s = ""
    for r in range(n):
        for c in range(n):
            v = vals[r][c] if vals else 0
            fill = f'fill="rgba(17,17,17,{0.08 + 0.72 * v:.2f})"' if vals else 'fill="none"'
            s += (f'<rect x="{x0 + c * cell}" y="{y0 + r * cell}" width="{cell}" '
                  f'height="{cell}" {fill} stroke="#111" stroke-width="{lw}" opacity=".9"/>')
    if hi:
        r, c, k = hi
        s += (f'<rect x="{x0 + c * cell}" y="{y0 + r * cell}" width="{cell * k}" '
              f'height="{cell * k}" stroke="{hi_stroke}" stroke-width="2.6" fill="none"/>')
    return s


# ------------------------------------------------------------ loss landscape
def loss_landscape():
    s = HEAD.format(w=880, h=320)
    panels = [(150, "Learning rate too small", "creeps; may never arrive"),
              (440, "About right", "a few steps, straight down"),
              (730, "Too large", "overshoots and diverges")]
    for cx, title, sub in panels:
        cy = 150
        for k in (1, .78, .56, .36, .18):
            s += f'<ellipse cx="{cx}" cy="{cy}" rx="{118 * k}" ry="{58 * k}" opacity=".32"/>'
        s += f'<circle cx="{cx}" cy="{cy}" r="3.5" fill="#111" stroke="none"/>'
        s += _t(cx, 60, title, 13.5, weight=600)
        s += _t(cx, 252, sub, 11.5, style='opacity=".6"')
    # small steps: creeping inward from the rim, still far from the bottom
    sx, sy = 258, 112
    pts = [(sx + (150 - sx) * k / 10 * .32, sy + (150 - sy) * k / 10 * .32) for k in range(11)]
    s += ('<path d="M' + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts) +
          f'" stroke="{ACC}" stroke-width="2" marker-end="url(#ao)"/>')
    for x, y in pts[:-1]:
        s += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.2" fill="{ACC}" stroke="none"/>'
    # good
    s += (f'<path d="M548,102 L512,124 L474,140 L452,148 L442,150" stroke="{ACC}" '
          f'stroke-width="2" marker-end="url(#ao)"/>')
    for x, y in [(548, 102), (512, 124), (474, 140), (452, 148)]:
        s += f'<circle cx="{x}" cy="{y}" r="2.6" fill="{ACC}" stroke="none"/>'
    # diverging
    s += (f'<path d="M700,138 L790,166 L640,176 L846,124 L612,110" stroke="{ACC}" '
          f'stroke-width="2" marker-end="url(#ao)"/>')
    for x, y in [(700, 138), (790, 166), (640, 176), (846, 124)]:
        s += f'<circle cx="{x}" cy="{y}" r="2.6" fill="{ACC}" stroke="none"/>'
    s += '<line x1="60" y1="276" x2="820" y2="276" opacity=".22"/>'
    s += _t(440, 302, "Same bowl, same start. The only difference is the step size &#951;. "
                      "If the loss rises every step, lower it first.", 13, weight=500)
    return s + "</svg>"


# ------------------------------------------------------------ backprop chain
def backprop_chain():
    s = HEAD.format(w=880, h=330)
    nodes = [(90, "x", "input"), (250, "z", "w&#183;x + b"), (410, "a", "&#966;(z)"),
             (570, "&#375;", "v&#183;a + c"), (740, "L", "(&#375; &#8722; y)&#178;")]
    for i, (x, lab, sub) in enumerate(nodes):
        s += f'<circle cx="{x}" cy="130" r="26" fill="#fff" stroke-width="{2 if i == 4 else 1.4}"/>'
        s += _t(x, 136, lab, 17, weight=600)
        s += _t(x, 176, sub, 11, style='opacity=".6"')
        if i < 4:
            nx = nodes[i + 1][0]
            s += f'<line x1="{x + 28}" y1="120" x2="{nx - 28}" y2="120" marker-end="url(#ao)"/>'
            s += (f'<line x1="{nx - 28}" y1="142" x2="{x + 28}" y2="142" marker-end="url(#ao)" '
                  f'stroke="{ACC}" stroke-dasharray="5 3"/>')
    s += _t(170, 108, "forward: values", 10.5, style='opacity=".6"')
    s += _t(660, 108, "forward", 10.5, style='opacity=".6"')
    grads = [(170, "&#8706;L/&#8706;x"), (330, "&#8706;L/&#8706;z"), (490, "&#8706;L/&#8706;a"),
             (655, "&#8706;L/&#8706;&#375;")]
    for x, g in grads:
        s += _t(x, 166, g, 11.5, weight=500, style=f'fill="{ACC}"')
    s += _t(440, 214, "&#8706;L/&#8706;w  =  &#8706;L/&#8706;&#375;  &#183;  &#8706;&#375;/&#8706;a  &#183;  "
                      "&#8706;a/&#8706;z  &#183;  &#8706;z/&#8706;w", 15.5, weight=500)
    s += _t(440, 238, "=  2(&#375;&#8722;y)  &#183;  v  &#183;  &#966;&#8242;(z)  &#183;  x", 14,
            style='opacity=".7"')
    s += '<line x1="60" y1="270" x2="820" y2="270" opacity=".22"/>'
    s += _t(440, 296, "The chain rule, applied backwards. Each factor is local; the product "
                      "reaches every weight in one sweep.", 13, weight=500)
    s += _t(440, 316, "The purple arrows are backpropagation. Nothing else.", 11.5,
            style='opacity=".6"')
    return s + "</svg>"


# ---------------------------------------------------------- split strategies
def split_strategies():
    s = HEAD.format(w=880, h=330)
    rows = [("Random split", "shuffle, hold out 20%",
             "Does the model know these buildings? &#8212; usually yes, by accident",
             [i % 5 == 2 for i in range(24)]),
            ("Chronological", "train on the past, test on the future",
             "Will it work next month?",
             [i >= 19 for i in range(24)]),
            ("Grouped by building", "no building on both sides",
             "Will it work on a building it has never seen?",
             [8 <= i < 13 for i in range(24)])]
    for ri, (name, how, q, mask) in enumerate(rows):
        y = 58 + ri * 82
        s += _t(60, y + 4, name, 13.5, anchor="start", weight=600)
        s += _t(60, y + 22, how, 10.5, anchor="start", style='opacity=".6"')
        for i, te in enumerate(mask):
            x = 318 + i * 21
            fill = f'fill="{ACC}"' if te else 'fill="#fff"'
            s += f'<rect x="{x}" y="{y - 12}" width="17" height="22" rx="2" {fill} stroke="#111"/>'
        s += _t(318, y + 32, q, 10.5, anchor="start", style='opacity=".7" font-style="italic"')
    s += _t(318, 36, "&#8592; time, or building index &#8594;", 10.5, anchor="start",
            style='opacity=".5"')
    s += f'<rect x="60" y="272" width="12" height="12" fill="{ACC}" stroke="#111"/>'
    s += _t(80, 283, "test", 11, anchor="start")
    s += '<rect x="120" y="272" width="12" height="12" fill="#fff" stroke="#111"/>'
    s += _t(140, 283, "train", 11, anchor="start")
    s += _t(830, 283, "Adjacent rows are near-duplicates. A random split lets the model see "
                      "the answer next door.", 11.5, anchor="end", weight=500)
    return s + "</svg>"


# -------------------------------------------------------------- fit regimes
def fit_regimes():
    s = HEAD.format(w=880, h=300)
    import random
    rnd = random.Random(4)
    pts = [(i / 11, math.sin(i / 11 * 4.2) * .55 + .5 + rnd.uniform(-.09, .09)) for i in range(12)]
    panels = [(70, "Underfit", "a line through a curve", 1),
              (330, "Good fit", "follows the pattern, not the noise", 2),
              (590, "Overfit", "hits every point, misses the next one", 3)]
    for x0, name, sub, kind in panels:
        w, h, y0 = 200, 150, 58
        X = lambda u: x0 + 10 + u * (w - 20)
        Y = lambda v: y0 + h - 10 - v * (h - 20)
        s += f'<line x1="{x0}" y1="{y0 + h}" x2="{x0 + w}" y2="{y0 + h}" opacity=".3"/>'
        s += f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y0 + h}" opacity=".3"/>'
        for u, v in pts:
            s += f'<circle cx="{X(u):.1f}" cy="{Y(v):.1f}" r="3.2" fill="#111" stroke="none"/>'
        if kind == 1:
            s += f'<line x1="{X(0)}" y1="{Y(.42)}" x2="{X(1)}" y2="{Y(.58)}" stroke="{ACC}" stroke-width="2"/>'
        elif kind == 2:
            d = " ".join(f"{X(u / 60):.1f},{Y(math.sin(u / 60 * 4.2) * .55 + .5):.1f}" for u in range(61))
            s += f'<polyline points="{d}" stroke="{ACC}" stroke-width="2"/>'
        else:
            d = ""
            for u in range(121):
                t = u / 120
                base = math.sin(t * 4.2) * .55 + .5
                wig = 0
                for (pu, pv) in pts:
                    wig += (pv - (math.sin(pu * 4.2) * .55 + .5)) * math.exp(-((t - pu) / .028) ** 2)
                d += f"{X(t):.1f},{Y(base + wig * 1.15):.1f} "
            s += f'<polyline points="{d}" stroke="{ACC}" stroke-width="2"/>'
        s += _t(x0 + w / 2, y0 - 18, name, 14, weight=600)
        s += _t(x0 + w / 2, y0 + h + 24, sub, 11.5, style='opacity=".65"')
    s += '<line x1="60" y1="252" x2="820" y2="252" opacity=".22"/>'
    s += _t(440, 280, "Training error falls left to right. Validation error is lowest in the "
                      "middle. Only the second number is yours to report.", 13, weight=500)
    return s + "</svg>"


# --------------------------------------------------------------- convolution
def convolution():
    s = HEAD.format(w=880, h=330)
    img = [[0, 0, 0, 0, 0, 0], [0, 1, 1, 0, 0, 0], [0, 1, 1, 0, 1, 1],
           [0, 0, 0, 0, 1, 1], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]]
    s += _grid(60, 70, 6, 24, img, hi=(1, 0, 3))
    s += _t(132, 54, "input 6&#215;6", 12, weight=600)
    s += _t(132, 240, "a window of 3&#215;3 pixels", 10.5, style='opacity=".6"')
    # kernel
    k = [["-1", "0", "1"], ["-1", "0", "1"], ["-1", "0", "1"]]
    for r in range(3):
        for c in range(3):
            x, y = 268 + c * 30, 108 + r * 30
            s += f'<rect x="{x}" y="{y}" width="30" height="30" stroke="{ACC}" stroke-width="1.6"/>'
            s += _t(x + 15, y + 20, k[r][c], 12.5, weight=500)
    s += _t(313, 54, "kernel 3&#215;3", 12, weight=600)
    s += _t(313, 90, "9 weights, learned", 10.5, style='opacity=".6"')
    s += _t(313, 226, "multiply, sum &#8594; one number", 10.5, style='opacity=".6"')
    s += '<line x1="212" y1="150" x2="258" y2="150" marker-end="url(#ao)"/>'
    s += _t(235, 142, "&#8857;", 14)
    s += '<line x1="366" y1="150" x2="416" y2="150" marker-end="url(#ao)"/>'
    out = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
    outv = [[.5, .1, .5, .5], [.85, .1, .6, .9], [.5, .1, .5, .9], [.1, .1, .5, .5]]
    s += _grid(424, 94, 4, 28, outv, hi=(0, 0, 1))
    s += _t(480, 54, "feature map 4&#215;4", 12, weight=600)
    s += _t(480, 80, "vertical edges, everywhere", 10.5, style='opacity=".6"')
    s += '<line x1="548" y1="150" x2="598" y2="150" marker-end="url(#ao)"/>'
    s += _t(573, 140, "pool", 10.5, style='opacity=".6"')
    s += _grid(606, 122, 2, 28, [[.85, .9], [.5, .9]])
    s += _t(634, 54, "pooled 2&#215;2", 12, weight=600)
    s += _t(634, 80, "max of each 2&#215;2", 10.5, style='opacity=".6"')
    s += _t(760, 120, "the same 9 weights", 11.5, weight=500)
    s += _t(760, 138, "slide over every position.", 11.5, weight=500)
    s += _t(760, 164, "A dense layer on 36 pixels", 10.5, style='opacity=".6"')
    s += _t(760, 180, "would need 36 weights per", 10.5, style='opacity=".6"')
    s += _t(760, 196, "output &#8212; and learn edges", 10.5, style='opacity=".6"')
    s += _t(760, 212, "separately at each place.", 10.5, style='opacity=".6"')
    s += '<line x1="60" y1="272" x2="820" y2="272" opacity=".22"/>'
    s += _t(440, 298, "Weight sharing across position is the whole idea. An edge detector "
                      "learned once finds edges anywhere.", 13, weight=500)
    return s + "</svg>"


# ------------------------------------------------------------------ cnn stack
def cnn_stack():
    s = HEAD.format(w=880, h=300)
    stages = [(90, 92, 1, "image", "224&#215;224&#215;3"),
              (232, 76, 3, "conv + ReLU", "112&#215;112&#215;32"),
              (372, 58, 5, "conv + pool", "56&#215;56&#215;64"),
              (500, 40, 7, "conv + pool", "14&#215;14&#215;128"),
              (620, 22, 9, "flatten", "25,088"),
              (720, 14, 1, "dense", "256"),
              (812, 10, 1, "output", "5 classes")]
    for i, (x, sz, depth, name, dim) in enumerate(stages):
        for d in range(min(depth, 4)):
            off = d * 5
            s += (f'<rect x="{x - sz / 2 + off}" y="{150 - sz / 2 - off}" width="{sz}" '
                  f'height="{sz}" fill="#fff" opacity=".95"/>')
        s += _t(x, 226, name, 11.5, weight=600)
        s += _t(x, 242, dim, 10, style='opacity=".6"')
        if i < len(stages) - 1:
            nx, nsz = stages[i + 1][0], stages[i + 1][1]
            s += (f'<line x1="{x + sz / 2 + 18}" y1="150" x2="{nx - nsz / 2 - 6}" y2="150" '
                  f'marker-end="url(#ao)" opacity=".7"/>')
    s += _t(300, 52, "spatial size shrinks &#8594;", 11, style='opacity=".6"')
    s += _t(300, 68, "channels (what is detected) grow &#8594;", 11, style='opacity=".6"')
    s += _t(760, 52, "edges &#8594; textures &#8594; parts &#8594; \"brick facade\"", 11,
            style=f'fill="{ACC}" font-weight="500"')
    s += '<line x1="60" y1="262" x2="820" y2="262" opacity=".22"/>'
    s += _t(440, 288, "Early layers see pixels. Late layers see the whole facade. The head "
                      "turns that into the answer you asked for.", 13, weight=500)
    return s + "</svg>"


# ------------------------------------------------------------ plan to graph
_ROOMS = [("Entry", 60, 70, 90, 60), ("Living", 150, 70, 150, 110), ("Kitchen", 300, 70, 100, 110),
          ("Hall", 60, 130, 90, 50), ("Bed 1", 60, 180, 120, 80), ("Bath", 180, 180, 70, 80),
          ("Bed 2", 250, 180, 150, 80)]
_ADJ = [("Entry", "Living"), ("Entry", "Hall"), ("Living", "Kitchen"), ("Hall", "Bed 1"),
        ("Hall", "Bath"), ("Living", "Bed 2"), ("Bath", "Bed 2"), ("Living", "Hall")]
_NODE = {"Entry": (540, 96), "Living": (650, 96), "Kitchen": (770, 96), "Hall": (560, 176),
         "Bed 1": (520, 256), "Bath": (640, 256), "Bed 2": (760, 226)}


def plan_to_graph():
    s = HEAD.format(w=880, h=330)
    for name, x, y, w, h in _ROOMS:
        s += f'<rect x="{x}" y="{y}" width="{w}" height="{h}"/>'
        s += _t(x + w / 2, y + h / 2 + 4, name, 11.5, weight=500)
    s += _t(230, 52, "a floor plan (geometry)", 12.5, weight=600)
    s += _t(230, 288, "rooms have positions and sizes", 10.5, style='opacity=".6"')
    s += '<line x1="426" y1="170" x2="482" y2="170" marker-end="url(#a)"/>'
    for a, b in _ADJ:
        (x1, y1), (x2, y2) = _NODE[a], _NODE[b]
        s += f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" opacity=".55"/>'
    for name, (x, y) in _NODE.items():
        s += f'<circle cx="{x}" cy="{y}" r="24" fill="#fff" stroke-width="1.6"/>'
        s += _t(x, y + 4, name, 10.5, weight=500)
    s += _t(650, 52, "the same plan as a graph (relationships)", 12.5, weight=600)
    s += _t(650, 300, "nodes: rooms with features (area, use) &#183; edges: doors, adjacency, sightlines",
            10.5, style='opacity=".6"')
    return s + "</svg>"


# ------------------------------------------------------------ message passing
def message_passing():
    s = HEAD.format(w=880, h=330)
    cx, cy = 200, 150
    nb = [(80, 70), (80, 230), (300, 60), (320, 230)]
    for (x, y) in nb:
        s += f'<line x1="{x}" y1="{y}" x2="{cx}" y2="{cy}" opacity=".35"/>'
        s += (f'<path d="M{x + (cx - x) * .28:.0f},{y + (cy - y) * .28:.0f} '
              f'L{x + (cx - x) * .72:.0f},{y + (cy - y) * .72:.0f}" stroke="{ACC}" '
              f'stroke-width="2" marker-end="url(#ao)"/>')
        s += f'<circle cx="{x}" cy="{y}" r="18" fill="#fff"/>'
        s += _t(x, y + 4, "h&#8342;", 12)
    s += f'<circle cx="{cx}" cy="{cy}" r="24" fill="#fff" stroke-width="2"/>'
    s += _t(cx, cy + 5, "h&#7522;", 14, weight=600)
    s += _t(200, 292, "1. neighbours send messages", 11.5, weight=500)

    s += '<line x1="356" y1="150" x2="404" y2="150" marker-end="url(#ao)"/>'
    s += '<rect x="410" y="118" width="120" height="64" rx="3"/>'
    s += _t(470, 144, "aggregate", 12.5, weight=600)
    s += _t(470, 164, "mean / sum / max", 10.5, style='opacity=".6"')
    s += _t(470, 292, "2. order must not matter", 11.5, weight=500)
    s += '<line x1="534" y1="150" x2="582" y2="150" marker-end="url(#ao)"/>'
    s += '<rect x="588" y="118" width="120" height="64" rx="3"/>'
    s += _t(648, 144, "update", 12.5, weight=600)
    s += _t(648, 164, "&#966;(W&#183;[h&#7522;, agg])", 10.5, style='opacity=".6"')
    s += _t(735, 292, "3. one small network, shared by every node", 11, weight=500)
    s += '<line x1="712" y1="150" x2="760" y2="150" marker-end="url(#ao)"/>'
    s += f'<circle cx="790" cy="150" r="24" fill="#fff" stroke="{ACC}" stroke-width="2.2"/>'
    s += _t(790, 155, "h&#7522;&#8242;", 14, weight=600, style=f'fill="{ACC}"')
    s += _t(790, 196, "new state", 10.5, style='opacity=".6"')
    s += _t(440, 40, "One GNN layer: a node's new state depends on itself and its neighbours. "
                     "Two layers reach neighbours of neighbours.", 12.5, weight=500)
    return s + "</svg>"


# ------------------------------------------------------------------ pinn loss
def pinn_loss():
    s = HEAD.format(w=880, h=350)
    s += '<rect x="60" y="112" width="90" height="70" rx="3"/>'
    s += _t(105, 140, "x, t", 15, weight=600)
    s += _t(105, 162, "coordinates", 10, style='opacity=".6"')
    s += '<line x1="152" y1="147" x2="196" y2="147" marker-end="url(#ao)"/>'
    s += '<rect x="200" y="100" width="130" height="94" rx="3" stroke-width="2"/>'
    s += _t(265, 134, "network", 14, weight=600)
    s += _t(265, 154, "u&#952;(x, t)", 13, weight=500)
    s += _t(265, 176, "tanh MLP", 10, style='opacity=".6"')
    s += '<line x1="332" y1="147" x2="376" y2="147" marker-end="url(#ao)"/>'
    s += '<rect x="380" y="100" width="130" height="94" rx="3" stroke-dasharray="5 3"/>'
    s += _t(445, 128, "autodiff", 13, weight=600)
    s += _t(445, 150, "&#8706;u/&#8706;t,  &#8706;&#178;u/&#8706;x&#178;", 12, weight=500)
    s += _t(445, 176, "exact, not finite differences", 9.5, style='opacity=".6"')
    losses = [(54, "data loss", "mean (u&#952;(x&#7522;) &#8722; u&#7522;)&#178;", "sensor points, if any"),
              (128, "PDE residual", "mean (&#8706;u/&#8706;t &#8722; &#945;&#8706;&#178;u/&#8706;x&#178;)&#178;",
               "collocation points"),
              (202, "boundary / initial", "mean (u&#952; &#8722; u&#7495;&#7580;)&#178;", "walls, t = 0")]
    for y, name, form, sub in losses:
        s += f'<rect x="560" y="{y}" width="176" height="60" rx="3"/>'
        s += _t(648, y + 20, name, 11.5, weight=600)
        s += _t(648, y + 38, form, 10, weight=500)
        s += _t(648, y + 52, sub, 9, style='opacity=".55"')
        s += f'<path d="M512,147 C 536,147 536,{y + 30} 556,{y + 30}" marker-end="url(#ao)" opacity=".7"/>'
        s += f'<path d="M738,{y + 30} C 762,{y + 30} 762,158 786,158" marker-end="url(#ao)" opacity=".7"/>'
    s += f'<circle cx="812" cy="158" r="26" stroke="{ACC}" stroke-width="2.2" fill="#fff"/>'
    s += _t(812, 163, "L", 16, weight=600, style=f'fill="{ACC}"')
    s += _t(828, 206, "&#955;&#8321;data + &#955;&#8322;PDE", 9, style='opacity=".65"')
    s += _t(828, 218, "+ &#955;&#8323;BC", 9, style='opacity=".65"')
    s += (f'<path d="M812,186 L812,284 L265,284 L265,198" stroke="{ACC}" stroke-dasharray="5 3" '
          f'marker-end="url(#ao)"/>')
    s += _t(540, 278, "backpropagate the whole thing into &#952;", 10.5, style=f'fill="{ACC}"')
    s += '<line x1="60" y1="302" x2="820" y2="302" opacity=".22"/>'
    s += _t(440, 328, "A normal network with an unusual loss. The physics is a penalty, "
                      "not a guarantee: the residual is minimised, never zero.", 13, weight=500)
    return s + "</svg>"


# --------------------------------------------------------- surrogate pipeline
def surrogate_pipeline():
    s = HEAD.format(w=880, h=330)
    boxes = [(60, "simulator", "CFD / EnergyPlus", "hours per run"),
             (250, "dataset", "N designs &#8594; N results", "the range you sampled"),
             (440, "surrogate", "MLP / GP / CNN", "milliseconds per query"),
             (630, "design loop", "optimise, explore", "thousands of queries")]
    for i, (x, name, sub, sub2) in enumerate(boxes):
        s += f'<rect x="{x}" y="96" width="150" height="80" rx="3" stroke-width="{2 if i == 2 else 1.4}"/>'
        s += _t(x + 75, 124, name, 13.5, weight=600)
        s += _t(x + 75, 144, sub, 10.5, style='opacity=".65"')
        s += _t(x + 75, 162, sub2, 10, style='opacity=".5" font-style="italic"')
        if i < 3:
            s += f'<line x1="{x + 152}" y1="136" x2="{x + 246}" y2="136" marker-end="url(#a)"/>'
    s += (f'<path d="M705,178 L705,226 L135,226 L135,178" marker-end="url(#ao)" '
          f'stroke="{ACC}" stroke-dasharray="5 3"/>')
    s += _t(420, 244, "re-check the surrogate's best designs in the real simulator before "
                      "believing them", 10.5, style=f'fill="{ACC}"')
    s += f'<rect x="242" y="60" width="166" height="26" rx="13" fill="#fff" stroke="{ACC}"/>'
    s += _t(325, 77, "this range defines validity", 10, weight=600, style=f'fill="{ACC}"')
    s += '<line x1="60" y1="272" x2="820" y2="272" opacity=".22"/>'
    s += _t(440, 298, "A surrogate is defined by what it replaces. It replaces the simulator "
                      "inside the sampled range, and nowhere else.", 12.5, weight=500)
    return s + "</svg>"


# ------------------------------------------------------ interpolation region
def interpolation_region():
    import random
    rnd = random.Random(11)
    s = HEAD.format(w=880, h=330)
    x0, y0, w, h = 110, 50, 380, 210
    s += f'<line x1="{x0}" y1="{y0 + h}" x2="{x0 + w}" y2="{y0 + h}" marker-end="url(#ao)"/>'
    s += f'<line x1="{x0}" y1="{y0 + h}" x2="{x0}" y2="{y0}" marker-end="url(#ao)"/>'
    s += _t(x0 + w / 2, y0 + h + 26, "window-to-wall ratio &#8594;", 11, style='opacity=".6"')
    s += ('<text x="88" y="155" font-size="11" text-anchor="middle" font-family="Montserrat, sans-serif" '
          'fill="#111" stroke="none" opacity=".6" transform="rotate(-90 88 155)">orientation &#8594;</text>')
    pts = [(x0 + 70 + rnd.random() * 210, y0 + 40 + rnd.random() * 120) for _ in range(38)]
    s += (f'<path d="M{x0 + 60},{y0 + 30} L{x0 + 290},{y0 + 30} L{x0 + 300},{y0 + 170} '
          f'L{x0 + 62},{y0 + 172} Z" stroke-dasharray="5 4" opacity=".6"/>')
    for x, y in pts:
        s += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="#111" stroke="none"/>'
    s += _t(x0 + 178, y0 + 20, "training runs", 10.5, style='opacity=".6"')
    s += f'<circle cx="{x0 + 180}" cy="{y0 + 100}" r="7" stroke="{ACC}" stroke-width="2.2" fill="#fff"/>'
    s += f'<rect x="{x0 + 96}" y="{y0 + 110}" width="168" height="18" rx="9" fill="#fff" opacity=".92" stroke="none"/>'
    s += _t(x0 + 180, y0 + 123, "query A: inside &#8212; interpolation", 10.5, weight=500,
            style=f'fill="{ACC}"')
    s += f'<circle cx="{x0 + 345}" cy="{y0 + 60}" r="7" stroke="{ACC}" stroke-width="2.2" fill="#fff"/>'
    s += _t(x0 + 345, y0 + 40, "query B: outside", 10.5, weight=500, style=f'fill="{ACC}"')
    s += _t(x0 + 345, y0 + 84, "extrapolation", 10.5, weight=500, style=f'fill="{ACC}"')
    s += _t(680, 78, "Inside the cloud", 13, weight=600)
    s += _t(680, 98, "the surrogate is interpolating between", 10.5, style='opacity=".65"')
    s += _t(680, 112, "runs it has seen. Error is measurable.", 10.5, style='opacity=".65"')
    s += _t(680, 150, "Outside the cloud", 13, weight=600)
    s += _t(680, 170, "it is guessing with a smooth function.", 10.5, style='opacity=".65"')
    s += _t(680, 184, "The output looks just as confident.", 10.5, style='opacity=".65"')
    s += _t(680, 198, "Nothing in the number tells you.", 10.5, style='opacity=".65"')
    s += _t(680, 236, "Report the sampled range with every result.", 11, weight=500,
            style=f'fill="{ACC}"')
    s += '<line x1="60" y1="290" x2="820" y2="290" opacity=".22"/>'
    s += _t(440, 314, "Marking where the range ends is part of the deliverable.", 13, weight=500)
    return s + "</svg>"


# ------------------------------------------------------------------------ inr
def inr():
    s = HEAD.format(w=880, h=320)
    s += '<rect x="60" y="112" width="110" height="70" rx="3"/>'
    s += _t(115, 140, "(x, y, z)", 14, weight=600)
    s += _t(115, 162, "one point", 10, style='opacity=".6"')
    s += '<line x1="172" y1="147" x2="216" y2="147" marker-end="url(#ao)"/>'
    s += '<rect x="220" y="96" width="150" height="102" rx="3" stroke-width="2"/>'
    s += _t(295, 128, "MLP", 15, weight=600)
    s += _t(295, 148, "+ shape code z", 11, style='opacity=".65"')
    s += _t(295, 166, "(sine or Fourier features", 9.5, style='opacity=".55"')
    s += _t(295, 179, "so fine detail survives)", 9.5, style='opacity=".55"')
    s += '<line x1="372" y1="147" x2="416" y2="147" marker-end="url(#ao)"/>'
    s += '<rect x="420" y="112" width="130" height="70" rx="3"/>'
    s += _t(485, 140, "value", 14, weight=600)
    s += _t(485, 162, "T, p, wind, or SDF", 10, style='opacity=".6"')
    # mesh vs points
    for r in range(5):
        for c in range(5):
            s += f'<rect x="{610 + c * 22}" y="{72 + r * 22}" width="22" height="22" opacity=".5"/>'
    s += _t(665, 60, "a grid stores values at fixed cells", 10, style='opacity=".6"')
    s += _t(665, 200, "the network stores a function:", 10.5, weight=500)
    s += _t(665, 216, "query anywhere, at any resolution", 10.5, weight=500)
    s += f'<circle cx="{610 + 2.5 * 22 + 7}" cy="{72 + 1.5 * 22 + 5}" r="4" fill="{ACC}" stroke="none"/>'
    s += _t(760, 128, "&#8592; between cells?", 9.5, anchor="start", style=f'fill="{ACC}"')
    s += '<line x1="60" y1="256" x2="820" y2="256" opacity=".22"/>'
    s += _t(440, 282, "An INR is a way of storing a field. It is not physics-informed "
                      "unless you add the physics to its loss.", 13, weight=500)
    s += _t(440, 302, "Coordinates in, value out. The mesh is gone.", 11.5, style='opacity=".6"')
    return s + "</svg>"


# ------------------------------------------------------------ sequence models
def sequence_models():
    s = HEAD.format(w=880, h=340)
    # panel 1: sliding window
    for i in range(6):
        s += f'<rect x="{60 + i * 26}" y="88" width="22" height="30" opacity=".85"/>'
    s += f'<rect x="{60 + 2 * 26 - 2}" y="84" width="{4 * 26 - 2}" height="38" stroke="{ACC}" stroke-width="2" fill="none"/>'
    s += '<line x1="140" y1="124" x2="140" y2="160" marker-end="url(#ao)"/>'
    s += '<rect x="96" y="164" width="88" height="40" rx="3"/>'
    s += _t(140, 189, "MLP", 12.5, weight=600)
    s += '<line x1="186" y1="184" x2="222" y2="184" marker-end="url(#ao)"/>'
    s += _t(240, 188, "&#375;", 14, weight=600)
    s += _t(150, 60, "Sliding window", 13.5, weight=600)
    s += _t(150, 236, "the last k readings as k features", 10.5, style='opacity=".6"')
    s += _t(150, 252, "simple; fixed memory length", 10.5, style='opacity=".6"')
    # panel 2: RNN unrolled
    for i in range(4):
        x = 330 + i * 60
        s += f'<rect x="{x}" y="128" width="42" height="42" rx="3"/>'
        s += _t(x + 21, 154, "h", 12, weight=600)
        s += f'<line x1="{x + 21}" y1="100" x2="{x + 21}" y2="124" marker-end="url(#ao)"/>'
        s += _t(x + 21, 94, f"x{i + 1}", 10.5, style='opacity=".65"')
        if i < 3:
            s += f'<line x1="{x + 44}" y1="149" x2="{x + 56}" y2="149" marker-end="url(#ao)" stroke="{ACC}" stroke-width="1.8"/>'
    s += '<line x1="531" y1="174" x2="531" y2="200" marker-end="url(#ao)"/>'
    s += _t(531, 216, "&#375;", 14, weight=600)
    s += _t(440, 60, "Recurrent (RNN / LSTM)", 13.5, weight=600)
    s += _t(440, 236, "a state carried step to step", 10.5, style='opacity=".6"')
    s += _t(440, 252, "unbounded memory; sequential, slow", 10.5, style='opacity=".6"')
    # panel 3: attention
    xs = [640, 676, 712, 748, 784]
    for i, x in enumerate(xs):
        s += f'<rect x="{x - 11}" y="128" width="22" height="30" opacity=".85"/>'
        s += _t(x, 118, f"x{i + 1}", 10, style='opacity=".65"')
        wgt = [.15, .1, .35, .2, .95][i]
        s += (f'<path d="M{x},162 C {x},200 760,200 760,224" stroke="{ACC}" '
              f'stroke-width="{0.6 + wgt * 3:.1f}" opacity="{0.35 + wgt * .6:.2f}" fill="none"/>')
    s += f'<circle cx="760" cy="236" r="12" fill="#fff" stroke="{ACC}" stroke-width="2"/>'
    s += _t(760, 262, "&#375;", 14, weight=600)
    s += _t(712, 60, "Attention (Transformer)", 13.5, weight=600)
    s += _t(712, 284, "every step is weighed against the query", 10.5, style='opacity=".6"')
    s += _t(712, 300, "parallel; the weights are inspectable", 10.5, style='opacity=".6"')
    s += '<line x1="300" y1="70" x2="300" y2="280" opacity=".2"/>'
    s += '<line x1="600" y1="70" x2="600" y2="280" opacity=".2"/>'
    s += _t(440, 326, "Three ways to let a model see the past. The first is often enough for building data.", 12.5, weight=500)
    return s + "</svg>"


# -------------------------------------------------------------------- attention
def attention():
    s = HEAD.format(w=880, h=330)
    vals = [.3, .35, .6, .9, .8, .5, .35, .3, .45, .85, .95, .6]
    wts = [.02, .02, .05, .16, .1, .03, .02, .02, .04, .22, .28, .04]
    x0 = 70
    for i, (v, w) in enumerate(zip(vals, wts)):
        x = x0 + i * 40
        hgt = 90 * v
        s += f'<rect x="{x}" y="{180 - hgt:.1f}" width="26" height="{hgt:.1f}" opacity=".85"/>'
        s += f'<rect x="{x}" y="{224}" width="26" height="{w * 160:.1f}" fill="{ACC}" stroke="none"/>'
        s += _t(x + 13, 200, f"t&#8722;{12 - i}", 9.5, style='opacity=".55"')
    s += f'<rect x="{x0 + 12 * 40}" y="120" width="26" height="60" stroke="{ACC}" stroke-width="2" stroke-dasharray="4 3"/>'
    s += _t(x0 + 12 * 40 + 13, 200, "now?", 9.5, weight=600, style=f'fill="{ACC}"')
    s += _t(x0, 74, "readings (values v)", 11.5, anchor="start", weight=600)
    s += _t(x0, 218, "attention weights &#945;", 11.5, anchor="start", weight=600, style=f'fill="{ACC}"')
    s += _t(760, 74, "query q = \"what is the load now?\"", 11, anchor="end", style='opacity=".65"')
    s += _t(440, 300, "&#945;&#7522; = softmax( q&#183;k&#7522; / &#8730;d ),   &#375; = &#931; &#945;&#7522; v&#7522;.   "
                      "The weights are learned, sum to one, and can be read.", 12.5, weight=500)
    s += _t(440, 320, "Here the model looks hardest at the same time yesterday and at the last hour.",
            10.5, style='opacity=".6"')
    return s + "</svg>"


# ------------------------------------------------------------- pinn problem
def pinn_problem():
    s = HEAD.format(w=880, h=330)
    x0, x1, yb = 100, 500, 210
    # the wall / rod
    s += f'<rect x="{x0}" y="{yb - 14}" width="{x1 - x0}" height="28" rx="2" opacity=".9"/>'
    s += _t(x0, yb + 40, "x = 0", 11, weight=500)
    s += _t(x1, yb + 40, "x = 1", 11, weight=500)
    s += _t(x0, yb + 56, "u = 0", 10.5, style=f'fill="{ACC}" font-weight="600"')
    s += _t(x1, yb + 56, "u = 0", 10.5, style=f'fill="{ACC}" font-weight="600"')
    # exact solution curve
    pts = " ".join(f"{x0 + (x1 - x0) * i / 60:.1f},{yb - 24 - 120 * math.sin(math.pi * i / 60):.1f}"
                   for i in range(61))
    s += f'<polyline points="{pts}" stroke-width="2.2"/>'
    s += _t(300, 58, "u(x) = sin(&#960;x)  &#8212; the exact answer", 12, weight=600)
    # source
    pts2 = " ".join(f"{x0 + (x1 - x0) * i / 60:.1f},{yb - 24 - 48 * math.sin(math.pi * i / 60):.1f}"
                    for i in range(61))
    s += f'<polyline points="{pts2}" stroke="{ACC}" stroke-width="1.6" stroke-dasharray="5 3"/>'
    s += _t(300, yb + 46, "dashed: f(x) = &#8722;&#960;&#178; sin(&#960;x), the source (scaled)", 10.5,
            style=f'fill="{ACC}"')
    # collocation points
    for i in range(9):
        x = x0 + (x1 - x0) * (i + 1) / 10
        s += f'<line x1="{x}" y1="{yb - 20}" x2="{x}" y2="{yb - 28}" stroke-width="1.6"/>'
    s += _t(300, yb - 36, "collocation points: where the residual is checked", 9.5, style='opacity=".6"')
    s += _t(680, 84, "The problem", 13.5, weight=600)
    s += _t(680, 108, "u&#8243;(x) = f(x)  on (0, 1)", 13, weight=500)
    s += _t(680, 130, "u(0) = u(1) = 0", 13, weight=500)
    s += _t(680, 166, "Read it as a wall 1 m thick, both faces", 10.5, style='opacity=".65"')
    s += _t(680, 181, "held at ambient, with a distributed heat", 10.5, style='opacity=".65"')
    s += _t(680, 196, "source inside. u is the temperature rise.", 10.5, style='opacity=".65"')
    s += _t(680, 228, "The network never sees u(x).", 11.5, weight=600, style=f'fill="{ACC}"')
    s += _t(680, 246, "It sees the equation, the two ends,", 10.5, style='opacity=".65"')
    s += _t(680, 261, "and where to check.", 10.5, style='opacity=".65"')
    s += '<line x1="60" y1="288" x2="820" y2="288" opacity=".22"/>'
    s += _t(440, 314, "Small enough to solve by hand, which is the point: you can check every "
                      "number the network produces.", 12.5, weight=500)
    return s + "</svg>"


ALL = {
    "loss_landscape": loss_landscape, "backprop_chain": backprop_chain,
    "split_strategies": split_strategies, "fit_regimes": fit_regimes,
    "convolution": convolution, "cnn_stack": cnn_stack,
    "plan_to_graph": plan_to_graph, "message_passing": message_passing,
    "pinn_loss": pinn_loss, "surrogate_pipeline": surrogate_pipeline,
    "interpolation_region": interpolation_region, "inr": inr,
    "sequence_models": sequence_models, "attention": attention,
    "pinn_problem": pinn_problem,
}
