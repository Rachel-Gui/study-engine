# Controlled Task 4 — Colab fallback

Local audit, 2026-09-17: this Codex host is macOS 15.7.3 ARM64, using
`/opt/anaconda3/bin/python` 3.13.5. That interpreter has no torch, diffusers,
transformers, accelerate or huggingface_hub installed. There is no default
Hugging Face model cache. The original setup explicitly requires CUDA; this
Mac cannot run that CUDA configuration. No model was run or substituted here.
The website, `examples.mjs`, and existing material comparison are unchanged.

## Run one cell

1. Open the completed course notebook in Colab and select a GPU runtime.
2. If starting a fresh session, run the original installation cell (cell 4,
   zero-based), restart as it instructs, and skip the other exercises.
3. Paste the **entire contents of `controlled_task4_colab.py` into one code cell**
   and run it. It loads its own pipeline; it does not depend on a previous `pipe`.
4. Allow the ZIP download when all four materials and the repeated-timber
   verification finish. Retain the saved notebook/cell as the execution record.

The cell generates timber, concrete, steel and glass, and rammed earth. It uses
Task 4's exact base prompt with `, primary material is {material}`, seed 200
reinitialized before every call, 30 steps, guidance 7.5, CUDA float16, disabled
safety checker and attention slicing as in the source notebook. All four outputs
use the same pipeline weights. The scheduler is loaded from the pinned model
and its class/config are preserved; its transient state is reset between calls.
Width/height are recovered from UNet sample size times VAE scale factor, the
pipeline's implicit default, and passed explicitly for every material. They are
not inferred from the resolution of a saved Matplotlib composite.

The notebook's cell-8 output records snapshot
`451f4fe16113bff5a5d2269ed5ad43b0592e9a14` for the **text encoder**. The new run pins
the entire pipeline to that repository revision. This is the best available
revision evidence, not proof of the original full pipeline's exact revision.
If the repository/revision is unavailable, the cell stops without choosing a
different model. No original scheduler class or dependency versions were saved
in the notebook: they are recovered/recorded from the new pinned load, not guessed.
Original package installation was unpinned, so historical pixel equivalence is
not promised. All versions/defaults remain fixed across the new comparison.

The ZIP contains `assets/generative/real-experiments/material/` with four original
PNG model outputs, individual JSON provenance, aggregate provenance, run settings,
and `requirements-freeze.txt`. Each output records prompt, generator state hash,
dimensions, scheduler config/timesteps, pinned model, runtime versions, defaults,
and PNG/pixel hashes. No resampling, cropping, compositing, or website publishing
occurs. A fifth inference repeats timber; export stops if its pixels differ.

## Website integration after output review

Do not register missing images or use original confounded Task-4 images as a
substitute. After reviewing a successful ZIP, register the four genuine outputs
in `examples.mjs` and bind them to a dedicated fixed-prompt material experiment.
The current schematic Prompt Builder uses a different library prompt and seed;
do not label pavilion outputs as if they came from that arbitrary builder state.
All non-material inputs in the real experiment must match the recorded settings.

Use **PREVIOUS — Timber** and **CURRENT — Concrete**, with the question
**“Did only the material appearance change?”** Explain that the material term was
the only intentionally changed input, but multiple visual/design characteristics
may change. These observations do not make prompt terms independent parametric
design variables or establish a mechanistic explanation for every difference.

API reference used to verify implicit dimensions and call parameters:
https://huggingface.co/docs/diffusers/api/pipelines/stable_diffusion/text2img

Validation here is limited to syntax and static checks against the source notebook;
GPU execution and generated-image review must take place in Colab.
