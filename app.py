"""AgroRoute AI — Phase 1 interactive farm designer."""
import json
import streamlit as st
from agroroute.farm import Farm, demo_farm

st.set_page_config(page_title='AgroRoute AI | Farm Designer', page_icon='🌱', layout='wide', initial_sidebar_state='expanded')
st.markdown('''<style>
.block-container {padding-top:1.4rem;max-width:1450px}
.hero {padding:1.4rem 1.7rem;border-radius:18px;background:linear-gradient(110deg,#123b2b,#207b50);color:white;margin-bottom:1.2rem}
.hero h1 {margin:0;color:white;font-size:2.1rem}.hero p {margin:.4rem 0 0;color:#e0f6e9}
.cell-legend {display:inline-block;padding:6px 11px;border-radius:8px;margin:3px;background:#edf4ed;color:#173e2a;font-size:13px}
</style>''', unsafe_allow_html=True)

if 'farm' not in st.session_state:
    st.session_state.farm = demo_farm()
if 'revision' not in st.session_state:
    st.session_state.revision = 0
if 'message' not in st.session_state:
    st.session_state.message = ''

farm: Farm = st.session_state.farm
st.markdown('<div class="hero"><h1>🌱 AgroRoute AI</h1><p>Intelligent Crop Monitoring · Search Algorithms · Autonomous Rover Simulation</p></div>', unsafe_allow_html=True)

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
    uploaded = st.file_uploader('Import scenario JSON', type=['json'], max_upload_size=2)
    if uploaded is not None and st.button('Import uploaded farm', use_container_width=True):
        try:
            imported = Farm.from_dict(json.loads(uploaded.getvalue().decode('utf-8')))
            st.session_state.farm = imported
            st.session_state.revision += 1
            st.rerun()
        except (ValueError, KeyError, TypeError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            st.error(f'Could not import scenario: {exc}')

counts = farm.counts()
c1,c2,c3,c4,c5 = st.columns(5)
c1.metric('Farm cells', farm.rows * farm.cols)
c2.metric('Healthy crops', counts['crop'])
c3.metric('Infected zones', counts['infected'])
c4.metric('Obstacles', counts['obstacle'])
c5.metric('Rover start', f'({farm.rover[0]+1}, {farm.rover[1]+1})')

left, right = st.columns([3.2, 1], gap='large')
with left:
    st.subheader(f'🗺️ {farm.name or "Untitled Farm"}')
    st.caption('Click a cell to apply the selected tool. Coordinates are 1-based in the interface.')
    # Native Streamlit buttons provide reliable click handling without custom JavaScript.
    # A keyed grid is rebuilt after every edit to prevent stale button state.
    for r in range(farm.rows):
        cells = st.columns(farm.cols, gap='small')
        for c in range(farm.cols):
            kind = farm.cells[r][c]
            symbol = ('🤖' if farm.rover == (r,c) else
                      {'crop':'🌿','empty':'·','obstacle':'🪨','infected':{'Low':'🟡','Medium':'🟠','High':'🔴'}[farm.severities.get(f'{r},{c}','Medium')]}[kind])
            if cells[c].button(symbol, key=f'cell_{st.session_state.revision}_{r}_{c}',
                               help=f'Row {r+1}, column {c+1} | {kind}', use_container_width=True):
                try:
                    farm.paint(r,c,tool,severity)
                    st.session_state.revision += 1
                    st.rerun()
                except ValueError as exc:
                    st.warning(str(exc))
    st.markdown('<span class="cell-legend">🤖 Rover</span><span class="cell-legend">🌿 Crop</span><span class="cell-legend">· Empty</span><span class="cell-legend">🪨 Obstacle</span><span class="cell-legend">🟡 Low</span><span class="cell-legend">🟠 Medium</span><span class="cell-legend">🔴 High</span>', unsafe_allow_html=True)
with right:
    st.subheader('📍 Zone details')
    infected = [(r+1,c+1,farm.severities.get(f'{r},{c}','Medium')) for r in range(farm.rows)
                for c in range(farm.cols) if farm.cells[r][c]=='infected']
    if infected:
        st.dataframe([{'Row':r,'Column':c,'Severity':s} for r,c,s in infected], hide_index=True, use_container_width=True)
    else:
        st.info('No infected zones yet. Choose Infected zone and click a cell.')
    st.subheader('🧭 Project status')
    st.success('Farm editor is operational')
    st.write('**Now available:** use the **Algorithm Lab** page in the navigation sidebar to run A*, UCS and Greedy Best-First.')
    st.caption('Use the navigation sidebar for Mission Planner, Virtual Rover, Expert System, CSP and Real Disease Detection.')
