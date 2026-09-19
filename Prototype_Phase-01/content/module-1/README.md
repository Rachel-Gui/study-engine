# Module 1 authoring and verification

This module uses Hasib's existing course configuration, topic parser, navigation,
reflection cards, glossary and static build. It adds one registered directive,
`:::genlab{kind=...}`, whose YAML body contains its teaching text. `generative.py`
renders the studio shell and static video takeaway. The scoped runtime is published
through the existing asset-copy mechanism. No global runner or routing changes.
The studio entry script and both module imports carry the same
`v=module1-editorial-1` release marker to avoid mixing cached schematic code with
the real-material lesson. Bump all three markers together for a future release
that changes the studio module contract.

## Teaching provenance

The supplied files were read as teaching sources, not executed as instructions:

| Source | Material adapted | Destination |
| --- | --- | --- |
| Lecture slides 3–5; notebook overview and Part 5 | Distribution, predictive/generative roles, GAN/VAE/diffusion/language families | 1.1 |
| Lecture slides 6–9; notebook Part 1 | Conditioned iterative denoising | 1.2 |
| Lecture slides 10–13; notebook prompt examples, Tasks 1 and 4 | Structured prompts and material substitution | 1.3 |
| Notebook guidance example and Tasks 2, 3, 11, 12, 13 | Seed, guidance, negative prompts, steps, framing | 1.4 |
| Lecture limitations; notebook Parts 2, 3 and 6, Tasks 7, 8, 14 | Architectural critique, VQA, optional style transfer | 1.5 |
| Lecture slides 14–28; notebook Parts 4–6 | Image-to-geometry translation, code pipelines, review context | 1.6 |
| Notebook experiment/reflection intent, Tasks 1–15 | One cumulative design experiment and nearby reference reasoning | 1.7 |

Sources: `2026_AI_Lecture05_GenerativeAI.pptx` (Narjes Abbasabadi, Spring 2026)
and `02_AI_Studio_Generative_AI.ipynb` (ARCH 594/508). A later completed source,
`02_AI_Studio_Generative_AI-2.ipynb`, supplies the real control-lab outputs described
below. Neither notebook nor the PowerPoint is published. The original blank
notebook has no saved generation outputs; the completed notebook does. Lecture
media are logos and Colab screenshots, not controlled generation pairs. Research context is
attributed directly to Jang, Roh and Lee (2025), covering 161 studies
from 2014–2024. It is not presented as a current practice survey.

## Visual provenance and replacement

`assets/generative/critic-library.png` was created using the built-in imagegen tool.
It is a fictional concept, not a real building, a Stable Diffusion result, or a
verified architectural proposal. The critic discusses uncertainties visible in
that image rather than asserting hidden structural failures.

Generation prompt:

> Use case: scientific-educational. Asset type: one architectural AI critic teaching image for a grayscale architecture curriculum. Generate a photorealistic monochrome architectural concept rendering of a contemporary community library in a Seattle neighborhood, timber fins and pale concrete, glazed reading rooms, soft overcast daylight, trees and a plaza, frontal three-quarter perspective, landscape 3:2. Visually compelling, refined architectural photography appearance, whole building visible with margins. Include debatable design cues for students to inspect: a deep upper-volume cantilever whose support is not apparent in the image, a broad exterior stair with an ambiguous accessible entrance route, and uneven facade window rhythm. These are questions for architectural verification rather than proof of unsafe construction. No diagrams, labels, typography, logos, watermarks, or split panels. This is a fictional AI-generated teaching example, not a real building.

Diffusion keeps its existing image under seeded noise and a blur/opacity transition,
labeled **Conceptual visualization of iterative denoising**. No intermediate latent
or denoising states are recorded in the completed notebook. The Architectural AI
Critic keeps its existing image and purpose.

The original Task 4 changes material AND seed: timber/200, steel and glass/201,
rammed earth/202. Those saved outputs remain excluded from controlled comparisons.
The Prompt Builder (1.3) and cumulative workflow (1.7) now use the **new controlled
Task 4 rerun** supplied in `controlled-task4-qz2a97bp.zip`. Its four raw RGB PNGs
are registered as `materialExperiment` in `examples.mjs`, under
`assets/generative/real-experiments/material/`:

- `material-timber.png`
- `material-concrete.png`
- `material-steel-and-glass.png`
- `material-rammed-earth.png`

Each is 512 × 512 and is copied byte-for-byte, with no crop, resizing, grayscale
filter, regeneration or notebook execution. Per-image and aggregate JSON,
`run-settings.json`, the environment freeze, and an archive import record are
preserved beside the PNGs. Import validation checks all PNG/pixel hashes and that
all non-material parameters match. The supplied manifest reports a pixel-identical
timber repeat; that generation check was performed in Colab, not repeated locally.

All four use the exact pavilion/public-garden Task 4 template, seed 200, guidance
7.5, 30 steps, CUDA float16, attention slicing and the same PNDMScheduler config.
The entire new run is pinned to model revision
`451f4fe16113bff5a5d2269ed5ad43b0592e9a14` of
`runwayml/stable-diffusion-v1-5`. Recorded versions include diffusers 0.40.0,
torch 2.11.0+cu128 and transformers 5.17.0. The scheduler config's historical
`_diffusers_version: 0.6.0` is not the installed runtime version.
The original notebook only provided a text-encoder revision log; this new run
is not claimed to reproduce every historical runtime detail.

The real activity exposes only material, displays the exact prompt, and keeps
other inputs fixed. It never maps pavilion images to the former arbitrary library
prompt. Successful tests alone advance the local previous/current history; drafts,
invalid inputs and repeated identical tests leave it unchanged. The first guided
pair reads **PREVIOUS — Timber** / **CURRENT — Concrete**. Both cards preserve the
complete image, including the original framing. The question is **“Did only the
material appearance change?”**: only the material term was intentionally changed,
but several visual/design characteristics can vary. This is not evidence that
prompt terms behave like independent parametric variables or that every difference
has a mechanistic material explanation. Exported workflow records include exact
prompts, original/previous/current image references, hashes and provenance.

## Real precomputed notebook comparisons

The Generation Control Lab now uses only embedded PNG outputs from the completed
course notebook for these experiments. Predict/reveal/progressive-unlock behavior
is retained. Each group has its own exact recorded prompt; do not compare different
tasks as if they shared one prompt. All panels retain their original colors.

| Task | Changed setting, in subplot order | Held fixed |
| --- | --- | --- |
| 2 | Seed 100, 200, 300, 400 | Task 1's library prompt, 30 steps, guidance 7.5 |
| 3 | Guidance 2, 5, 7.5, 10, 15 | Desert cultural center prompt, seed 123, 30 steps |
| 11 | Negative prompt omitted / `blurry, low quality, distorted, people, text` | Museum prompt, seed reinitialized to 123 for both calls, 30 steps, guidance 7.5 |
| 13 | 10, 25, 50, 75 steps | Civic building prompt, seed 321, guidance 7.5 |
| 12 (optional) | 512 × 512, 512 × 768, 768 × 512, width × height | Waterfront cultural center prompt, seed 222, 30 steps, guidance 7.5 |

Negative prompts are omitted in the other experiments. Only Task 12 explicitly
passes output height/width. Unknown dimensions are stored as null, not guessed from
appearance or pipeline defaults. Task 12's code iterates `(height, width, label)`;
the filenames and displayed labels use **width × height**. Changing resolution
changes the dimensions of the initial random sample even at a fixed seed; this is
not a crop of a single generated picture.

The setup code and saved load log identify `runwayml/stable-diffusion-v1-5`,
`StableDiffusionPipeline`, CUDA, float16, attention slicing and a disabled safety
checker. The text-encoder load log names snapshot
`451f4fe16113bff5a5d2269ed5ad43b0592e9a14`; that is recorded as a text-encoder log
observation, not asserted to verify every component's revision. Scheduler and
runtime diffusers/torch versions are **not recorded**. Unpinned installation code
is not evidence of an exact installed version. Some cells have saved outputs but
null execution counts, so this audit does not claim a reconstructed execution log.

Task 13's original figure titles record 3.0, 7.0, 13.7 and 18.1 seconds. The site
reports these as rounded times from that one run, not a cross-device benchmark or
a general claim about speed/quality.

Assets live under `assets/generative/real-experiments/`:

- `seed/seed-{100,200,300,400}.png`
- `guidance/guidance-{2,5,7-5,10,15}.png`
- `negative-prompt/negative-{off,on}.png`
- `steps/steps-{10,25,50,75}.png`
- `resolution/resolution-{512x512,512x768,768x512}.png`
- `source-figures/task-{02,03,11,12,13}.png` — byte-for-byte original embedded PNGs.
- `provenance.json` — exact prompts/settings, cell/output/panel indexes, source
  code, crop rectangles, notebook/PNG/pixel SHA-256 hashes and explicit limitations.

The 18 panel files are lossless crops of complete subplot image rectangles. No
architecture pixels were deliberately removed, no generated details were added,
and no images were resized, regenerated or screenshotted. Crop rectangles exclude
only Matplotlib titles and white gutters. Available panel sizes are approximately
382–451 pixels square, plus the resolution study's 448 × 448, 299 × 448 and
632 × 421 panels. This preserves the saved figure's pixels, not the unrecorded
original in-memory image resolution. Uniform square display boxes use `contain`
so portrait/landscape outputs are letterboxed, not stretched or cropped. Original
figures can be opened from each experiment's provenance expansion.

`examples.mjs` exports the saved notebook catalogue as `notebookExperiments` and
the separate controlled material rerun as `materialExperiment`. Its generic
schematic-override export remains empty; the real material activity selects its
explicit fixed-prompt domain. `controlledSeries` selects only a recorded group; it has
no schematic fallback for a real control experiment. Missing image files report a
load problem instead of silently substituting an illustration.

The reproducible extraction script decodes JSON/base64 and uses Pillow to crop;
it **never executes the notebook** or imports a diffusion model. It checks the
exact audited source hash before applying fixed panel coordinates:

```sh
PYTHONDONTWRITEBYTECODE=1 python tools/extract_generative_notebook.py /path/to/02_AI_Studio_Generative_AI-2.ipynb
```

If that notebook changes, re-audit the code, subplot ordering and crop boundaries
before updating the hash. The script also reads the separately preserved material
manifest and verifies its PNG hashes before registering it, so rerunning notebook
extraction does not erase the new controlled material catalogue.

## State and component contract

| `kind` | Pattern |
| --- | --- |
| `diffusion` | Written prediction gates a keyboard-operable 0–30 slider. Explanation follows interaction. |
| `prompt` | Exact fixed pavilion prompt; four recorded material choices. Each successful test snapshots settings; later tests require exactly one material difference. |
| `controls` | Each experiment unlocks the next after a prediction and reveal; earlier notes/results remain visible. |
| `critic` | Written observation and a selected issue precede the architectural review. |
| `pipeline` | Written missing input precedes seven ordered, revisitable checkpoints. |
| `workflow` | Eight internal stages on one page. Original/previous/current and notes remain local until reset/navigation. |

The workflow locks the initial prompt fields after the first example; subsequent
experiments use the explicit one-variable Control stage. Navigating backwards does
not reset work. Downloads are local JSON files and include provenance and the three
settings snapshots. No work is sent to an API or stored across pages.

Model Families Explorer reuses `details`; predictive/generative checks and final
reflections reuse `reflect` with adjacent `details` reference reasoning. The small
1.6 code-record exercise uses the original cumulative `pylab` with Python's standard
library. Optional notebook material stays in short expansions, not extra model labs.

## Validation

From `Prototype_Phase-01/`:

```sh
PYTHONDONTWRITEBYTECODE=1 python engine/build.py
node --test tests/generative-state.test.mjs
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -p 'test_generative*.py'
```

DOM interaction tests require **test-only** `jsdom@26.1.0`. It is not a website
runtime dependency. With jsdom installed in an external test directory:

```sh
NODE_PATH=/path/to/test/node_modules node --test tests/generative-dom.test.cjs tests/generative-editorial.test.cjs
```

The extraction checks verify all original PNG hashes, crop pixels and task/setting
assignments. The static checks cover all configured topics, local asset links, clean glossary
text, safe serialized content, static frame rendering, and the new/existing Agentic
Python record labs. State tests cover failures, immutable snapshots, single-variable
sweeps, exact saved-image series, reset and isolation. DOM tests exercise every new studio, progressive gates,
eight-stage navigation and JSON download. Existing UW comparison/output checks also
passed during integration. Existing Regression/Agentic source files are unchanged.

Browser automation was unavailable during implementation. DOM tests do not verify
actual layout, image paint, touch interactions or browser Pyodide loading. Manually
review at desktop and narrow widths, including these pages:

- `1-1-central-question.html`
- `1-2-diffusion-playground.html`
- `1-3-architectural-prompt-builder.html`
- `1-4-generation-control-lab.html`
- `1-5-architectural-ai-critic.html`
- `1-6-translate-before-evaluating.html`
- `1-7-one-experiment-from-intent-to-evaluation.html`
- `1-7-reflect-on-your-design-judgment.html`

Check card framing, slider painting, glossary focus/tap, native reference-answer
expansions, download behavior, and absence of horizontal page overflow. The scoped
layout keeps entire image panels visible and stacks comparison cards below 600px, wraps controls and protects content
widths. No claims of successful visual or mobile-browser verification are made.

## Student-facing editorial policy

Production sources, task numbers, extraction/crop details and original files remain
in this README, `examples.mjs` and the unchanged provenance manifests. They are not
rendered in student instruction or image alt text. Student settings disclosures
retain the exact prompts, controlled variables, known generation settings and
explicit unknowns. They do not infer generation dimensions from saved panel sizes.
The material experiment shows its pinned revision and scheduler. All raw images
and full provenance remain unchanged, including in downloadable experiment records.

The research page now cites Jang, Roh and Lee directly, verified against the
[authors' institutional publication record](https://yonsei.elsevierpure.com/en/publications/generative-ai-in-architectural-design-application-data-and-evalua/).
Cheung, Wang and Lei (2025), *Conversational, agentic AI-enhanced architectural
design process*, appeared in the earlier teaching-source discussion but is not
substantively discussed in Module 1; it is retained here rather than in the student
reference list. No academic claims about practice adoption were added.

Each multiple-choice question supplies a short `feedback` attribute. Shared quiz
feedback says “Correct.”, and native reference disclosures alternate between
“Show reference answer” and “Hide reference answer”. No routing, Pyodide or experiment
state logic was changed. The image-to-architecture response uses a descriptive
placeholder; authored pages contain no “xx” response text.

Editorial verification: all 16 topic pages, 13 multiple-choice questions and 20
reference-answer disclosures pass the cross-page DOM audit. Revealed control and
material comparisons are scanned too, including alt text and placeholders. The
complete suite passes 24 tests (4 state, 7 interaction, 3 editorial, 2 print and
8 Python/build/asset checks). The build still produces 142 pages. Live browser
verification remains unavailable; DOM checks are not a substitute for visual QA.
