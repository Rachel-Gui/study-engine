# DesignAI Curriculum — Prototype, Phase 01

**AI for Architecture**, ARCH 594/508 — generative AI, agentic AI, machine learning
and deep learning for the built environment.

**One markdown file per lesson, plus a short storyboard. Two outputs: an
interactive site and one narrated, animated video per lesson.** The lesson file
(`6.3-regression.md`) makes the web pages; its storyboard (`6.3-regression.video.md`)
makes the 4-to-8-minute video, scene by scene — motion graphics, a pause-and-predict
quiz, a pointer back to the labs on the site. Change one scene, re-render one scene.

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
> `run.bat` prints the folder path and a list of every lesson it built, then a line
> like `302 pages · 43 lessons · 43 video storyboards · 515 video scenes`. **If it
> says 1 lesson, you are running an old copy.** Delete stale folders rather than
> keeping them around.

The site opens on a full-screen **landing page** (`index.html`): the course title,
the instructor, one *Start the course* button and — once a student has read
something — a *Continue where you left off* link. *Start* leads to the **modules
page** (`modules.html`): a block for every module with its question, an expandable
list of its lessons and an *Open* link, plus a short "how to use" strip. Neither
page shows the contents panel; it appears once a module is opened, and *All modules*
at its top goes back. Every page except the landing has a **search box** in the
header (press `/` to focus it) that searches every topic, lab and lesson from a
static index the build writes to `site/search.json`. The footer has only the
Previous / Next arrows.

It builds the site and opens `http://localhost:8000`. Leave the window open; press
`Ctrl+C` when you're done. Or type it yourself:

```
python engine/build.py --serve
```

> **Don't double-click `site/index.html`.** Most of it looks fine, which is the trap
> — but the Python labs won't run. Pyodide fetches its WebAssembly from a CDN, and a
> `file://` page has a null origin, so the browser blocks it. `--serve` fixes it.

## Publish it as a website

The built `site/` folder is a static website: no server code, so any static host
serves it. The lab's DesignAI-Curriculum repository is private, and GitHub Pages
only publishes private repositories on paid organisation plans, so the simplest
route is a **public repository of your own that holds only the built site**:

1. On github.com, **New repository** → name it (say `ai-for-architecture`) → **Public**
   → tick *Add a README* → Create.
2. Clone it with GitHub Desktop (*File → Clone repository*) to a short path such as
   `D:\ai-for-architecture`.
3. Repo **Settings → Pages → Build and deployment**: Source *Deploy from a branch*,
   Branch *main*, folder */ (root)* → Save.
4. Open `publish-site.bat` (Mac: `publish-site.sh`) in a text editor and set the
   `SITE_REPO` line to that folder. Save.
5. Double-click **`publish-site.bat`**. It builds the site and mirrors `site/` into the
   website repo. Then, in GitHub Desktop with that repo selected: type a summary,
   **Commit to main**, **Push origin**.
6. About a minute later the site is live at `https://<your-username>.github.io/ai-for-architecture/`
   (the exact URL is on the Settings → Pages screen). Repeat step 5 to update it.

The build writes a `.nojekyll` file into `site/`, which tells GitHub Pages to serve the
files exactly as built. The labs (Pyodide from a CDN), the fonts and the search box all
work on Pages as they do locally. If the lab repository is ever made public, or the
organisation is on a plan that publishes private repositories, the workflow in
`publish-to-github-pages/` (delivered alongside this folder) does the same thing
automatically on every push, straight from the lab repo.

Alternatives that also work with a private source: Netlify Drop (drag the `site/`
folder onto app.netlify.com/drop — instant URL, no git), or Cloudflare Pages, which
can also put the site behind an email login for a class.

### Before a presentation

Build and serve beforehand, then **run one Python lab while you still have wifi**.
Pyodide downloads about 10 MB the first time and the browser caches it. Load every
page you plan to show, too — the fonts come from Google Fonts.

---

# 2 · Add a chapter

Two steps. That's the whole process.

**Step 1** — create the file:

```
content/advanced-dl/8.6-vision-transformers.md
```

**Step 2** — add one line to `course.yml`, under the right module:

```yaml
  - title: "Module 8 — Advanced Deep Learning for Architecture"
    short: "Advanced Deep Learning"
    episodes:
      - advanced-dl/8.5-pinn-from-scratch.md
      - advanced-dl/8.6-vision-transformers.md  # ← your new line
```

The sidebar, the landing page, the topic counters, the Previous/Next buttons (with
the neighbouring topic's title), the module and lesson landing pages, and the
instructor block all generate themselves. You never edit them.

Each module in `course.yml` has a `title`, a `short` name (used in the contents
panel and on the landing-page cards), a `question` (the module's lede) and,
optionally, a list of module-level `objectives` shown on its landing page. Each
lesson carries one or two specific `objectives:` in its frontmatter (see §3); they
appear on the lesson's landing page and on its video's title card.

**The fastest start is to copy an existing lesson.** `advanced-dl/8.4-physics-informed.md`
uses nearly every feature (figures, two widgets, a lab, a step-through, predict,
technical, boundary); `ml/6.2-statistics.md` is a simpler one; `coding/1.1-setup-python.md`
shows the Windows/macOS panes and tables; `generative/2.8-llms-and-structured-generation.md`
is a compact concept-plus-lab lesson with objectives.

## Editing on github.com — no git needed

Open any file on GitHub, click the **pencil icon**, type, and press **Propose
changes**. GitHub makes a branch and a pull request for you. Narjes reviews and
merges. You never install anything.

---

# 3 · Write an episode

You need to know three things. Everything else is ordinary Markdown.

1. **`## Heading`** starts a new **topic** — one screen, one page.
2. **`:::narration`** is the topic's spoken-voice prose (and the video fallback, §4).
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

Add one or two lesson objectives right there in the frontmatter — they are shown
on the lesson's landing page and on its video's title card:

```yaml
objectives:
  - Explain what a language model does — predict the next token, repeatedly — and why that makes its output fluent but not verified.
  - Turn a prompt and context into a structured output and validate it before anything downstream depends on it.
```

Keep them specific to the lesson; module-wide goals belong in `course.yml` under
the module's `objectives:`.

## Narration

```markdown
:::narration
Write it the way you would say it out loud. Spell out numbers and acronyms — "R
squared", "G P Us", "nineteen eighty six" — because a speech engine reads this
literally.
:::
```

**Narration is the lesson's spoken voice on the page**, and it is optional per
topic. The videos do **not** read the page aloud: every lesson has its own storyboard
(`<lesson>.video.md`, section 4), written for a student who has never met the topic.
The narration blocks are the fallback — a lesson *without* a storyboard gets a plain
automatic video built from its narrated topics — and they still feed the `--scripts`
narration scripts.

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
| `:::trace{title="…"}` | A **step-through recording**: the program runs once at build time and the page replays it line by line with a variables table and output pane (Python Tutor style). See below. |
| `:::resources` | Link cards |
| `:::refs` | Reference list with DOIs |
| `:::readings` | **Selected readings** box — the papers a lesson leans on, each with a DOI link and one line on why to read it. See below. |
| `:::gallery{cols=4 caption="…"}` | A grid of images (or pictograms / figures) with a title and caption under each — for the example images Narjes asked for. See below. |
| `:::screen{kind=terminal|editor|notebook|browser|installer}` | A drawn **mock-up of a real screen** — a terminal, VS Code, a Colab notebook, a browser page, a Windows installer — described in a few YAML lines. Used in 1.1 to show every environment before the student meets it. See below. |
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

Cell counts: `cards`, `compare`, `refs`, `gallery` and `workflow` take **3**; `stats` and
`boundary` take **2**; `readings` takes **4**; `resources` takes **5** (`KIND | Title | Source | Description | URL`).

**Selected readings** (`:::readings`) — one paper per row: `Authors (year) | Title. Venue,
volume, pages. | https://doi.org/… | why read it`. Put it near the end of a lesson,
before `:::boundary`. The same papers also go in `course.yml` under the module's
`readings:` key (`cite`, `title`, `venue`, `doi`, `why`, `access`), which is what
fills the module page's reading list and the site-wide **Selected readings** page
(`readings.html`). `access` says how a student gets the paper: "open access (CC BY
4.0)", "subscription (UW Libraries)", "preprint arXiv:…".

**Galleries** (`:::gallery{cols=4 caption="Figure 1. …"}`) — one tile per row:
`src | Title | one-line caption`. `src` is an image path under `assets/`, or
`art:m2` for one of the module pictograms, or `fig:course_map` for a figure. Use it
where a topic is introduced that a student has never seen — the four seeds of one
prompt in 2.1, say — so the first encounter is visual.

**Screens** (`:::screen{kind=terminal caption="…"}`) — the body is YAML describing
the screen, and the engine draws it (no screenshots, so nothing goes stale or
carries someone's username). Each kind takes a few fields:

```markdown
:::screen{kind=terminal caption="Check the install."}
title: Command Prompt
prompt: "C:\\Users\\you>"
lines:
  - "$ python --version"        # "$ " marks a typed command
  - "Python 3.13.2"             # anything else is output
callout: The prompt is the folder you are in
:::
```

`editor` takes `files`, `file`, `code`, `terminal`; `notebook` takes `runtime` and
`cells: [{code, output}]`; `browser` takes `url` and `page: {title, lines, button,
small}`; `installer` takes `dialog`, `options` (first is primary), `checks` (a leading
`*` ticks and highlights one) and `callout`. The same YAML, as a `screen` scene in a
storyboard, is drawn on the video stage and animated line by line. `engine/screens.py`
has every field with an example.

`:::compare` is labelled **A / B** by the stylesheet — never a tick or a cross. A
comparison is not a verdict.

### Tables, code blocks, and evidence labels

Ordinary Markdown tables (`| a | b |` rows with a `|---|---|` line) and fenced code
blocks (three backticks) work anywhere in prose, in every component. Use a fence
whenever line breaks matter — a three-line command
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

A student picks a tab once and the site remembers it on every page.

### Step-through recordings

```markdown
:::trace{title="A running total"}
areas = [12, 30, 5]
total = 0
for a in areas:
    total = total + a
print(total)
:::
```

`engine/tracer.py` runs the program **while the site builds** (it is course content,
not student input) and records, before every line, which line is about to run, every
variable in the global frame and in the current function frame, and what has been
printed. The page replays that recording with Back / Next / Run to end; nothing
executes in the browser. Functions, classes, loops, and crashes all work — a program
that raises shows the error as its last step, which is the point of the errors page.
`inputs="4|3.5"` feeds `input()` calls. Recordings are capped at 300 steps.

### Labs that need a library the browser Python does not ship

```markdown
:::pylab{title="seaborn" packages=numpy,pandas,matplotlib pip=seaborn}
```

`packages=` names Pyodide's own packages (numpy, pandas, scipy, matplotlib,
scikit-learn). `pip=` names pure-Python wheels vendored under `assets/wheels/`, which
the page installs with micropip from the site itself — no PyPI, works offline. Seaborn
0.13.2 is the one shipped; to add another, `pip download <name> --no-deps -d
assets/wheels` and add its file name to `PIP_WHEELS` in `engine/theme/site.js`.

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
for Modules 7–8 and `engine/figures_lit.py` for the diagrams drawn after the selected
readings — so they stay sharp on the site, in the 4K video (a `diagram` scene
draws any of them stroke by stroke), and can be diffed in git. Add a function, register it in the file's `ALL` dict, and reference it by that
key in `:::figure{id=…}`. Black line art; Spirit Purple for at most one emphasis
element per figure.

**No published figure is ever reproduced.** Where a lesson leans on a paper's
taxonomy, workflow or numbers, the figure is drawn from scratch in the course's own
language and its footer says so — "Original diagram after Lee et al. (2025) …" — with
the paper's percentages quoted as the paper's. Material under a Creative Commons
licence (Lystbæk 2025 is CC BY 4.0) is still redrawn, and attributed in the footer.
The nine literature figures: `course_map`, `genai_review_map` (Jang et al.),
`human_ai_collab` (Fang et al.), `agentic_framework` (Lee et al.), `ethics_map`
(Liang et al.), `data_centric` (the data-centric AI literature), `ml_design_stages`
(Lystbæk), `piml_taxonomy` (Ma et al.), `code_comprehension_loop` (Qiao et al.).
The same file holds the eight **module pictograms** (`figures_lit.ART`), used on the
modules page, the course map and the intro video's module gallery.

Interactive widgets live in `engine/widgets.py` and `engine/widgets_dl.py` and work
the same way: each has a `web()` for the site and a static diagram the video's
`diagram` scene can draw. Sixteen exist:

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
| `slice-lab` | 0.4 | list indexing and slicing with Python's exact rules, errors included |
| `hist-lab` | 0.6 | the 768-building dataset: bins, columns, split by orientation |
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
are CSS tokens (`--accent`, `--gold`) in `engine/theme/site.css`; the video scenes
(`engine/stage.py`) use the same two values. Don't add colours to content — if a diagram needs emphasis, use
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

# 4 · Make the videos

Every lesson has **one video, 4 to 9 minutes long**, and it is **not a recording of
the web page**. It is built from a short **storyboard** — `content/<module>/<lesson>.video.md`,
next to the lesson — as a sequence of animated scenes: a title card, one idea at a
time in big type, cards and lists that slide in as the voice reaches them, code that
types itself and prints its output, diagrams that draw themselves stroke by stroke,
bar and line charts that grow, a **pause-and-predict quiz** with a five-second
countdown ring before the answer is revealed, a "now go to the lesson page and run
this" scene, a recap, and a *next lesson* card. The sentence being spoken is shown as
a caption; the eyebrow names the lesson.

The tool is `engine/make_videos.py`. It renders **lesson by lesson** (43 files);
joining a module or the whole course into one file is opt-in (`--modules`, `--course`).
It also writes a **narration script** per video, which is what to circulate for review
before spending render time.

## The storyboard

A storyboard is a list of scenes. Each scene is a `:::scene{type=…}` block whose
body is YAML — a `narration:` (what the voice says, plain sentences, numbers written
out the way they should be spoken) plus the fields that scene type shows. This is
`content/eda/5.1-looking-before-modelling.video.md`, cut down:

```
---
episode: "5.1"
---

:::scene{type=title}
narration: |
  Welcome to module five, exploratory data analysis, and to lesson five point one. ...
:::

:::scene{type=idea icon=warn}
text: These are simulations, not measurements.
sub: Every conclusion in this module is a conclusion about the simulator, on those twelve shapes, in Athens.
narration: |
  Where a dataset came from matters more than anything you will compute from it. ...
:::

:::scene{type=quiz}
question: df[df["orientation"] == "N"] returns zero rows. Why?
options:
  - pandas cannot filter by text
  - The column holds the numbers 2 to 5, not letters, so nothing equals "N"
  - The dataset has no north-facing buildings
answer: 1
pause: 5
explain: Look before you filter. df.dtypes and df["orientation"].unique() would have shown the codes.
narration: |
  A check. You filter for buildings whose orientation is N, and get zero rows. Why? A: ...
  Pause and pick.
after: |
  It is B. Look before you filter. ...
:::

:::scene{type=site}
heading: Now load it yourself
page: Looking before modelling
path: Module 5 › 5.1 › pandas — tables
text: Run the numpy lab, then the pandas lab — head, describe, filter, groupby.
button: RUN STEP
narration: |
  Now go to the lesson page. ...
:::
```

The scene types, and what each one takes:

| type | shows | fields |
|---|---|---|
| `title` | the lesson number, title and objectives on a purple cover | `narration` |
| `idea` | one sentence in big type, with an optional line under it and an icon | `text` (use ` / ` for a line break), `sub`, `icon` = bulb · eye · code · check · warn · spark · build · data · net · loop · agent · question |
| `list` | items that appear one by one | `heading`, `items` — write `term — explanation` and the term is set bold |
| `cards` | two to four cards sliding in | `heading`, `items:` of `{title, text, tag}` |
| `steps` | boxes joined by arrows | `heading`, `steps` (a `*` prefix highlights a box), `note` |
| `compare` | two panes and a verdict | `heading`, `left`/`right` as `{title, points}`, `verdict` |
| `number` | two to four big numbers that count up | `heading`, `items:` of `{value, label, count: false}` |
| `code` | code that types itself, then its output | `heading`, `code` (≤ 12 lines, ≤ 80 columns), `output`, `note` |
| `chart` | a bar or line chart that grows | `kind` bar · line, `labels`, `series:` of `{name, values}`, `max`, `min`, `note` |
| `diagram` | a course figure drawing itself, plus up to four points | `id` (a figure or widget id), `heading`, `points`, `groups` |
| `quiz` | question, options, countdown, reveal | `question`, `options`, `answer` (0-based), `pause` seconds, `explain`, `narration` (ends with *pause and pick*), `after` |
| `site` | a laptop with the lesson page and a button | `heading`, `page`, `path`, `text`, `button` |
| `gallery` | a grid of pictures that pop in one by one — images, module pictograms or figures | `heading`, `items:` of `{image` or `art` or `figure, title, text, tag}`, `cols`, `aspect: square`, `note` |
| `image` | one picture large, with a heading, caption and up to three points beside it | `src` (under `assets/`), `heading`, `caption`, `credit`, `points` |
| `screen` | a drawn mock-up of a real screen, animated line by line — see `:::screen` in §3 | `kind` terminal · editor · notebook · browser · installer, the kind's YAML fields, plus `heading`, `text`, `points` for the panel beside it (leave them out for a full-width screen) |
| `recap` | what to remember, ticked off | `items` |
| `next` | the next lesson, on a cover card | `text`, `sub` |

Rules that keep the videos good: one idea per scene; ten to fourteen scenes; 650 to
1,200 narration words (the script tool prints the estimate); write for someone who
has never met the topic — say what a word means the first time it appears; the
`quiz` narration reads the options aloud and ends with *Pause and pick*; every number
on screen is a number from the lesson page or its dataset; the `site` scene tells
the student exactly which lab to run. YAML gotchas: quote a value that contains `: `
or that starts with a quote or a `*`; keep `#` out of unquoted values.

A lesson **without** a storyboard still gets a video — a plain automatic one built
from its narrated topics — and the render log lists which lessons those are, so
nothing is silently missing.

Scenes are content-addressed: the id is a hash of the quality, the lesson, the
scene's rendered HTML, its narration, its timing and the voice. Audio, captions and
the encoded scene cache under `.cache/` by that id, so **editing one scene re-renders
one scene** and the rest of the lesson is stitched from cache.

### The voice

The narration voice is set once, in `course.yml`:

```yaml
voice: "en-US-AvaMultilingualNeural"   # a U.S. female voice; the most natural edge-tts offers
voice_rate: "-3%"                      # a touch slower than the voice's own pace
```

To audition others before choosing, run **`voice-samples.bat`** (Windows) or
**`./voice-samples.sh`** (Mac/Linux). It records the same paragraph — the start of the
course introduction — in ten voices (U.S., U.K. and Australian, female and male,
`en-US-AvaMultilingualNeural` first) into `dist/voice-samples/`, with an
`index.html` that plays each one and shows the line to paste into `course.yml`.
`--all-english` records every English voice edge-tts has; `--rate -5%` tries a pace.
Changing the voice re-records every scene on the next run (the voice is part of the
scene id), so choose before the 4K render, not after. `--voice` and `--rate` on
`make_videos.py` override `course.yml` for one run.

## Setup — only on the machine that renders

Not everyone needs this.

```
pip install -r requirements.txt
playwright install chromium
```

**ffmpeg** — this is a *program*, not a Python package. `pip install ffmpeg` does
**not** work. The captions need an ffmpeg built with libass, which every normal
build (winget, Homebrew, apt) is.

- Windows: `winget install Gyan.FFmpeg`
- Mac: `brew install ffmpeg`
- Linux: `sudo apt install ffmpeg`

> ### ⚠ On Windows, close the terminal afterwards
> Windows only picks up a changed PATH in a **new** terminal. Install ffmpeg, close
> the window, open a fresh one, then run `python engine/build.py --doctor`. If it
> still says MISSING, the install didn't land on PATH.

**Fonts** — headless Chromium renders the video frames and libass renders the
captions, so Montserrat and IBM Plex Mono must be installed *on this machine*. The
web fonts in the site don't cover it.

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
and then renders one video per lesson at 4K. Or do it by hand:

```
python engine/build.py --doctor                             # what's installed?
python engine/make_videos.py --engine edge                  # every lesson, 4K
python engine/make_videos.py --engine edge --episode 2.8    # one lesson
python engine/make_videos.py --engine edge --module 6       # the lessons of one module
python engine/make_videos.py --engine edge --modules        # ...and also one joined file per module
python engine/make_videos.py --engine edge --course         # ...and also one file for the whole course
python engine/make_videos.py --scripts                      # only the narration scripts, no render
python engine/make_videos.py --engine edge --quality 1080p  # a fast preview (about 3x quicker)
python engine/make_videos.py --engine edge --force          # ignore the scene cache
```

Output:

```
dist/video/6-3-regression-predicting-continuous-outcomes.mp4    one per lesson (43 files)
dist/video/module-6-machine-learning.mp4                        only with --modules
dist/video/course.mp4                                           only with --course
dist/scripts/6-3-regression-predicting-continuous-outcomes.md   the narration script for that video
```

`python engine/build.py --video` still works — it builds the site and then runs
`make_videos.py` for every lesson.

Render 1080p first and watch two or three lessons before starting the 4K run. The
4K render of the whole course is hours, not minutes, and every scene it finishes is
cached, so it can be stopped and resumed.

### The narration scripts

Every video gets a markdown script in `dist/scripts/`: a table of scenes with start
times and lengths, and for every scene what appears on screen and the narration,
sentence by sentence. Timings are estimated at 2.45 words per second before a render
and measured from the audio after one. The scripts are the thing to share for review
before spending hours on a 4K render — `--scripts` writes all 43 in a second, with no
ffmpeg or voice needed. To change what a video says, edit the storyboard, not the
script; the script is generated from it.

### Resolution

Videos render at **3840×2160 (4K, 16:9) by default.** The frames are laid out on a
fixed 1280×720 canvas and rendered at three device pixels per CSS pixel, so text,
diagrams, code and captions scale together — enlarging the viewport would only add
empty margin. Lower resolutions for a quick preview:

```
python engine/make_videos.py --engine edge --quality 1080p    # 1920×1080
python engine/make_videos.py --engine edge --quality 720p     # 1280×720
```

Choices: `4k` (default), `1440p`, `1080p`, `720p`. The quality is part of the scene
id, so a 720p preview and the 4K render cache separately and never mix. Budget
roughly three minutes per lesson at 720p and five to eight at 4K on a laptop (frames
are captured only while something moves; holds are one frame); the voice step is the
same at every quality.

> ### Rendering can stop partway, and that's fine
> edge-tts uses Microsoft's free online voice service, which throttles a long run of
> requests. If it stops at scene 19, **every scene before it is already cached** —
> wait a minute, run the same command again, and it resumes from 19. The renderer
> retries four times with backoff before giving up, so this is rarer than it was,
> but on a 488-scene course it can still happen. Two or three runs and you have
> everything.

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
> silence** and you get mute videos that report success. `--engine edge` makes that
> a hard error instead.

Any Microsoft neural voice works, and re-rendering the whole course in a different
voice costs only the audio step:

```
python engine/make_videos.py --engine edge --voice en-US-AriaNeural
edge-tts --list-voices | grep en-        # see them all
```

`dist/` is gitignored. Send the files, or attach them to a GitHub Release.

## All the commands

```
python engine/build.py                        site only, about a second
python engine/build.py --serve                site + local server + browser
python engine/build.py --video --engine edge  site + one video per lesson, 4K
python engine/make_videos.py --engine edge    the videos alone (see above for --episode, --module, --modules, --course)
python engine/make_videos.py --scripts        the narration scripts alone
python engine/make_videos.py --engine edge --quality 1080p   faster preview
python engine/make_videos.py --engine edge --force           ignore the scene cache
```

---

# 5 · What's in here

```
course.yml                    module order, short names, questions, objectives, instructor, glossary,
                                the narration voice, and each module's selected readings
content/                      one <lesson>.md (the pages) + one <lesson>.video.md (the video) per lesson
  intro/                      0.1 Course Introduction (Narjes's text goes here; a :::todo marks the draft)
  coding/                     Module 1 · Coding Foundations: 1.1 setup (Python, VS Code, Colab);
                                1.2–1.4 Python from zero, three chapters for students who have
                                never coded (step-through recordings, labs, quizzes)
  generative/                 Module 2 · Generative AI: 2.1–2.7 (Rachel's studio lessons),
                                2.8 LLMs and structured generation, 2.9 a local model with Ollama,
                                2.10 Critical AI in architecture (bias, responsibility, evidence)
  vibe-coding/                Module 3 · AI-Assisted Coding and Vibe Coding: 3.1 what changes when
                                AI writes code, 3.2 code as design medium, 3.3 Claude Code on your
                                own model, 3.4 hands-on: vibe-code a design tool
  agentic/                    Module 4 · Agentic AI: 4.1–4.3 concepts, 4.4 setup on your laptop,
                                4.5 the Environmental Negotiators (hands-on)
  eda/                        Module 5 · Exploratory Data Analysis: numpy, pandas, matplotlib,
                                seaborn, scipy on the Energy Efficiency dataset + resources
  ml/                         Module 6 · Machine Learning: 6.1–6.6
  deep-learning/              Module 7 · Deep Learning Foundations: neuron, learning,
                                generalization, the ANN demo
  advanced-dl/                Module 8 · Advanced Deep Learning: CNN, GNN, sequences,
                                physics-informed + INR, a PINN from scratch
  reference/                  9.1 accuracy boundaries
assets/                       images, slides, assets/data/ for lab CSVs (UW campus energy;
                                Energy Efficiency, Tsanas & Xifara 2012, UCI/Kaggle, CC BY 4.0),
                                assets/wheels/ for pure-Python wheels the browser labs install,
                                assets/generative/ for Rachel's studio component
engine/                       the pipeline — nobody edits this
  build.py                      the only command for the site
  make_videos.py                the videos: one per lesson from its storyboard, plus narration scripts
  storyboard.py                 reads <lesson>.video.md; builds the automatic fallback for a lesson without one
  stage.py                      the scene templates (title, idea, cards, code, chart, diagram, quiz, gallery, image, screen, …) and their animation runtime
  screens.py                    the drawn screen mock-ups (terminal, editor, notebook, browser, installer) for :::screen and screen scenes
  voice_samples.py              records one paragraph in several narration voices so you can choose (voice-samples.bat / .sh)
  parse.py                      markdown + :::directives → topic tree
  components.py                 each component: web() and frame()
  figures.py  figures_dl.py  figures_py.py  figures_gen.py    static SVG diagrams
  figures_lit.py                the original diagrams drawn after the selected readings (course map, review maps, PIML routes, …) and the module pictograms
  widgets.py  widgets_dl.py  widgets_py.py    interactive figures
  tracer.py                     runs :::trace programs at build time and records them
  generative.py                 Module 2's generative studio component
  render_web.py                 → site/  (landing page, module and lesson pages, topics, readings.html)
  render_video.py               voice → beat timing → frames → ffmpeg; .cache/ → dist/video/*.mp4
  theme/site.css  site.js       theme: black, white, greys, Spirit Purple, Husky Gold
tests/                        checks for the studio component, quizzes, printing and the build
                                (python -m pytest tests · NODE_PATH=<jsdom> node --test tests/*.cjs tests/*.mjs)
run.bat  run.sh               build and open the site
publish-site.bat  publish-site.sh   build, then copy site/ into your public website repo (README section 1)
make-video.bat  make-video.sh  check prerequisites, then render one video per lesson (--modules / --course to join)
voice-samples.bat  voice-samples.sh   hear the narration voices, pick one, paste its name into course.yml
```

## Why every component has two renderers

Every component has a `web()` and a `frame()`. `web()` is the live thing on the site —
a Python lab is an editor, a widget is interactive. `frame()` is its static picture,
which the automatic fallback video uses for a lesson without a storyboard, and which
`diagram` scenes use for figures and widgets. Adding a component means writing those
two functions and adding one line to `REGISTRY`. Nothing else changes.

## Episodes that still need work

Search the site for the **Needs work** marker, or grep `:::todo` in `content/`.
Currently: **0.1** carries a draft Course Introduction until Narjes's text arrives;
**6.2 and 6.5** are starter drafts (6.1 was completed in the September revision). Modules 7 and 8 are complete to a first full
draft (every topic narrated, a widget, step-through or lab in every lesson); the
natural next additions are a 2D PINN in 8.5 and a real facade-image lab in 8.1,
both of which need Colab rather than the browser.

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
| No video anywhere | The site build never makes one. Run `make-video.bat`, or `python engine/make_videos.py --engine edge`. Videos land in `dist/video/`, not in `site/`. |
| Videos have no captions | Your ffmpeg was built without libass. The winget / Homebrew / apt builds have it; a minimal static build may not. |
| A scene's text is cut off in the video | The storyboard scene has too much in it. Keep `code` to 12 lines × 80 columns, lists to six items, cards to four, and split the scene in two. |
| `storyboard … scene N` error | That scene's YAML is invalid — usually a value with `: ` in it, or one that starts with a quote or `*`. Quote the whole value. The message names the scene. |
| A lesson's video is plain and short | It has no `<lesson>.video.md`, so it got the automatic fallback. The render log lists these under *no storyboard*. Write the storyboard (section 4). |
| `WinError 2 · cannot find the file specified` | ffmpeg isn't on PATH. Install it, then **open a new terminal**. |
| `NOT READY` from make-video | Something in the checklist is missing. It names each one and how to fix it. Nothing was rendered. |
| Render stops partway with a TTS error | Microsoft's free voice service throttles long runs. Every scene before it is cached — wait a minute and run `make-video` again; it resumes where it stopped. |
| The voice sounds mechanical, or you want another | Run `voice-samples.bat` / `./voice-samples.sh`, listen, paste the chosen `voice:` line into `course.yml`, and re-render. Every scene re-records (the voice is in the scene id), so decide before the 4K run. |
| A gallery tile is empty | The `src` path is wrong — it is relative to the site root, so `assets/generative/…`, no leading slash — or the `art:` / `fig:` key doesn't exist. `--doctor` doesn't check this; the page does. |
| A `:::screen` shows nothing | Its body isn't valid YAML. Quote Windows paths (`"C:\\Users\\you>"`) and any value with `: ` in it. The build prints the lesson and the error. |
| A paper is missing from `readings.html` | `readings.html` is built from `course.yml`, not from the lessons. Add the paper under the module's `readings:` key there too. |

---

**Course instructor:** Narjes Abbasabadi, Ph.D. · Assistant Professor
Department of Architecture · College of Built Environments · University of Washington
