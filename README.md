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
- `assets/data/UW_building_energy.csv` — instructor-approved, de-identified deployment dataset for the Regression episode
- `assets/module_3_deep_learning_workflow.png` — Module 3 workflow visual
- `assets/uw_husky_avatar.png` — animated header avatar asset

The frontend is fully static and does not require a build step.

## Regression Episode 2.6 — Implementation Notes

- `reference_materials/` remains local development/course-reference material and is not included in GitHub or Vercel deployments. The PPTX, DOCX, IPYNB, and original reference CSV remain excluded.
- The instructor-approved, de-identified CSV is deployed separately at `assets/data/UW_building_energy.csv`; the learner workflow loads it automatically. An optional CSV picker remains only as a local debugging fallback.
- Dataset loading, Python execution, feature selection, and reflection storage remain browser-local. There is no backend submission.
- The guided workflow runs real Python in a persistent Pyodide Web Worker. It preloads pandas and NumPy for Steps 1–4 and defers scikit-learn until the modeling steps need it.
- The faster feature-selection activity uses the browser-local JavaScript OLS implementation. It detects redundant or linearly dependent predictors and explains the resulting multicollinearity issue instead of returning arbitrary coefficients.

### Dataset review status

The current teaching module uses Annual Energy (`Energy_Use_kWh`) provisionally. It does not switch the target to derived EUI.

Open review questions include confirmation of the `Area_m` definition, four zero-energy records, the duplicated Odegaard Library name, the Animal Research and Care Facility extreme derived EUI, the derivation of `Occupants`, and train/test split sensitivity. These records and questions are not silently resolved in code so the module can be updated when the final teaching dataset is confirmed.
