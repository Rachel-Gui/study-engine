# Response to comments — academic grounding and lesson revisions

Prototype Phase 01 · ARCH 594/508 AI for Architecture · September 2026

This note answers each point of the September review, in its order. Every paper listed
below was checked by DOI; statements attributed to a paper come from its full text where
that was open (Lystbæk; Liang, arXiv version; Ma, NSF accepted manuscript; Qiao, arXiv
version) and otherwise from its abstract, highlights and visible sections only. Where a
detail could not be verified (for example, the exact role labels in Lee et al. or the
stage labels in Fang et al.), the course does not attribute it to the paper.

## 1. The three uses of the papers

**Selected readings.** Every module page now ends with a *Selected readings* list
(authors, title, venue, DOI link, one line on why to read it, and how to get it: open
access, subscription through UW Libraries, or preprint). A site-wide page,
`readings.html`, collects all of them, linked from the sidebar and the modules page.
Lessons that lean on a paper also carry a short readings box at the end of the lesson.
30 papers in total (34 module entries, since a few serve two modules); the list is in `course.yml` under each module's `readings:` key,
so it can be copied into Canvas directly.

**Checking definitions, classifications, applications and limitations.** Each lesson
below was revised against its paper(s); section 2 lists what changed.

**Diagrams.** No published figure is reproduced. Nine new diagrams were drawn from
scratch in the course's own visual language, each with a footer naming the paper whose
taxonomy or workflow it follows ("Original diagram after …"). The one CC BY source
(Lystbæk 2025) is still redrawn, and attributed with its licence.

| Diagram | Lesson | After |
|---|---|---|
| Course map with module pictograms | 0.1 | course's own |
| Generative AI in architectural design: models, phases, data, evaluation | 2.1 | Jang, Roh & Lee (2025) |
| Human–AI collaboration: stages, roles, media | 2.10 | Fang et al. (2025) |
| Nine ethical issues and seven research directions | 2.10 | Liang et al. (2024) |
| The comprehension–verification–debugging loop | 3.1 | Qiao, Shihab & Hundhausen (2026) |
| Perception → generative → agentic → physical AI; applications, DIKW roles, learning approaches | 4.1 | Lee et al. (2025) |
| Model-centric vs data-centric; five checks before modelling | 5.1 | Zha, Jakubik, Whang, Sambasivan, Gebru |
| Design stages, influence/cost curves, ML-driven effort, five domains | 6.1 | Lystbæk (2025), CC BY 4.0 |
| Four ways physics enters a model, with benefits and costs | 8.4 | Ma, Jiang, Hu & Chen (2025) |

## 2. Module by module

**Coding Foundations / AI-Assisted Coding (Qiao et al. 2026).** Module 3 is renamed
*AI-Assisted Coding and Vibe Coding*. Lesson 3.1 now frames the topic with Qiao et al.'s
shift "from writing code to comprehending, refining, and integrating LLM-generated code",
and adds a section on what the evidence shows: explanations are often partly right and
partly wrong at once (93 % / 50 % in one study), code plus the error message raised one
tool's fix rate from 11 % to 78 %, and over-reliance can erode independent comprehension.
The loop taught is describe → generate → comprehend → verify → debug → integrate. The
3.1 video gained a scene on these findings.

**Generative AI (Jang et al. 2025; Fang et al. 2025).** Lesson 2.1's definition and
model-family taxonomy were checked against Jang et al. (161 papers, 2014–2024: GANs lead
the corpus, transformers and diffusion rising since 2021; 68.94 % of studies in schematic
design; images dominate inputs and outputs; evaluation mostly comparative or by the
authors themselves). A new figure and paragraph present this. Lesson 2.5 cites the
evaluation findings and Fang et al. on designer judgment.

**Critical AI in Architecture (Liang et al. 2024; Fang et al. 2025).** New Lesson 2.10,
*Critical AI in architecture: bias, responsibility, and evidence*, placed as the last
lesson of Module 2 so it carries into every module after it. It covers: Liang et al.'s
nine ethical issues and seven research directions (noting that bias, explainability and
oversight appear among the directions, not the nine issues); where bias enters a
workflow; authorship, attribution and agency (after Fang et al.); human oversight and
appropriate reliance (over- vs under-reliance); the distinction between AI-generated
output and validated architectural evidence; and a five-part AI-use statement. It has
its own 15-scene video. *If a separate ninth module is preferred, the lesson moves as
one file and one line in `course.yml`.*

**Agentic AI (Lee et al. 2025).** "Workshop" is removed throughout (21 files): Lesson
4.4 is *Setup: Environmental Negotiators on your own laptop* and 4.5 is *Environmental
Negotiators: a multi-agent design negotiation*. Lesson 4.1 now gives Lee et al.'s
definitions of an agent and of agentic AI, the perception → generative → agentic →
physical sequence, the five application areas, roles on the DIKW ladder (ending in
decision *support*), and the four learning approaches — and maps the definition onto
the course's fifteen-line agent class. The 4.1 video has a new scene on this.

**Data Literacy / EDA (data-centric AI literature).** The Python/EDA content is kept.
Lesson 5.1 adds a section on the data-centric view (Zha et al. 2025; Jakubik et al.
2024; Whang et al. 2023), data cascades (Sambasivan et al. 2021: 92 % of 53
practitioners), and five checks before modelling — provenance, distributions,
missingness, imbalance, readiness and leakage. Lesson 5.3 adds missingness mechanisms
(MCAR / MAR / MNAR, after Emmanuel et al. 2021) and class imbalance (Johnson &
Khoshgoftaar 2019), with a browser lab that removes the highest loads from the dataset
and shows the mean shift from 22.31 to 19.44 kWh/m². Both videos were updated.

**Machine Learning (Lystbæk 2025).** Lesson 6.1, previously a starter draft, is now
complete: an architectural example for each learning type; Lystbæk's 230-paper review
(five domains — building performance 99, design generation 71, evaluation 26,
structural 20, BIM automation 14 — design stages PD–OP, the ML pipeline, and the
ML-driven effort curve); the finding that most applications target early design; and
the review's open problems. Lesson 6.4 cites the class-imbalance literature. The 6.1
video has a new diagram scene.

**Deep Learning / Advanced Deep Learning (Ma et al. 2025; AEC reviews).** Lesson 8.4's
"four ways physics enters a model" now follows Ma et al. exactly: inputs, loss functions,
architecture, ensembles, each with the review's benefit and cost. Two corrections
followed: a PINN is one instance of the loss route, not a synonym for physics-informed
ML; and a monotonic bound belongs to the architecture route. Pure surrogates are noted
as outside the review's scope. Lessons 8.1–8.3 now cite recent reviews for their
application and limitation lists: CNNs/vision (Khan et al. 2026; Li et al. 2026;
Pizarro et al. 2022; Biljecki & Ito 2021), GNNs (Jia et al. 2023; Wettewa et al. 2024;
Zhao et al. 2024), sequences/transformers (Mathumitha et al. 2024; Zhao et al. 2026;
Eren & Küçükdemiral 2024). Lessons 7.1, 7.4 and 8.5 carry readings. The accuracy-
boundaries page (9.1) gained two rules: quote a review's percentage with its scope, and
never reproduce a published figure.

## 3. Specific comments

**0.1 / Introduction video.**
- "Workshop" removed from Agentic AI everywhere.
- "test them honestly" replaced by "evaluate them on unseen data" (and "honest"
  phrasing about evaluation replaced course-wide).
- Modules are now introduced visually: an original pictogram for each module on the
  course map (page) and a module gallery scene in the video.
- Voice: the default is now a U.S. female voice, `en-US-AvaMultilingualNeural` (one of
  Microsoft's newer, most natural neural voices), slightly slowed. The voice cannot be
  auditioned from the build environment, so a sampler is included:
  `voice-samples.bat` / `voice-samples.sh` records the same paragraph in ten voices
  (U.S., U.K., Australian; female and male) with a page to play them side by side.
  Changing the voice is one line in `course.yml`.

**1.1.** Every environment is now shown as it is introduced — the python.org download
page, the Windows installer with the *Add python.exe to PATH* box highlighted, the
terminal, VS Code (explorer, editor, terminal panel), the pip install, and a Colab
notebook with cells and outputs — on the page and as animated scenes in the video
(six of its fifteen scenes). These are drawn mock-ups of the real interfaces rather
than screenshots, so they stay current and carry no personal details.

**2.1.** Example images now appear at the point image generation is introduced: four
outputs of one prompt with four seeds, from the course's own Stable Diffusion
experiments, followed by one image examined "as an architect" (plausible vs. buildable
vs. evidence).

## 4. Status

- Site: 302 pages, 43 lessons, 43 video storyboards (515 scenes); all tests pass; no
  JavaScript errors on any page.
- Videos: all changed lessons render; previews are silent 720p/1080p because the build
  environment cannot reach the voice service. The final 4K narrated render is one
  command on a machine with internet access (README §4).
- Still to do: 6.2 and 6.5 remain starter drafts; subscription papers (Jang, Fang, Lee)
  should be read in full through UW Libraries before quoting further detail.
