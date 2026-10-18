import streamlit as st
from agroroute.expert import forward_chain,backward_chain
st.set_page_config(page_title='AgroRoute | Expert System',page_icon='📚',layout='wide')
st.title('📚 Agricultural Expert System')
st.caption('Unit 3 + Unit 6 · Rule-based inference with visible explanation traces; educational rules only.')
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
    st.json(result.facts)
    st.subheader('Inference trace')
    for item in result.trace:st.write('• '+item)
    goal=st.selectbox('Backward-chain a goal',['needs_inspection','dispatch_allowed','spraying_allowed'])
    if st.button('Check goal'):
        success,trace=backward_chain(result,goal)
        st.write('Goal supported:',success)
        st.write('Reasoning:',trace)
st.warning('Never use these demonstration rules as instructions for chemical application. Verify local agricultural recommendations and product labels.')
