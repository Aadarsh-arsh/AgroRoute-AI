import streamlit as st
from agroroute.farm import demo_farm
from agroroute.mission import infected_zones
from agroroute.scheduler import schedule
st.set_page_config(page_title='AgroRoute | CSP',page_icon='📅',layout='wide')
st.title('📅 CSP Inspection Scheduler')
st.caption('Unit 4 · Backtracking + Minimum Remaining Values (MRV) · one rover, non-overlapping task slots')
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
        st.dataframe([{'Zone':k,'Start slot':v,'End slot':v+duration} for k,v in sorted(result.assignments.items(),key=lambda x:x[1])],hide_index=True,use_container_width=True)
    else:st.error('No feasible schedule. Increase available slots or reduce task duration.')
st.caption('This simplified CSP does not yet include travel-time constraints. Route scheduling integration remains a future enhancement.')
