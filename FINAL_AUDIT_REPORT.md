# AgroRoute AI — Final Functional Audit

## Scope
Inspected the Python source for the Farm Designer and all 11 numbered Streamlit pages, the shared farm/mission/pathfinding/rover/disease modules, and cross-page session-state transfers. Added 12 regression checks.

## Verified
- 76 of 76 automated tests pass (`python -m unittest discover -s tests -q`).
- Python source compiles for all 12 application pages and support modules.
- All 12 pages use the shared UI theme and set page configuration.
- Imported farm scenarios are isolated from the source JSON data.
- Farm replacement and grid repainting invalidate stale disease assignments.
- Rover refuses invalid battery settings, terminal-state resumes, and inspections beyond capacity.
- Preflight rejects nonfinite numeric settings and out-of-bounds route legs.
- One-click mission execution rejects post-preflight changes to inspection capacity or battery use.
- Dashboard and Autonomous Workflow transfer rover safety settings consistently.
- Dashboard's MobileNetV2 status reflects presence of saved model files, not an unconditional claim.

## Fixed
1. Farm.from_dict formerly reused input nested lists/dicts by reference.
2. RoverState.tick formerly advanced onto a new infected cell before checking capacity.
3. RoverState.tick formerly could be called after a terminal stop.
4. Preflight formerly did not check every leg's source bounds and finite settings.
5. Autonomous execution formerly accepted altered settings after preflight.
6. Farm replacement/repainting formerly retained obsolete diagnoses.
7. Dashboard mission transfer formerly dropped safety settings.
8. Virtual Rover formerly allowed changing mission safety settings while reusing an approved route.
9. Farm Designer's old sidebar-specific dark CSS conflicted with the shared light theme.
10. Smart Dashboard formerly claimed MobileNetV2 was active even without model files.

## Remaining verification on the user's Windows machine
- Streamlit is not installed in the audit container, so actual browser rendering, widget interactions, and automated end-to-end browser tests were not executed here.
- TensorFlow and the user's trained model/dataset are not bundled; test real image classification locally.
- A 30×30 farm may still have an impractically dense click-button grid at narrow screen widths.
- CSP scheduling is simplified and does not account for travel time.
- Prediction probabilities are not calibrated; this remains an educational simulation, not an autonomous field-spraying system.

## Installation
Preserve `.git`, `.venv`, `data/plant_leaves`, `models/mobile_net_v2`, and `.streamlit/secrets.toml` when replacing files.

```powershell
cd D:\AgroRoute_AI
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m streamlit run app.py
```
