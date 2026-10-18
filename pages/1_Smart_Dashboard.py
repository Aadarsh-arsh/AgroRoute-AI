"""Unified, guided farm -> AI diagnosis -> advisory -> routing -> rover flow."""
import json
from collections import Counter
from dataclasses import asdict
from datetime import datetime, timezone
import streamlit as st
from html import escape
from agroroute.ui import apply_theme, footer
import plotly.graph_objects as go
from agroroute.farm import demo_farm
from agroroute.dashboard import overview, prepare_mission, PLANNERS
from agroroute.visualization import farm_figure

st.set_page_config(page_title='AgroRoute AI | Smart Dashboard', page_icon='🌱', layout='wide')

st.markdown("""
<style>
.block-container{max-width:1500px;padding-top:1.15rem;padding-bottom:2rem}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#0e201a 0%,#12271f 100%)}
[data-testid="stSidebar"] *{color:#eef8f1 !important}
.main-shell{background:linear-gradient(180deg,#f3f8f4 0%,#edf4ef 100%);padding:1.2rem;border-radius:28px;border:1px solid rgba(18,75,45,.08);box-shadow:0 20px 40px rgba(15,35,25,.08)}
.topbar{display:flex;justify-content:space-between;align-items:center;gap:1rem;background:#ffffff;border:1px solid rgba(17,68,43,.08);box-shadow:0 10px 24px rgba(12,28,18,.06);padding:0.9rem 1rem;border-radius:22px;margin-bottom:1rem}
.brand{display:flex;align-items:center;gap:.9rem}
.brand .logo{width:52px;height:52px;border-radius:16px;background:linear-gradient(145deg,#116a42,#2fb56f);display:flex;align-items:center;justify-content:center;font-size:1.6rem;box-shadow:0 10px 18px rgba(24,129,78,.25)}
.brand h1{margin:0;font-size:1.8rem;color:#113923;font-weight:800}
.brand p{margin:.2rem 0 0;color:#63816f;font-size:.95rem}
.top-actions{display:flex;gap:.7rem;flex-wrap:wrap}
.pill{display:inline-flex;align-items:center;gap:.45rem;padding:.62rem 1rem;border-radius:999px;background:#f2f8f4;border:1px solid rgba(16,84,50,.12);color:#17462d;font-weight:600;font-size:.92rem}
.hero{display:grid;grid-template-columns:1.4fr .9fr;gap:1rem;align-items:stretch;margin-bottom:1rem}
.hero-card{border-radius:28px;padding:1.4rem 1.5rem;background:linear-gradient(135deg,#13462f 0%,#1a8d57 58%,#31be74 100%);color:#fff;box-shadow:0 18px 40px rgba(24,102,64,.25)}
.hero-card h2{margin:0;font-size:2.05rem;color:white;font-weight:800}
.hero-card p{margin:.7rem 0 0;color:#e3f6ea;max-width:92%;line-height:1.55}
.badges{display:flex;flex-wrap:wrap;gap:.6rem;margin-top:1rem}
.badge{padding:.45rem .8rem;border-radius:999px;background:rgba(255,255,255,.15);border:1px solid rgba(255,255,255,.18);color:#fff;font-weight:600;font-size:.85rem}
.hero-panel{border-radius:28px;background:#ffffff;border:1px solid rgba(17,68,43,.08);box-shadow:0 10px 24px rgba(12,28,18,.06);padding:1.25rem}
.panel-title{font-size:1.04rem;font-weight:800;color:#133d26;margin:0 0 .8rem 0}
.panel-caption{font-size:.9rem;color:#6b8574;margin:0 0 .9rem 0}
.kpi-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:1rem;margin:1rem 0 1.2rem}
.kpi-card{background:#ffffff;border:1px solid rgba(17,68,43,.08);border-radius:24px;padding:1rem 1.05rem;box-shadow:0 10px 24px rgba(12,28,18,.06)}
.kpi-card.primary{background:linear-gradient(135deg,#155437 0%,#1d8d57 100%);color:#fff}
.kpi-label{font-size:.88rem;color:#6c8574;font-weight:700;letter-spacing:.01em}
.kpi-card.primary .kpi-label{color:#def3e6}
.kpi-value{font-size:2.05rem;line-height:1.1;font-weight:800;color:#143c26;margin:.45rem 0 .2rem}
.kpi-card.primary .kpi-value{color:#fff}
.kpi-note{font-size:.88rem;color:#7b9484}
.kpi-card.primary .kpi-note{color:#d6efdf}
.section-card{background:#ffffff;border:1px solid rgba(17,68,43,.08);border-radius:28px;padding:1.15rem;box-shadow:0 10px 24px rgba(12,28,18,.06);height:100%}
.workflow-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:.85rem;margin:0.65rem 0 1rem}
.workflow-card{background:#ffffff;border:1px solid rgba(17,68,43,.08);border-radius:22px;padding:1rem;box-shadow:0 8px 20px rgba(12,28,18,.05)}
.workflow-step{width:34px;height:34px;border-radius:10px;background:linear-gradient(145deg,#e7f5ec,#d3efde);display:flex;align-items:center;justify-content:center;font-weight:800;color:#185033;margin-bottom:.75rem}
.workflow-card h4{margin:0 0 .35rem 0;color:#143d27;font-size:1rem}
.workflow-card p{margin:0;color:#73907d;font-size:.9rem;min-height:48px}
.audit-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:1rem}
.audit-card{border-radius:22px;padding:1rem;background:#f9fcfa;border:1px solid rgba(17,68,43,.08)}
.audit-ok{display:inline-block;padding:.28rem .6rem;border-radius:999px;background:#e1f7ea;color:#117342;font-weight:700;font-size:.8rem;margin-bottom:.55rem}
.audit-watch{display:inline-block;padding:.28rem .6rem;border-radius:999px;background:#fff2d7;color:#9d6900;font-weight:700;font-size:.8rem;margin-bottom:.55rem}
.subtle{color:#708a79;font-size:.92rem}
.result-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;margin:.75rem 0 1rem}
.result-card{background:#f6faf7;border:1px solid rgba(17,68,43,.08);border-radius:20px;padding:1rem}
.result-label{font-size:.85rem;color:#6d8776;font-weight:700}
.result-value{font-size:1.6rem;color:#153e27;font-weight:800;margin-top:.25rem}
.footer-note{margin-top:1rem;font-size:.84rem;color:#748d7e}
@media (max-width: 1200px){
  .hero{grid-template-columns:1fr}
  .kpi-grid,.workflow-grid,.audit-grid,.result-grid{grid-template-columns:repeat(2,1fr)}
}
@media (max-width: 760px){
  .kpi-grid,.workflow-grid,.audit-grid,.result-grid{grid-template-columns:1fr}
  .topbar{flex-direction:column;align-items:flex-start}
}
</style>
""", unsafe_allow_html=True)
apply_theme()

farm = st.session_state.setdefault('farm', demo_farm())
diagnoses = st.session_state.get('zone_diagnoses', {})

with st.sidebar:
    st.header('🌦 Mission settings')
    st.caption('Configure mission constraints and planner settings.')
    rain = st.checkbox('Rain expected during treatment', value=False, key='dashboard_rain')
    threshold = st.slider('Manual-review threshold', 0.40, 0.95, 0.65, 0.05, key='dashboard_threshold')
    planner = st.selectbox('Route planner', PLANNERS, index=1, key='dashboard_planner')
    rate = st.slider('Battery use per step (%)', 0.1, 2.0, 0.4, 0.1, key='dashboard_rate')
    reserve = st.slider('Minimum battery reserve (%)', 0, 50, 15, 5, key='dashboard_reserve')
    capacity = st.number_input('Inspection capacity', min_value=1, max_value=30, value=20, key='dashboard_capacity')
    st.divider()
    st.caption('Use this dashboard as the main control room for the whole AgroRoute workflow.')

info = overview(farm, diagnoses, rain, threshold)
counts = info['counts']
safe_name = escape(farm.name)
known_diseases = [p.disease for p in info['plans'] if p.disease != 'Unknown']
priority_text = 'High priority attention needed' if info['high_priority'] else 'No high priority alerts'
manual_text = f"{info['manual_review']} zone(s) need manual validation" if info['manual_review'] else 'All current zones are reviewed'

st.markdown('<div class="main-shell">', unsafe_allow_html=True)
st.markdown(
    f'''
    <div class="topbar">
      <div class="brand">
        <div class="logo">🌱</div>
        <div>
          <h1>AgroRoute AI</h1>
          <p>Smart Agriculture Command Center · Crop intelligence, mission planning and autonomous rover simulation</p>
        </div>
      </div>
      <div class="top-actions">
        <div class="pill">🧠 MobileNetV2 Active</div>
        <div class="pill">🤖 Rover Ready</div>
        <div class="pill">🛰 Planner: {planner}</div>
      </div>
    </div>
    ''',
    unsafe_allow_html=True,
)

st.markdown(
    f'''
    <div class="hero">
      <div class="hero-card">
        <h2>Monitor crop health, prioritize risk, and execute field missions intelligently.</h2>
        <p>AgroRoute AI combines disease detection, expert review, search algorithms, mission feasibility, and a virtual rover in one connected interface built for your AI project demonstration.</p>
        <div class="badges">
          <span class="badge">Farm: {safe_name}</span>
          <span class="badge">{info['total_zones']} Infected Zones</span>
          <span class="badge">Battery Reserve: {reserve}%</span>
          <span class="badge">Inspection Capacity: {capacity}</span>
        </div>
      </div>
      <div class="hero-panel">
        <div class="panel-title">Mission Snapshot</div>
        <div class="panel-caption">Quick view of the current field state before route generation.</div>
        <div class="pill" style="margin-bottom:.55rem;display:flex;width:fit-content;">⚠️ {manual_text}</div>
        <div class="pill" style="margin-bottom:.55rem;display:flex;width:fit-content;">📍 {priority_text}</div>
        <div class="pill" style="display:flex;width:fit-content;">🌧️ Rain mode: {'On' if rain else 'Off'}</div>
      </div>
    </div>
    ''',
    unsafe_allow_html=True,
)

kpi_html = f'''
<div class="kpi-grid">
  <div class="kpi-card primary">
    <div class="kpi-label">Farm Cells</div>
    <div class="kpi-value">{info['cells']}</div>
    <div class="kpi-note">Total editable field cells</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Infected Zones</div>
    <div class="kpi-value">{info['total_zones']}</div>
    <div class="kpi-note">Marked for inspection</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">High Priority</div>
    <div class="kpi-value">{info['high_priority']}</div>
    <div class="kpi-note">Critical review required</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Manual Review</div>
    <div class="kpi-value">{info['manual_review']}</div>
    <div class="kpi-note">Low-confidence predictions</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Obstacles</div>
    <div class="kpi-value">{counts['obstacle']}</div>
    <div class="kpi-note">Route-blocking cells</div>
  </div>
</div>
'''
st.markdown(kpi_html, unsafe_allow_html=True)

st.markdown('<div class="section-card" style="margin-bottom:1rem;">', unsafe_allow_html=True)
st.markdown('<div class="panel-title">Guided workflow</div><div class="panel-caption">Move through the project logically during your demo or viva.</div>', unsafe_allow_html=True)
workflow_cards = [
    ('1', 'Design the Field', 'Create crop zones, obstacles, infected cells and rover start.', 'app.py', 'Farm Designer'),
    ('2', 'Classify a Leaf', 'Use the trained disease model and compare against the decision tree.', 'pages/9_Model_Comparison.py', 'Model Comparison'),
    ('3', 'Review Treatment', 'Check confidence, severity and mission readiness before action.', 'pages/10_Smart_Treatment.py', 'Smart Treatment'),
    ('4', 'Optimize Route', 'Generate obstacle-aware routes using AI planning algorithms.', 'pages/3_Mission_Planner.py', 'Mission Planner'),
    ('5', 'Run Rover', 'Send the selected mission to the virtual rover and simulate execution.', 'pages/4_Virtual_Rover.py', 'Virtual Rover'),
]
link_cols = st.columns(5)
for col, (step, title, desc, target, label) in zip(link_cols, workflow_cards):
    with col:
        st.markdown(f'<div class="workflow-card"><div class="workflow-step">{step}</div><h4>{title}</h4><p>{desc}</p></div>', unsafe_allow_html=True)
        st.page_link(target, label='Open ' + label, icon='➡️', use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="audit-grid" style="margin-bottom:1rem;">', unsafe_allow_html=True)
audit_items = [
    ('Integrated Workflow', 'OK', 'Disease detection, treatment review, mission planning and rover share the farm state.'),
    ('Model Evaluation', 'OK', 'MobileNetV2 and Decision Tree comparison is available when saved model files are present.'),
    ('Mission Checks', 'OK', 'Planned routes are checked for capacity, battery reserve and return-to-base constraints.'),
    ('Field Validation', 'WATCH', 'Disease predictions and battery consumption remain experimental and uncalibrated.'),
]
for title, status, desc in audit_items:
    badge = 'audit-ok' if status == 'OK' else 'audit-watch'
    st.markdown(f'<div class="audit-card"><div class="{badge}">{status}</div><div class="panel-title" style="margin:0 0 .35rem 0;">{title}</div><div class="subtle">{desc}</div></div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

left, right = st.columns([1.5, 1], gap='large')
with left:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">Farm Intelligence Map</div><div class="panel-caption">Live field view showing infected zones, rover start and path constraints.</div>', unsafe_allow_html=True)
    fig = farm_figure(farm)
    fig.update_layout(height=520, margin=dict(l=20, r=20, t=20, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
with right:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">Inspection Priorities</div><div class="panel-caption">Disease, severity and confidence review for each infected zone.</div>', unsafe_allow_html=True)
    if info['plans']:
        rows = [{
            'Row': p.row,
            'Column': p.column,
            'Severity': p.severity,
            'Disease': p.disease,
            'Probability': f'{p.probability:.1%}' if p.probability is not None else '—',
            'Manual review': 'Yes' if p.manual_review else 'No'
        } for p in info['plans']]
        st.dataframe(rows, hide_index=True, use_container_width=True)
        if info['manual_review']:
            st.warning(f"{info['manual_review']} zone(s) require manual disease verification. Do not treat uncertain predictions as confirmed diagnoses.")
        if rain:
            st.info('Rain restriction active: defer spraying decisions.')
    else:
        st.info('No infected zones yet. Mark a zone in Farm Designer or assign a disease prediction from the model pages.')
    if known_diseases:
        disease_counts = Counter(known_diseases)
        chart = go.Figure(go.Bar(
            x=list(disease_counts.keys()),
            y=list(disease_counts.values()),
            marker_color=['#2a9d63', '#55bf83', '#0d693d', '#9ad8b3'][:len(disease_counts)]
        ))
        chart.update_layout(height=260, margin=dict(l=10, r=10, t=10, b=30), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', yaxis_title='Zones')
        st.plotly_chart(chart, use_container_width=True)
    else:
        st.caption('Assign a disease prediction to a zone to unlock the disease distribution chart.')
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="section-card" style="margin-top:1rem;">', unsafe_allow_html=True)
st.markdown('<div class="panel-title">Integrated Mission Control</div><div class="panel-caption">Generate a complete obstacle-aware, return-to-base mission and validate it before sending it to the rover.</div>', unsafe_allow_html=True)

if st.button('⚡ Calculate complete mission', type='primary', use_container_width=True):
    with st.spinner('Computing mission and checking feasibility...'):
        result, check = prepare_mission(farm, planner, rate, int(capacity), float(reserve))
    st.session_state.dashboard_result = result
    st.session_state.dashboard_check = check
    st.session_state.dashboard_signature = (repr(farm.to_dict()), planner, rate, int(capacity), reserve)

signature = (repr(farm.to_dict()), planner, rate, int(capacity), reserve)
result = st.session_state.get('dashboard_result')
check = st.session_state.get('dashboard_check')

if result and st.session_state.get('dashboard_signature') != signature:
    st.info('The farm or mission settings changed. Recalculate the mission to refresh the results.')
elif result and not result.found:
    st.error('No feasible route was generated: ' + result.message)
elif result and check:
    st.markdown(
        f'''
        <div class="result-grid">
          <div class="result-card"><div class="result-label">Route Steps</div><div class="result-value">{check.steps}</div></div>
          <div class="result-card"><div class="result-label">Projected Battery</div><div class="result-value">{check.estimated_battery_end:.1f}%</div></div>
          <div class="result-card"><div class="result-label">Zones to Inspect</div><div class="result-value">{info['total_zones']}</div></div>
          <div class="result-card"><div class="result-label">Planner Runtime</div><div class="result-value">{result.elapsed_ms:.1f} ms</div></div>
        </div>
        ''',
        unsafe_allow_html=True,
    )
    if check.feasible:
        st.success('Preflight passed: all marked infected zones are visited, the route returns to base, and battery/capacity constraints are satisfied.')
    else:
        st.error('Preflight blocked: ' + '; '.join(check.issues))

    route_fig = farm_figure(farm)
    route_fig.add_trace(go.Scatter(
        x=[c + 1 for r, c in result.path],
        y=[r + 1 for r, c in result.path],
        mode='lines',
        name='Mission route',
        line=dict(color='#078448', width=4)
    ))
    route_fig.update_layout(height=480, margin=dict(l=20, r=20, t=20, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(route_fig, use_container_width=True)

    report = {
        'generated_at_utc': datetime.now(timezone.utc).isoformat(),
        'farm': farm.name,
        'algorithm': result.algorithm,
        'preflight_passed': check.feasible,
        'issues': list(check.issues),
        'route_steps': check.steps,
        'projected_remaining_battery_pct': check.estimated_battery_end,
        'zones': [asdict(p) for p in info['plans']],
        'route': [{'row': r + 1, 'column': c + 1} for r, c in result.path],
        'disclaimer': 'Planning and battery estimates are simulated; disease predictions are experimental.'
    }
    action_a, action_b = st.columns([1.2, 1])
    with action_a:
        st.download_button('⬇ Download integrated mission JSON', json.dumps(report, indent=2), 'agroroute_integrated_mission.json', 'application/json', use_container_width=True)
    with action_b:
        if check.feasible:
            if st.button('🚜 Send this route to Virtual Rover', use_container_width=True):
                from agroroute.rover import RoverState
                st.session_state.rover_scenario = str(farm.to_dict())
                st.session_state.rover_mission = result
                st.session_state.rover_state = RoverState(result.path, capacity=int(capacity))
                st.session_state.rover_playing = False
                st.session_state.rover_preflight = check
                st.switch_page('pages/4_Virtual_Rover.py')

st.markdown('<div class="footer-note">AgroRoute AI is an academic software simulation. Disease prediction confidence is approximate, and treatment recommendations should be validated with trusted agricultural sources.</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

footer()
