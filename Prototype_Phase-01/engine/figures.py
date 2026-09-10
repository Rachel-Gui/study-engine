"""Line-art SVG diagrams. Black on white, no fills, no colour.
Every diagram is a standalone <svg> string with a viewBox, so it scales
identically in the player and in the rendered video frame."""

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
    return (f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" '
            f'font-weight="{weight}" {_S} stroke="none" {style}>{s}</text>')


# ---------------------------------------------------------------- 1. timeline
def timeline():
    ev = [(1943, "McCulloch", "&amp; Pitts", "formal neuron"),
          (1958, "Rosenblatt", "", "the perceptron"),
          (1986, "Rumelhart,", "Hinton, Williams", "backpropagation"),
          (1989, "Cybenko;", "Hornik et al.", "universal approx."),
          (2012, "Krizhevsky", "et al.", "AlexNet, GPUs"),
          (2026, "", "", "this notebook")]
    s = HEAD.format(w=880, h=210)
    s += '<line x1="60" y1="112" x2="820" y2="112" marker-end="url(#a)"/>'
    for i, (yr, a, b, c) in enumerate(ev):
        x = 92 + i * 146
        s += f'<line x1="{x}" y1="104" x2="{x}" y2="120"/>'
        s += f'<circle cx="{x}" cy="112" r="4.5" fill="#111"/>'
        s += _t(x, 88, str(yr), 15, weight=600)
        s += _t(x, 146, a, 11.5)
        s += _t(x, 160, b, 11.5)
        s += _t(x, 180, c, 11.5, style='font-style="italic" opacity=".62"')
    return s + "</svg>"





# ------------------------------------------------------------- 3. activations
def activations():
    s = HEAD.format(w=880, h=300)
    panels = [(70, "ReLU", "max(0, z)", "relu"),
              (330, "Sigmoid", "1 / (1 + e&#8315;&#7523;)", "sig"),
              (590, "Tanh", "tanh(z)", "tanh")]
    for (x0, name, form, kind) in panels:
        w, h, y0 = 200, 140, 60
        cx, cy = x0 + w / 2, y0 + h / 2
        s += f'<line x1="{x0}" y1="{cy}" x2="{x0+w}" y2="{cy}" opacity=".3"/>'
        s += f'<line x1="{cx}" y1="{y0}" x2="{cx}" y2="{y0+h}" opacity=".3"/>'
        if kind == "relu":
            s += f'<path d="M{x0+10},{cy} L{cx},{cy} L{x0+w-10},{y0+14}" stroke-width="2"/>'
        elif kind == "sig":
            pts = " ".join(f"{x0+10+i*(w-20)/40},{cy+58-116/(1+2.718**(-(i-20)/3.2))}"
                           for i in range(41))
            s += f'<polyline points="{pts}" stroke-width="2"/>'
        else:
            import math
            pts = " ".join(f"{x0+10+i*(w-20)/40},{cy-58*math.tanh((i-20)/5)}"
                           for i in range(41))
            s += f'<polyline points="{pts}" stroke-width="2"/>'
        s += _t(cx, y0 - 16, name, 14, weight=600)
        s += _t(cx, y0 + h + 24, form, 12.5, style='opacity=".65"')
    s += '<line x1="60" y1="248" x2="820" y2="248" opacity=".22"/>'
    s += _t(440, 278,
            "Without &#966;, stacking layers collapses:  W&#8322;(W&#8321;x) = (W&#8322;W&#8321;)x  "
            "&#8212; still one linear map.", 13.5, weight=500)
    return s + "</svg>"





# ------------------------------------------------------------ 5. training loop
def training_loop():
    s = HEAD.format(w=880, h=300)
    box = [(70, "Forward pass", "predict &#375; from x"),
           (280, "Loss", "how wrong?  (&#375; &#8722; y)&#178;"),
           (490, "Backprop", "&#8706;loss / &#8706;w for every w"),
           (700, "Update", "w &#8592; w &#8722; &#951; &#183; &#8706;loss/&#8706;w")]
    for i, (x, t, sub) in enumerate(box):
        s += f'<rect x="{x}" y="86" width="150" height="76" rx="3"/>'
        s += _t(x + 75, 116, t, 14, weight=600)
        s += _t(x + 75, 138, sub, 11, style='opacity=".6"')
        if i < 3:
            s += f'<line x1="{x+152}" y1="124" x2="{x+206}" y2="124" marker-end="url(#a)"/>'
    s += ('<path d="M775,164 L775,206 L145,206 L145,164" marker-end="url(#a)" '
          'stroke-dasharray="5 4"/>')
    s += _t(460, 226, "repeat for every batch, for every epoch", 12,
            style='font-style="italic" opacity=".6"')
    s += '<line x1="60" y1="252" x2="820" y2="252" opacity=".22"/>'
    s += _t(440, 278, "&#951; is the learning rate. Adam adapts it per weight "
                      "(Kingma &amp; Ba, 2015).", 13, weight=500)
    return s + "</svg>"







# ------------------------------------------------------------------ 2. neuron
def neuron():
    s = HEAD.format(w=880, h=330)
    xs = [(96, 72, "1"), (96, 132, "2"), (96, 216, "n")]
    for (x, y, sub) in xs:
        s += f'<circle cx="{x}" cy="{y}" r="21"/>'
        s += _t(x, y + 5, f'x<tspan font-size="10" dy="3">{sub}</tspan>', 15)
    s += _t(96, 178, "&#8942;", 20)
    s += '<circle cx="96" cy="282" r="21" stroke-dasharray="3 3"/>' + _t(96, 287, "1", 15)
    s += _t(96, 320, "bias input", 10.5, style='opacity=".55"')

    rows = [(72, "w<tspan font-size='9.5' dy='3'>1</tspan>"),
            (132, "w<tspan font-size='9.5' dy='3'>2</tspan>"),
            (216, "w<tspan font-size='9.5' dy='3'>n</tspan>"),
            (282, "b")]
    for (y, lab) in rows:
        s += f'<path d="M118,{y} C 200,{y} 214,168 288,168" marker-end="url(#ao)"/>'
        s += _t(150, y - 9 if lab != "b" else y + 20, lab, 13, anchor="start", weight=500)

    s += '<rect x="292" y="126" width="84" height="84" rx="3"/>'
    s += _t(334, 166, "&#931;", 30)
    s += _t(334, 196, "sum", 10.5, style='opacity=".55"')
    s += '<line x1="376" y1="168" x2="434" y2="168" marker-end="url(#a)"/>'
    s += _t(405, 155, "z", 13, weight=600)
    s += '<rect x="438" y="126" width="84" height="84" rx="3"/>'
    s += _t(480, 172, "&#966;", 28)
    s += _t(480, 200, "activation", 10.5, style='opacity=".55"')
    s += '<line x1="522" y1="168" x2="590" y2="168" marker-end="url(#a)"/>'
    s += '<circle cx="614" cy="168" r="23" stroke-width="2"/>' + _t(614, 174, "a", 16, weight=600)
    s += _t(614, 212, "output", 10.5, style='opacity=".55"')

    s += '<line x1="684" y1="104" x2="684" y2="234" opacity=".25"/>'
    s += _t(786, 142, "z = &#8721; w&#7522;x&#7522; + b", 17, weight=500)
    s += _t(786, 174, "a = &#966;(z)", 17, weight=500)
    s += _t(786, 208, "w and b are learned.", 11.5, style='opacity=".6"')
    s += _t(786, 224, "&#966; is chosen by you.", 11.5, style='opacity=".6"')
    return s + "</svg>"


# ----------------------------------------------------------------- 4. network
def network():
    s = HEAD.format(w=880, h=340)
    layers = [(140, 4, "Input", "28 sensor readings"),
              (350, 5, "Hidden 1", "256 neurons"),
              (560, 5, "Hidden 2", "128 neurons"),
              (760, 1, "Output", "1 number, Wh")]
    pos = []
    for (x, n, name, sub) in layers:
        ys = [186 + (i - (n - 1) / 2) * 42 for i in range(n)]
        pos.append(ys)
        s += _t(x, 44, name, 13.5, weight=600)
        s += _t(x, 62, sub, 11, style='opacity=".55"')
    for li in range(len(layers) - 1):
        for y1 in pos[li]:
            for y2 in pos[li + 1]:
                s += (f'<line x1="{layers[li][0]+17}" y1="{y1}" '
                      f'x2="{layers[li+1][0]-17}" y2="{y2}" opacity=".16"/>')
    for li, (x, n, _, _) in enumerate(layers):
        for y in pos[li]:
            s += f'<circle cx="{x}" cy="{y}" r="16" fill="#fff"/>'
    s += '<line x1="60" y1="300" x2="820" y2="300" opacity=".22"/>'
    s += _t(440, 326, "Every edge is one weight. Every circle adds one bias. "
                      "This network has about 42,000 of them.", 13, weight=500)
    return s + "</svg>"


# ------------------------------------------------------------- 6. overfitting
def overfitting():
    e = 2.718281828
    s = HEAD.format(w=880, h=330)
    x0, y0, w, h = 96, 56, 400, 190
    s += f'<line x1="{x0}" y1="{y0+h}" x2="{x0+w}" y2="{y0+h}"/>'
    s += f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y0+h}"/>'
    s += _t(x0 + w / 2, y0 + h + 30, "epoch &#8594;", 11.5, style='opacity=".6"')
    s += _t(x0 - 16, y0 + 10, "loss", 11.5, anchor="end", style='opacity=".6"')

    def ytr(i):  return y0 + 16 + 152 * (1 - e ** (-i / 10))
    def yval(i): return y0 + 16 + 152 * (1 - e ** (-i / 7)) - 0.085 * max(0, i - 20) ** 2

    s += ('<polyline stroke-width="2" points="'
          + " ".join(f"{x0+i*w/50},{ytr(i):.1f}" for i in range(51)) + '"/>')
    s += ('<polyline stroke-width="2" stroke-dasharray="6 4" points="'
          + " ".join(f"{x0+i*w/50},{yval(i):.1f}" for i in range(51)) + '"/>')
    bx = x0 + 21 * w / 50
    s += f'<line x1="{bx}" y1="{y0}" x2="{bx}" y2="{y0+h}" opacity=".45" stroke-dasharray="2 4"/>'
    s += f'<circle cx="{bx}" cy="{yval(21):.1f}" r="4" fill="#111" stroke="none"/>'
    s += _t(bx, y0 - 12, "stop here", 11, weight=500)
    s += _t(x0 + w, y0 + 44, "validation", 12, anchor="end", weight=500)
    s += _t(x0 + w - 8, y0 + h - 40, "training", 12, anchor="end", weight=500)
    s += _t(x0 + w - 4, y0 + 70, "memorising, not learning", 10.5, anchor="end",
            style='opacity=".55"')

    s += '<line x1="548" y1="56" x2="548" y2="252" opacity=".25"/>'
    s += _t(710, 78, "One dataset, three jobs", 13.5, weight=600)
    bx0 = 596
    for (lab, wdt, sub) in [("TRAIN", 132, "fit the weights"),
                            ("VAL", 52, "when to stop"),
                            ("TEST", 52, "report once")]:
        s += f'<rect x="{bx0}" y="102" width="{wdt}" height="34" rx="2"/>'
        s += _t(bx0 + wdt / 2, 124, lab, 11.5, weight=600)
        bx0 += wdt + 4
    s += _t(596, 156, "70%", 10.5, anchor="start", style='opacity=".55"')
    s += _t(758, 156, "15%", 10.5, style='opacity=".55"')
    s += _t(814, 156, "15%", 10.5, style='opacity=".55"')
    s += _t(710, 194, "Touch TEST more than once", 11.5, style='opacity=".6"')
    s += _t(710, 210, "and it stops being a test.", 11.5, style='opacity=".6"')

    s += '<line x1="60" y1="282" x2="820" y2="282" opacity=".22"/>'
    s += _t(440, 308, "Dropout and early stopping are the two cheapest defences "
                      "(Srivastava et al., 2014).", 13, weight=500)
    return s + "</svg>"


# ----------------------------------------------------------------- 7. scaling
def scaling():
    s = HEAD.format(w=880, h=310)
    # elongated bowl - gradient bounces across the narrow axis
    cx, cy = 236, 152
    for k in (1, .74, .5, .28, .12):
        s += f'<ellipse cx="{cx}" cy="{cy}" rx="{126*k}" ry="{40*k}" opacity=".38"/>'
    zig = ("M340,124 L146,170 L318,141 L166,163 L296,149 L192,157 "
           "L266,152 L214,155 L246,152")
    s += f'<path d="{zig}" stroke-width="1.9" marker-end="url(#ao)"/>'
    s += f'<circle cx="{cx}" cy="{cy}" r="3.5" fill="#111" stroke="none"/>'
    s += _t(cx, 56, "Unscaled features", 14, weight=600)
    s += _t(cx, 246, "many small steps, mostly sideways", 11.5, style='opacity=".6"')

    cx2 = 642
    for k in (1, .74, .5, .28, .12):
        s += f'<circle cx="{cx2}" cy="{cy}" r="{72*k}" opacity=".38"/>'
    s += (f'<path d="M712,96 L668,128 L648,146 L643,151" stroke-width="1.9" '
          f'marker-end="url(#ao)"/>')
    s += f'<circle cx="{cx2}" cy="{cy}" r="3.5" fill="#111" stroke="none"/>'
    s += _t(cx2, 56, "Standardised features", 14, weight=600)
    s += _t(cx2, 246, "a few steps, straight to the bottom", 11.5, style='opacity=".6"')
    s += _t(440, 156, "vs", 13, style='opacity=".4"')

    s += '<line x1="60" y1="266" x2="820" y2="266" opacity=".22"/>'
    s += _t(440, 292, "One learning rate is shared by every weight, so features on "
                      "bigger scales dominate the step.", 13, weight=500)
    return s + "</svg>"


ALL = {"timeline": timeline, "neuron": neuron, "activations": activations,
       "network": network, "training_loop": training_loop,
       "overfitting": overfitting, "scaling": scaling}


# ------------------------------------------------------- 8. agent anatomy
def agent_anatomy():
    s = HEAD.format(w=880, h=330)
    s += '<rect x="40" y="56" width="176" height="184" rx="3"/>'
    s += _t(128, 44, "Agent definition", 12.5, weight=600)
    for i, (k, v) in enumerate([("name", "Energy Advocate"),
                                ("role", "argue for low EUI"),
                                ("instructions", "your ONLY concern is..."),
                                ("color", "#3B82F6"),
                                ("icon", "zap")]):
        y = 84 + i * 32
        s += _t(56, y, k, 11.5, anchor="start", weight=500)
        s += _t(56, y + 14, v, 10, anchor="start", style='opacity=".55"')
    s += _t(128, 262, "five fields, no magic", 10.5, style='opacity=".55"')

    s += '<path d="M216,116 L286,116" marker-end="url(#a)"/>'
    s += '<path d="M216,180 L286,180" marker-end="url(#a)" stroke-dasharray="4 3"/>'
    s += '<rect x="290" y="86" width="196" height="60" rx="3"/>'
    s += _t(388, 110, "system prompt", 12.5, weight=600)
    s += _t(388, 130, "instructions + output schema", 10.5, style='opacity=".55"')
    s += '<rect x="290" y="158" width="196" height="60" rx="3"/>'
    s += _t(388, 182, "user message", 12.5, weight=600)
    s += _t(388, 202, "geometry + climate data", 10.5, style='opacity=".55"')
    s += _t(388, 250, "context injected at run time", 10.5, style='opacity=".55"')

    s += '<path d="M486,116 C 520,116 520,152 552,152" marker-end="url(#ao)"/>'
    s += '<path d="M486,188 C 520,188 520,152 552,152" marker-end="url(#ao)"/>'
    s += '<rect x="556" y="122" width="104" height="60" rx="3" stroke-width="2"/>'
    s += _t(608, 158, "LLM", 17, weight=600)
    s += '<line x1="660" y1="152" x2="716" y2="152" marker-end="url(#a)"/>'
    s += '<rect x="720" y="122" width="120" height="60" rx="3"/>'
    s += _t(780, 148, "structured", 12, weight=600)
    s += _t(780, 166, "JSON response", 12, weight=600)

    s += '<line x1="60" y1="288" x2="820" y2="288" opacity=".22"/>'
    s += _t(440, 312, "Every agent framework wraps this. The wrappers differ; "
                      "the pattern does not.", 13, weight=500)
    return s + "</svg>"


# ------------------------------------------------------ 9. orchestration
def orchestration():
    s = HEAD.format(w=880, h=320)
    s += '<line x1="292" y1="46" x2="292" y2="236" opacity=".25" stroke-dasharray="3 4"/>'
    s += '<line x1="596" y1="46" x2="596" y2="236" opacity=".25" stroke-dasharray="3 4"/>'
    for x, n, lab in [(150, "PHASE 1", "sequential"), (444, "PHASE 2", "parallel"),
                      (740, "PHASE 3", "sequential")]:
        s += _t(x, 40, n, 10.5, weight=700)
        s += _t(x, 258, lab, 11, style='font-style="italic" opacity=".6"')

    s += '<rect x="76" y="122" width="148" height="52" rx="3"/>'
    s += _t(150, 146, "Site Researcher", 12.5, weight=600)
    s += _t(150, 164, "climate, grid, code", 10, style='opacity=".55"')
    s += _t(150, 200, "everyone needs its output", 10, style='opacity=".5"')

    for i, (nm, sub) in enumerate([("Energy Advocate", "wants less glass"),
                                   ("Daylight Advocate", "wants more glass"),
                                   ("Carbon Advocate", "wants compact form")]):
        y = 76 + i * 62
        s += f'<rect x="370" y="{y}" width="150" height="48" rx="3"/>'
        s += _t(445, y + 20, nm, 11.5, weight=600)
        s += _t(445, y + 36, sub, 9.5, style='opacity=".55"')
        s += f'<path d="M226,148 C 300,148 300,{y+24} 366,{y+24}" marker-end="url(#ao)"/>'
        s += f'<path d="M522,{y+24} C 590,{y+24} 590,148 662,148" marker-end="url(#ao)"/>'
    s += _t(445, 240, "they never see each other", 10, style='opacity=".5"')

    s += '<rect x="666" y="118" width="150" height="60" rx="3" stroke-width="2"/>'
    s += _t(741, 142, "Manager", 13, weight=600)
    s += _t(741, 160, "resolves the conflicts", 10, style='opacity=".55"')
    s += _t(741, 200, "needs all of them", 10, style='opacity=".5"')

    s += '<line x1="60" y1="276" x2="820" y2="276" opacity=".22"/>'
    s += _t(440, 302, "Gather context, fan out in parallel, synthesise. "
                      "The orchestration decision is what waits for what.", 13, weight=500)
    return s + "</svg>"


# ------------------------------------------------- 10. framework landscape
def framework_landscape():
    s = HEAD.format(w=880, h=360)
    s += '<line x1="90" y1="292" x2="820" y2="292" marker-end="url(#a)"/>'
    s += '<line x1="90" y1="292" x2="90" y2="48" marker-end="url(#a)"/>'
    s += _t(455, 320, "programming background required &#8594;", 11.5,
            style='opacity=".6"')
    s += ('<text x="52" y="170" font-size="11.5" text-anchor="middle" '
          'font-family="Montserrat, sans-serif" fill="#111" stroke="none" '
          'opacity=".6" transform="rotate(-90 52 170)">CAD integration &#8594;</text>')

    pts = [(170, 258, "01", "OpenAI SDK", "raw Python"),
           (168, 128, "02", "OpenAI SDK", "in Grasshopper"),
           (386, 252, "03", "FastMCP", "+ any LLM UI"),
           (556, 160, "04", "+ RhinoCompute", "large functions"),
           (742, 92, "05", "+ Strands + Streamlit", "3D in-app"),
           (330, 92, "06", "Grasshopper + Swiftlet", "no code, instant 3D")]
    for x, y, n, a, b in pts:
        s += f'<circle cx="{x}" cy="{y}" r="17" fill="#fff" stroke-width="1.6"/>'
        s += _t(x, y + 5, n, 12.5, weight=700)
        s += _t(x, y - 26, a, 11, weight=600)
        s += _t(x, y + 34, b, 9.5, style='opacity=".55"')
    return s + "</svg>"


ALL.update({"agent_anatomy": agent_anatomy, "orchestration": orchestration,
            "framework_landscape": framework_landscape})
