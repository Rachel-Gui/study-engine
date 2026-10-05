#!/usr/bin/env python3
"""
denoising_steps.py - record what a diffusion model's image looks like part-way through
generation, for Lesson 2.2 ("From noise to design").

Runs Stable Diffusion v1.5 (the model of the course notebook, same revision) on the
library prompt of the notebook's seed experiment, and saves the decoded latent after
selected denoising steps, plus a provenance file with every setting and version.

    python tools/denoising_steps.py                     # CPU is fine; about 10 minutes
    python tools/denoising_steps.py --out assets/generative/denoising

Needs: torch, diffusers, transformers, accelerate, safetensors, Pillow.
The CPU and a GPU draw different random numbers for the same seed, so this run's final
image is not the notebook's seed-100 image. That is recorded, not hidden.
"""
import argparse, hashlib, json, os, platform, time
import torch
from diffusers import StableDiffusionPipeline
import diffusers, transformers

MODEL = "stable-diffusion-v1-5/stable-diffusion-v1-5"
REVISION = "451f4fe16113bff5a5d2269ed5ad43b0592e9a14"      # the revision the course notebook loaded
PROMPT = ("A community library with exposed timber structure, large glass facade, located on a sloped "
          "urban site in Seattle, soft overcast morning light, contemporary Scandinavian style, "
          "architectural photography, 8K")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..", "assets", "generative", "denoising"))
    ap.add_argument("--seed", type=int, default=100)
    ap.add_argument("--steps", type=int, default=30)
    ap.add_argument("--guidance", type=float, default=7.5)
    ap.add_argument("--keep", default="1,2,3,5,8,12,18,24,30", help="steps whose state is saved")
    a = ap.parse_args()
    out = os.path.normpath(a.out); os.makedirs(out, exist_ok=True)
    keep = sorted({int(k) for k in a.keep.split(",")})
    torch.set_num_threads(max(1, os.cpu_count() or 1))

    t0 = time.time()
    pipe = StableDiffusionPipeline.from_pretrained(MODEL, revision=REVISION, variant="fp16",
                                                   torch_dtype=torch.float32, safety_checker=None,
                                                   requires_safety_checker=False)
    pipe.set_progress_bar_config(disable=False)
    load_s = time.time() - t0

    saved = {}

    def decode(latents):
        with torch.no_grad():
            img = pipe.vae.decode(latents / pipe.vae.config.scaling_factor, return_dict=False)[0]
        img = (img / 2 + 0.5).clamp(0, 1)[0].permute(1, 2, 0).float().numpy()
        from PIL import Image
        return Image.fromarray((img * 255).round().astype("uint8"))

    def on_step_end(p, i, t, kw):
        step = i + 1
        if step in keep:
            saved[step] = (int(t), kw["latents"].detach().clone())
        return kw

    g = torch.Generator("cpu").manual_seed(a.seed)
    # the starting noise itself, decoded, is "step 0"
    shape = (1, pipe.unet.config.in_channels, 64, 64)
    noise = torch.randn(shape, generator=torch.Generator("cpu").manual_seed(a.seed), dtype=torch.float32)
    t1 = time.time()
    result = pipe(PROMPT, num_inference_steps=a.steps, guidance_scale=a.guidance, generator=g,
                  callback_on_step_end=on_step_end, callback_on_step_end_tensor_inputs=["latents"])
    gen_s = time.time() - t1

    files = []
    im = decode(noise * pipe.scheduler.init_noise_sigma)
    path = os.path.join(out, "step-00.png"); im.save(path); files.append((0, None, path))
    for step, (tstep, lat) in sorted(saved.items()):
        im = decode(lat)
        path = os.path.join(out, f"step-{step:02d}.png"); im.save(path); files.append((step, tstep, path))
    final = os.path.join(out, "final.png"); result.images[0].save(final)

    def sha(p):
        return hashlib.sha256(open(p, "rb").read()).hexdigest()
    prov = {
        "what": "Decoded latents part-way through one Stable Diffusion generation (Lesson 2.2).",
        "model": MODEL, "revision": REVISION, "weights_variant": "fp16 weights, run in float32",
        "pipeline": "StableDiffusionPipeline", "scheduler": pipe.scheduler.__class__.__name__,
        "scheduler_config": {k: v for k, v in dict(pipe.scheduler.config).items() if not k.startswith("_")},
        "prompt": PROMPT, "negative_prompt": None, "seed": a.seed, "generator_device": "cpu",
        "steps": a.steps, "guidance_scale": a.guidance, "width": 512, "height": 512,
        "device": "cpu", "torch": torch.__version__, "diffusers": diffusers.__version__,
        "transformers": transformers.__version__, "python": platform.python_version(),
        "load_seconds": round(load_s, 1), "generation_seconds": round(gen_s, 1),
        "note": ("Each image decodes the latent the model holds after that many of the 30 denoising steps; "
                 "step 0 is the starting noise. CPU and GPU generators draw different numbers for the same "
                 "seed, so the final image is not the course notebook's seed-100 image."),
        "files": [{"step": s, "timestep": ts, "file": os.path.basename(p), "sha256": sha(p)} for s, ts, p in files]
                 + [{"step": "final (pipeline output)", "file": "final.png", "sha256": sha(final)}],
    }
    json.dump(prov, open(os.path.join(out, "provenance.json"), "w"), indent=2)
    print(json.dumps({k: prov[k] for k in ("load_seconds", "generation_seconds", "scheduler")}, indent=1))


if __name__ == "__main__":
    main()
