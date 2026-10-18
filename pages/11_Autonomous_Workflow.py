"""Single-screen guided AI inspection mission: predict, review, plan, simulate, export."""
import json
from pathlib import Path
import streamlit as st
import plotly.graph_objects as go
from agroroute.farm import demo_farm
from agroroute.autonomous import build_workflow, simulate_to_completion, workflow_report, image_fingerprint
from agroroute.visualization import farm_figure
from agroroute.ui import apply_theme, page_hero, info_strip, footer

st.set_page_config(page_title="AgroRoute | Autonomous Workflow", page_icon="🚜", layout="wide")
apply_theme()
page_hero("Autonomous Mission Control",
          "Upload a leaf, detect disease, review zone priorities, optimize a safe round-trip route, and run a virtual rover from one page.",
          icon="🚜", eyebrow="END-TO-END AI WORKFLOW")
info_strip("One-click planning uses your saved MobileNetV2 model. Low-probability diagnoses are flagged for human review. All battery and treatment values are simulated.")

farm = st.session_state.setdefault("farm", demo_farm())
model_dir = Path("models/mobile_net_v2")
model_ready = (model_dir/"model.keras").is_file() and (model_dir/"metadata.json").is_file()
with st.sidebar:
    st.header("⚙️ Autonomous mission")
    planner = st.selectbox("Route optimizer", ["Genetic Algorithm", "Nearest Neighbor", "Exact Dynamic Programming"])
    per_step = st.slider("Battery use per step (%)", 0.1, 2.0, 0.4, 0.1)
    reserve = st.slider("Battery reserve (%)", 0, 50, 15, 5)
    capacity = st.number_input("Inspection capacity", 1, 30, 20)
    threshold = st.slider("Manual review below probability", 0.40, 0.95, 0.65, 0.05)
    rain = st.checkbox("Rain expected", value=False)
    st.caption("All controls affect the next generated mission.")

st.subheader("01  ·  Disease input & field assignment")
a, b = st.columns([1, 1], gap="large")
with a:
    source = st.radio("Inspection source", ["Upload new leaf image", "Use existing infected zones"], horizontal=True)
    uploaded = st.file_uploader("Tomato leaf image", type=["jpg", "jpeg", "png", "webp"]) if source.startswith("Upload") else None
    if uploaded is not None:
        st.image(uploaded, width=220)
    if source.startswith("Upload") and not model_ready:
        st.warning("MobileNetV2 model is missing. Keep your models/mobile_net_v2 folder or train the model first.")
with b:
    available = [(r,c) for r in range(farm.rows) for c in range(farm.cols)
                 if (r,c) != farm.rover and farm.cells[r][c] != "obstacle"]
    chosen = st.selectbox("Associated field zone", available,
                          format_func=lambda pos: f"Row {pos[0]+1}, Column {pos[1]+1}",
                          disabled=not source.startswith("Upload"))
    severity = st.selectbox("Observed disease severity (manual)", ["Low", "Medium", "High"],
                            index=1, disabled=not source.startswith("Upload"))
    st.caption(f"Current field: {farm.name} · {farm.counts()['infected']} infected zone(s)")
    st.page_link("app.py", label="Edit farm map", icon="🌱")

image_bytes = uploaded.getvalue() if uploaded else None
signature = (str(farm.to_dict()), str(st.session_state.get("zone_diagnoses", {})),
             image_fingerprint(image_bytes) if image_bytes else None, source,
             chosen if source.startswith("Upload") else None, severity, planner, per_step,
             int(capacity), reserve, rain, threshold)
if st.session_state.get("auto_signature") != signature:
    st.session_state.pop("auto_result", None)
    st.session_state.pop("auto_rover", None)

disabled = (source.startswith("Upload") and (image_bytes is None or not model_ready))
if st.button("⚡ Analyze leaf + prepare complete autonomous mission", type="primary",
             use_container_width=True, disabled=disabled):
    try:
        with st.spinner("Classifying, applying expert rules, calculating route and checking safety..."):
            result = build_workflow(
                farm, st.session_state.get("zone_diagnoses", {}),
                image_bytes=image_bytes if source.startswith("Upload") else None,
                zone=chosen if source.startswith("Upload") else None, severity=severity,
                planner=planner, battery_per_step=per_step, capacity=int(capacity),
                reserve=float(reserve), rain=rain, confidence_threshold=threshold)
        st.session_state.auto_result = result
        st.session_state.auto_signature = signature
        st.session_state.pop("auto_rover", None)
    except (ValueError, OSError, ImportError, RuntimeError, KeyError) as exc:
        st.error(f"Could not prepare mission: {exc}")

result = st.session_state.get("auto_result")
if result:
    st.divider()
    st.subheader("02  ·  AI findings & inspection priorities")
    m1,m2,m3,m4 = st.columns(4)
    m1.metric("Predicted disease", result.predicted_label or "Existing zones")
    m2.metric("Model probability", f"{result.probability:.1%}" if result.probability is not None else "—")
    m3.metric("Zones to inspect", result.overview["total_zones"])
    m4.metric("Manual reviews", result.overview["manual_review"])
    if result.predicted_label and result.predicted_label.lower() == "healthy":
        st.info("The model predicted Healthy. No new infected zone was created; existing zones are still inspected.")
    if result.overview["manual_review"]:
        st.warning("One or more diagnoses are uncertain or unverified. The rover is performing inspection only, not automatic spraying.")
    if rain:
        st.info("Rain mode is active. Spraying is deferred.")
    st.dataframe([p.to_dict() for p in result.overview["plans"]], hide_index=True, use_container_width=True)
    st.subheader("03  ·  Optimized route & preflight")
    if not result.route.found:
        st.error(result.route.message)
    else:
        r1,r2,r3 = st.columns(3)
        r1.metric("Round-trip steps", result.preflight.steps)
        r2.metric("Projected battery", f"{result.preflight.estimated_battery_end:.1f}%")
        r3.metric("Safety check", "PASS" if result.ready else "BLOCKED")
        if result.ready:
            st.success("Route reaches all infected zones and returns to base within the selected safety constraints.")
        else:
            st.error("; ".join(result.preflight.issues))
        fig = farm_figure(result.farm)
        fig.add_trace(go.Scatter(x=[c+1 for r,c in result.route.path],
                                 y=[r+1 for r,c in result.route.path],
                                 mode="lines", line=dict(color="#138a52",width=4), name="Planned route"))
        st.plotly_chart(fig, use_container_width=True)
    if result.ready:
        st.subheader("04  ·  Virtual rover execution")
        st.caption("Choose an instant complete simulation or open the existing animated rover controls.")
        c1,c2 = st.columns(2)
        with c1:
            if st.button("🚜 Run entire mission automatically", type="primary", use_container_width=True):
                st.session_state.auto_rover = simulate_to_completion(result, per_step, int(capacity))
        with c2:
            if st.button("▶ Open animated rover with this mission", use_container_width=True):
                from agroroute.rover import RoverState
                # Commit the proposed zone only after the user approves the mission.
                st.session_state.farm = result.farm
                st.session_state.zone_diagnoses = result.diagnoses
                st.session_state.rover_scenario = str(result.farm.to_dict())
                st.session_state.rover_mission = result.route
                st.session_state.rover_state = RoverState(result.route.path, capacity=int(capacity))
                st.session_state.rover_playing = False
                st.session_state.rover_preflight = result.preflight
                st.session_state.rover_transfer_settings = (per_step, int(capacity), reserve)
                st.switch_page("pages/4_Virtual_Rover.py")
        rover = st.session_state.get("auto_rover")
        if rover:
            t1,t2,t3 = st.columns(3)
            t1.metric("Mission status", rover.status)
            t2.metric("Battery remaining", f"{rover.battery:.1f}%")
            t3.metric("Zones inspected", len(rover.inspected))
            st.progress(rover.step/max(1,len(rover.path)-1))
            if rover.status == "Completed":
                st.success("Inspection mission complete. Rover returned to base.")
            else:
                st.error("Rover stopped: " + rover.status)
    report = workflow_report(result, st.session_state.get("auto_rover"))
    st.download_button("⬇ Download complete autonomous mission report (JSON)",
                       json.dumps(report, indent=2), file_name="agroroute_autonomous_report.json",
                       mime="application/json", use_container_width=True)
footer()
