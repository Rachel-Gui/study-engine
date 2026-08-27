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
- `assets/module_code_lab.js` — navigation, topic pagination, ANN Code Lab, interactive regression plot, Pyodide workflow, and browser-based UW regression demo
- `assets/module_3_deep_learning_workflow.png` — Module 3 workflow visual
- `assets/uw_husky_avatar.png` — animated header avatar asset

The frontend is fully static and does not require a build step.

## Regression Episode 2.6 — Implementation Notes

- `reference_materials/` contains local development and course-reference material only. It is not tracked by Git and is not included in GitHub or Vercel deployments.
- During local development, the Regression demo may automatically load `reference_materials/UW_building_energy.csv` when that private file exists.
- In production, when no publishable dataset is bundled, learners connect their own local copy through the CSV file picker. The file and all resulting calculations remain inside the learner's browser.
- The guided workflow runs real Python in a persistent Pyodide Web Worker. It preloads pandas and NumPy for Steps 1–4 and defers scikit-learn until the modeling steps need it.
- The faster feature-selection activity uses the browser-local JavaScript OLS implementation. It detects redundant or linearly dependent predictors and explains the resulting multicollinearity issue instead of returning arbitrary coefficients.

No private CSV is copied into or implied to be part of the deployed website.
