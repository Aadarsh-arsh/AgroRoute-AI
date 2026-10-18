"""Phase 3: obstacle-aware multi-zone mission planning and virtual rover preview."""
import streamlit as st
import plotly.graph_objects as go
from agroroute.farm import demo_farm
from agroroute.mission import mission, infected_zones
from agroroute.visualization import farm_figure

st.set_page_config(page_title='AgroRoute AI | Mission Planner',page_icon='🚜',layout='wide')
if 'farm' not in st.session_state:
    st.session_state.farm=demo_farm()
farm=st.session_state.farm
st.title('🚜 Multi-Zone Mission Planner')
st.caption('Phase 3 · Visit all infected zones · Obstacle-aware UCS distance matrix · Genetic Algorithm vs nearest-neighbor vs exact optimum')
zones=infected_zones(farm)
with st.sidebar:
    st.header('Mission settings')
    algo=st.selectbox('Planner',['Genetic Algorithm','Nearest Neighbor','Exact Dynamic Programming'])
    back=st.checkbox('Return to rover start',value=True)
    if algo=='Genetic Algorithm':
        pop=st.slider('Population',10,200,80,10)
        generations=st.slider('Generations',20,500,180,20)
        seed=st.number_input('Random seed',0,100000,42)
    else:pop,generations,seed=80,180,42
    run=st.button('🚀 Plan mission',type='primary',use_container_width=True)
    compare=st.button('📊 Compare all planners',use_container_width=True)

scenario=str(farm.to_dict())
settings=(scenario,back,algo,pop,generations,seed)
if st.session_state.get('mission_signature')!=settings:
    st.session_state.mission_signature=settings
    st.session_state.mission_results=None
if run or compare:
    names=['Nearest Neighbor','Genetic Algorithm','Exact Dynamic Programming'] if compare else [algo]
    st.session_state.mission_results=[mission(farm,name,back,pop,generations,int(seed)) for name in names]
results=st.session_state.get('mission_results')
if not zones:
    st.warning('Add infected zones in the Farm Designer to plan a mission.')
elif len(zones)>20:
    st.warning('The interactive mission planner supports up to 20 zones. Reduce infected zones in Farm Designer.')
elif results:
    available=[r for r in results if r.found]
    st.dataframe([{'Planner':r.algorithm,'Feasible':r.found,'Distance (cells)':r.cost,
       'Runtime (ms)':round(r.elapsed_ms,2),'Evaluations / DP states':r.evaluations,'Note':r.message} for r in results],
       use_container_width=True,hide_index=True)
    if available:
        selected=next((r for r in available if r.algorithm==algo),available[0])
        best_exact=next((r for r in available if r.algorithm=='Exact Dynamic Programming'),None)
        c1,c2,c3=st.columns(3)
        c1.metric('Total distance',f'{selected.cost} cells')
        c2.metric('Zones to visit',len(zones))
        c3.metric('Optimality gap',f'{(selected.cost-best_exact.cost)/best_exact.cost*100:.1f}%' if best_exact and best_exact.cost else 'Run exact comparison')
        st.subheader('Route and virtual rover preview')
        step=st.slider('Rover movement step',0,len(selected.path)-1,0)
        fig=farm_figure(farm)
        fig.add_trace(go.Scatter(x=[p[1]+1 for p in selected.path],y=[p[0]+1 for p in selected.path],
           mode='lines',name='Mission path',line=dict(color='#0d784b',width=5)))
        r,c=selected.path[step]
        fig.add_trace(go.Scatter(x=[c+1],y=[r+1],mode='markers+text',name='Virtual rover',text=['🚜'],
           textposition='top center',marker=dict(color='#1b63b2',size=19,line=dict(color='white',width=2))))
        st.plotly_chart(fig,use_container_width=True)
        st.progress(step/max(1,len(selected.path)-1))
        st.caption(f'Step {step} of {len(selected.path)-1} · Rover at row {r+1}, column {c+1}. Use slider to replay; automated animation is Phase 4.')
        st.write('**Visit sequence:** '+' → '.join(f'({r+1},{c+1})' for r,c in selected.order))
        if best_exact:
            st.caption('Exact Dynamic Programming supplies a verified optimum for missions with up to 11 zones. GA is approximate; repeated runs can vary with seed.')
    else:
        st.error('No feasible mission found. '+'; '.join(r.message for r in results if r.message))
else:
    st.info(f'{len(zones)} infected zones found. Select a planner and click Plan mission.')
    st.plotly_chart(farm_figure(farm),use_container_width=True)
    st.caption('Farm scenarios are shared with the Phase 1 designer through Streamlit session state.')
