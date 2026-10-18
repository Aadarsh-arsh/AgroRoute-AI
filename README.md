# AgroRoute AI — Phase 1: Farm Designer

A working Streamlit farm-grid editor for a future intelligent crop-treatment route optimizer. This phase **does not yet implement route planning, disease classification, or animated rover movement**.

## Requirements
- Windows 10/11
- Python 3.11 or 3.12 (recommended)
- Internet connection for initial package installation

## Install and run (PowerShell)
```powershell
cd "C:\path\to\AgroRoute_AI"
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m streamlit run app.py
```
If `py -3.11` is not available, install Python 3.11 or use `py -3.12` if installed. If PowerShell blocks activation, skip activation and run:
```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```
The browser normally opens at `http://localhost:8501`. Stop with Ctrl+C.

## Features
- Grid dimensions 5×5 to 30×30
- Click-to-paint healthy crops, empty paths, obstacles, and infected zones
- Set infection severity (Low, Medium, High)
- Set rover start position with placement validation
- Demo field and reset to blank field
- Download/import JSON scenario (schema version 1)
- Live cell counts and infected-zone table

## How to use
1. Choose a painting tool in the left sidebar.
2. For infected zones, choose a severity.
3. Click any cell in the farm grid to paint it.
4. Select Rover start to move the rover to a traversable cell.
5. Download the scenario as JSON to preserve your work.
6. To reload, upload the JSON and click Import uploaded farm.

## Run tests
```powershell
python -m unittest discover -s tests -v
```

## Next phases
Phase 2: A*, UCS, Greedy and Genetic Algorithm routing. Phase 3: virtual rover animation. Later: disease classification, CSP and expert system.
