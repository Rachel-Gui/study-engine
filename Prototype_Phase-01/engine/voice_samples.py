"""
voice_samples.py - hear the same paragraph in several narration voices, then pick one.

    python engine/voice_samples.py                 the shortlist below, into dist/voice-samples/
    python engine/voice_samples.py --all-english   every English voice edge-tts offers (slow)
    python engine/voice_samples.py --voice en-US-JennyNeural --voice en-GB-SoniaNeural
    python engine/voice_samples.py --rate -5%      a little slower (the course default is -3%)

It writes one mp3 per voice and an index.html with a player for each, plus the
line to paste into course.yml. Nothing else in the course changes until you edit
course.yml (the `voice:` and `voice_rate:` keys); the next make-video run then
re-records every scene, because the voice is part of each scene's cache id.

Needs edge-tts (pip install edge-tts) and an internet connection: the voices are
Microsoft's free online neural voices.
"""
import argparse, html, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# A shortlist: the newer "multilingual" voices are the most natural-sounding ones
# edge-tts offers; the rest are the long-standing favourites. U.S. female first.
SHORTLIST = [
    ("en-US-AvaMultilingualNeural", "U.S. · female · natural, warm (course default)"),
    ("en-US-EmmaMultilingualNeural", "U.S. · female · natural, bright"),
    ("en-US-JennyNeural", "U.S. · female · clear, even"),
    ("en-US-AriaNeural", "U.S. · female · expressive"),
    ("en-US-MichelleNeural", "U.S. · female · calm"),
    ("en-US-AndrewMultilingualNeural", "U.S. · male · natural"),
    ("en-US-BrianMultilingualNeural", "U.S. · male · natural, lower"),
    ("en-GB-SoniaNeural", "U.K. · female"),
    ("en-GB-RyanNeural", "U.K. · male (the previous default)"),
    ("en-AU-NatashaNeural", "Australian · female"),
]

SAMPLE = ("Welcome to AI for Architecture. AI is not one method. In architecture, many contemporary AI workflows "
          "can be understood through three broad roles. Generative AI creates or proposes new content, such as images, "
          "text, code, or design representations. Agentic AI goes beyond a single response: agents can plan, use tools, "
          "take actions, and respond to feedback. Machine learning and deep learning learn patterns from data to support "
          "tasks such as prediction, classification, analysis, and representation.")


def list_voices():
    r = subprocess.run([sys.executable, "-m", "edge_tts", "--list-voices"], capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        sys.exit("  edge-tts could not list voices. Install it (pip install edge-tts) and check the connection.\n  " + (r.stderr or "").strip()[-300:])
    names = []
    for line in r.stdout.splitlines():
        parts = line.split()
        if parts and parts[0].endswith("Neural"):
            names.append(parts[0])
    return names


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--voice", action="append", help="a voice name (repeatable); default: the shortlist")
    ap.add_argument("--all-english", action="store_true", help="every en-* voice edge-tts offers")
    ap.add_argument("--rate", default="-3%", help='speaking rate, e.g. "-5%%" or "+0%%"')
    ap.add_argument("--text", default=None, help="a different sample paragraph")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "voice-samples"))
    a = ap.parse_args(argv)

    available = list_voices()
    if a.all_english:
        want = [(v, "") for v in available if v.startswith("en-")]
    elif a.voice:
        want = [(v, "") for v in a.voice]
    else:
        want = SHORTLIST
    os.makedirs(a.out, exist_ok=True)
    text = a.text or SAMPLE
    tmp = os.path.join(a.out, "_sample.txt")
    open(tmp, "w", encoding="utf-8").write(text)

    rows, skipped = [], []
    for name, note in want:
        if name not in available:
            skipped.append(name); continue
        mp3 = os.path.join(a.out, name + ".mp3")
        cmd = [sys.executable, "-m", "edge_tts", "--voice", name, "--file", tmp, "--write-media", mp3]
        if a.rate not in ("+0%", "0%"):
            cmd += [f"--rate={a.rate}"]
        print(f"  {name:36s} ", end="", flush=True)
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        if r.returncode == 0 and os.path.exists(mp3) and os.path.getsize(mp3) > 1024:
            print("ok"); rows.append((name, note, os.path.basename(mp3)))
        else:
            print("FAILED"); skipped.append(name)
    os.remove(tmp)

    items = "".join(
        f'<li><div class="v"><b>{html.escape(n)}</b><span>{html.escape(note)}</span></div>'
        f'<audio controls preload="none" src="{html.escape(f)}"></audio>'
        f'<code>voice: "{html.escape(n)}"</code></li>' for n, note, f in rows)
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Narration voice samples</title>
<style>body{{font-family:Montserrat,system-ui,sans-serif;max-width:860px;margin:40px auto;padding:0 20px;color:#111}}
h1{{font-size:24px}}p{{color:#444;line-height:1.5}}ul{{list-style:none;padding:0}}li{{display:grid;grid-template-columns:1fr 300px 280px;gap:16px;align-items:center;padding:14px 0;border-top:1px solid #e4e4e4}}
.v b{{display:block}}.v span{{font-size:13px;color:#666}}code{{font-size:12px;background:#f4f4f2;padding:4px 8px;border-radius:4px}}audio{{width:100%}}</style></head>
<body><h1>Narration voice samples</h1>
<p>The same paragraph (the start of the course introduction) at rate {html.escape(a.rate)}. Pick one, paste its line into
<code>course.yml</code> (the <code>voice:</code> key), and the next <code>make-video</code> run re-records every lesson with it.
<code>voice_rate:</code> sets the pace; "-3%" is a touch slower than the voice's own.</p>
<ul>{items}</ul>
<p style="font-size:13px;color:#666">Voices are Microsoft neural voices served through edge-tts. Generated: {len(rows)}; not available or failed: {", ".join(skipped) or "none"}.</p>
</body></html>"""
    open(os.path.join(a.out, "index.html"), "w", encoding="utf-8").write(page)
    print(f"\n  {len(rows)} samples in {a.out}\n  open {os.path.join(a.out, 'index.html')} and listen.")
    if skipped:
        print(f"  not available or failed: {', '.join(skipped)}")


if __name__ == "__main__":
    main()
