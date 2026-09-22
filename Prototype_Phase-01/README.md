# DesignAI Curriculum — Prototype, Phase 01

Machine learning and deep learning for architecture, ARCH 594/508.

**One markdown file per episode. Two outputs: an interactive site and a narrated
video.** Change one topic, re-render one scene. Nobody writes anything twice.

> **Where this sits.** This folder is `Prototype_Phase 01/` inside the
> **DesignAI-Curriculum** repository. It is self-contained — everything it needs is
> in here, and it doesn't read or touch anything outside it. The existing files at
> the top of the repo are untouched.
>
> Every path in this README is relative to *this folder*, so `cd` into
> `Prototype_Phase 01` before running anything.

---

# 1 · Run it

## Once, on your machine

1. **Install Python** — [python.org/downloads](https://www.python.org/downloads/).
   On Windows, tick **"Add Python to PATH"** on the first installer screen.
2. **Install GitHub Desktop** — [desktop.github.com](https://desktop.github.com/),
   then `File → Clone repository` and paste the repo URL. Put it somewhere short
   like `D:\course`. **Not inside OneDrive or Dropbox** — they corrupt git repos.
3. **Install the one dependency:**
   ```
   pip install pyyaml
   ```

That's everything you need to write and read content.

## Every time

**Windows:** double-click **`run.bat`**  ·  **Mac/Linux:** run **`./run.sh`**

> ### Am I in the right folder?
> `run.bat` prints the folder path and a list of every episode it built, then a line
> like `207 pages · 31 episodes · 103 video scenes`. **If it says 1 episode, you are
> running an old copy.** The site footer agrees — the small grey counter under
> *Topic k of n in this lesson* should read *… / 207*. Delete stale folders rather
> than keeping them around.

It builds the site and opens `http://localhost:8000`. Leave the window open; press
`Ctrl+C` when you're done. Or type it yourself:

```
python engine/build.py --serve
```

> **Don't double-click `site/index.html`.** Most of it looks fine, which is the trap
> — but the Python labs won't run. Pyodide fetches its WebAssembly from a CDN, and a
> `file://` page has a null origin, so the browser blocks it. `--serve` fixes it.

### Before a presentation

Build and serve beforehand, then **run one Python lab while you still have wifi**.
Pyodide downloads about 10 MB the first time and the browser caches it. Load every
page you plan to show, too — the fonts come from Google Fonts.

---

# 2 · Add a chapter

Two steps. That's the whole process.

**Step 1** — create the file:

```
content/module-3/3.10-vision-transformers.md
```

**Step 2** — add one line to `course.yml`, under the right module:

```yaml
  - title: "Module 3 — Deep Learning for Architecture"
    episodes:
      - module-3/3.9-pinn-from-scratch.md
      - module-3/3.10-vision-transformers.md  # ← your new line
```

The sidebar, the topic counters, the Previous/Next buttons (with the neighbouring
topic's title), the module and episode landing pages, and the instructor block all
generate themselves. You never edit them.

**The fastest start is to copy an existing episode.** `module-3/3.6-physics-informed.md`
uses nearly every feature (figures, two widgets, a lab, predict, technical, boundary);
`module-2/2.2-statistics.md` is a simpler one; `overview/0.2-setup-python.md` shows
the Windows/macOS panes and tables.

## Editing on github.com — no git needed

Open any file on GitHub, click the **pencil icon**, type, and press **Propose
changes**. GitHub makes a branch and a pull request for you. Narjes reviews and
merges. You never install anything.

---

# 3 · Write an episode

You need to know three things. Everything else is ordinary Markdown.

1. **`## Heading`** starts a new **topic** — one screen, one page, one video scene.
2. **`:::narration`** is what the voice says over that topic.
3. **`{{term}}`** shows a glossary tooltip.

## The top of every file

```yaml
---
episode: "3.10"                      # ALWAYS quote this. See the warning below.
title: Vision transformers
duration: 25
level: Beginner                      # Beginner / Intermediate / Advanced / All
kind: Concept                        # Concept / Interactive lab / Demo / Reference
---
```

> ### ⚠ Quote the episode number
> `episode: 3.1` — no quotes — is read by YAML as the **number** 3.1, and every
> filename is built from it. The build stops with an error naming your file. Write
> `episode: "3.1"`. This is the single most common way to break the build.

## Narration

```markdown
:::narration
Write it the way you would say it out loud. Spell out numbers and acronyms — "R
squared", "G P Us", "nineteen eighty six" — because a speech engine reads this
literally.
:::
```

**Narration is opt-in per topic.** A topic *with* it becomes a video scene. A topic
*without* it is web-only — which is what you want for exercises, resource lists, and
reference pages. Most episodes here narrate the central question and the two or three
ideas that matter, and leave the rest to the page.

## Components

Every component is `:::name` … `:::`. Options go in `{braces}` on the opening line.

| Component | What it renders |
|---|---|
| `:::keyidea` | Boxed callout with a rule down the left |
| `:::figure{id=neuron caption="…"}` | An SVG diagram from `engine/figures.py` |
| `:::widget{id=neuron-lab}` | An **interactive** figure you can push on |
| `:::pylab{title="…" packages=numpy}` | Runnable Python, in the browser |
| `:::cards` | Grid of concept cards with icons |
| `:::compare` | Two options side by side |
| `:::stats` | Number strip |
| `:::flow` | `A > B > C` arrow sequence |
| `:::workflow` | Numbered grid with expandable examples |
| `:::details{summary="…"}` | Click-to-expand section |
| `:::reflect` | Question with a Check answer button |
| `:::predict` | Same, labelled **Try / Predict** — commit before reading on |
| `:::transfer` | Same, labelled **Transfer task** |
| `:::technical{summary="…"}` | Collapsed **Technical detail** accordion: equations, framework code |
| `:::boundary` | **Claim boundary** card: `Data \| …`, `Split \| …`, `Evidence \| …`, `Establishes \| …`, `Does not establish \| …` |
| `:::os` | Windows / macOS tabs — see below |
| `:::resources` | Link cards |
| `:::refs` | Reference list with DOIs |
| `:::slide{src=… label=…}` | One lecture slide, labelled |
| `:::deck{dir=… count=12 label=…}` | Slide viewer with arrows and a slider |
| `:::glossarynote` | The "AI terms" banner |
| `:::todo` | **Needs work** marker — impossible to miss, delete when done |

### Components that take rows

One row per line, cells separated by pipes:

```markdown
:::cards
Binary | Two possible classes | Review now / monitor
Multiclass | One of several classes | Brick / glass / concrete
:::

:::stats
19,735 | ten-minute readings
Jan–May | 4.5 months, no cooling season
:::

:::refs
Rumelhart et al. (1986) | Learning representations by back-propagating errors. Nature 323, 533-536. | https://doi.org/10.1038/323533a0
:::
```

Cell counts: `cards`, `compare`, `refs` and `workflow` take **3**; `stats` and
`boundary` take **2**; `resources` takes **5** (`KIND | Title | Source | Description | URL`).

`:::compare` is labelled **A / B** by the stylesheet — never a tick or a cross. A
comparison is not a verdict.

### Tables, code blocks, and evidence labels

Ordinary Markdown tables (`| a | b |` rows with a `|---|---|` line) and fenced code
blocks (three backticks) work anywhere in prose, in every component, on the site and
in the video frame. Use a fence whenever line breaks matter — a three-line command
block written as prose collapses into one paragraph.

Tag any number or output with where it came from and the site shows a small label:
`[[measured]]`, `[[simulated]]`, `[[model-predicted]]`, `[[generated]]`,
`[[retrieved]]`, `[[human]]`. Narration strips them.

### Windows / macOS panes

````markdown
:::os
[windows]
Open a terminal (Start → `cmd`) and type:
```
python --version
```
[mac]
Open Terminal (Cmd+Space, type `Terminal`) and type:
```
python3 --version
```
:::
````

A student picks a tab once and the site remembers it on every page. The video frame
shows the Windows pane.

### Reflect questions

Mark the correct option with `*` and the card gains a **Check answer** button. Add
`| feedback` after any option and the student sees *why* when they pick it. The
question may run over several lines.

```markdown
:::predict
You double the learning rate and the loss rises on every step.
What happened?
- The dataset is too small | A small dataset overfits; it does not make the loss climb.
- *The step overshoots the valley | Yes. Lower the rate first; that is always the first thing to try.
- The network needs more layers | Depth does not repair a diverging optimiser.
:::
```

## Python labs — read before writing one

Labs run on **Pyodide**: Python compiled to WebAssembly, running in the student's
browser. It ships **numpy, pandas, scipy, matplotlib and scikit-learn**.

> ### ⚠ TensorFlow and Keras do not work in the browser
> They are not ported to Pyodide and cannot be installed. For a neural-network lab
> use `sklearn.neural_network.MLPRegressor`, or write the forward pass in numpy —
> which is better teaching anyway. Keras belongs in a downloadable notebook.

Split a lab into steps with a `# step: Title` comment. Steps unlock in order, so a
student can't run step 3 before step 1 has defined its variables.

```markdown
:::pylab{title="Fit a small network" packages="numpy,pandas,scikit-learn"}
# step: Load the data
import pandas as pd
from pyodide.http import open_url          # NOT pd.read_csv(url) - no sockets
df = pd.read_csv(open_url("https://raw.githubusercontent.com/.../data.csv"))

# step: Train
from sklearn.neural_network import MLPRegressor
:::
```

**Loading data:** `pd.read_csv(url)` does not work — the browser has no sockets. Use
`from pyodide.http import open_url` and pass `open_url(URL)`. Local files go in
`assets/data/` and load as `open_url("../assets/data/yourfile.csv")`.

**Keep labs small.** WebAssembly is several times slower than native Python.
Subsample large datasets (`df.iloc[::4]`) and cap `max_iter` so a step finishes in
seconds, not minutes.

## Glossary

Add the term once to `course.yml`, then wrap it in `{{double braces}}` anywhere in
any episode. Matching is case-insensitive, so `{{ReLU}}` and `{{relu}}` both work.

## Diagrams

Diagrams are SVG written in Python — `engine/figures.py`, plus `engine/figures_dl.py`
for Module 3 — so they stay sharp on the site, in the 4K video, and can be diffed in
git. Add a function, register it in the file's `ALL` dict, and reference it by that
key in `:::figure{id=…}`. Black line art; Spirit Purple for at most one emphasis
element per figure.

Interactive widgets live in `engine/widgets.py` and `engine/widgets_dl.py` and work
the same way: each has a `web()` for the site and falls back to a static diagram in
the video. Fourteen exist:

| Widget | Episode | What you push on |
|---|---|---|
| `neuron-lab`, `activation-lab`, `capacity-lab` | 3.1 | one neuron; nonlinearity; depth and parameter count |
| `gradient-lab` | 3.2 | gradient descent on a loss bowl: learning rate, momentum, feature scaling |
| `fit-lab` | 3.3 | polynomial capacity vs train / validation error |
| `conv-lab` | 3.4 | a 3×3 kernel over a paintable facade, ReLU, max-pool |
| `message-lab` | 3.5 | message passing on a seven-room plan; over-smoothing |
| `pinn-lab` | 3.6, 3.9 | a PINN training live: collocation points, λ boundary, λ data, extrapolation |
| `surrogate-lab` | 3.6 | a surrogate queried inside and outside its sampled range |
| `attention-lab` | 3.8 | attention weights over 24 hours of load |
| `regression-line-lab`, `uw-feature-lab` | 2.3, 2.6 | Everly's regression widgets |
| `prompt-lab`, `orchestration-lab` | 4.1, 4.2 | an agent's prompt; sequential vs parallel time-to-result |

> ### ⚠ Widget strings must be raw strings
> The JS inside a widget contains `\n` escapes that belong to **JavaScript**. Define
> the constant as `r"""..."""`, not `"""..."""`, or Python turns them into real
> newlines and the JS string literals break silently — the page renders, the widget
> just doesn't work.

## Colour, motion, and the design system

The palette is black, white, five greys, and two UW accents used sparingly:
**Spirit Purple `#4b2e83`** for wayfinding and emphasis (the current topic, section
rules, buttons, widget headers, the one highlighted element in a figure) and **Husky
Gold `#e8e3d3`** as a warm wash (key-idea boxes, the sampled range in a plot). Both
are CSS tokens (`--accent`, `--gold`) in `engine/theme/site.css`; the video frames use
the same two values. Don't add colours to content — if a diagram needs emphasis, use
the accent once.

Motion is restrained and all in CSS: sections reveal as they scroll into view, cards
and widgets lift on hover, the contents tree animates open, and a thin purple bar at
the top of the window tracks reading progress. Everything respects
`prefers-reduced-motion`.

## House rules

Every script and diagram is checked against the **Accuracy boundaries** page
(`content/reference/9.1-accuracy-boundaries.md`) before it ships. Read it first. The
two that catch people most:

- **Always state the range.** Data range, geometry range, climate range, metrics,
  uncertainty, and known failure conditions — every time you report a number.
- **Never imply deeper is better.** Greater capacity raises the requirement for data,
  tuning and validation. It does not raise accuracy on its own.

---

# 4 · Make the video

The site and the video come from the same markdown. You do not write a separate
script, and you do not re-record when something changes.

## How it works

Every narrated topic becomes a **scene**, content-addressed:

```
scene_id = sha256(quality + kind + title + narration + every block's rendered frame)[:12]
```

The course opens with a title card, and every module opens with a purple card that
speaks the module's question. Those are scenes too.

Rendered frames, audio and per-scene MP4s cache under `.cache/` by that id. Rebuild,
and **only the scenes whose hash moved get re-rendered.**

```
$ python engine/build.py --video          # cold
  28 rebuilt, 0 cached

$ # change one sentence of narration in one topic
$ python engine/build.py --video
  06  REBUILT  46bfa6c8e918  Where neural networks came from
      ...27 others cached...
  1 rebuilt, 27 cached
```

Scene 03's audio is byte-identical to the previous run. That is what makes partial
re-rendering possible at all: a human voice varies take to take and the splice is
audible; a synthetic one doesn't.

## Setup — only on the machine that renders

Not everyone needs this.

```
pip install -r requirements.txt
playwright install chromium
```

**ffmpeg** — this is a *program*, not a Python package. `pip install ffmpeg` does
**not** work.

- Windows: `winget install Gyan.FFmpeg`
- Mac: `brew install ffmpeg`
- Linux: `sudo apt install ffmpeg`

> ### ⚠ On Windows, close the terminal afterwards
> Windows only picks up a changed PATH in a **new** terminal. Install ffmpeg, close
> the window, open a fresh one, then run `python engine/build.py --doctor`. If it
> still says MISSING, the install didn't land on PATH.

**Fonts** — headless Chromium renders the video frames, so Montserrat and IBM Plex
Mono must be installed *on this machine*. The web fonts in the site don't cover it.

```
mkdir -p ~/.fonts && cd ~/.fonts
curl -sSLO "https://raw.githubusercontent.com/google/fonts/main/ofl/montserrat/Montserrat%5Bwght%5D.ttf"
curl -sSLO "https://raw.githubusercontent.com/google/fonts/main/ofl/ibmplexmono/IBMPlexMono-Regular.ttf"
fc-cache -f
```

On Windows, download those two `.ttf` files in a browser, select both, right-click →
**Install**.

## Render

**Windows:** double-click **`make-video.bat`**  ·  **Mac/Linux:** run **`./make-video.sh`**

It checks what's installed, tells you exactly what's missing and how to install it,
and only then renders. Or do it by hand:

```
python engine/build.py --doctor                 # what's installed?
python engine/build.py --video --engine edge    # render, 4K
```

### Resolution

The video renders at **3840×2160 (4K, 16:9) by default.** The frames are laid out on
a fixed 1280×720 canvas and rendered at three device pixels per CSS pixel, so text,
diagrams and code scale together — enlarging the viewport would only add empty
margin. Lower resolutions for a quick preview:

```
python engine/build.py --video --engine edge --quality 1080p    # 1920×1080
python engine/build.py --video --engine edge --quality 720p     # 1280×720
```

Choices: `4k` (default), `1440p`, `1080p`, `720p`. The quality is part of the scene
id, so a 720p preview and the 4K render cache separately and never mix. A 4K scene
takes a few seconds longer to encode; the audio step is unchanged.

> ### Rendering can stop partway, and that's fine
> edge-tts uses Microsoft's free online voice service, which throttles a long run of
> requests. If it stops at scene 19, **every scene before it is already cached** —
> wait a minute, run `make-video` again, and it resumes from 19. The build retries
> four times with backoff before giving up, so this is rarer than it was, but on a
> 28-scene course it can still happen. Two or three runs and you have the whole video.

`--doctor` prints a checklist:

```
  OK       pyyaml (needed for the site)
  OK       playwright (renders video frames)
  MISSING  edge-tts (the narration voice)
             fix:  pip install edge-tts
  OK       ffmpeg (stitches the video)
  OK       Montserrat font
```

> ### ⚠ Always pass `--engine edge`
> Without it, a missing or offline edge-tts **silently falls back to correctly-timed
> silence** and you get a mute video that reports success. `--engine edge` makes that
> a hard error instead.

Any Microsoft neural voice works, and re-rendering the whole course in a different
voice costs only the audio step:

```
python engine/build.py --video --engine edge --voice en-US-AriaNeural
edge-tts --list-voices | grep en-        # see them all
```

The MP4 lands in `dist/course.mp4` and is gitignored. Send the file, or attach it to
a GitHub Release.

## All the commands

```
python engine/build.py                        site only, about a second
python engine/build.py --serve                site + local server + browser
python engine/build.py --video --engine edge  site + 4K MP4
python engine/build.py --video --engine edge --quality 1080p   faster preview
python engine/build.py --video --force        ignore the scene cache
python engine/build.py --no-video             explicit site-only
```

---

# 5 · What's in here

```
course.yml                    module order, instructor, glossary, Pyodide version
content/
  overview/                   0.1 learning outcomes · 0.2–0.4 setup guides
                                (Python + VS Code + Colab · Ollama + Claude Code ·
                                 the Negotiators workshop), Windows and macOS
  module-1/                   1.1 – 1.7, generative AI (Rachel)
  module-2/                   2.1 – 2.6, machine learning fundamentals
  module-3/                   3.1 – 3.9, deep learning: neuron, learning, generalization,
                                CNN, GNN, physics-informed, the ANN demo, sequences,
                                and a PINN from scratch
  module-4/                   4.1 – 4.4, agentic AI + the Negotiators workshop
  reference/                  accuracy boundaries
assets/                       images, slides, and assets/data/ for lab CSVs
engine/                       the pipeline — nobody edits this
  build.py                      the only command
  parse.py                      markdown + :::directives → topic tree
  components.py                 each component: web() and frame()
  figures.py  figures_dl.py     static SVG diagrams
  widgets.py  widgets_dl.py     interactive figures
  generative.py                 Module 1's generative lab component
  render_web.py                 → site/
  render_video.py               → .cache/ → dist/course.mp4 (4K)
  theme/site.css  site.js       theme: black, white, greys, Spirit Purple, Husky Gold
run.bat  run.sh               build and open the site
make-video.bat  make-video.sh  check prerequisites, then render the MP4
```

## Why the engine has two renderers

Every component has a `web()` and a `frame()`. A Python lab is a live editor on the
site and a static code frame in the video. An interactive widget degrades to its
diagram. `:::reflect` returns nothing from `frame()` — an exercise isn't a scene.

**That pair is the whole reason one markdown file produces both outputs.** Adding a
component means writing those two functions and adding one line to `REGISTRY`.
Nothing else changes.

## Episodes that still need work

Search the site for the **Needs work** marker, or grep `:::todo` in `content/`.
Currently: **2.1, 2.2, 2.5** are starter drafts. Module 3 is now complete to a
first full draft (every topic narrated, a widget or lab in every episode); the
natural next additions are a 2D PINN in 3.9 and a real facade-image lab in 3.4, both
of which need Colab rather than the browser.

---

# 6 · When something goes wrong

| What you see | What it means |
|---|---|
| `'python' is not recognized` | Python isn't on PATH. Reinstall with "Add Python to PATH", or use `py` on Windows. |
| `No module named yaml` | Run `pip install pyyaml`. |
| `The engine is incomplete` | Files were downloaded individually and the folders were lost. Clone the repo or unzip the archive — don't move files by hand. |
| `course.yml lists a file that is not there` | A path in `course.yml` doesn't match `content/`. The error prints where the file actually is. |
| `has no episode: in its frontmatter` | You wrote `episode: 3.1` unquoted. Quote it. |
| A lab hangs at "loading python…" | You opened `site/index.html` directly, or you're offline. Use `--serve`. |
| The page loads but has no styling | Same cause. Use `--serve`. |
| `NO SPEECH` warning after `--video` | edge-tts wasn't available. `pip install edge-tts`, then re-render with `--engine edge`. |
| Everything looks stale | Delete `site/` and rebuild. It's generated; nothing in it is precious. |
| Only one episode shows up | You're running an old copy of the folder. Check the path `run.bat` prints. |
| No video anywhere | The site build never makes one. Run `make-video.bat`. |
| `WinError 2 · cannot find the file specified` | ffmpeg isn't on PATH. Install it, then **open a new terminal**. |
| `NOT READY` from make-video | Something in the checklist is missing. It names each one and how to fix it. Nothing was rendered. |
| Render stops partway with a TTS error | Microsoft's free voice service throttles long runs. Every scene before it is cached — wait a minute and run `make-video` again; it resumes where it stopped. |

---

**Course instructor:** Narjes Abbasabadi, Ph.D. · Assistant Professor
Department of Architecture · College of Built Environments · University of Washington
