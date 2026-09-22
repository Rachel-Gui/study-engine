"""
parse.py - turns an episode markdown file into a list of topics.

Authors never touch this. The contract they write against is in CONTRIBUTING.md:

    ---                      YAML frontmatter: episode metadata
    episode: "3.1"
    ---

    ## Topic title           starts a new topic page

    :::narration             what the voice says over this topic
    ...
    :::

    :::keyidea{...}          any registered component
    ...
    :::

    {{term}}                 glossary tooltip
"""
import html, io, re, yaml

# ------------------------------------------------------------------ directives

DIRECTIVE = re.compile(r"^:::([a-z][a-z0-9-]*)(\{.*\})?\s*$")
ATTR = re.compile(r'([a-zA-Z_][\w-]*)\s*=\s*(?:"([^"]*)"|([^\s}]+))')


def _attrs(raw):
    """Parse {key=value key2="value two"} into a dict."""
    return {m.group(1): (m.group(2) if m.group(2) is not None else m.group(3))
            for m in ATTR.finditer(raw or "")}


def parse_episode(path):
    """-> (episode_meta_dict, [topic, ...])"""
    text = io.open(path, encoding="utf-8").read().replace("\r\n", "\n")
    meta, body = _frontmatter(text)

    topics, cur = [], None
    lines, i = body.split("\n"), 0
    while i < len(lines):
        line = lines[i]

        if line.startswith("## "):
            cur = {"title": line[3:].strip(), "blocks": [], "narration": ""}
            topics.append(cur)
            i += 1
            continue

        m = DIRECTIVE.match(line)
        if m:
            name, attrs = m.group(1), _attrs(m.group(2))
            buf, i = [], i + 1
            while i < len(lines) and lines[i].rstrip() != ":::":
                buf.append(lines[i]); i += 1
            i += 1                                    # consume the closing :::
            if cur is None:                           # content before any ##
                cur = {"title": meta.get("title", ""), "blocks": [], "narration": ""}
                topics.append(cur)
            if name == "narration":
                cur["narration"] = "\n".join(buf).strip()
            else:
                cur["blocks"].append({"kind": name, "attrs": attrs,
                                      "body": "\n".join(buf).strip()})
            continue

        if line.strip() and cur is not None:          # prose paragraph
            buf = []
            while i < len(lines) and lines[i].strip() and not lines[i].startswith("## ") \
                    and not DIRECTIVE.match(lines[i]):
                buf.append(lines[i]); i += 1
            cur["blocks"].append({"kind": "prose", "attrs": {},
                                  "body": "\n".join(buf)})
            continue

        i += 1

    for n, t in enumerate(topics, 1):
        t["n"] = n
    return meta, topics


def _frontmatter(text):
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end < 0:
        raise ValueError("the frontmatter block is never closed - it needs a "
                         "line containing only --- after the last setting")
    meta = yaml.safe_load(text[3:end])
    if not isinstance(meta, dict):
        raise ValueError("the frontmatter is not a set of key: value settings")
    # YAML turns `episode: 3.1` into the number 3.1, which breaks every path
    # built from it. Coerce, and keep a sensible string form.
    for k in ("episode", "title", "level", "kind"):
        if k in meta and not isinstance(meta[k], str):
            meta[k] = str(meta[k])
    return meta, text[end + 4:]


# ------------------------------------------------------- inline markdown -> html

GLOSSARY = {}          # filled from course.yml; term -> definition


def inline(s, glossary=True):
    """Bold, italic, code, links, and {{glossary}} terms. Deliberately small."""
    s = html.escape(s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![*\w])\*([^*]+)\*", r"<em>\1</em>", s)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)",
               r'<a href="\2" target="_blank" rel="noopener">\1</a>', s)
    if glossary:
        s = re.sub(r"\{\{([^}]+)\}\}", _term, s)
    s = re.sub(r"\[\[([a-z -]+)\]\]", _evidence, s)
    return re.sub(r"&amp;([#\w]+;)", r"&\1", s)      # let HTML entities through


# The six evidence labels the course uses everywhere, and nowhere else.
EVIDENCE = {
    "measured":        ("measured",  "Measured"),
    "simulated":       ("simulated", "Simulated"),
    "model-predicted": ("predicted", "Model-predicted"),
    "predicted":       ("predicted", "Model-predicted"),
    "generated":       ("generated", "LLM-generated"),
    "llm-generated":   ("generated", "LLM-generated"),
    "retrieved":       ("retrieved", "Retrieved"),
    "human":           ("human",     "Human judgment"),
    "human-judged":    ("human",     "Human judgment"),
}


def _evidence(m):
    hit = EVIDENCE.get(m.group(1).strip().lower())
    if not hit:
        return m.group(0)
    return f'<span class="ev ev-{hit[0]}">{hit[1]}</span>'


def _term(m):
    key = m.group(1).strip()
    d = GLOSSARY.get(key.lower())
    if not d:
        return f'<span class="term">{key}</span>'
    return (f'<span class="term" tabindex="0" data-def="{html.escape(d)}">'
            f'{key}<span class="tip">{html.escape(d)}</span></span>')


def plain(s):
    """Strip markup - used for video frames and alt text."""
    s = re.sub(r"\{\{([^}]+)\}\}", r"\1", s)
    s = re.sub(r"\[\[([a-z -]+)\]\]",
               lambda m: EVIDENCE.get(m.group(1).lower(), ("", m.group(1)))[1], s)
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)
    return re.sub(r"[*`]", "", s)


def rows(body, n=None):
    """Pipe-delimited rows: 'a | b | c' per line. Blank lines ignored."""
    out = []
    for line in body.split("\n"):
        if not line.strip():
            continue
        cells = [c.strip() for c in line.split("|")]
        if n:
            cells = (cells + [""] * n)[:n]
        out.append(cells)
    return out
