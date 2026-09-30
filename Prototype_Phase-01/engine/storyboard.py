"""
storyboard.py - reads a lesson's video storyboard.

A storyboard lives next to its lesson and shares its name:

    content/generative/2.8-llms-and-structured-generation.md          the lesson
    content/generative/2.8-llms-and-structured-generation.video.md    its video

It is a list of scenes. Each scene is one directive whose body is YAML:

    :::scene{type=idea}
    text: A language model does one thing. It guesses the next word.
    sub: Then it does it again.
    narration: |
      Here is the whole idea in one sentence ...
    :::

Scene types and their fields are documented in README section 4. Every scene has
`narration` (what the voice says while the scene builds); a `quiz` scene may also
have `after` (what the voice says once the answer is revealed).

A lesson with no storyboard still gets a video: `auto()` builds a plain one from
the lesson's topics, narration blocks and key ideas.
"""
import io, os, re, yaml
from parse import plain

SCENE = re.compile(r"^:::scene(\{[^}]*\})?\s*$")
ATTR = re.compile(r'([a-zA-Z_][\w-]*)\s*=\s*(?:"([^"]*)"|([^\s}]+))')


def path_for(lesson_path):
    base, _ = os.path.splitext(lesson_path)
    return base + ".video.md"


def load(path):
    """-> (meta, [scene dicts]). Raises ValueError with the scene number on a bad body."""
    text = io.open(path, encoding="utf-8").read().replace("\r\n", "\n")
    meta = {}
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end > 0:
            meta = yaml.safe_load(text[3:end]) or {}
            text = text[end + 4:]
    scenes, lines, i = [], text.split("\n"), 0
    while i < len(lines):
        m = SCENE.match(lines[i])
        if not m:
            i += 1; continue
        attrs = {a.group(1): (a.group(2) if a.group(2) is not None else a.group(3)) for a in ATTR.finditer(m.group(1) or "")}
        buf, i = [], i + 1
        while i < len(lines) and lines[i].rstrip() != ":::":
            buf.append(lines[i]); i += 1
        i += 1
        body = "\n".join(buf)
        try:
            fields = yaml.safe_load(body) if body.strip() else {}
        except Exception as e:
            raise ValueError(f"scene {len(scenes) + 1} ({attrs.get('type', '?')}) in {os.path.basename(path)}: {e}")
        if not isinstance(fields, dict):
            raise ValueError(f"scene {len(scenes) + 1} in {os.path.basename(path)}: the body must be key: value lines")
        sc = dict(fields); sc.update(attrs)
        sc.setdefault("type", "idea")
        sc["narration"] = str(sc.get("narration", "") or "").strip()
        scenes.append(sc)
    return meta, scenes


def _first_sentences(text, n=2):
    parts = re.split(r"(?<=[.!?])\s+", " ".join(plain(text).split()))
    return " ".join(parts[:n])


def auto(meta, topics, nxt=None):
    """A plain storyboard from the lesson itself: title, one scene per topic (with
    the topic's diagram when it has one), the key ideas as a recap, the next lesson."""
    scenes = [{"type": "title", "narration": f'Lesson {meta["episode"]}. {meta.get("title", "")}.'}]
    keyideas = []
    for t in topics:
        prose = [b for b in t["blocks"] if b["kind"] == "prose"]
        keys = [b for b in t["blocks"] if b["kind"] == "keyidea"]
        figs = [b for b in t["blocks"] if b["kind"] in ("figure", "widget")]
        narration = t.get("narration") or " ".join(_first_sentences(b["body"], 3) for b in prose[:2])
        if not narration.strip():
            continue
        keyideas += [" ".join(plain(b["body"]).split()) for b in keys]
        scenes.append({"type": "idea", "text": t["title"],
                       "sub": _first_sentences(prose[0]["body"], 1) if prose else "",
                       "narration": narration})
        if figs:
            fid = figs[0]["attrs"].get("id", "")
            cap = " ".join(plain(figs[0]["attrs"].get("caption", "")).split()) or t["title"]
            scenes.append({"type": "diagram", "id": fid, "heading": t["title"], "narration": cap})
    if keyideas:
        scenes.append({"type": "recap", "items": [k[:160] for k in keyideas[:3]],
                       "narration": " ".join(keyideas[:3])[:700]})
    if nxt:
        scenes.append({"type": "next", "text": nxt, "narration": f"Next: {nxt}."})
    return scenes
