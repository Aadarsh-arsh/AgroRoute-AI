"""Phase 2 search lab; shares Farm via Streamlit session state."""
import streamlit as st
from agroroute.farm import demo_farm
from agroroute.pathfinding import ALGORITHMS, search, compare
from agroroute.visualization import farm_figure

st.set_page_config(page_title='AgroRoute AI | Algorithm Lab',page_icon='🧭',layout='wide')
if 'farm' not in st.session_state:
    st.session_state.farm = demo_farm()
farm = st.session_state.farm
st.title('🧭 AI Pathfinding Laboratory')
st.caption('Phase 2 · A* / UCS / Greedy Best-First · 4-direction movement · 1 cost per cell · obstacles are impassable')
with st.sidebar:
    st.header('Search configuration')
    algo = st.selectbox('Algorithm',ALGORITHMS)
    infected = [(r,c) for r in range(farm.rows) for c in range(farm.cols) if farm.cells[r][c]=='infected']
    mode = st.radio('Destination selection',['Infected zone','Any traversable cell'],horizontal=False)
    if mode == 'Infected zone' and infected:
        goal = st.selectbox('Choose infected zone',infected,format_func=lambda p:f'Row {p[0]+1}, Col {p[1]+1} · {farm.severities.get(f"{p[0]},{p[1]}","Medium")}')
    else:
        if mode == 'Infected zone': st.warning('No infected zones; using manual coordinates.')
        r = st.number_input('Destination row (1-based)',1,farm.rows,min(2,farm.rows))
        c = st.number_input('Destination column (1-based)',1,farm.cols,min(2,farm.cols))
        goal = (int(r)-1,int(c)-1)
    show_explored = st.checkbox('Show expanded search states',value=True)
    run = st.button('▶ Run selected algorithm',type='primary',use_container_width=True)
    run_all = st.button('📊 Compare all three',use_container_width=True)

# Recompute only on demand; invalidate cached results if the farm is edited.
scenario = str(farm.to_dict())
if st.session_state.get('lab_scenario') != scenario:
    st.session_state.lab_scenario = scenario
    st.session_state.lab_results = None
    st.session_state.lab_goal = None
if run or run_all:
    try:
        results = compare(farm,goal) if run_all else [search(farm,goal,algo)]
        st.session_state.lab_results = results
        st.session_state.lab_goal = goal
    except ValueError as exc:
        st.error(str(exc))
results = st.session_state.get('lab_results')
if results:
    selected = next((x for x in results if x.algorithm == algo),results[0])
    if not selected.found:
        st.warning('No reachable path to the destination. Change obstacles or choose another target.')
    a,b,c,d = st.columns(4)
    a.metric('Path steps',selected.steps if selected.found else 'Unreachable')
    b.metric('Expanded states',selected.expanded_count)
    c.metric('Runtime',f'{selected.elapsed_ms:.3f} ms')
    d.metric('Peak frontier',selected.frontier_peak)
    st.plotly_chart(farm_figure(farm,selected,show_explored),use_container_width=True)
    st.subheader('Algorithm results')
    st.dataframe([{'Algorithm':x.algorithm,'Found':x.found,'Path cost':x.cost,'Steps':x.steps if x.found else None,
        'Expanded states':x.expanded_count,'Peak frontier':x.frontier_peak,'Runtime (ms)':round(x.elapsed_ms,3)} for x in results],
        use_container_width=True,hide_index=True)
    st.caption('Runtime depends on hardware and run conditions. UCS and A* return shortest paths for this unit-cost grid; Greedy is not guaranteed optimal.')
    if selected.found:
        with st.expander('Show exact path coordinates'):
            st.code(' → '.join(f'({r+1},{c+1})' for r,c in selected.path))
else:
    st.info('Select a destination in the sidebar and click Run selected algorithm or Compare all three.')
    st.plotly_chart(farm_figure(farm),use_container_width=True)
    st.caption('To edit the farm, return to the Farm Designer page using the navigation menu.')
