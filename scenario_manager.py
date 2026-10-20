"""Small Streamlit page for managing saved farm scenarios."""
import json
from pathlib import Path
import streamlit as st
from agroroute.farm import Farm
from agroroute.scenario_io import load_scenario, save_scenario

st.title("Farm Scenario Manager")
directory = Path("scenarios")
directory.mkdir(exist_ok=True)
uploaded = st.file_uploader("Import scenario JSON", type=["json"])
if uploaded is not None:
    try:
        data = json.loads(uploaded.getvalue().decode("utf-8"))
        farm = Farm.from_dict(data)
        st.success(f"Loaded {farm.name or 'farm scenario'} ({farm.rows} × {farm.cols})")
        if st.button("Save imported scenario"):
            target = directory / f"{uploaded.name}"
            save_scenario(farm, target)
            st.success(f"Saved to {target}")
    except (ValueError, TypeError, KeyError, UnicodeDecodeError) as exc:
        st.error(f"Could not load scenario: {exc}")
saved = sorted(directory.glob("*.json"))
st.write("Saved scenarios:", [p.name for p in saved])
for path in saved:
    if st.button(f"Preview {path.name}", key=str(path)):
        try:
            farm = load_scenario(path)
            st.json(farm.to_dict())
        except (ValueError, OSError) as exc:
            st.error(str(exc))
