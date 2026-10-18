"""AgroRoute AI — premium farm designer landing page."""
import json
import streamlit as st
from html import escape
from agroroute.ui import apply_theme, footer
from agroroute.farm import Farm, demo_farm

st.set_page_config(page_title='AgroRoute AI | Farm Designer', page_icon='🌱', layout='wide', initial_sidebar_state='expanded')
st.markdown('''<style>
.block-container{padding-top:1.1rem;max-width:1500px;padding-bottom:2rem}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#0f221b,#132a21)}
[data-testid="stSidebar"] *{color:#eef7f0 !important}
.main-shell{background:linear-gradient(180deg,#f3f8f4 0%,#edf4ef 100%);padding:1.2rem;border-radius:28px;border:1px solid rgba(18,75,45,.08);box-shadow:0 20px 40px rgba(15,35,25,.08)}
.topbar{display:flex;justify-content:space-between;align-items:center;gap:1rem;background:#fff;border:1px solid rgba(17,68,43,.08);box-shadow:0 10px 24px rgba(12,28,18,.06);padding:.95rem 1rem;border-radius:22px;margin-bottom:1rem}
.brand{display:flex;align-items:center;gap:.9rem}.brand .logo{width:50px;height:50px;border-radius:16px;background:linear-gradient(145deg,#116a42,#2fb56f);display:flex;align-items:center;justify-content:center;font-size:1.5rem;box-shadow:0 10px 18px rgba(24,129,78,.25)}
.brand h1{margin:0;font-size:1.8rem;color:#113923;font-weight:800}.brand p{margin:.15rem 0 0;color:#6a8675}
.hero{display:grid;grid-template-columns:1.5fr .95fr;gap:1rem;margin-bottom:1rem}
.hero-card{padding:1.35rem 1.5rem;border-radius:28px;background:linear-gradient(135deg,#13462f 0%,#1a8d57 58%,#31be74 100%);box-shadow:0 18px 40px rgba(24,102,64,.25);color:#fff}
.hero-card h2{margin:0;color:#fff;font-size:2rem}.hero-card p{margin:.65rem 0 0;color:#e4f7ea;line-height:1.55}
.hero-panel{padding:1.2rem;border-radius:28px;background:#fff;border:1px solid rgba(17,68,43,.08);box-shadow:0 10px 24px rgba(12,28,18,.06)}
.badge{display:inline-block;padding:.45rem .8rem;border-radius:999px;background:rgba(255,255,255,.16);color:#fff;border:1px solid rgba(255,255,255,.2);margin:.65rem .4rem 0 0;font-size:.86rem;font-weight:700}
.badge-light{display:inline-block;padding:.48rem .8rem;border-radius:999px;background:#f1f7f3;border:1px solid rgba(17,68,43,.1);color:#18472d;font-size:.86rem;font-weight:700;margin:0 .4rem .5rem 0}
.kpi-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:1rem;margin:1rem 0 1.2rem}
.kpi-card{background:#fff;border:1px solid rgba(17,68,43,.08);border-radius:24px;padding:1rem 1.05rem;box-shadow:0 10px 24px rgba(12,28,18,.06)}
.kpi-card.primary{background:linear-gradient(135deg,#155437 0%,#1d8d57 100%);color:#fff}
.kpi-label{font-size:.88rem;color:#6d8776;font-weight:700}.kpi-card.primary .kpi-label{color:#def3e6}
.kpi-value{font-size:2rem;color:#143c26;font-weight:800;margin:.45rem 0 .2rem}.kpi-card.primary .kpi-value{color:#fff}
.kpi-note{font-size:.88rem;color:#7d9686}.kpi-card.primary .kpi-note{color:#d9f0e0}
.section-card{background:#fff;border:1px solid rgba(17,68,43,.08);border-radius:28px;padding:1.15rem;box-shadow:0 10px 24px rgba(12,28,18,.06);height:100%}
.legend-chip{display:inline-block;padding:7px 11px;border-radius:999px;margin:4px;background:#f1f7f3;color:#173e2a;font-size:13px;border:1px solid rgba(17,68,43,.08)}
.status-good{display:inline-block;padding:.32rem .62rem;border-radius:999px;background:#e1f7ea;color:#117342;font-weight:700;font-size:.8rem}
@media (max-width: 1200px){.hero{grid-template-columns:1fr}.kpi-grid{grid-template-columns:repeat(2,1fr)}}
@media (max-width: 760px){.kpi-grid{grid-template-columns:1fr}.topbar{flex-direction:column;align-items:flex-start}}
</style>''', unsafe_allow_html=True)
apply_theme()

if 'farm' not in st.session_state:
    st.session_state.farm = demo_farm()
if 'revision' not in st.session_state:
    st.session_state.revision = 0
if 'message' not in st.session_state:
    st.session_state.message = ''

farm: Farm = st.session_state.farm

with st.sidebar:
    st.header('🛠️ Farm tools')
    st.caption('Select a tool, then click a grid cell to paint it.')
    tool = st.radio('Painting tool', ['crop', 'empty', 'obstacle', 'infected', 'rover'],
                    format_func=lambda x: {'crop':'🌿 Healthy crop', 'empty':'⬜ Empty path', 'obstacle':'🪨 Obstacle', 'infected':'🔴 Infected zone', 'rover':'🤖 Rover start'}[x])
    severity = st.selectbox('Disease severity', ['Low', 'Medium', 'High'], index=1,
                            disabled=(tool != 'infected'))
    st.divider()
    st.subheader('Farm settings')
    name = st.text_input('Farm name', value=farm.name)
    if name != farm.name:
        farm.name = name[:100]
    col_a, col_b = st.columns(2)
    rows = col_a.number_input('Rows', min_value=5, max_value=30, value=farm.rows)
    cols = col_b.number_input('Columns', min_value=5, max_value=30, value=farm.cols)
    if st.button('Create blank farm', use_container_width=True):
        st.session_state.farm = Farm(rows=int(rows), cols=int(cols), name=name[:100])
        st.session_state.revision += 1
        st.rerun()
    if st.button('Load demo farm', use_container_width=True):
        st.session_state.farm = demo_farm()
        st.session_state.revision += 1
        st.rerun()
    st.divider()
    st.subheader('Scenario file')
    payload = json.dumps(farm.to_dict(), indent=2)
    st.download_button('⬇️ Download farm JSON', data=payload, file_name='agroroute_farm.json',
                       mime='application/json', use_container_width=True)
    uploaded = st.file_uploader('Import scenario JSON', type=['json'])
    if uploaded is not None and st.button('Import uploaded farm', use_container_width=True):
        try:
            imported = Farm.from_dict(json.loads(uploaded.getvalue().decode('utf-8')))
            st.session_state.farm = imported
            st.session_state.revision += 1
            st.rerun()
        except (ValueError, KeyError, TypeError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            st.error(f'Could not import scenario: {exc}')

safe_name = escape(farm.name or 'Untitled Farm')
counts = farm.counts()
infected = [(r+1,c+1,farm.severities.get(f'{r},{c}','Medium')) for r in range(farm.rows)
            for c in range(farm.cols) if farm.cells[r][c]=='infected']

st.markdown('<div class="main-shell">', unsafe_allow_html=True)
st.markdown(f'''
<div class="topbar">
  <div class="brand">
    <div class="logo">🌱</div>
    <div>
      <h1>AgroRoute AI</h1>
      <p>Farm Designer · Search Algorithms · Disease Detection · Autonomous Rover Simulation</p>
    </div>
  </div>
  <div>
    <span class="badge-light">🧠 AI Project Ready</span>
    <span class="badge-light">🤖 Rover Workflow Connected</span>
    <span class="badge-light">🗂️ Editable Scenario</span>
  </div>
</div>
<div class="hero">
  <div class="hero-card">
    <h2>Design your field, mark infections, and build the foundation for intelligent crop missions.</h2>
    <p>Create the digital farm environment used by AgroRoute AI for pathfinding, mission planning, disease-linked zone prioritization, and rover execution.</p>
    <span class="badge">Farm: {safe_name}</span>
    <span class="badge">Grid: {farm.rows} × {farm.cols}</span>
    <span class="badge">Rover Start: ({farm.rover[0]+1}, {farm.rover[1]+1})</span>
  </div>
  <div class="hero-panel">
    <div style="font-size:1.05rem;font-weight:800;color:#133d26;margin-bottom:.7rem;">Editor Status</div>
    <div class="status-good">Operational</div>
    <p style="color:#6f8978;line-height:1.55;margin-top:.8rem;">Use this page to define the map that powers the mission planner, disease-priority dashboard, and virtual rover simulation.</p>
    <span class="badge-light">✅ JSON export/import</span>
    <span class="badge-light">✅ Severity tagging</span>
    <span class="badge-light">✅ Demo farm support</span>
  </div>
</div>
''', unsafe_allow_html=True)

st.markdown(f'''
<div class="kpi-grid">
  <div class="kpi-card primary"><div class="kpi-label">Farm Cells</div><div class="kpi-value">{farm.rows * farm.cols}</div><div class="kpi-note">Total working grid size</div></div>
  <div class="kpi-card"><div class="kpi-label">Healthy Crops</div><div class="kpi-value">{counts['crop']}</div><div class="kpi-note">Current healthy crop cells</div></div>
  <div class="kpi-card"><div class="kpi-label">Infected Zones</div><div class="kpi-value">{counts['infected']}</div><div class="kpi-note">Priority inspection points</div></div>
  <div class="kpi-card"><div class="kpi-label">Obstacles</div><div class="kpi-value">{counts['obstacle']}</div><div class="kpi-note">Route-blocking cells</div></div>
  <div class="kpi-card"><div class="kpi-label">Rover Start</div><div class="kpi-value">({farm.rover[0]+1},{farm.rover[1]+1})</div><div class="kpi-note">Initial simulation position</div></div>
</div>
''', unsafe_allow_html=True)

left, right = st.columns([3.15, 1.15], gap='large')
with left:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader(f'🗺️ {farm.name or "Untitled Farm"}')
    st.caption('Click a cell to apply the selected tool. Coordinates are 1-based in the interface.')
    for r in range(farm.rows):
        cells = st.columns(farm.cols, gap='small')
        for c in range(farm.cols):
            kind = farm.cells[r][c]
            symbol = ('🤖' if farm.rover == (r,c) else
                      {'crop':'🌿','empty':'·','obstacle':'🪨','infected':{'Low':'🟡','Medium':'🟠','High':'🔴'}[farm.severities.get(f'{r},{c}','Medium')]}[kind])
            if cells[c].button(symbol, key=f'cell_{st.session_state.revision}_{r}_{c}', help=f'Row {r+1}, column {c+1} | {kind}', use_container_width=True):
                try:
                    farm.paint(r,c,tool,severity)
                    st.session_state.revision += 1
                    st.rerun()
                except ValueError as exc:
                    st.warning(str(exc))
    st.markdown('<span class="legend-chip">🤖 Rover</span><span class="legend-chip">🌿 Crop</span><span class="legend-chip">· Empty</span><span class="legend-chip">🪨 Obstacle</span><span class="legend-chip">🟡 Low</span><span class="legend-chip">🟠 Medium</span><span class="legend-chip">🔴 High</span>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
with right:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader('📍 Zone details')
    if infected:
        st.dataframe([{'Row':r,'Column':c,'Severity':s} for r,c,s in infected], hide_index=True, use_container_width=True)
    else:
        st.info('No infected zones yet. Choose Infected zone and click a cell.')
    st.subheader('🧭 Project status')
    st.success('Farm editor is operational')
    st.write('**Recommended next step:** continue into the premium **Smart Dashboard** for a guided AI workflow.')
    st.page_link('pages/1_Smart_Dashboard.py', label='🌱 Open Smart Dashboard', use_container_width=True)
    st.page_link('pages/3_Mission_Planner.py', label='🧭 Open Mission Planner', use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

footer()
