"""tracer.py - run a small Python program at BUILD time and record what happens
line by line, so the site can replay it like Python Tutor: which line is about
to run, what every variable holds, what has been printed so far.

    :::trace{title="Your first loop"}
    total = 0
    for n in [3, 5, 7]:
        total = total + n
    print(total)
    :::

The program runs once, here, while the site is built (it is course content, not
student input). Only frames belonging to the traced code are recorded, so calls
into libraries are a single step. A cap keeps runaway loops from producing a
thousand steps.
"""
import contextlib, io, sys, types

FILENAME = "<trace>"
MAX_STEPS = 300
MAX_REPR = 72


def _show(v, depth=0):
    """A student-friendly repr: functions and classes by name, objects by their
    attributes, everything else by repr, truncated."""
    if isinstance(v, types.ModuleType):
        return f"module {v.__name__}"
    if isinstance(v, (types.FunctionType, types.BuiltinFunctionType)):
        return f"function {getattr(v, '__name__', '?')}()"
    if isinstance(v, type):
        return f"class {v.__name__}"
    if hasattr(v, "__dict__") and not isinstance(v, (list, dict, tuple, set, str, int, float, bool)) \
            and type(v).__module__ not in ("builtins",) and depth == 0:
        attrs = ", ".join(f"{k}={_show(x, 1)}" for k, x in vars(v).items() if not k.startswith("_"))
        return f"{type(v).__name__}({attrs})"
    try:
        r = repr(v)
    except Exception:
        r = f"<{type(v).__name__}>"
    if isinstance(v, float):
        r = f"{v:.6g}"
    return r if len(r) <= MAX_REPR else r[:MAX_REPR - 1] + "…"


def _snapshot(ns):
    out = []
    for k, v in ns.items():
        if k.startswith("__") or isinstance(v, types.ModuleType) or k == "input":
            continue
        out.append([k, _show(v), type(v).__name__])
    return out


def run(code, inputs=None):
    """Returns {"steps": [...], "truncated": bool, "error": str|None}.
    Each step: {"line": int, "ev": "line"|"call"|"return"|"exception"|"end",
                "fn": "<module>"|name, "depth": int, "g": [[name, value, type]...],
                "l": [[...]] or None, "out": "printed so far", "note": str}"""
    steps, state = [], {"truncated": False, "error": None}
    buf = io.StringIO()
    ns = {"__name__": "__main__"}
    if inputs is not None:
        feed = list(inputs)
        def fake_input(prompt=""):
            print(prompt, end="")
            v = feed.pop(0) if feed else ""
            print(v)                      # echo what the student "typed"
            return v
        ns["input"] = fake_input
    compiled = compile(code, FILENAME, "exec")

    def rec(frame, ev, note, fn=None, depth=0):
        if len(steps) >= MAX_STEPS:
            state["truncated"] = True
            sys.settrace(None)
            return
        g = _snapshot(frame.f_globals) if frame is not None else _snapshot(ns)
        l = None
        if frame is not None and frame.f_code.co_name != "<module>":
            l = _snapshot(frame.f_locals)
        steps.append({"line": frame.f_lineno if frame is not None else 0, "ev": ev,
                      "fn": fn or (frame.f_code.co_name if frame is not None else "<module>"),
                      "depth": depth, "g": g, "l": l, "out": buf.getvalue(), "note": note})

    depth = [0]

    def tracer(frame, event, arg):
        if frame.f_code.co_filename != FILENAME:
            return None                     # a library frame: don't step inside
        name = frame.f_code.co_name
        if event == "call":
            if name != "<module>":
                depth[0] += 1
                rec(frame, "call", f"Calling {name}() — a new frame with its own variables", depth=depth[0])
            return tracer
        if event == "line":
            rec(frame, "line", f"About to run line {frame.f_lineno}", depth=depth[0])
        elif event == "return":
            if name != "<module>":
                rec(frame, "return", f"{name}() returns {_show(arg)} — its frame is discarded", depth=depth[0])
                depth[0] -= 1
        elif event == "exception":
            exc = arg[0].__name__
            rec(frame, "exception", f"{exc} raised here", depth=depth[0])
        return tracer

    with contextlib.redirect_stdout(buf):
        sys.settrace(tracer)
        try:
            exec(compiled, ns)
        except Exception as e:             # the program crashed: that is a step too
            state["error"] = f"{type(e).__name__}: {e}"
        finally:
            sys.settrace(None)
    steps.append({"line": 0, "ev": "end",
                  "fn": "<module>", "depth": 0, "g": _snapshot(ns), "l": None,
                  "out": buf.getvalue(),
                  "note": ("The program stopped with an error: " + state["error"]) if state["error"]
                          else "Finished. Every line has run."})
    return {"steps": steps, "truncated": state["truncated"], "error": state["error"]}
