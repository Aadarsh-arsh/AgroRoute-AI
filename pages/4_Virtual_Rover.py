import streamlit as st
import json
from datetime import datetime, timezone
import plotly.graph_objects as go
from agroroute.farm import demo_farm
from agroroute.mission import mission
from agroroute.rover import RoverState
from agroroute.mission_control import preflight
from agroroute.visualization import farm_figure
from agroroute.ui import apply_theme, page_hero, info_strip, footer
st.set_page_config(page_title='AgroRoute | Virtual Rover',page_icon='🤖',layout='wide')
apply_theme()
page_hero('Virtual Rover Simulator', 'Execute optimized missions, inspect infected crop zones and watch battery telemetry update during live playback.', icon='🚜', eyebrow='SIMULATION • AUTONOMOUS MISSION')
info_strip('Deterministic tick-based simulation  •  Play, Pause, Step and Reset  •  Battery consumption is illustrative, not hardware-calibrated')
farm=st.session_state.get('farm',demo_farm())
scenario=str(farm.to_dict())
if st.session_state.get('rover_scenario')!=scenario:
    st.session_state.rover_scenario=scenario
    st.session_state.rover_state=None
    st.session_state.rover_mission=None
    st.session_state.rover_playing=False
# Preserve the safety settings of missions transferred from Autonomous Workflow.
transfer = st.session_state.pop("rover_transfer_settings", None)
if transfer is not None:
    st.session_state["rover_battery_rate"] = float(transfer[0])
    st.session_state["rover_capacity_input"] = int(transfer[1])
    st.session_state["rover_reserve_input"] = int(transfer[2])
with st.sidebar:
    planner=st.selectbox('Mission planner',['Nearest Neighbor','Genetic Algorithm','Exact Dynamic Programming'])
    per_step=st.slider('Battery consumption per step (%)',0.1,2.0,0.4,0.1,key='rover_battery_rate')
    capacity=st.number_input('Inspection capacity',1,30,20,key='rover_capacity_input')
    reserve=st.slider('Required battery reserve (%)',0,50,15,5,key='rover_reserve_input')
    if st.button('Generate mission',type='primary',use_container_width=True):
        st.session_state.rover_playing=False
        result=mission(farm,planner,return_to_base=True)
        if result.found:
            check=preflight(farm,result.path,per_step,int(capacity),reserve)
            st.session_state.rover_preflight=check
            st.session_state.rover_mission=result
            st.session_state.rover_state=RoverState(result.path,capacity=int(capacity))
            st.session_state.rover_mission_settings=(per_step,int(capacity),reserve)
        else: st.error(result.message)
result=st.session_state.get('rover_mission'); rover=st.session_state.get('rover_state')
if result is not None and 'rover_mission_settings' not in st.session_state:
    st.session_state.rover_mission_settings=(per_step,int(capacity),reserve)
settings_changed = (result is not None and st.session_state.get('rover_mission_settings') != (per_step,int(capacity),reserve))
if settings_changed:
    st.session_state.rover_playing=False
    st.warning('Mission settings changed. Generate a new mission before resuming the rover.')
if rover and result:
    a,b,c,d=st.columns(4)
    a.metric('Status',rover.status); b.metric('Battery',f'{rover.battery:.1f}%')
    c.metric('Inspected zones',len(rover.inspected)); d.metric('Movement',f'{rover.step}/{len(rover.path)-1}')
    check=preflight(farm,result.path,per_step,int(capacity),reserve,rover.battery+rover.step*per_step)
    if check.feasible and not settings_changed:
        st.success(f'Return-to-base route validated · {check.steps} steps · projected final battery {check.estimated_battery_end:.1f}%')
    else:
        st.error('Mission preflight failed: ' + '; '.join(check.issues))
        st.session_state.rover_playing=False
    speed=st.slider('Playback interval (seconds)',0.2,2.0,0.5,0.1)
    st.session_state.rover_speed=speed
    a1,a2,a3,a4=st.columns(4)
    if a1.button('▶ Play / Resume',disabled=not check.feasible or settings_changed or rover.status in ('Completed','Blocked','Battery depleted','Invalid route','Inspection capacity reached','No route'),use_container_width=True):
        st.session_state.rover_playing=True
    if a2.button('⏸ Pause',use_container_width=True):
        st.session_state.rover_playing=False
    if a3.button('⏭ Step',disabled=not check.feasible or settings_changed or rover.status in ('Completed','Blocked','Battery depleted','Invalid route','Inspection capacity reached','No route') or st.session_state.get('rover_playing',False),use_container_width=True):
        rover.tick(farm,per_step)
    if a4.button('↺ Reset',disabled=settings_changed,use_container_width=True):
        st.session_state.rover_playing=False
        st.session_state.rover_state=RoverState(result.path,capacity=int(capacity))
        rover=st.session_state.rover_state

    # Fragment reruns only the telemetry/chart, not the entire page. It stops on Pause.
    @st.fragment(run_every=speed)
    def live_rover():
        active=st.session_state.get('rover_state')
        if st.session_state.get('rover_playing',False) and not settings_changed and active is not None:
            if not active.tick(farm,per_step):
                st.session_state.rover_playing=False
            if active.status in ('Completed','Blocked','Battery depleted','Invalid route','Inspection capacity reached'):
                st.session_state.rover_playing=False
        if active is None:
            return
        m1,m2,m3,m4=st.columns(4)
        m1.metric('Live status',active.status)
        m2.metric('Live battery',f'{active.battery:.1f}%')
        m3.metric('Zones inspected',len(active.inspected))
        m4.metric('Live movement',f'{active.step}/{len(active.path)-1}')
        live_fig=farm_figure(farm)
        live_fig.add_trace(go.Scatter(x=[c+1 for r,c in active.path],y=[r+1 for r,c in active.path],mode='lines',name='Planned route',line=dict(color='#198754',width=4)))
        live_fig.add_trace(go.Scatter(x=[c+1 for r,c in active.path[:active.step+1]],y=[r+1 for r,c in active.path[:active.step+1]],mode='lines',name='Travelled',line=dict(color='#2365b7',width=5)))
        r,c=active.position
        live_fig.add_trace(go.Scatter(x=[c+1],y=[r+1],mode='markers+text',text=['🚜'],textposition='top center',name='Rover',marker=dict(size=20,color='#2365b7')))
        st.plotly_chart(live_fig,use_container_width=True,key='live_rover_chart')
        st.progress(active.step/max(1,len(active.path)-1))
        if active.status=='Completed':
            st.success('Mission completed; rover returned to base!')
        report={'generated_at_utc':datetime.now(timezone.utc).isoformat(),'farm':farm.name,'planner':result.algorithm,'status':active.status,'steps_completed':active.step,'planned_steps':len(active.path)-1,'battery_remaining_pct':active.battery,'inspected_zones':[{'row':r+1,'column':c+1,'severity':farm.severities.get(farm.key(r,c),'Medium'),'diagnosis':st.session_state.get('zone_diagnoses',{}).get(farm.key(r,c))} for r,c in active.inspected],'route':[{'row':r+1,'column':c+1} for r,c in active.path]}
        st.download_button('⬇ Download mission report (JSON)',json.dumps(report,indent=2),file_name='agroroute_mission_report.json',mime='application/json')
        if report['inspected_zones']:
            st.dataframe(report['inspected_zones'],use_container_width=True)
    live_rover()

else:
    st.info('Click Generate mission to begin rover simulation. Configure infected zones in the Farm Designer first.')
    st.plotly_chart(farm_figure(farm),use_container_width=True)

footer()
