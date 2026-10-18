"""Unified, guided farm -> AI diagnosis -> advisory -> routing -> rover flow."""
import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
import streamlit as st
import plotly.graph_objects as go
from agroroute.farm import demo_farm
from agroroute.dashboard import overview, prepare_mission, PLANNERS
from agroroute.visualization import farm_figure

st.set_page_config(page_title='AgroRoute AI | Smart Dashboard', page_icon='🌱', layout='wide')
st.markdown("""<style>
.block-container{max-width:1480px;padding-top:1.5rem}
.agrohero{border-radius:17px;padding:1.3rem 1.6rem;background:linear-gradient(105deg,#102f24,#1b7548);color:#fff}
.agrohero h1{color:#fff;font-size:2rem;margin:0}.agrohero p{color:#d8f2e2;margin:.3rem 0 0}
</style>""",unsafe_allow_html=True)
st.markdown('<div class="agrohero"><h1>🌱 AgroRoute AI — Smart Agriculture Command Center</h1><p>Disease observations → expert review → route optimization → virtual rover</p></div>',unsafe_allow_html=True)
st.caption('Software simulation for academic evaluation. AI disease predictions are experimental and do not replace agronomist diagnosis.')
farm=st.session_state.setdefault('farm',demo_farm())
diagnoses=st.session_state.get('zone_diagnoses',{})
with st.sidebar:
    st.header('🌦 Mission settings')
    rain=st.checkbox('Rain expected during treatment',value=False,key='dashboard_rain')
    threshold=st.slider('Manual-review threshold',0.40,0.95,0.65,0.05,key='dashboard_threshold')
    planner=st.selectbox('Route planner',PLANNERS,index=1,key='dashboard_planner')
    rate=st.slider('Battery use per step (%)',0.1,2.0,0.4,0.1,key='dashboard_rate')
    reserve=st.slider('Minimum battery reserve (%)',0,50,15,5,key='dashboard_reserve')
    capacity=st.number_input('Inspection capacity',min_value=1,max_value=30,value=20,key='dashboard_capacity')
info=overview(farm,diagnoses,rain,threshold)
counts=info['counts']
a,b,c,d,e=st.columns(5)
a.metric('Farm cells',info['cells'])
b.metric('Infected zones',info['total_zones'])
c.metric('High priority',info['high_priority'])
d.metric('Needs manual review',info['manual_review'])
e.metric('Obstacles',counts['obstacle'])

st.subheader('Your guided AI workflow')
steps=[
    ('1. Design the field','app.py','Farm Designer'),
    ('2. Classify a leaf','pages/9_Model_Comparison.py','MobileNetV2 comparison'),
    ('3. Review advisory','pages/10_Smart_Treatment.py','Smart Treatment'),
    ('4. Compare routes','pages/3_Mission_Planner.py','Mission Planner'),
    ('5. Execute the mission','pages/4_Virtual_Rover.py','Virtual Rover'),
]
columns=st.columns(5)
for col,(heading,target,label) in zip(columns,steps):
    with col:
        st.markdown('**'+heading+'**')
        st.page_link(target,label='Open '+label,icon='➡️',use_container_width=True)
st.divider()

left,right=st.columns([1.55,1],gap='large')
with left:
    st.subheader('🗺 Farm & diagnosed zones')
    st.plotly_chart(farm_figure(farm),use_container_width=True)
with right:
    st.subheader('🩺 Inspection priorities')
    if info['plans']:
        rows=[{'Row':p.row,'Column':p.column,'Severity':p.severity,'Disease':p.disease,
               'Probability':f'{p.probability:.1%}' if p.probability is not None else '—',
               'Manual review':'Yes' if p.manual_review else 'No'} for p in info['plans']]
        st.dataframe(rows,hide_index=True,use_container_width=True)
        if info['manual_review']:
            st.warning(f"{info['manual_review']} zone(s) require manual disease verification. Do not treat uncertain predictions as confirmed diagnoses.")
        if rain: st.info('Rain restriction active: defer spraying decisions.')
    else:
        st.info('No infected zones. Mark a zone in Farm Designer or assign an image prediction.')
    st.subheader('📊 Disease class distribution')
    known=[p.disease for p in info['plans'] if p.disease!='Unknown']
    if known:
        from collections import Counter
        disease_counts=Counter(known)
        fig=go.Figure(go.Bar(x=list(disease_counts.keys()),y=list(disease_counts.values()),marker_color='#25965c'))
        fig.update_layout(height=255,margin=dict(l=10,r=10,t=8,b=30),yaxis_title='Zones',paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig,use_container_width=True)
    else: st.caption('Assign a leaf prediction to a zone to populate this chart.')

st.divider()
st.subheader('🧭 Integrated mission readiness')
st.caption('Generate a complete obstacle-aware multi-zone mission returning to base. The battery calculations are simulated assumptions.')
if st.button('⚡ Calculate complete mission',type='primary',use_container_width=True):
    with st.spinner('Computing mission and checking feasibility...'):
        result,check=prepare_mission(farm,planner,rate,int(capacity),float(reserve))
    st.session_state.dashboard_result=result
    st.session_state.dashboard_check=check
    st.session_state.dashboard_signature=(repr(farm.to_dict()),planner,rate,int(capacity),reserve)

signature=(repr(farm.to_dict()),planner,rate,int(capacity),reserve)
result=st.session_state.get('dashboard_result')
check=st.session_state.get('dashboard_check')
if result and st.session_state.get('dashboard_signature')!=signature:
    st.info('The farm or mission settings changed. Calculate the mission again.')
elif result and not result.found:
    st.error('No feasible route was generated: '+result.message)
elif result and check:
    x,y,z,w=st.columns(4)
    x.metric('Route steps',check.steps)
    y.metric('Projected battery',f'{check.estimated_battery_end:.1f}%')
    z.metric('Zones to inspect',info['total_zones'])
    w.metric('Planner runtime',f'{result.elapsed_ms:.1f} ms')
    if check.feasible:
        st.success('Preflight passed: all marked infected zones are visited, route returns to base, and battery/capacity constraints are satisfied.')
    else:
        st.error('Preflight blocked: '+'; '.join(check.issues))
    route_fig=farm_figure(farm)
    route_fig.add_trace(go.Scatter(x=[c+1 for r,c in result.path],y=[r+1 for r,c in result.path],
                                   mode='lines',name='Mission route',line=dict(color='#078448',width=4)))
    st.plotly_chart(route_fig,use_container_width=True)
    report={
        'generated_at_utc':datetime.now(timezone.utc).isoformat(),
        'farm':farm.name,'algorithm':result.algorithm,'preflight_passed':check.feasible,
        'issues':list(check.issues),'route_steps':check.steps,
        'projected_remaining_battery_pct':check.estimated_battery_end,
        'zones':[asdict(p) for p in info['plans']],
        'route':[{'row':r+1,'column':c+1} for r,c in result.path],
        'disclaimer':'Planning and battery estimates are simulated; disease predictions are experimental.'
    }
    st.download_button('⬇ Download integrated mission JSON',json.dumps(report,indent=2),
                       'agroroute_integrated_mission.json','application/json')
    if check.feasible:
        if st.button('🚜 Send this route to Virtual Rover',use_container_width=True):
            from agroroute.rover import RoverState
            st.session_state.rover_scenario=str(farm.to_dict())
            st.session_state.rover_mission=result
            st.session_state.rover_state=RoverState(result.path,capacity=int(capacity))
            st.session_state.rover_playing=False
            st.session_state.rover_preflight=check
            # Virtual Rover has independent settings: it will revalidate using the settings shown there.
            st.switch_page('pages/4_Virtual_Rover.py')
