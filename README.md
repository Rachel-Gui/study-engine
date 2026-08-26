# Study Engine

An interactive course frontend for Modules 2–3: Machine Learning and Deep Learning for Architecture.

## Run locally

From the repository directory:

```bash
python3 -m http.server 8000
```

Then open `http://127.0.0.1:8000/`.

## Project structure

- `index.html` — generated course frontend
- `course-content.md` — editable English course-content source
- `assets/module_code_lab.css` — course layout and visual styling
- `assets/module_code_lab.js` — navigation, topic pagination, avatar animation, and runnable Code Lab
- `assets/module_3_deep_learning_workflow.png` — Module 3 workflow visual
- `assets/uw_husky_avatar.png` — animated header avatar asset

The frontend is fully static and does not require a build step.
