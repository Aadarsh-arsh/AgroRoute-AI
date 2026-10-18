import streamlit as st
import time
import json
from datetime import datetime, timezone
import plotly.graph_objects as go
from agroroute.farm import demo_farm
from agroroute.mission import mission
from agroroute.rover import RoverState
from agroroute.visualization import farm_figure
st.set_page_config(page_title='AgroRoute | Virtual Rover',page_icon='🤖',layout='wide')
st.title('🤖 Virtual Rover Simulator')
st.caption('Live mission dashboard · route execution · inspection telemetry')
st.caption('Deterministic tick-based rover simulation. Battery use and capacity are illustrative, not hardware-calibrated.')
farm=st.session_state.get('farm',demo_farm())
scenario=str(farm.to_dict())
if st.session_state.get('rover_scenario')!=scenario:
    st.session_state.rover_scenario=scenario
    st.session_state.rover_state=None
    st.session_state.rover_mission=None
with st.sidebar:
    planner=st.selectbox('Mission planner',['Nearest Neighbor','Genetic Algorithm','Exact Dynamic Programming'])
    per_step=st.slider('Battery consumption per step (%)',0.1,2.0,0.4,0.1)
    capacity=st.number_input('Inspection capacity',1,30,20)
    if st.button('Generate mission',type='primary',use_container_width=True):
        result=mission(farm,planner)
        if result.found:
            st.session_state.rover_mission=result
            st.session_state.rover_state=RoverState(result.path,capacity=int(capacity))
        else: st.error(result.message)
result=st.session_state.get('rover_mission'); rover=st.session_state.get('rover_state')
if rover and result:
    a,b,c,d=st.columns(4)
    a.metric('Status',rover.status); b.metric('Battery',f'{rover.battery:.1f}%')
    c.metric('Inspected zones',len(rover.inspected)); d.metric('Movement',f'{rover.step}/{len(rover.path)-1}')
    left,middle,right=st.columns(3)
    if left.button('▶ Advance one step',use_container_width=True): rover.tick(farm,per_step)
    if middle.button('⏭ Advance 10 steps',use_container_width=True):
        for _ in range(10):
            if not rover.tick(farm,per_step): break
    if right.button('↺ Reset rover',use_container_width=True):
        st.session_state.rover_state=RoverState(result.path,capacity=int(capacity)); rover=st.session_state.rover_state
    st.markdown('#### Automatic simulation')
    auto1,auto2,auto3=st.columns([1,1,2])
    speed=auto3.slider('Playback delay (seconds)',0.1,1.5,0.4,0.1)
    if auto1.button('▶ Play 10 steps',use_container_width=True):
        progress=st.progress(rover.step/max(1,len(rover.path)-1))
        for _ in range(10):
            if not rover.tick(farm,per_step): break
            progress.progress(rover.step/max(1,len(rover.path)-1))
            time.sleep(speed)
        st.rerun()
    if auto2.button('⏭ Run to completion',use_container_width=True):
        progress=st.progress(rover.step/max(1,len(rover.path)-1))
        while rover.tick(farm,per_step):
            progress.progress(rover.step/max(1,len(rover.path)-1))
        st.rerun()
    fig=farm_figure(farm)
    fig.add_trace(go.Scatter(x=[c+1 for r,c in rover.path],y=[r+1 for r,c in rover.path],mode='lines',name='Planned route',line=dict(color='#198754',width=4)))
    fig.add_trace(go.Scatter(x=[c+1 for r,c in rover.path[:rover.step+1]],y=[r+1 for r,c in rover.path[:rover.step+1]],mode='lines',name='Travelled',line=dict(color='#2365b7',width=5)))
    r,c=rover.position
    fig.add_trace(go.Scatter(x=[c+1],y=[r+1],mode='markers+text',text=['🚜'],textposition='top center',name='Rover',marker=dict(size=20,color='#2365b7')))
    st.plotly_chart(fig,use_container_width=True)
    st.progress(rover.step/max(1,len(rover.path)-1))
    st.write('Visited:',[(r+1,c+1) for r,c in rover.inspected])
    if rover.status=='Completed':st.success('Mission completed!')
    report={'generated_at_utc':datetime.now(timezone.utc).isoformat(),'farm':farm.name,'planner':result.algorithm,'status':rover.status,'steps_completed':rover.step,'planned_steps':len(rover.path)-1,'battery_remaining_pct':rover.battery,'inspected_zones':[{'row':r+1,'column':c+1,'severity':farm.severities.get(farm.key(r,c),'Medium'),'diagnosis':st.session_state.get('zone_diagnoses',{}).get(farm.key(r,c))} for r,c in rover.inspected],'route':[{'row':r+1,'column':c+1} for r,c in rover.path]}
    st.download_button('⬇ Download mission report (JSON)',json.dumps(report,indent=2),file_name='agroroute_mission_report.json',mime='application/json')
    if report['inspected_zones']:
        st.dataframe(report['inspected_zones'],use_container_width=True)
else:
    st.info('Click Generate mission to begin rover simulation. Configure infected zones in the Farm Designer first.')
    st.plotly_chart(farm_figure(farm),use_container_width=True)
