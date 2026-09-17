"""Paste this entire file into ONE Colab code cell on a GPU runtime.

First run the original notebook's installation cell and restart the session.
This cell loads its own pinned pipeline; it does not run the other exercises.
No website files are changed. Download the resulting ZIP for review.
"""
import hashlib
import importlib.metadata
import inspect
import json
import platform
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import torch
from diffusers import StableDiffusionPipeline
from IPython.display import HTML, display

if not torch.cuda.is_available():
    raise RuntimeError("Select a Colab GPU runtime. CPU/MPS substitution is not used.")

MODEL = "runwayml/stable-diffusion-v1-5"
# Recovered from the saved cell-8 text_encoder cache path. This is evidence for
# that component, NOT proof of the original complete pipeline's revision.
# Pin the entire NEW experiment to this revision; fail if it cannot be loaded.
REVISION = "451f4fe16113bff5a5d2269ed5ad43b0592e9a14"
BASE = "A small pavilion in a public garden, open structure, elegant proportions, surrounded by trees, soft afternoon light, architectural photography"
MATERIALS = ("timber", "concrete", "steel and glass", "rammed earth")
SEED = 200  # Task 4's original timber seed, now reinitialized for EVERY image.

material_pipe = StableDiffusionPipeline.from_pretrained(
    MODEL, revision=REVISION, torch_dtype=torch.float16, safety_checker=None,
).to("cuda")
material_pipe.enable_attention_slicing()  # Same setup as notebook cell 8.

# Recover implicit Task-4 dimensions from the model, not the Matplotlib image.
sample_size = material_pipe.unet.config.sample_size
if not isinstance(sample_size, int):
    raise RuntimeError("Unexpected UNet sample_size; inspect before generating.")
side = sample_size * material_pipe.vae_scale_factor
scheduler_type = type(material_pipe.scheduler)
scheduler_config = dict(material_pipe.scheduler.config)

def plain(value):
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, dict):
        return {str(k): plain(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [plain(v) for v in value]
    if hasattr(value, "tolist"):
        return value.tolist()
    return str(value)

def digest(data):
    return hashlib.sha256(data).hexdigest()

def write_json(path, data):
    path.write_text(json.dumps(plain(data), indent=2, ensure_ascii=False) + "\n")

def component_config(component):
    config = component.config
    return plain(config.to_dict() if hasattr(config, "to_dict") else dict(config))

# Record ALL installed pipeline-call defaults, including implicit negative
# prompt, eta, clip_skip, guidance_rescale and optional conditioning/callbacks.
signature = inspect.signature(material_pipe.__call__)
defaults = {
    name: plain(parameter.default)
    for name, parameter in signature.parameters.items()
    if parameter.default is not inspect.Parameter.empty
}
fixed = dict(height=side, width=side, num_inference_steps=30, guidance_scale=7.5)
run_root = Path(tempfile.mkdtemp(prefix="controlled-task4-", dir="/content"))
out = run_root / "assets/generative/real-experiments/material"
out.mkdir(parents=True)
versions = {}
for package in ("torch", "diffusers", "transformers", "accelerate",
                "huggingface-hub", "safetensors", "numpy", "Pillow"):
    try:
        versions[package] = importlib.metadata.version(package)
    except importlib.metadata.PackageNotFoundError:
        versions[package] = "not installed"

common = {
    "source": "New controlled rerun of completed course notebook Task 4",
    "source_notebook": "02_AI_Studio_Generative_AI-2.ipynb",
    "source_notebook_sha256": "6f935c8115fb3ec4084c5ed1c442d7957e7a3e3287fb5fe0247010c802b8af7b",
    "source_cells_zero_based": {"setup": 8, "task": 48},
    "created_at_utc": datetime.now(timezone.utc).isoformat(),
    "model": MODEL, "model_revision": REVISION,
    "revision_evidence": "Original saved text_encoder cache path only; full new pipeline explicitly pinned to this revision.",
    "original_runtime_versions": "Not recorded; this is not a claim of pixel-identical historical reproduction.",
    "pipeline_class": type(material_pipe).__name__,
    "pipeline_config": plain(dict(material_pipe.config)),
    "component_configs": {
        name: component_config(getattr(material_pipe, name))
        for name in ("unet", "vae", "text_encoder")
    },
    "tokenizer_settings": plain(material_pipe.tokenizer.init_kwargs),
    "scheduler_class": scheduler_type.__module__ + "." + scheduler_type.__name__,
    "scheduler_config": plain(scheduler_config),
    "dtype": str(material_pipe.unet.dtype), "device": "cuda",
    "attention_slicing": "auto (enable_attention_slicing default, as in original setup)",
    "safety_checker": None,
    "seed": SEED, "generator_device": "cuda",
    "prompt_template": BASE + ", primary material is {material}",
    "fixed_explicit_call_arguments": fixed,
    "installed_pipeline_call_defaults": defaults,
    "dimension_derivation": {"unet_sample_size": sample_size,
                             "vae_scale_factor": material_pipe.vae_scale_factor},
    "versions": versions, "python": sys.version, "platform": platform.platform(),
    "gpu": torch.cuda.get_device_name(0), "cuda_version": torch.version.cuda,
    "cudnn_version": torch.backends.cudnn.version(),
    "deterministic_algorithms": torch.are_deterministic_algorithms_enabled(),
    "cudnn_benchmark": torch.backends.cudnn.benchmark,
    "cudnn_deterministic": torch.backends.cudnn.deterministic,
    "cuda_matmul_allow_tf32": torch.backends.cuda.matmul.allow_tf32,
    "teaching": {
        "previous_label": "PREVIOUS — Timber", "current_label": "CURRENT — Concrete",
        "question": "Did only the material appearance change?",
        "explanation": "The material term was the only intentionally changed input. The model may change multiple visual/design characteristics in response. These observed output differences occurred under controlled generation; prompt terms are not independent parametric design variables, and this comparison does not establish a mechanistic attribution for every visual difference.",
    },
}
write_json(out / "run-settings.json", common)
(out / "requirements-freeze.txt").write_text(
    subprocess.check_output([sys.executable, "-m", "pip", "freeze"], text=True)
)

def generate(material):
    # Fresh scheduler state AND fresh generator, with identical config/seed.
    material_pipe.scheduler = scheduler_type.from_config(scheduler_config)
    generator = torch.Generator("cuda").manual_seed(SEED)
    rng_hash = digest(generator.get_state().cpu().numpy().tobytes())
    prompt = f"{BASE}, primary material is {material}"
    with torch.inference_mode():
        result = material_pipe(prompt, generator=generator, **fixed)
    image = result.images[0]
    if image.size != (side, side):
        raise RuntimeError("Output dimensions do not match the fixed configuration.")
    return image, prompt, rng_hash, plain(material_pipe.scheduler.timesteps)

samples, first_pixels, initial_rng = [], None, None
for material in MATERIALS:
    image, prompt, rng_hash, timesteps = generate(material)
    if initial_rng is None:
        initial_rng, first_pixels = rng_hash, image.tobytes()
    if rng_hash != initial_rng:
        raise RuntimeError("Generator state changed between materials; stop.")
    filename = "material-" + material.replace(" ", "-") + ".png"
    image.save(out / filename, format="PNG")  # Raw PIL model output; no crop/resize.
    record = {**common, "material": material, "prompt": prompt,
              "file": filename, "width": image.width, "height": image.height,
              "image_mode": image.mode, "initial_generator_state_sha256": rng_hash,
              "scheduler_timesteps": timesteps,
              "png_sha256": digest((out / filename).read_bytes()),
              "pixels_sha256": digest(image.tobytes())}
    write_json(out / filename.replace(".png", ".json"), record)
    samples.append(record)
    display(HTML("<b>" + material.title() + " — raw model output</b>"))
    display(image)

# Verify repeatability within this runtime before exporting the experiment.
repeated, _, _, _ = generate("timber")
if repeated.tobytes() != first_pixels:
    raise RuntimeError("Timber repeatability check failed. Do not publish this run; inspect runtime determinism.")
write_json(out / "provenance.json", {
    "status": "complete", "same_runtime_timber_repeatability": "pixel-identical",
    "samples": samples,
})
archive = shutil.make_archive(str(run_root), "zip", root_dir=run_root)
print("PREVIOUS — Timber vs. CURRENT — Concrete")
print(common["teaching"]["question"])
print(common["teaching"]["explanation"])
print("Saved four raw PNGs and provenance:", archive)
from google.colab import files
files.download(archive)
