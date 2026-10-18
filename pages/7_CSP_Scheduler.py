import streamlit as st
import plotly.graph_objects as go
from agroroute.farm import demo_farm
from agroroute.mission import infected_zones
from agroroute.scheduler import schedule
from agroroute.ui import apply_theme, page_hero, info_strip, footer
st.set_page_config(page_title='AgroRoute | CSP',page_icon='📅',layout='wide')
apply_theme()
page_hero('CSP Inspection Scheduler', 'Plan non-overlapping inspection tasks using constraint satisfaction, backtracking and Minimum Remaining Values.', icon='📅', eyebrow='UNIT 4 • CONSTRAINT SATISFACTION')
info_strip('One simulated rover  •  Non-overlapping time slots  •  Travel-time constraints are not included yet')
farm=st.session_state.get('farm',demo_farm())
zones=infected_zones(farm)
slots=st.slider('Available time slots',2,24,12)
duration=st.slider('Inspection duration per zone (slots)',1,4,2)
use_mrv=st.checkbox('Use MRV variable ordering',value=True)
tasks=[{'id':f'Zone ({r+1},{c+1})','duration':duration,'earliest':0,'latest':slots,'priority':{'High':3,'Medium':2,'Low':1}[farm.severities.get(f'{r},{c}','Medium')]} for r,c in zones]
st.write(f'{len(tasks)} inspection tasks found.')
if st.button('Solve schedule',type='primary'):
    result=schedule(tasks,slots,use_mrv)
    st.metric('Backtracking nodes',result.nodes)
    if result.feasible:
        st.success('Feasible inspection schedule found')
        ordered=sorted(result.assignments.items(),key=lambda x:x[1])
        st.dataframe([{'Zone':k,'Start slot':v,'End slot':v+duration} for k,v in ordered],hide_index=True,use_container_width=True)
        timeline=go.Figure(go.Bar(y=[k for k,v in ordered],x=[duration]*len(ordered),
                                 base=[v for k,v in ordered],orientation='h',
                                 marker_color='#248a59',text=[f'Slot {v}–{v+duration}' for k,v in ordered],
                                 textposition='auto'))
        timeline.update_layout(title='Inspection schedule timeline',height=max(250,80+len(ordered)*42),
            margin=dict(l=12,r=15,t=42,b=30),xaxis=dict(title='Simulation time slot',range=[0,slots],dtick=1,gridcolor='#e0ede4'),
            yaxis=dict(title=None,autorange='reversed'),paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='#fff',showlegend=False)
        st.plotly_chart(timeline,use_container_width=True)
    else:st.error('No feasible schedule. Increase available slots or reduce task duration.')
st.caption('This simplified CSP does not yet include travel-time constraints. Route scheduling integration remains a future enhancement.')

footer()
