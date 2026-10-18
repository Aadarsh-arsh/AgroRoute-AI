import streamlit as st
from agroroute.expert import forward_chain,backward_chain
from agroroute.ui import apply_theme, page_hero, info_strip, footer
st.set_page_config(page_title='AgroRoute | Expert System',page_icon='📚',layout='wide')
apply_theme()
page_hero('Agricultural Expert System', 'Investigate transparent agricultural rules with forward and backward chaining, supporting visible reasoning traces.', icon='📚', eyebrow='UNIT 3 + UNIT 6 • REASONING & EXPERT SYSTEMS')
info_strip('Educational inference rules only  •  Do not use the rules as authorization for chemical treatment')
a,b=st.columns(2)
with a:
    disease=st.selectbox('Suspected disease',['Unknown','Healthy','Early Blight','Late Blight','Bacterial Spot','Leaf Mold'])
    severity=st.selectbox('Severity (user assessed)',['Low','Medium','High'])
with b:
    rain=st.checkbox('Heavy rain expected')
    accessible=st.checkbox('Zone accessible',value=True)
if st.button('Run forward chaining',type='primary'):
    st.session_state.inference=forward_chain(disease,severity,rain,accessible)
if 'inference' in st.session_state:
    result=st.session_state.inference
    st.subheader('Derived facts')
    st.dataframe([{'Fact':key,'Value':str(value)} for key,value in result.facts.items()],
                 hide_index=True,use_container_width=True)
    with st.expander('View raw inference facts (JSON)'):
        st.json(result.facts)
    st.subheader('Inference trace')
    for idx,item in enumerate(result.trace,start=1):
        st.markdown(f'**{idx}.** {item}')
    goal=st.selectbox('Backward-chain a goal',['needs_inspection','dispatch_allowed','spraying_allowed'])
    if st.button('Check goal'):
        success,trace=backward_chain(result,goal)
        st.write('Goal supported:',success)
        st.write('Reasoning:',trace)
st.warning('Never use these demonstration rules as instructions for chemical application. Verify local agricultural recommendations and product labels.')

footer()
