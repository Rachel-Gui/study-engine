"""figures_py.py - diagrams for the Python-from-zero and EDA chapters.
Same conventions as figures.py: black line art, Montserrat, Spirit Purple for
one emphasis element, a viewBox so it scales on the site and in 4K frames."""
import math

ACC = "#4b2e83"
GOLD = "#e8e3d3"
_S = ('font-family="Montserrat, sans-serif" fill="#111"')
HEAD = ('<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" '
        'stroke="#111" fill="none" stroke-width="1.4" '
        'stroke-linecap="round" stroke-linejoin="round">'
        '<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" '
        'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
        '<path d="M0,0 L10,5 L0,10 z" fill="#111" stroke="none"/></marker>'
        '<marker id="ao" viewBox="0 0 10 10" refX="9" refY="5" '
        'markerWidth="5" markerHeight="5" orient="auto-start-reverse">'
        '<path d="M0,0 L10,5 L0,10 z" fill="#111" stroke="none"/></marker>'
        '<marker id="ap" viewBox="0 0 10 10" refX="9" refY="5" '
        'markerWidth="5" markerHeight="5" orient="auto-start-reverse">'
        f'<path d="M0,0 L10,5 L0,10 z" fill="{ACC}" stroke="none"/></marker></defs>')
MONO = 'font-family="IBM Plex Mono, Menlo, monospace"'


def _t(x, y, s, size=13, anchor="middle", weight=400, style=""):
    base = _S.replace(' fill="#111"', "") if "fill=" in style else _S   # first attribute wins in SVG
    return (f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" '
            f'font-weight="{weight}" {base} stroke="none" {style}>{s}</text>')


def _m(x, y, s, size=12.5, anchor="middle", style=""):
    fill = "" if "fill=" in style else 'fill="#111"'
    s = s.replace("  ", "&#160;&#160;")          # SVG collapses runs of spaces
    return (f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" '
            f'{MONO} {fill} stroke="none" {style}>{s}</text>')


def _box(x, y, w, h, lw=1.4, dash="", fill="#fff", rx=3, stroke="#111"):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{lw}"{d}/>'


def _arrow(x1, y1, x2, y2, purple=False, dash=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    col = f' stroke="{ACC}"' if purple else ""
    mk = "ap" if purple else "ao"
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" marker-end="url(#{mk})"{col}{d}/>'


def _foot(s, y, text, w=880):
    s += f'<line x1="60" y1="{y}" x2="{w - 60}" y2="{y}" opacity=".22"/>'
    return s + _t(w / 2, y + 26, text, 13, weight=500)


# ---------------------------------------------------------------- run model
def run_model():
    s = HEAD.format(w=880, h=320)
    s += _box(50, 70, 230, 150, fill="#fbfbfa")
    s += _t(165, 56, "1. your program (a text file)", 12, weight=600)
    for i, l in enumerate(["width = 6", "depth = 4", "area = width * depth", 'print("area", area)']):
        s += _m(66, 100 + i * 26, f"{i + 1}  {l}", 12, anchor="start")
    s += _arrow(284, 145, 336, 145)
    s += _box(340, 96, 150, 98, lw=2)
    s += _t(415, 128, "2. Python", 14, weight=600)
    s += _t(415, 148, "reads line 1, runs it,", 10, style='opacity=".6"')
    s += _t(415, 162, "reads line 2, runs it …", 10, style='opacity=".6"')
    s += _t(415, 180, "top to bottom, one at a time", 10, style='opacity=".6"')
    s += _arrow(494, 120, 546, 96)
    s += _arrow(494, 170, 546, 196)
    s += _box(550, 46, 280, 100, fill="#fff")
    s += _t(690, 40, "3. memory: names → values", 12, weight=600)
    for i, (k, v) in enumerate([("width", "6"), ("depth", "4"), ("area", "24")]):
        y = 70 + i * 26
        s += _box(566, y - 14, 70, 20, fill=GOLD, stroke=ACC, lw=1)
        s += _m(601, y, k, 11.5)
        s += _arrow(640, y - 4, 664, y - 4, purple=True)
        s += _box(670, y - 14, 44, 20, fill="#fff", lw=1)
        s += _m(692, y, v, 11.5)
    s += _box(550, 176, 280, 60, fill="#111")
    s += _t(690, 170, "4. the screen", 12, weight=600)
    s += _m(566, 210, "area 24", 13, anchor="start", style='fill="#f3f3f1"')
    s = _foot(s, 262, "A line either changes memory (a name gets a value) or produces output. That is all a program is.")
    return s + "</svg>"


# ------------------------------------------------------------- variable box
def variable_box():
    s = HEAD.format(w=880, h=300)
    s += _t(200, 52, "width = 6", 14, weight=600, style=MONO)
    s += _box(150, 100, 100, 26, fill=GOLD, stroke=ACC, lw=1.2)
    s += _m(200, 118, "width", 12.5)
    s += _arrow(254, 113, 300, 113, purple=True)
    s += _box(306, 92, 64, 42, lw=1.6)
    s += _m(338, 118, "6", 15)
    s += _t(200, 160, "a name is a label, not a box", 11, style='opacity=".6"')
    s += _t(200, 176, "the value lives elsewhere", 11, style='opacity=".6"')

    s += _t(600, 52, "width = width + 2", 14, weight=600, style=MONO)
    s += _box(550, 100, 100, 26, fill=GOLD, stroke=ACC, lw=1.2)
    s += _m(600, 118, "width", 12.5)
    s += _box(706, 92, 64, 42, lw=1, dash="4 3", stroke="#999")
    s += _m(738, 118, "6", 15, style='fill="#999"')
    s += _box(706, 150, 64, 42, lw=1.6)
    s += _m(738, 176, "8", 15)
    s += _arrow(654, 113, 700, 166, purple=True)
    s += _t(600, 220, "the right side is computed first (6 + 2),", 11, style='opacity=".6"')
    s += _t(600, 236, "then the label moves to the new value", 11, style='opacity=".6"')
    s = _foot(s, 262, "= does not mean \"equals\". It means: work out the right side, then attach the name on the left to it.")
    return s + "</svg>"


# ---------------------------------------------------------------- four types
def types_four():
    s = HEAD.format(w=880, h=300)
    cols = [("int", "whole numbers", ["3", "-12", "768"], "count, index, loop"),
            ("float", "decimal numbers", ["0.98", "22.31", "3.0"], "measure, average"),
            ("str", "text, in quotes", ['"kitchen"', "'N'", '"3"'], "names, labels, files"),
            ("bool", "true or false", ["True", "False"], "decisions, filters")]
    for i, (name, sub, ex, use) in enumerate(cols):
        x = 60 + i * 200
        s += _box(x, 56, 176, 176, lw=1.4)
        s += _box(x, 56, 176, 40, fill=GOLD, stroke="#111", lw=1.4)
        s += _m(x + 88, 82, name, 15, style='font-weight="600"')
        s += _t(x + 88, 116, sub, 11.5, style='opacity=".65"')
        for j, e in enumerate(ex):
            s += _m(x + 88, 146 + j * 22, e, 12.5)
        s += _t(x + 88, 222, use, 10.5, style=f'fill="{ACC}" font-weight="500"')
    s = _foot(s, 258, "type(x) tells you which one you have. \"3\" + 1 is an error; 3 + 1 is 4. The quotes are the difference.")
    return s + "</svg>"


# ------------------------------------------------------------------ indexing
def indexing():
    s = HEAD.format(w=880, h=330)
    items = ["kitchen", "living", "hall", "bed 1", "bath", "bed 2"]
    x0, w = 110, 110
    s += _m(60, 52, 'rooms = ["kitchen", "living", "hall", "bed 1", "bath", "bed 2"]', 13, anchor="start")
    for i, it in enumerate(items):
        x = x0 + i * w
        s += _box(x, 110, w - 6, 50, lw=1.4)
        s += _m(x + (w - 6) / 2, 141, f'"{it}"', 12.5)
        s += _t(x + (w - 6) / 2, 98, str(i), 13, weight=700, style=f'fill="{ACC}"')
        s += _t(x + (w - 6) / 2, 184, str(i - len(items)), 12, style='opacity=".55"')
    s += _t(x0 - 26, 98, "index", 10.5, anchor="end", style=f'fill="{ACC}"')
    s += _t(x0 - 26, 184, "from the end", 10.5, anchor="end", style='opacity=".55"')
    # slice bracket rooms[1:4]
    s += f'<path d="M{x0 + w + 2},214 L{x0 + w + 2},226 L{x0 + 4 * w - 8},226 L{x0 + 4 * w - 8},214" stroke="{ACC}" stroke-width="2"/>'
    s += _m(x0 + 2.5 * w, 246, 'rooms[1:4]  →  ["living", "hall", "bed 1"]', 12.5, style=f'fill="{ACC}"')
    s += _t(x0 + 2.5 * w, 264, "start is included, stop is not: 1, 2, 3", 10.5, style='opacity=".6"')
    s = _foot(s, 288, 'Counting starts at 0. rooms[0] is the first item, rooms[-1] the last, rooms[1:4] a slice of three.')
    return s + "</svg>"


# --------------------------------------------------------------- collections
def collections():
    s = HEAD.format(w=880, h=330)
    cols = [("list", "[ ]", '["N", "S", "N"]', ["ordered", "changeable", "repeats allowed"], "a sequence you build up"),
            ("tuple", "( )", '(6, 4)', ["ordered", "fixed once made", "repeats allowed"], "a record: width, depth"),
            ("set", "{ }", '{"N", "S"}', ["no order", "changeable", "no repeats"], "which orientations occur"),
            ("dict", "{k: v}", '{"kitchen": 12}', ["key → value", "changeable", "keys unique"], "look something up by name")]
    for i, (name, br, ex, props, use) in enumerate(cols):
        x = 60 + i * 200
        s += _box(x, 56, 176, 214)
        s += _box(x, 56, 176, 42, fill=GOLD, lw=1.4)
        s += _m(x + 60, 84, name, 15, style='font-weight="600"')
        s += _m(x + 140, 84, br, 13, style='opacity=".6"')
        s += _m(x + 88, 122, ex, 11.5)
        for j, p in enumerate(props):
            s += _t(x + 16, 156 + j * 20, "• " + p, 11.5, anchor="start")
        s += _t(x + 88, 246, use, 10.5, style=f'fill="{ACC}" font-weight="500"')
    s = _foot(s, 294, "Four ways to hold several values. Choose by what you need: order, change, uniqueness, or lookup by name.")
    return s + "</svg>"


# --------------------------------------------------------------- dict lookup
def dict_lookup():
    s = HEAD.format(w=880, h=300)
    s += _m(60, 52, 'areas = {"kitchen": 12, "living": 30, "bath": 5}', 13, anchor="start")
    pairs = [("kitchen", "12"), ("living", "30"), ("bath", "5")]
    for i, (k, v) in enumerate(pairs):
        y = 100 + i * 44
        s += _box(150, y - 15, 120, 30, fill=GOLD, stroke=ACC, lw=1.2)
        s += _m(210, y + 5, f'"{k}"', 12.5)
        s += _arrow(276, y, 330, y, purple=True)
        s += _box(336, y - 15, 60, 30)
        s += _m(366, y + 5, v, 12.5)
    s += _t(210, 76, "keys", 11, style=f'fill="{ACC}" font-weight="600"')
    s += _t(366, 76, "values", 11, weight=600)
    s += _m(560, 104, 'areas["living"]', 13, anchor="start")
    s += _t(560, 122, "→ 30   (look up by key, not by position)", 11, anchor="start", style='opacity=".65"')
    s += _m(560, 156, 'areas["garage"] = 18', 13, anchor="start")
    s += _t(560, 174, "→ adds a new pair", 11, anchor="start", style='opacity=".65"')
    s += _m(560, 208, 'areas["attic"]', 13, anchor="start")
    s += _t(560, 226, "→ KeyError: no such key", 11, anchor="start", style='fill="#b23b3b"')
    s = _foot(s, 258, "A dictionary is a lookup table. Position does not matter; the key does.")
    return s + "</svg>"


# ------------------------------------------------------------------ for loop
def for_loop():
    s = HEAD.format(w=880, h=320)
    s += _m(60, 48, "for room in rooms:", 13, anchor="start")
    s += _m(60, 68, "    print(room)", 13, anchor="start")
    # flow
    s += _box(340, 60, 190, 44, lw=1.6)
    s += _t(435, 87, "any items left?", 13, weight=600)
    s += _arrow(435, 106, 435, 146)
    s += _t(452, 128, "yes", 11, anchor="start", style=f'fill="{ACC}"')
    s += _box(340, 150, 190, 44, fill=GOLD, stroke=ACC, lw=1.2)
    s += _t(435, 170, "room = the next item", 12, weight=500)
    s += _t(435, 186, "run the indented block", 10.5, style='opacity=".65"')
    s += f'<path d="M340,172 L300,172 L300,82 L336,82" marker-end="url(#ao)"/>'
    s += _t(292, 130, "back", 10.5, anchor="end", style='opacity=".6"')
    s += _arrow(534, 82, 640, 82)
    s += _t(590, 72, "no", 11, style=f'fill="{ACC}"')
    s += _box(646, 60, 170, 44)
    s += _t(731, 87, "carry on after the loop", 12)
    # the sequence
    for i, r in enumerate(["kitchen", "living", "hall"]):
        s += _box(60 + i * 90, 110, 82, 28, lw=1)
        s += _m(101 + i * 90, 129, r, 11)
    s += _t(60, 164, "rooms — the loop visits each one, in order,", 10.5, anchor="start", style='opacity=".65"')
    s += _t(60, 180, "and the name room points at the current one", 10.5, anchor="start", style='opacity=".65"')
    s += _t(60, 220, "1st pass: room = \"kitchen\"", 11, anchor="start", style=MONO)
    s += _t(60, 238, "2nd pass: room = \"living\"", 11, anchor="start", style=MONO)
    s += _t(60, 256, "3rd pass: room = \"hall\"  → items left? no", 11, anchor="start", style=MONO)
    s = _foot(s, 280, "A for loop runs the indented block once per item. You never write the counting yourself.")
    return s + "</svg>"


# ---------------------------------------------------------------- while loop
def while_loop():
    s = HEAD.format(w=880, h=320)
    s += _m(60, 48, "floors = 0", 13, anchor="start")
    s += _m(60, 68, "while floors < 3:", 13, anchor="start")
    s += _m(60, 88, "    floors = floors + 1", 13, anchor="start")
    s += _box(340, 60, 190, 44, lw=1.6)
    s += _t(435, 87, "is floors < 3 true?", 13, weight=600)
    s += _arrow(435, 106, 435, 146)
    s += _t(452, 128, "yes", 11, anchor="start", style=f'fill="{ACC}"')
    s += _box(340, 150, 190, 44, fill=GOLD, stroke=ACC, lw=1.2)
    s += _t(435, 176, "run the indented block", 12, weight=500)
    s += f'<path d="M340,172 L300,172 L300,82 L336,82" marker-end="url(#ao)"/>'
    s += _t(292, 130, "check again", 10.5, anchor="end", style='opacity=".6"')
    s += _arrow(534, 82, 640, 82)
    s += _t(590, 72, "no", 11, style=f'fill="{ACC}"')
    s += _box(646, 60, 170, 44)
    s += _t(731, 87, "carry on after the loop", 12)
    for i, (f, chk) in enumerate([("0", "0 < 3  true"), ("1", "1 < 3  true"), ("2", "2 < 3  true"), ("3", "3 < 3  FALSE → stop")]):
        s += _t(60, 130 + i * 20, f"floors = {f}   check: {chk}", 11, anchor="start", style=MONO)
    s += _t(60, 226, "The block must change something the condition looks at.", 11, anchor="start", weight=500)
    s += _t(60, 244, "Forget that, and the loop never ends (Ctrl+C stops it).", 11, anchor="start", style='fill="#b23b3b"')
    s = _foot(s, 280, "for: when you know what to visit. while: when you know when to stop.")
    return s + "</svg>"


# ------------------------------------------------------------- function call
def function_call():
    s = HEAD.format(w=880, h=340)
    s += _m(60, 48, "def area(width, depth):", 13, anchor="start")
    s += _m(60, 68, "    result = width * depth", 13, anchor="start")
    s += _m(60, 88, "    return result", 13, anchor="start")
    s += _m(60, 122, "kitchen = area(4, 3)", 13, anchor="start", style=f'fill="{ACC}" font-weight="600"')
    # the call
    s += _box(420, 60, 300, 150, lw=1.8)
    s += _t(570, 50, "inside the call: a private workspace", 11.5, weight=600)
    s += _box(440, 80, 110, 26, fill=GOLD, stroke=ACC, lw=1.2); s += _m(495, 98, "width", 12)
    s += _arrow(554, 93, 588, 93, purple=True); s += _box(594, 80, 40, 26); s += _m(614, 98, "4", 12)
    s += _box(440, 116, 110, 26, fill=GOLD, stroke=ACC, lw=1.2); s += _m(495, 134, "depth", 12)
    s += _arrow(554, 129, 588, 129, purple=True); s += _box(594, 116, 40, 26); s += _m(614, 134, "3", 12)
    s += _box(440, 152, 110, 26, fill=GOLD, stroke=ACC, lw=1.2); s += _m(495, 170, "result", 12)
    s += _arrow(554, 165, 588, 165, purple=True); s += _box(594, 152, 40, 26); s += _m(614, 170, "12", 12)
    s += _t(730, 98, "arguments", 10.5, anchor="start", style='opacity=".6"')
    s += _t(730, 112, "arrive here", 10.5, anchor="start", style='opacity=".6"')
    # arrows in and out
    s += f'<path d="M232,118 C 300,118 330,93 416,93" marker-end="url(#ap)" stroke="{ACC}"/>'
    s += _t(320, 100, "4, 3 go in", 10.5, style=f'fill="{ACC}"')
    s += f'<path d="M420,190 C 340,190 320,140 250,132" marker-end="url(#ap)" stroke="{ACC}" stroke-dasharray="5 3"/>'
    s += _t(318, 178, "12 comes back", 10.5, style=f'fill="{ACC}"')
    s += _t(60, 160, "→ kitchen is now 12", 12, anchor="start", weight=500)
    s += _t(60, 200, "width, depth and result exist only inside the call.", 11, anchor="start", style='opacity=".7"')
    s += _t(60, 216, "After return, the workspace is thrown away.", 11, anchor="start", style='opacity=".7"')
    s += _t(60, 232, "Only the returned value survives — because you kept it.", 11, anchor="start", style='opacity=".7"')
    s = _foot(s, 296, "A function is a named block with its own workspace: values go in as arguments, one value comes back with return.")
    return s + "</svg>"


# ----------------------------------------------------------- class blueprint
def class_blueprint():
    s = HEAD.format(w=880, h=340)
    s += _box(60, 56, 250, 190, lw=1.8)
    s += _box(60, 56, 250, 36, fill=GOLD, lw=1.8)
    s += _m(185, 80, "class Room", 14, style='font-weight="600"')
    s += _t(76, 116, "attributes (data each room has)", 10.5, anchor="start", style=f'fill="{ACC}" font-weight="600"')
    s += _m(76, 136, "name, width, depth", 12, anchor="start")
    s += _t(76, 166, "methods (things a room can do)", 10.5, anchor="start", style=f'fill="{ACC}" font-weight="600"')
    s += _m(76, 186, "area()", 12, anchor="start")
    s += _m(76, 206, "describe()", 12, anchor="start")
    s += _t(185, 232, "the blueprint — no actual room yet", 10.5, style='opacity=".6"')
    s += _arrow(314, 150, 366, 150, purple=True)
    s += _t(340, 140, "Room(...)", 9.5, style=f'fill="{ACC}"')
    for i, (nm, w, d, a) in enumerate([("kitchen", 4, 3, 12), ("living", 6, 5, 30), ("bath", 2.5, 2, 5)]):
        x = 372 + i * 160
        s += _m(x + 73, 66, f'Room("{nm}", {w}, {d})', 9.5, style='opacity=".65"')
        s += _box(x, 76, 146, 150, lw=1.4)
        s += _box(x, 76, 146, 30, fill=GOLD, stroke=ACC, lw=1.2)
        s += _m(x + 73, 96, nm, 12.5, style='font-weight="600"')
        s += _m(x + 12, 128, f'name = "{nm}"', 10.5, anchor="start")
        s += _m(x + 12, 146, f"width = {w}", 10.5, anchor="start")
        s += _m(x + 12, 164, f"depth = {d}", 10.5, anchor="start")
        s += _m(x + 12, 196, f".area() -> {a}", 10.5, anchor="start", style=f'fill="{ACC}"')
    s += _t(612, 250, "three objects made from one class: same methods, their own data", 10.5, style='opacity=".65"')
    s = _foot(s, 296, "A class is a blueprint. Each object built from it carries its own attribute values and shares the methods.")
    return s + "</svg>"


# ------------------------------------------------------------------ imports
def imports():
    s = HEAD.format(w=880, h=320)
    s += _box(60, 80, 200, 150, lw=1.8)
    s += _t(160, 70, "your program", 12.5, weight=600)
    s += _m(76, 110, "import math", 11.5, anchor="start")
    s += _m(76, 130, "import numpy as np", 11.5, anchor="start")
    s += _m(76, 150, "from statistics import mean", 11.5, anchor="start")
    s += _m(76, 184, "math.sqrt(2)", 11.5, anchor="start", style=f'fill="{ACC}"')
    s += _m(76, 202, "np.array([1, 2])", 11.5, anchor="start", style=f'fill="{ACC}"')
    s += _m(76, 220, "mean([1, 2, 3])", 11.5, anchor="start", style=f'fill="{ACC}"')
    tools = [("math", "sqrt, pi, sin", "built in"), ("statistics", "mean, median", "built in"),
             ("random", "choice, shuffle", "built in"), ("numpy", "arrays, fast maths", "installed"),
             ("pandas", "tables", "installed"), ("matplotlib", "plots", "installed")]
    for i, (n, what, kind) in enumerate(tools):
        x = 330 + (i % 3) * 180; y = 80 + (i // 3) * 80
        s += _box(x, y, 160, 58, lw=1.2, fill="#fbfbfa")
        s += _m(x + 80, y + 22, n, 12.5, style='font-weight="600"')
        s += _t(x + 80, y + 38, what, 10.5, style='opacity=".65"')
        s += _t(x + 80, y + 52, kind, 9.5, style=f'fill="{ACC}"')
    s += _arrow(264, 130, 322, 110, dash="4 3")
    s += _arrow(264, 160, 322, 190, dash="4 3")
    s += _t(590, 250, "\"built in\" ships with Python. \"installed\" came from pip install (Setup 1).", 10.5, style='opacity=".65"')
    s = _foot(s, 276, "A library is a toolbox someone else wrote. import brings it in; the dot reaches inside it.")
    return s + "</svg>"


# ---------------------------------------------------------------- traceback
def traceback():
    s = HEAD.format(w=880, h=300)
    s += _box(60, 50, 520, 150, fill="#111", rx=4)
    lines = ['Traceback (most recent call last):', '  File "plan.py", line 4, in <module>',
             '    total = total + areas["attic"]', "                    ~~~~~^^^^^^^^^", "KeyError: 'attic'"]
    for i, l in enumerate(lines):
        col = "#f3f3f1" if i < 4 else "#ffb4b4"
        s += _m(76, 78 + i * 24, l, 12, anchor="start", style=f'fill="{col}"')
    notes = [(72, "read from the bottom up", 74), (78 + 24, "which file and which line", 98),
             (78 + 48, "the line itself", 122), (78 + 96, "the error type, then the detail", 170)]
    for _, txt, y in notes:
        s += _arrow(650, y, 588, y, purple=True)
        s += _t(656, y + 4, txt, 11, anchor="start", style=f'fill="{ACC}"')
    s += _t(60, 226, "Errors are not punishments; they are the most specific help you will get all day.", 11.5, anchor="start", weight=500)
    s += _t(60, 244, "Copy the last line into a search engine and you will usually find your answer in one click.", 11, anchor="start", style='opacity=".65"')
    s = _foot(s, 262, "Start at the bottom: the error type and message. Then go up one line to see where.")
    return s + "</svg>"


# ------------------------------------------------------------------ eda loop
def eda_loop():
    s = HEAD.format(w=880, h=350)
    steps = [("Load", "read the file"), ("Look", "head, shape, dtypes"), ("Clean", "missing, units, names"),
             ("Summarise", "describe, groupby"), ("Visualise", "hist, scatter, box"), ("Ask", "what does it show?")]
    n = len(steps); cx, cy, r = 300, 170, 78
    for i, (nm, sub) in enumerate(steps):
        a = -math.pi / 2 + i * 2 * math.pi / n
        x, y = cx + r * math.cos(a), cy + r * math.sin(a)
        s += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="30" fill="{"#fff" if i else GOLD}" stroke="{ACC if i == 0 else "#111"}" stroke-width="{2 if i == 0 else 1.4}"/>'
        s += _t(x, y + 4, nm, 11, weight=600)
        a2 = a + 2 * math.pi / n
        x1, y1 = cx + (r + 0) * math.cos(a + 0.34), cy + r * math.sin(a + 0.34)
        x2, y2 = cx + r * math.cos(a2 - 0.34), cy + r * math.sin(a2 - 0.34)
        s += f'<path d="M{x1:.1f},{y1:.1f} A{r},{r} 0 0 1 {x2:.1f},{y2:.1f}" marker-end="url(#ao)" opacity=".7"/>'
        c = math.cos(a)
        anchor = "start" if c > 0.1 else "end" if c < -0.1 else "middle"
        lx, ly = cx + (r + 38) * c, cy + (r + 44) * math.sin(a)
        s += _t(lx, ly + 4, sub, 10, anchor=anchor, style='opacity=".6"')
    s += _t(660, 116, "It is a loop, not a checklist.", 13.5, weight=600)
    s += _t(660, 142, "A plot raises a question; the question", 11, style='opacity=".7"')
    s += _t(660, 158, "sends you back to filter, group, or plot", 11, style='opacity=".7"')
    s += _t(660, 174, "again. Most of the value is in round two.", 11, style='opacity=".7"')
    s += _t(660, 216, "Write the question down before you plot.", 11.5, weight=500, style=f'fill="{ACC}"')
    s = _foot(s, 310, "Exploratory data analysis: looking before modelling. Every model in this course started here.")
    return s + "</svg>"


# --------------------------------------------------------- dataframe anatomy
def dataframe_anatomy():
    s = HEAD.format(w=880, h=330)
    cols = ["surface_area", "orientation", "glazing_area", "heating_load"]
    rows = [["514.5", "2", "0.0", "15.55"], ["563.5", "3", "0.1", "20.84"], ["588.0", "4", "0.25", "29.79"]]
    x0, y0, cw, rh = 150, 80, 150, 32
    s += _box(x0 - 60, y0, 60, rh, fill=GOLD, lw=1.2)
    for j, c in enumerate(cols):
        s += _box(x0 + j * cw, y0, cw, rh, fill=GOLD, lw=1.2)
        s += _m(x0 + j * cw + cw / 2, y0 + 21, c, 11.5, style='font-weight="600"')
    for i, r in enumerate(rows):
        y = y0 + rh * (i + 1)
        s += _box(x0 - 60, y, 60, rh, fill="#fbfbfa", lw=1.2)
        s += _m(x0 - 30, y + 21, str(i), 11.5, style='opacity=".6"')
        for j, v in enumerate(r):
            s += _box(x0 + j * cw, y, cw, rh, lw=1.2, fill=("#fff" if not (i == 1 and j == 3) else "#efeaf7"))
            s += _m(x0 + j * cw + cw / 2, y + 21, v, 11.5)
    s += _t(x0 - 30, y0 - 12, "index", 10.5, style=f'fill="{ACC}" font-weight="600"')
    s += _t(x0 + 2 * cw, y0 - 12, "columns — each one is a Series", 10.5, style=f'fill="{ACC}" font-weight="600"')
    s += f'<rect x="{x0 + 3 * cw}" y="{y0}" width="{cw}" height="{rh * 4}" fill="none" stroke="{ACC}" stroke-width="2" stroke-dasharray="5 3"/>'
    s += _m(x0 + 3 * cw + cw / 2, y0 + rh * 4 + 20, 'df["heating_load"]', 11.5, style=f'fill="{ACC}"')
    s += _m(x0 + 1 * cw + cw / 2, y0 + rh * 4 + 20, 'df.loc[1, "heating_load"] → 20.84', 11.5, style='opacity=".7"')
    s += _t(60, 262, "df.shape → (768, 10)     df.dtypes → float64, int64 …     df.head() → the first five rows", 11.5, anchor="start", style=MONO)
    s = _foot(s, 288, "A DataFrame is a table with named columns and a row index: pick columns, filter rows, summarise.")
    return s + "</svg>"


# ------------------------------------------------------------- array shapes
def array_shapes():
    s = HEAD.format(w=880, h=300)
    # 1D
    for i in range(5):
        s += _box(70 + i * 34, 90, 30, 30, lw=1.2)
    s += _m(150, 70, "shape (5,)", 12, style='font-weight="600"')
    s += _t(150, 146, "one row of numbers: a column of a table", 10.5, style='opacity=".65"')
    s += _t(150, 162, "np.array([1, 2, 3, 4, 5])", 10.5, style=MONO)
    # 2D
    for r in range(3):
        for c in range(4):
            s += _box(350 + c * 34, 74 + r * 34, 30, 30, lw=1.2, fill=("#efeaf7" if r == 1 else "#fff"))
    s += _m(415, 56, "shape (3, 4)", 12, style='font-weight="600"')
    s += _t(415, 200, "rows × columns: a table, an image", 10.5, style='opacity=".65"')
    s += _t(415, 216, "a[1, :]  → the highlighted row", 10.5, style=MONO)
    s += _t(415, 232, "a.mean(axis=0) → one number per column", 10.5, style=MONO)
    # 3D
    for k in range(3):
        off = k * 10
        for r in range(3):
            for c in range(3):
                s += _box(600 + c * 30 + off, 100 + r * 30 - off, 26, 26, lw=1, fill="#fff")
    s += _m(660, 56, "shape (3, 3, 3)", 12, style='font-weight="600"')
    s += _t(660, 218, "stacked tables: hours × rows × columns,", 10.5, style='opacity=".65"')
    s += _t(660, 234, "or colour images (height × width × RGB)", 10.5, style='opacity=".65"')
    s = _foot(s, 258, "An array is a grid of numbers of one type. Its shape says how many along each axis. Maths applies to the whole grid at once.")
    return s + "</svg>"


# ------------------------------------------------------------ figure anatomy
def figure_anatomy():
    s = HEAD.format(w=880, h=340)
    s += _box(60, 40, 520, 250, lw=1.2, dash="5 4", stroke="#888")
    s += _t(80, 60, "Figure — the whole canvas", 10.5, anchor="start", style='fill="#888"')
    ax0, ay0, aw, ah = 140, 80, 400, 170
    s += f'<line x1="{ax0}" y1="{ay0 + ah}" x2="{ax0 + aw}" y2="{ay0 + ah}"/>'
    s += f'<line x1="{ax0}" y1="{ay0}" x2="{ax0}" y2="{ay0 + ah}"/>'
    pts = [(0.05, 0.75), (0.15, 0.7), (0.3, 0.55), (0.42, 0.5), (0.55, 0.35), (0.65, 0.3), (0.8, 0.2), (0.92, 0.12)]
    for u, v in pts:
        s += f'<circle cx="{ax0 + u * aw:.1f}" cy="{ay0 + v * ah:.1f}" r="4" fill="{ACC}" stroke="none"/>'
    s += f'<line x1="{ax0 + 0.05 * aw}" y1="{ay0 + 0.78 * ah}" x2="{ax0 + 0.92 * aw}" y2="{ay0 + 0.1 * ah}" stroke="#111" stroke-width="1.6"/>'
    s += _t(ax0 + aw / 2, ay0 - 8, "Heating load vs relative compactness", 12, weight=600)
    s += _t(ax0 + aw / 2, ay0 + ah + 30, "relative compactness", 11)
    s += ('<text x="112" y="165" font-size="11" text-anchor="middle" font-family="Montserrat, sans-serif" fill="#111" '
          'stroke="none" transform="rotate(-90 112 165)">heating load (kWh/m²)</text>')
    s += _box(ax0 + aw - 130, ay0 + 8, 120, 40, lw=1, fill="#fff")
    s += f'<circle cx="{ax0 + aw - 116}" cy="{ay0 + 22}" r="3.5" fill="{ACC}" stroke="none"/>'
    s += _t(ax0 + aw - 106, ay0 + 26, "buildings", 10, anchor="start")
    s += f'<line x1="{ax0 + aw - 122}" y1="{ay0 + 38}" x2="{ax0 + aw - 110}" y2="{ay0 + 38}" stroke-width="1.6"/>'
    s += _t(ax0 + aw - 106, ay0 + 42, "trend", 10, anchor="start")
    for i in range(5):
        x = ax0 + i * aw / 4
        s += f'<line x1="{x}" y1="{ay0 + ah}" x2="{x}" y2="{ay0 + ah + 5}"/>'
    labels = [(620, 88, "ax.set_title(...)"), (620, 118, "ax.set_xlabel / ax.set_ylabel"), (620, 148, "ax.legend()"),
              (620, 178, "ax.scatter(x, y)   the marks"), (620, 208, "ax.plot(x, y)   a line"), (620, 238, "ticks — automatic, usually fine")]
    for x, y, t in labels:
        s += _m(x, y, t, 11, anchor="start")
    s += _t(620, 60, "Axes — one plot; a figure can hold several", 10.5, anchor="start", style=f'fill="{ACC}" font-weight="600"')
    s = _foot(s, 304, "fig, ax = plt.subplots()  gives you the canvas and one plot. Everything else is a method on ax.")
    return s + "</svg>"


# ------------------------------------------------------------------- groupby
def groupby():
    s = HEAD.format(w=880, h=330)
    rows = [("N", "15.6"), ("S", "20.8"), ("N", "29.8"), ("E", "12.1"), ("S", "33.5"), ("E", "14.4")]
    s += _t(120, 50, "split", 12.5, weight=600, style=f'fill="{ACC}"')
    for i, (g, v) in enumerate(rows):
        y = 66 + i * 26
        s += _box(60, y, 50, 22, lw=1, fill=GOLD); s += _m(85, y + 15, g, 11)
        s += _box(110, y, 60, 22, lw=1); s += _m(140, y + 15, v, 11)
    groups = {"N": ["15.6", "29.8"], "S": ["20.8", "33.5"], "E": ["12.1", "14.4"]}
    s += _t(360, 50, "apply: mean()", 12.5, weight=600, style=f'fill="{ACC}"')
    for gi, (g, vals) in enumerate(groups.items()):
        y = 66 + gi * 66
        s += _box(300, y, 40, 22, lw=1, fill=GOLD); s += _m(320, y + 15, g, 11)
        for vi, v in enumerate(vals):
            s += _box(340, y + vi * 24, 60, 22, lw=1); s += _m(370, y + 15 + vi * 24, v, 11)
        mean = (float(vals[0]) + float(vals[1])) / 2
        s += _arrow(404, y + 22, 456, y + 22)
        s += _box(460, y + 11, 70, 22, lw=1.4, stroke=ACC); s += _m(495, y + 26, f"{mean:.1f}", 11, style=f'fill="{ACC}"')
    s += _arrow(176, 140, 292, 100, dash="4 3")
    s += _arrow(176, 140, 292, 166, dash="4 3")
    s += _arrow(176, 140, 292, 232, dash="4 3")
    s += _t(660, 50, "combine", 12.5, weight=600, style=f'fill="{ACC}"')
    s += _m(600, 84, 'df.groupby("orientation")', 12, anchor="start")
    s += _m(600, 104, '  ["heating_load"].mean()', 12, anchor="start")
    means = {g: f"{(float(v[0]) + float(v[1])) / 2:.1f}" for g, v in groups.items()}
    for gi, (g, m) in enumerate([("E", means["E"]), ("N", means["N"]), ("S", means["S"])]):
        y = 130 + gi * 26
        s += _box(600, y, 40, 22, lw=1, fill=GOLD); s += _m(620, y + 15, g, 11)
        s += _box(640, y, 70, 22, lw=1); s += _m(675, y + 15, m, 11)
    s += _t(600, 230, "one row per group: the question", 10.5, anchor="start", style='opacity=".65"')
    s += _t(600, 246, "\"does orientation matter?\" in three numbers", 10.5, anchor="start", style='opacity=".65"')
    s = _foot(s, 290, "groupby = split the rows by a column, apply a summary to each group, combine the results into a small table.")
    return s + "</svg>"


ALL = {"run_model": run_model, "variable_box": variable_box, "types_four": types_four,
       "indexing": indexing, "collections": collections, "dict_lookup": dict_lookup,
       "for_loop": for_loop, "while_loop": while_loop, "function_call": function_call,
       "class_blueprint": class_blueprint, "imports": imports, "traceback": traceback,
       "eda_loop": eda_loop, "dataframe_anatomy": dataframe_anatomy,
       "array_shapes": array_shapes, "figure_anatomy": figure_anatomy, "groupby": groupby}
