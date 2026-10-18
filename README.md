# AgroRoute AI — Phase 2

An AI-based farm designer and pathfinding laboratory built with Python and Streamlit.

## Features

- **Phase 1 preserved:** paint healthy crops, empty ground, obstacles, infected zones (Low/Medium/High), and rover start; create 5×5–30×30 farms; save/load scenario JSON.
- **Phase 2:** run A*, Uniform Cost Search (UCS), or Greedy Best-First Search to a selected infected zone or manually specified destination.
- View the calculated path, expanded states, and a comparison table showing path cost, steps, expanded nodes, frontier peak, and runtime.
- Unit tests for the farm model and search algorithms.

## Windows PowerShell installation

Extract this ZIP. Open the folder **AgroRoute_AI** (the folder containing `app.py`) in VS Code.

```powershell
cd D:\AgroRoute_AI
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Open http://localhost:8501 if the browser does not open automatically. In the Streamlit navigation sidebar, select **Algorithm Lab**.

If `.venv` already exists from Phase 1, skip `py -m venv .venv` and install the updated requirements.

## Tests

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## Search assumptions

- Coordinates are stored as **zero-based (row, column)** and displayed as **one-based**.
- Movement: up, right, down, left; one unit per move.
- Obstacles are impassable; healthy crops, empty ground and infected zones are traversable in this simplified simulation.
- Manhattan distance is the A* and Greedy heuristic.
- UCS and A* return minimum-step paths on this unit-cost grid. Greedy is not guaranteed optimal.
- Phase 2 plans one destination at a time. Phase 3 will optimize multi-stop missions using a Genetic Algorithm.
- Times are illustrative performance measurements on the machine running the app, not controlled benchmarks.

## GitHub update (existing repo)

Keep your existing `.git` folder when updating your local project. Copy new/updated files from the ZIP **into** `D:\AgroRoute_AI`, rather than replacing the entire folder. Do not copy the `.venv` folder.

```powershell
cd D:\AgroRoute_AI
git status
git add app.py requirements.txt README.md .gitignore agroroute pages tests
git commit -m "feat: add phase 2 AI pathfinding laboratory"
git push origin main
```

Repository: https://github.com/Aadarsh-arsh/AgroRoute-AI

## Phase 3: Multi-zone mission planner

The new **Mission Planner** page plans visits to **all infected zones**, optionally returning to base.

- **Nearest Neighbor:** deterministic fast baseline.
- **Genetic Algorithm:** seeded evolutionary optimization (population, generations, mutation, order crossover).
- **Exact Dynamic Programming:** Held–Karp-style optimal multi-zone solver for **up to 11 infected zones**.
- Each pair of points uses **UCS on the real farm grid**, so obstacles are respected.
- Compare total route length, execution time, and GA/greedy optimality gap against exact results.
- A movement-step slider previews the virtual rover on the computed route; full animation is planned for Phase 4.

### Update your existing Windows checkout

Extract the ZIP, then copy the files **inside** the extracted `AgroRoute_AI` directory into `D:\AgroRoute_AI`, preserving `.git` and `.venv`. Run:

```powershell
cd D:\AgroRoute_AI
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m streamlit run app.py
```

After checking the new **Mission Planner** page, commit and push:

```powershell
git status
git add .
git commit -m "feat: add phase 3 genetic algorithm multi-zone mission planner"
git push origin main
```

**Scope note:** This is Phase 3, not the complete eight-phase system. Disease detection, expert reasoning, scheduling and full rover animation remain separate milestones.


## Integrated prototype (Phases 4–7)

Additional Streamlit pages: Virtual Rover, AI Learning, Expert System, CSP Scheduler.

**Important limitations:** The AI Learning page contains a synthetic-data Decision Tree and K-Means teaching demonstration and image feature extraction, NOT a trained plant disease detector. The rover battery/capacity model is illustrative. The CSP scheduler currently ignores travel times. Rule-based advice is educational only. Do not represent these as field-validated models or agricultural recommendations.

Windows:
```powershell
cd D:\AgroRoute_AI
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Next priorities: labeled tomato dataset training, proper test split and disease evaluation, travel-aware scheduling, scenario persistence, integration and UI testing.

## Final integration: real labeled-image learning (new page)

The **Real Disease Detection** page trains a real Decision Tree using labeled images on your own computer. No dataset is included and **no validated pretrained disease detector is claimed**. Create directories such as:

```text
data/plant_leaves/
  Healthy/leaf1.jpg ...
  Early_blight/leaf1.jpg ...
  Late_blight/leaf1.jpg ...
```

Use **at least five readable images per class** (preferably hundreds). The app extracts RGB/HSV/texture features, creates a stratified held-out split, trains a Decision Tree, reports accuracy, per-class metrics and confusion matrix, and evaluates K-Means clustering via adjusted Rand index. The uploaded photo can be associated with a specific farm cell, and the user must manually assign severity. The updated zone becomes available in Farm Designer and Mission Planner in the same Streamlit session.

**Limitations:** PlantVillage-style images may not generalize to field photos. Avoid data leakage from near-duplicate images and images of the same plant; for research-grade evaluation, use plant-level or source-separated splits and field images. Class probabilities are not calibrated. Never treat these results as pesticide prescriptions. The previous synthetic teaching lab remains separate and clearly labeled.

### Update GitHub after validation

```powershell
cd D:\AgroRoute_AI
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m streamlit run app.py
# After validating the application:
git add .
git commit -m "feat: add real leaf dataset training and zone integration"
git push origin main
```

## MobileNetV2 model comparison (optional)

Phase 8 extension adds a real MobileNetV2 classifier and a Decision Tree trained on the **same** stratified 60% training, 15% validation, 25% test split (seed 42). No dataset or trained model is bundled. This is a small educational experiment, not a validated crop diagnosis system.

Windows PowerShell, in the project directory:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-ml.txt
.\.venv\Scripts\python.exe train_mobilenet.py --data data/plant_leaves --epochs 8
.\.venv\Scripts\python.exe -m streamlit run app.py
```

The training script downloads ImageNet MobileNetV2 weights on first use (internet required). CPU training may take several minutes. If TensorFlow cannot install, use a supported 64-bit Python 3.11 virtual environment. Model results and the `.keras` file are saved under `models/mobile_net_v2/` and excluded from Git. The Streamlit **Model Comparison** page shows the saved evaluation and supports image-to-zone assignment. To compare with your earlier 73% baseline, note that this new experiment uses a different train/test split; the new on-page Decision Tree score is the fair same-split comparison.

**Caution:** Review duplicates and related photos across splits. ImageNet pretraining is not a field-validation guarantee; probabilities are uncalibrated. A healthy prediction does not automatically prove a plant is disease-free.


## Final refinement update

- Farm Plotly visualization has constrained axes to reduce negative tick labels and excess whitespace.
- Virtual Rover offers Play 10 steps with adjustable delay, Run to completion, and downloadable mission JSON with zone metadata. The playback is a short blocking demonstration, not background playback or a true pause/resume animation.
- Model Comparison has a compact percentage-scaled Plotly chart, low-probability warnings, and a downloadable evaluation JSON.
- Disease labels are saved in Streamlit session state; they do not persist across restarts unless separately exported.
- Rover battery values are illustrative and not calibrated against hardware.

### Updating GitHub

From the project directory, after verifying the updated pages:

```powershell
git status
git add .
git commit -m "feat: polish rover dashboard and evaluation reporting"
git push origin main
```


## Unified Smart Agriculture Dashboard (new)

Open **Smart Dashboard** in the Streamlit sidebar. Its guided workflow links farm design, MobileNetV2 prediction, Smart Treatment, Mission Planner and Virtual Rover. Set route and battery parameters and click **Calculate complete mission** to produce a cross-module route and JSON report. Click **Send this route to Virtual Rover** when preflight passes. The rover page independently validates its own settings; match battery settings across both pages if desired.

The dashboard reads the current farm and `zone_diagnoses` from Streamlit session state, so preserve the current browser session as you move between pages. Training data and model files are local and excluded from Git.
