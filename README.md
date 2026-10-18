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
