"""figures_gen.py - diagrams for the Generative AI and AI-assisted coding modules.
Same conventions as the other figure modules."""
from figures_py import HEAD, _t, _m, _box, _arrow, _foot, ACC, GOLD


# ------------------------------------------------------- generative approaches
def gen_families():
    s = HEAD.format(w=880, h=360)
    # GAN
    x = 60
    s += _t(x + 90, 50, "GAN", 13.5, weight=600)
    s += _box(x, 70, 80, 36); s += _t(x + 40, 92, "generator", 10.5)
    s += _box(x + 100, 70, 80, 36); s += _t(x + 140, 92, "discriminator", 9.5)
    s += _arrow(x + 82, 88, x + 98, 88)
    s += f'<path d="M{x + 140},108 L{x + 140},130 L{x + 40},130 L{x + 40},108" marker-end="url(#ap)" stroke="{ACC}" stroke-dasharray="4 3"/>'
    s += _t(x + 90, 146, "real or fake?", 9.5, style=f'fill="{ACC}"')
    s += _t(x + 90, 172, "two networks compete;", 10, style='opacity=".65"')
    s += _t(x + 90, 186, "the generator learns to fool", 10, style='opacity=".65"')
    s += _t(x + 90, 200, "the discriminator", 10, style='opacity=".65"')
    # VAE
    x = 270
    s += _t(x + 90, 50, "VAE", 13.5, weight=600)
    s += _box(x, 74, 60, 30); s += _t(x + 30, 93, "encoder", 9.5)
    s += _box(x + 70, 70, 40, 38, fill=GOLD, stroke=ACC, lw=1.2); s += _t(x + 90, 93, "z", 13, weight=600)
    s += _box(x + 120, 74, 60, 30); s += _t(x + 150, 93, "decoder", 9.5)
    s += _arrow(x + 62, 89, x + 68, 89); s += _arrow(x + 112, 89, x + 118, 89)
    s += _t(x + 90, 128, "a compressed latent space", 9.5, style=f'fill="{ACC}"')
    s += _t(x + 90, 172, "encode examples to z,", 10, style='opacity=".65"')
    s += _t(x + 90, 186, "decode samples and", 10, style='opacity=".65"')
    s += _t(x + 90, 200, "smooth variations of z", 10, style='opacity=".65"')
    # Diffusion
    x = 480
    s += _t(x + 90, 50, "Diffusion", 13.5, weight=600)
    for i in range(5):
        op = 0.15 + i * 0.2
        s += f'<rect x="{x + i * 36}" y="72" width="30" height="30" rx="2" fill="rgba(75,46,131,{op:.2f})" stroke="#111" stroke-width="1"/>'
        if i < 4: s += _arrow(x + i * 36 + 31, 87, x + i * 36 + 35, 87)
    s += _t(x + 15, 118, "noise", 9.5); s += _t(x + 160, 118, "image", 9.5)
    s += _t(x + 90, 134, "conditioned on the prompt", 9.5, style=f'fill="{ACC}"')
    s += _t(x + 90, 172, "learn to remove noise;", 10, style='opacity=".65"')
    s += _t(x + 90, 186, "generate by denoising", 10, style='opacity=".65"')
    s += _t(x + 90, 200, "step by step", 10, style='opacity=".65"')
    # Autoregressive / transformer
    x = 680
    s += _t(x + 88, 50, "Autoregressive", 13.5, weight=600)
    toks = ["a", "timber", "roof", "in", "?"]
    for i, tk in enumerate(toks):
        on = i == 4
        s += _box(x + i * 36, 74, 32, 26, fill=(GOLD if on else "#fff"), stroke=(ACC if on else "#111"), lw=1.1)
        s += _m(x + i * 36 + 16, 91, tk, 8.5 if len(tk) > 3 else 10)
    s += _arrow(x + 40, 112, x + 150, 112, purple=True)
    s += _t(x + 88, 128, "predict the next token", 9.5, style=f'fill="{ACC}"')
    s += _t(x + 88, 172, "text, code, and tokenised", 10, style='opacity=".65"')
    s += _t(x + 88, 186, "geometry, one piece at a", 10, style='opacity=".65"')
    s += _t(x + 88, 200, "time; LLMs work this way", 10, style='opacity=".65"')
    # multimodal strip
    s += _box(60, 232, 760, 56, dash="5 4", stroke="#888", lw=1.2)
    s += _t(80, 254, "Multimodal systems", 12, anchor="start", weight=600)
    s += _t(80, 272, "not a fifth approach: systems that combine encoders and generators so text, images and other modalities are inputs and outputs of one model", 10, anchor="start", style='opacity=".7"')
    s = _foot(s, 314, "Four ways to learn a distribution and sample from it. The approach sets what is easy to control and what is not.")
    return s + "</svg>"


# ---------------------------------------------------------- control hierarchy
def control_hierarchy():
    s = HEAD.format(w=880, h=350)
    rungs = [("Prompt control", "words: intent, vocabulary, hints", "cheap; steers a distribution, guarantees nothing", "2.3"),
             ("Settings & stochastic control", "seed, guidance, steps, negative prompt, resolution", "repeatable runs; still no geometry", "2.4"),
             ("Reference conditioning", "an image, a sketch, a style or a depth map as input", "the output follows a given picture, not just a phrase", "2.4"),
             ("Structural control", "edges, masks, layouts, poses; control networks", "where things go is imposed, not suggested", "2.4"),
             ("Explicit design constraints", "dimensions, adjacencies, code, physics", "the only level that can be checked", "2.6")]
    for i, (name, what, gives, ep) in enumerate(rungs):
        y = 44 + i * 50
        x = 60 + i * 44
        w = 460 - i * 44
        s += _box(x, y, w, 40, fill=("#fff" if i < 4 else GOLD), stroke=(ACC if i == 4 else "#111"), lw=(1.8 if i == 4 else 1.3))
        s += _t(x + 14, y + 17, name, 12, anchor="start", weight=600)
        s += _t(x + 14, y + 32, what, 9.5, anchor="start", style='opacity=".65"')
        s += _t(538, y + 22, gives, 10.5, anchor="start", style=f'fill="{ACC if i == 4 else "#454545"}"')
        s += _t(850, y + 22, ep, 10, anchor="end", style='opacity=".5"')
        if i < 4:
            s += _arrow(x + 200, y + 42, x + 244, y + 48)
    s += _t(60, 306, "more control, more work, more that can be verified  →", 10.5, anchor="start", style=f'fill="{ACC}" font-weight="600"')
    s = _foot(s, 318, "Each rung imposes more and suggests less. A generated image only becomes a checkable design at the last one.")
    return s + "</svg>"


# ------------------------------------------------------ structured generation
def llm_structured():
    s = HEAD.format(w=880, h=340)
    s += _box(60, 70, 170, 120, fill="#fbfbfa")
    s += _t(145, 60, "prompt + context", 12, weight=600)
    for i, l in enumerate(["role & task", "the brief, the site", "examples of the format", "constraints to respect"]):
        s += _t(76, 96 + i * 22, "• " + l, 10.5, anchor="start", style='opacity=".75"')
    s += _arrow(234, 130, 286, 130)
    s += _box(290, 96, 120, 68, lw=2)
    s += _t(350, 126, "LLM", 16, weight=600)
    s += _t(350, 148, "next-token generation", 9.5, style='opacity=".6"')
    outs = [("text", "a brief, a rationale, a summary", 50), ("JSON", '{"wwr": 0.35, "orient": 180}', 104), ("code", "a Grasshopper or Python script", 158), ("design representation", "adjacency graph, parameter set", 212)]
    for i, (k, ex, y) in enumerate(outs):
        s += f'<path d="M412,130 C 440,130 440,{y + 14} 466,{y + 14}" marker-end="url(#ao)" opacity=".7"/>'
        s += _box(470, y, 170, 30, fill=(GOLD if i in (1, 3) else "#fff"), stroke=(ACC if i in (1, 3) else "#111"), lw=1.2)
        s += _t(484, y + 19, k, 11, anchor="start", weight=600)
        s += _m(650, y + 19, ex, 9.5, anchor="start", style='opacity=".7"')
    s += _box(470, 258, 170, 30, dash="4 3", stroke=ACC, lw=1.3)
    s += _t(555, 277, "validator / schema check", 10.5, weight=600, style=f'fill="{ACC}"')
    s += f'<path d="M555,244 L555,254" marker-end="url(#ap)" stroke="{ACC}"/>'
    s += _t(650, 277, "→ a tool, a model, an agent (Module 4)", 10, anchor="start", style=f'fill="{ACC}"')
    s = _foot(s, 304, "Structured output is what makes a model's answer usable by code. The check after it is what makes it trustworthy.")
    return s + "</svg>"


# --------------------------------------------------------- image to model
def image_to_model():
    s = HEAD.format(w=880, h=300)
    steps = [("generated image", "a visual hypothesis", "pixels"), ("extract", "walls, glazing, levels", "labels + scale"),
             ("structured info", "dimensions, unknowns", "fields"), ("geometry model", "parametric / BIM, checked", "surfaces, levels"),
             ("simulate", "weather, schedules", "numbers"), ("claim", "with range + uncertainty", "a decision")]
    for i, (name, sub, kind) in enumerate(steps):
        x = 60 + i * 130
        last = i == 5
        s += _box(x, 84, 122, 70, fill=(GOLD if last else "#fff"), stroke=(ACC if last else "#111"), lw=(1.8 if last else 1.3))
        s += _t(x + 61, 108, name, 11, weight=600)
        s += _t(x + 61, 126, sub, 8.5, style='opacity=".65"')
        s += _t(x + 61, 144, kind, 9, style=f'fill="{ACC}"')
        if i < 5: s += _arrow(x + 124, 119, x + 128, 119)
    s += f'<path d="M121,156 L121,196 L771,196 L771,156" stroke="{ACC}" stroke-dasharray="5 3" fill="none"/>'
    s += _t(438, 214, "no performance claim can jump this gap: the image is the start, the checked model is what gets simulated", 10.5, style=f'fill="{ACC}"')
    s = _foot(s, 250, "Translate before evaluating. Every arrow is a place where information is added by a person, and can be wrong.")
    return s + "</svg>"


# --------------------------------------------------------- vibe coding loop
def vibe_loop():
    s = HEAD.format(w=880, h=330)
    stages = [("Describe", "what, for whom, inputs,|outputs, one example", 70), ("Generate", "the assistant|writes the code", 230),
              ("Run", "execute it on|a real case", 390), ("Read", "does it do what you said?|line by line", 550), ("Refine", "narrow the brief, add|a test, ask again", 710)]
    for i, (name, sub, x) in enumerate(stages):
        s += _box(x, 66, 130, 72, fill=(GOLD if i in (0, 3) else "#fff"), stroke=(ACC if i in (0, 3) else "#111"), lw=(1.8 if i in (0, 3) else 1.3))
        s += _t(x + 65, 90, name, 13, weight=600)
        a, b = sub.split("|")
        s += _t(x + 65, 108, a, 8.5, style='opacity=".65"')
        s += _t(x + 65, 121, b, 8.5, style='opacity=".65"')
        if i < 4: s += _arrow(x + 132, 102, x + 156, 102)
    s += f'<path d="M775,140 L775,172 L135,172 L135,140" marker-end="url(#ap)" stroke="{ACC}" stroke-dasharray="5 3"/>'
    s += _t(455, 188, "the loop runs three to ten times for a small tool; the human steps are the gold ones", 10.5, style=f'fill="{ACC}"')
    s += _t(60, 230, "What the assistant is good at: boilerplate, library syntax, a first draft, explaining an error.", 11, anchor="start", style='opacity=".75"')
    s += _t(60, 250, "What it is bad at: knowing what you meant, noticing a wrong unit, and telling you it is unsure.", 11, anchor="start", style='opacity=".75"')
    s = _foot(s, 282, "Vibe coding is fast because the machine writes. It is safe only because the human reads.")
    return s + "</svg>"


ALL = {"gen_families": gen_families, "control_hierarchy": control_hierarchy,
       "llm_structured": llm_structured, "image_to_model": image_to_model, "vibe_loop": vibe_loop}
