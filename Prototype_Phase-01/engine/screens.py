"""
screens.py - original mock-ups of the software environments the course uses
(a terminal, a code editor, a notebook, a browser download page, an installer
dialog), drawn in HTML/CSS in the course's own visual language.

They are deliberately schematic: no vendor logos, no copied screenshots - just the
recognisable *shape* of each environment, with the exact commands and steps the
lesson asks for. One source feeds both outputs:

    web   - :::screen{kind=terminal ...} on a lesson page (static)
    video - :::scene{type=screen kind=terminal} in a storyboard (animated, the
            commands type themselves and the output appears in time with the voice)

The spec is a small dict (YAML in the markdown):

    kind: terminal | editor | notebook | browser | installer
    title: window title text
    prompt: "C:\\Users\\you\\arch594>"          terminal prompt (default per OS)
    lines: ["$ python --version", "Python 3.13.2"]   "$ " = a command that is typed
    files / file / code / terminal                   editor
    cells: [{code: ..., output: ...}]                notebook
    url / page: {title, lines, button}               browser
    button / checks: ["*Add python.exe to PATH"]     installer ("*" = ticked + highlighted)
    callout: "Tick this before Install"              a pointer badge, any kind
"""
import html

ACCENT, GOLD = "#4b2e83", "#e8e3d3"

CSS = """
.mk{border:1.5px solid #1a1a1a;border-radius:10px;background:#fff;overflow:hidden;font-family:Montserrat,sans-serif;position:relative;box-shadow:0 10px 30px rgba(0,0,0,.08)}
.mk-bar{display:flex;align-items:center;gap:7px;height:34px;padding:0 14px;background:#ececea;border-bottom:1px solid #d9d9d6;font-size:12.5px;color:#444}
.mk-bar i{width:11px;height:11px;border-radius:50%;background:#c9c9c5;display:inline-block}
.mk-bar span{margin-left:8px;font-weight:600;letter-spacing:.01em;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.mk-body{position:relative}
/* terminal */
.mk-terminal .mk-body{background:#141414;color:#e8e8e6;font:400 14.5px/1.7 'IBM Plex Mono',monospace;padding:16px 18px;min-height:220px}
.mk-terminal .mk-ps{color:#9fd39f}
.mk-terminal .mk-cmd{color:#fff}
.mk-terminal .mk-out{color:#c9c9c5;white-space:pre-wrap}
.mk-terminal .mk-out.err{color:#f2a3a3}
.mk-terminal .mk-cur{display:inline-block;width:8px;height:15px;background:#e8e8e6;vertical-align:-2px;margin-left:2px}
/* editor */
.mk-editor .mk-body{display:grid;grid-template-columns:190px 1fr;min-height:300px;background:#1f1f24;color:#d8d8d8;font:400 13.5px/1.6 'IBM Plex Mono',monospace}
.mk-side{background:#26262c;border-right:1px solid #35353d;padding:12px 0}
.mk-side .mk-h{font:700 10.5px Montserrat,sans-serif;letter-spacing:.18em;color:#9a9aa5;padding:0 14px 10px}
.mk-side .mk-f{padding:3px 14px;white-space:pre;color:#cfcfd6}
.mk-side .mk-f.on{background:#3a3a46;color:#fff}
.mk-main{display:flex;flex-direction:column;min-width:0}
.mk-tabs{display:flex;gap:2px;background:#26262c;border-bottom:1px solid #35353d}
.mk-tab{padding:8px 16px;font:500 12.5px Montserrat,sans-serif;color:#9a9aa5;background:#1f1f24;border-right:1px solid #35353d}
.mk-tab.on{color:#fff;border-top:2px solid __ACCENT2__}
.mk-run{margin-left:auto;padding:6px 14px;font:700 11px Montserrat,sans-serif;color:#9fd39f;letter-spacing:.1em}
.mk-code{padding:14px 18px;white-space:pre;min-height:120px;flex:1}
.mk-code .mk-n{display:inline-block;width:26px;color:#6a6a75;text-align:right;margin-right:16px;user-select:none}
.mk-code .kw{color:#c792ea}.mk-code .st{color:#c3e88d}.mk-code .fn{color:#82aaff}.mk-code .cm{color:#7a7a85}
.mk-term{border-top:1px solid #35353d;background:#161619;padding:10px 18px;min-height:74px}
.mk-term .mk-h{font:700 10.5px Montserrat,sans-serif;letter-spacing:.18em;color:#9a9aa5;margin-bottom:6px}
.mk-term .mk-ps{color:#9fd39f}.mk-term .mk-out{color:#c9c9c5;white-space:pre-wrap}
/* notebook */
.mk-notebook .mk-body{background:#fff;padding:14px 18px 18px;min-height:280px;font-family:Montserrat,sans-serif}
.mk-nbmenu{display:flex;gap:18px;font-size:12.5px;color:#444;border-bottom:1px solid #e6e6e6;padding-bottom:10px;margin-bottom:14px}
.mk-nbmenu b{color:#111;font-weight:600}
.mk-nbmenu .mk-rt{margin-left:auto;font:500 11.5px 'IBM Plex Mono',monospace;color:#2a7d2a}
.mk-cell{display:grid;grid-template-columns:34px 1fr;gap:10px;align-items:start;margin-bottom:10px}
.mk-play{width:26px;height:26px;border-radius:50%;background:#111;color:#fff;display:grid;place-items:center;font-size:10px;margin-top:6px}
.mk-play.done{background:__ACCENT__}
.mk-cellcode{background:#f5f5f3;border:1px solid #e3e3e0;border-radius:6px;padding:10px 14px;font:400 13.5px/1.6 'IBM Plex Mono',monospace;white-space:pre;color:#111;min-height:40px}
.mk-cellout{grid-column:2;font:400 13.5px/1.6 'IBM Plex Mono',monospace;color:#222;white-space:pre-wrap;padding:6px 14px 2px}
/* browser */
.mk-browser .mk-addr{height:30px;margin:8px 12px;border-radius:15px;background:#f1f1ef;border:1px solid #dcdcd9;font:500 12.5px 'IBM Plex Mono',monospace;color:#333;padding:6px 14px;white-space:nowrap;overflow:hidden}
.mk-browser .mk-page{padding:24px 34px 30px;min-height:230px;background:#fff}
.mk-browser .mk-page h3{font-size:22px;font-weight:600;letter-spacing:-.01em;margin-bottom:12px;color:#111}
.mk-browser .mk-page p{font-size:14px;line-height:1.5;color:#3a3a3a;margin:0 0 8px;max-width:52ch}
.mk-browser .mk-dl{display:inline-block;margin-top:14px;background:__ACCENT__;color:#fff;font-weight:700;font-size:14px;padding:12px 22px;border-radius:6px;letter-spacing:.02em}
.mk-browser .mk-page .mk-sm{font-size:12px;color:#777;margin-top:12px}
/* installer dialog */
.mk-installer .mk-body{background:#fff;padding:24px 30px 26px;min-height:250px}
.mk-installer h3{font-size:20px;font-weight:600;margin-bottom:6px}
.mk-installer p{font-size:13.5px;color:#3a3a3a;margin:0 0 16px;line-height:1.5}
.mk-installer .mk-opt{border:1.5px solid #111;border-radius:8px;padding:12px 16px;margin-bottom:10px;background:#fff}
.mk-installer .mk-opt b{display:block;font-size:15px;font-weight:600}
.mk-installer .mk-opt span{font-size:12.5px;color:#555}
.mk-installer .mk-opt.primary{background:__GOLD__;border-color:__ACCENT__}
.mk-chk{display:flex;align-items:center;gap:10px;font-size:14px;color:#222;margin-top:10px}
.mk-chk i{width:18px;height:18px;border:1.5px solid #333;border-radius:3px;display:inline-grid;place-items:center;font-style:normal;font-size:13px;line-height:1;background:#fff}
.mk-chk.on i{background:__ACCENT__;border-color:__ACCENT__;color:#fff}
.mk-chk.on{font-weight:600;color:#111}
/* callout badge */
.mk-callout{position:absolute;right:18px;bottom:18px;max-width:260px;background:#111;color:#fff;font:600 13px/1.4 Montserrat,sans-serif;padding:10px 14px;border-radius:8px;box-shadow:0 8px 24px rgba(0,0,0,.25)}
.mk-callout::before{content:"";position:absolute;left:-9px;top:50%;margin-top:-7px;border:7px solid transparent;border-right-color:#111;border-left:0}
.mk-callout.top{bottom:auto;top:18px}
.mk-terminal .mk-callout{background:__GOLD__;color:#111;box-shadow:none}
.mk-terminal .mk-callout::before{border-right-color:__GOLD__}
.mk-tip{display:inline-block;margin-left:12px;background:#111;color:#fff;font:600 11.5px Montserrat,sans-serif;padding:5px 10px;border-radius:6px;position:relative}
.mk-tip::before{content:"";position:absolute;left:-7px;top:50%;margin-top:-6px;border:6px solid transparent;border-right-color:#111;border-left:0}
""".replace("__ACCENT__", ACCENT).replace("__ACCENT2__", "#8a6fd1").replace("__GOLD__", GOLD)

_KEYWORDS = {"import", "from", "print", "def", "return", "for", "in", "if", "else", "elif", "while", "and", "or", "not",
             "as", "with", "class", "True", "False", "None"}


def _e(s):
    return html.escape(str(s if s is not None else ""))


def _hl(line):
    """Very small syntax colouring for editor code (strings, comments, keywords)."""
    out = []
    s = str(line)
    if s.lstrip().startswith("#"):
        return f'<span class="cm">{_e(s)}</span>'
    if "#" in s:
        code, cm = s.split("#", 1)
        return _hl(code) + f'<span class="cm">#{_e(cm)}</span>'
    import re
    for tok in re.split(r'("[^"]*"|\'[^\']*\'|\b\w+\b)', s):
        if not tok:
            continue
        if (tok.startswith('"') and tok.endswith('"')) or (tok.startswith("'") and tok.endswith("'")):
            out.append(f'<span class="st">{_e(tok)}</span>')
        elif tok in _KEYWORDS:
            out.append(f'<span class="kw">{_e(tok)}</span>')
        else:
            out.append(_e(tok))
    return "".join(out)


class _Beats:
    """Hands out beat numbers and attributes; in static mode every attribute is empty."""

    def __init__(self, animate, start=1):
        self.animate, self.n = animate, start

    def next(self, anim="rise", delay=0.0, dur=0.5, text=None):
        if not self.animate:
            return ""
        k = self.n
        self.n += 1
        extra = f' data-text="{_e(text)}"' if text is not None else ""
        return f' data-beat="{k}" data-delay="{delay:.2f}" data-dur="{dur:.2f}" data-anim="{anim}"{extra}'

    def same(self, anim="rise", delay=0.0, dur=0.5):
        """An attribute on the most recently handed-out beat."""
        if not self.animate:
            return ""
        return f' data-beat="{self.n - 1}" data-delay="{delay:.2f}" data-dur="{dur:.2f}" data-anim="{anim}"'


def _window(kind, title, body, beats, callout=None, callout_top=False):
    bar = f'<div class="mk-bar"><i></i><i></i><i></i><span>{_e(title)}</span></div>'
    co = ""
    if callout:
        co = f'<div class="mk-callout{" top" if callout_top else ""}"{beats.next("pop", 0.2, 0.45)}>{_e(callout)}</div>'
    win = ' data-beat="0" data-anim="rise" data-dur="0.6"' if beats.animate else ""
    return f'<div class="mk mk-{kind}"{win}>{bar}<div class="mk-body">{body}{co}</div></div>'


def terminal(spec, animate=False):
    b = _Beats(animate)
    prompt = spec.get("prompt") or "C:\\Users\\you\\Documents\\arch594>"
    rows = []
    for ln in spec.get("lines") or []:
        ln = str(ln)
        if ln.startswith("$ ") or ln.startswith("> "):
            cmd = ln[2:]
            if animate:
                rows.append(f'<div><span class="mk-ps">{_e(prompt)}</span> <span class="mk-cmd"{b.next("type", 0, min(1.6, 0.35 + 0.04 * len(cmd)), text=cmd)}></span></div>')
            else:
                rows.append(f'<div><span class="mk-ps">{_e(prompt)}</span> <span class="mk-cmd">{_e(cmd)}</span></div>')
        else:
            cls = "mk-out err" if ln.lower().startswith(("error", "traceback", "'python' is not", "command not found")) or "not recognized" in ln else "mk-out"
            rows.append(f'<div class="{cls}"{b.next("fade", 0.1, 0.35)}>{_e(ln)}</div>')
    if animate:
        rows.append(f'<div><span class="mk-ps">{_e(prompt)}</span> <span class="mk-cur"{b.same("fade", 0.6, 0.3)}></span></div>')
    else:
        rows.append(f'<div><span class="mk-ps">{_e(prompt)}</span> <span class="mk-cur"></span></div>')
    return _window("terminal", spec.get("title", "Terminal"), "".join(rows), b, spec.get("callout"), False), b.n


def editor(spec, animate=False):
    b = _Beats(animate)
    files = spec.get("files") or ["arch594/", "  hello.py"]
    cur = spec.get("file") or "hello.py"
    side = '<div class="mk-side"><div class="mk-h">EXPLORER</div>' + "".join(
        f'<div class="mk-f{" on" if str(f).strip() == cur else ""}">{_e(f)}</div>' for f in files) + "</div>"
    code_lines = str(spec.get("code") or "").rstrip("\n").split("\n")
    code = []
    for i, ln in enumerate(code_lines):
        attrs = b.next("fade", 0.0, 0.25) if animate and i == 0 else (b.same("fade", 0.12 * i, 0.25) if animate else "")
        code.append(f'<div{attrs}><span class="mk-n">{i + 1}</span>{_hl(ln)}</div>')
    term_rows = []
    for ln in spec.get("terminal") or []:
        ln = str(ln)
        if ln.startswith("$ "):
            cmd = ln[2:]
            term_rows.append(f'<div><span class="mk-ps">{_e(spec.get("prompt") or "arch594 $")}</span> '
                             + (f'<span{b.next("type", 0, min(1.4, 0.3 + 0.04 * len(cmd)), text=cmd)}></span>' if animate else f'<span>{_e(cmd)}</span>') + '</div>')
        else:
            term_rows.append(f'<div class="mk-out"{b.next("fade", 0.1, 0.3)}>{_e(ln)}</div>')
    main = (f'<div class="mk-main"><div class="mk-tabs"><div class="mk-tab on">{_e(cur)}</div><div class="mk-run">▶ RUN</div></div>'
            f'<div class="mk-code">{"".join(code)}</div>'
            + (f'<div class="mk-term"><div class="mk-h">TERMINAL</div>{"".join(term_rows)}</div>' if term_rows else "") + "</div>")
    return _window("editor", spec.get("title", "Visual Studio Code"), side + main, b, spec.get("callout")), b.n


def notebook(spec, animate=False):
    b = _Beats(animate)
    menu = ('<div class="mk-nbmenu"><b>File</b><span>Edit</span><span>View</span><span>Insert</span><span>Runtime</span><span>Tools</span>'
            f'<span class="mk-rt">{_e(spec.get("runtime", "Connected · Python 3"))}</span></div>')
    cells = []
    for c in spec.get("cells") or []:
        code = str(c.get("code", "")).rstrip("\n")
        out = str(c.get("output", "") or "").rstrip("\n")
        if animate:
            cells.append(f'<div class="mk-cell"><div class="mk-play done"{b.next("pop", 0.0, 0.3)}>▶</div>'
                         f'<div class="mk-cellcode"{b.same("type", 0.1, min(1.8, 0.4 + 0.02 * len(code)))} data-text="{_e(code)}"></div>'
                         + (f'<div class="mk-cellout"{b.next("fade", 0.15, 0.35)}>{_e(out)}</div>' if out else "") + "</div>")
        else:
            cells.append(f'<div class="mk-cell"><div class="mk-play done">▶</div><div class="mk-cellcode">{_e(code)}</div>'
                         + (f'<div class="mk-cellout">{_e(out)}</div>' if out else "") + "</div>")
    return _window("notebook", spec.get("title", "Untitled.ipynb - Colab"), menu + "".join(cells), b, spec.get("callout")), b.n


def browser(spec, animate=False):
    b = _Beats(animate)
    page = spec.get("page") or {}
    body = [f'<div class="mk-addr">{_e(spec.get("url", ""))}</div><div class="mk-page">',
            f'<h3{b.next("rise", 0, 0.45)}>{_e(page.get("title", ""))}</h3>']
    for ln in page.get("lines") or []:
        body.append(f'<p{b.same("rise", 0.15, 0.4)}>{_e(ln)}</p>')
    if page.get("button"):
        body.append(f'<span class="mk-dl"{b.next("pop", 0.1, 0.4)}>{_e(page["button"])}</span>')
    if page.get("small"):
        body.append(f'<div class="mk-sm"{b.same("fade", 0.3, 0.3)}>{_e(page["small"])}</div>')
    body.append("</div>")
    return _window("browser", spec.get("title", "Browser"), "".join(body), b, spec.get("callout")), b.n


def installer(spec, animate=False):
    b = _Beats(animate)
    body = [f'<h3{b.next("rise", 0, 0.4)}>{_e(spec.get("dialog") or spec.get("title", "Setup"))}</h3>',
            f'<p{b.same("rise", 0.1, 0.4)}>{_e(spec.get("text", ""))}</p>']
    for i, opt in enumerate(spec.get("options") or [spec.get("button", "Install Now")]):
        opt = str(opt)
        primary = opt.startswith("*") or i == 0
        opt = opt.lstrip("*")
        t, _, s = opt.partition(" — ")
        body.append(f'<div class="mk-opt{" primary" if primary else ""}"{b.next("rise", 0.05, 0.4)}><b>{_e(t)}</b>' + (f'<span>{_e(s)}</span>' if s else "") + "</div>")
    for ch in spec.get("checks") or []:
        ch = str(ch)
        on = ch.startswith("*")
        tip = f'<span class="mk-tip"{b.same("pop", 0.35, 0.4)}>{_e(spec["callout"])}</span>' if on and spec.get("callout") else ""
        body.append(f'<div class="mk-chk{" on" if on else ""}"{b.next("pop" if on else "fade", 0.05, 0.4)}><i>{"✓" if on else ""}</i>{_e(ch.lstrip("*"))}{tip}</div>')
    return _window("installer", spec.get("title", "Setup"), "".join(body), b, None), b.n


KINDS = {"terminal": terminal, "editor": editor, "notebook": notebook, "browser": browser, "installer": installer}


def mock(spec, animate=False):
    """(html, beats_used) for a spec dict with a `kind`."""
    fn = KINDS.get(str(spec.get("kind", "terminal")), terminal)
    return fn(spec, animate)
