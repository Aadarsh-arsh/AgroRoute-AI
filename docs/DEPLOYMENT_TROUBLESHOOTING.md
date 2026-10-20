# Deployment and troubleshooting

## Setup
1. Install Python 3.10 or newer.
2. From the repository root, create a virtual environment with `python -m venv .venv`.
3. Activate it using `.venv\Scripts\Activate.ps1` in PowerShell.
4. Install dependencies with `python -m pip install -r requirements.txt`.
5. Launch the app with `streamlit run app.py` (use the repository's actual Streamlit entry point if different).

## Troubleshooting
- If `python` is not found, reinstall Python and enable the PATH option.
- If Streamlit is missing, install the requirements in the active environment.
- If a scenario fails to load, validate its JSON schema and coordinate dimensions.
- If a route cannot reach a target, check for obstacles or disconnected cells.

## Continuous integration
Run the unit tests with `python -m unittest discover -s tests -v`.
