"""Integrated, conservative agronomy decision-support and route feasibility dashboard."""
import json
from datetime import datetime, timezone
import streamlit as st
import plotly.graph_objects as go
from agroroute.farm import demo_farm
from agroroute.mission import mission
from agroroute.treatment import build_zone_plans, mission_feasibility

from agroroute.ui import apply_theme, page_hero, info_strip, footer
st.set_page_config(page_title='AgroRoute | Smart Treatment',page_icon='🌾',layout='wide')
apply_theme()
page_hero('Smart Treatment & Mission Readiness', 'Translate disease observations into risk-aware inspection plans and check rover mission feasibility before execution.', icon='🌾', eyebrow='EXPERT REVIEW • OPERATIONAL READINESS')
info_strip('Decision support only  •  No pesticide prescriptions, dosage recommendations or spraying authorization')
farm = st.session_state.get('farm',demo_farm())
diagnoses = st.session_state.get('zone_diagnoses',{})
with st.sidebar:
    st.subheader('Planning assumptions')
    rain = st.checkbox('Rain or unsuitable spraying weather',value=False)
    threshold = st.slider('Manual review threshold',0.5,0.95,0.65,0.05)
    planner = st.selectbox('Route planner',['Genetic Algorithm','Nearest Neighbor','Exact Dynamic Programming'])
    battery = st.slider('Current battery (%)',0,100,100)
    per_step = st.slider('Estimated battery consumption per step (%)',0.1,2.0,0.4,0.1)
    reserve = st.slider('Required battery reserve (%)',0,50,15)
    capacity = st.number_input('Available inspection capacity',1,100,20)
plans = build_zone_plans(farm,diagnoses,rain,threshold)
cols = st.columns(3)
cols[0].metric('Affected zones',len(plans))
cols[1].metric('High-priority zones',sum(p.priority=='High' for p in plans))
cols[2].metric('Manual reviews required',sum(p.manual_review for p in plans))
if plans:
    st.subheader('Zone-specific inspection plan')
    st.dataframe([p.to_dict() for p in plans],use_container_width=True,hide_index=True)
    priority_colors={'High':'#c7514b','Medium':'#d98c40','Low':'#6eae85'}
    zone_chart=go.Figure(go.Bar(y=[f'R{p.row} · C{p.column}' for p in plans],
         x=[{'High':3,'Medium':2,'Low':1}[p.priority] for p in plans],orientation='h',
         marker_color=[priority_colors[p.priority] for p in plans],
         text=[p.priority + (' · Verify' if p.manual_review else '') for p in plans],textposition='auto'))
    zone_chart.update_layout(height=max(240,100+42*len(plans)),margin=dict(l=15,r=10,t=20,b=25),
        xaxis=dict(title='Inspection priority',tickvals=[1,2,3],ticktext=['Low','Medium','High'],range=[0,3.5]),
        yaxis=dict(title=None,autorange='reversed'),paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='#ffffff',showlegend=False)
    st.plotly_chart(zone_chart,use_container_width=True)
    st.info('Treatment decisions require field confirmation, local agronomic guidance, and product-label checks. Disease classifications are not verified diagnoses.')
else:
    st.info('No infected zones. Mark zones in Farm Designer or classify a leaf image first.')
st.subheader('Mission readiness')
if st.button('Evaluate proposed mission',type='primary'):
    result = mission(farm,planner)
    if not result.found:
        st.error(result.message)
    else:
        steps = len(result.path)-1
        feasibility = mission_feasibility(steps,float(battery),float(per_step),float(reserve),len(plans),int(capacity))
        a,b,c = st.columns(3)
        a.metric('Planned movement steps',steps)
        b.metric('Estimated battery remaining',f"{feasibility['estimated_remaining_pct']:.1f}%")
        c.metric('Mission readiness','Feasible' if feasibility['feasible'] else 'Needs changes')
        if feasibility['feasible']:
            st.success('Mission satisfies the selected simulation assumptions.')
        else:
            for issue in feasibility['issues']:
                st.warning(issue)
        st.caption(feasibility['note'])
        report = {'created_at_utc':datetime.now(timezone.utc).isoformat(),
                  'farm':farm.name,'algorithm':planner,'steps':steps,
                  'zones':[p.to_dict() for p in plans], 'feasibility':feasibility}
        st.download_button('Download treatment and mission plan (JSON)',
                           json.dumps(report,indent=2),file_name='agroroute_treatment_plan.json',mime='application/json')

footer()
