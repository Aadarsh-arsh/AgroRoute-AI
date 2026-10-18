# Autonomous Mission Workflow — User Guide

## New page
Open **Autonomous Workflow** from the sidebar or from the Smart Dashboard shortcut.

1. Upload a new tomato leaf photo, or choose existing infected zones.
2. If uploading, choose its associated field zone and manually observed severity.
3. Configure the route planner, simulated battery use, reserve, capacity and rain restriction.
4. Click **Analyze leaf + prepare complete autonomous mission**.
5. Review the predicted disease and probability, inspection priorities, obstacle-aware route and preflight.
6. Choose **Run entire mission automatically** for an instant deterministic simulation, or **Open animated rover with this mission** for Play/Pause controls.
7. Download the JSON report.

## Safety and persistence
- The one-click plan does **not** modify the active farm until you choose to transfer the mission to Virtual Rover.
- Healthy predictions do not create infected zones.
- Low-confidence diagnoses are flagged for human review. The rover performs simulated inspection, not automatic pesticide spraying.
- The full simulation is a rapid computation rather than a real-time animation. For animation, use Virtual Rover.
- The trained model files are **not** included. Preserve `models/mobile_net_v2` and `data/plant_leaves`.
- Changing the farm, image, or mission settings invalidates the previously prepared plan.
- Planning checks route obstacles, visit coverage, inspection capacity, return to base and battery reserve.
- No cloud upload or remote image storage is performed by this module.

## Windows run
```powershell
cd D:\\AgroRoute_AI
.\\.venv\\Scripts\\python.exe -m pip install -r requirements.txt
.\\.venv\\Scripts\\python.exe -m unittest discover -s tests -v
.\\.venv\\Scripts\\python.exe -m streamlit run app.py
```
For MobileNetV2 inference, TensorFlow must already be installed in the virtual environment (`requirements-ml.txt`).
