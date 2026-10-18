"""Saved MobileNetV2 model results and integrated farm-zone prediction."""
from pathlib import Path
import json
import pandas as pd
import plotly.express as px
import streamlit as st
from agroroute.farm import demo_farm
from agroroute.deep_learning import predict_image

st.set_page_config(page_title='AgroRoute | Model Comparison',page_icon='🧠',layout='wide')
st.title('🧠 MobileNetV2 vs Decision Tree')
st.caption('Train models using train_mobilenet.py in the VS Code terminal. This page reads the saved results without retraining on every reload.')
folder=Path('models/mobile_net_v2')
metadata=folder/'metadata.json'
if not metadata.exists() or not (folder/'model.keras').exists():
    st.warning('No trained MobileNetV2 model found. Run: python train_mobilenet.py --data data/plant_leaves --epochs 8')
    st.stop()
result=json.loads(metadata.read_text(encoding='utf-8'))
st.success(f"Model loaded. Shared split: {result['split_counts']['train']} training, {result['split_counts']['val']} validation, {result['split_counts']['test']} testing images.")
c1,c2=st.columns(2)
c1.metric('MobileNetV2 test accuracy',f"{result['mobilenet']['accuracy']:.1%}")
c2.metric('Decision Tree test accuracy',f"{result['decision_tree']['accuracy']:.1%}")
st.subheader('Model comparison')
comparison=pd.DataFrame({'Model':['Decision Tree','MobileNetV2'],'Accuracy (%)':[100*result['decision_tree']['accuracy'],100*result['mobilenet']['accuracy']]})
chart=px.bar(comparison,x='Model',y='Accuracy (%)',text='Accuracy (%)',color='Model',color_discrete_sequence=['#789b83','#178650'])
chart.update_traces(texttemplate='%{text:.1f}%',textposition='outside')
chart.update_layout(height=330,showlegend=False,margin=dict(l=10,r=10,t=15,b=10),yaxis_range=[0,100],paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)')
st.plotly_chart(chart,use_container_width=True)
st.download_button('⬇ Download model evaluation (JSON)',json.dumps(result,indent=2),file_name='agroroute_model_evaluation.json',mime='application/json')
for key,name in [('mobilenet','MobileNetV2'),('decision_tree','Decision Tree')]:
    with st.expander(f'{name} — Confusion matrix and classification report'):
        st.dataframe(pd.DataFrame(result[key]['confusion'],index=result['classes'],columns=result['classes']))
        st.dataframe(pd.DataFrame(result[key]['report']).T)
st.subheader('Training history')
st.line_chart(pd.DataFrame(result['history']))
st.divider()
st.subheader('Classify an image and assign a farm zone')
st.caption('These are experimental model outputs, not validated field diagnoses. Disease severity must be assessed separately.')
upload=st.file_uploader('Upload a tomato leaf',type=['jpg','jpeg','png','webp'])
if upload:
    st.image(upload,width=280)
    try:
        label,prob,all_probs=predict_image(folder,upload.getvalue())
        st.write(f'**Predicted:** {label} · **Uncalibrated model probability:** {prob:.1%}')
        st.bar_chart(pd.Series(all_probs,name='Model probability'))
        if prob < 0.65:
            st.warning('Low model probability: request manual review before using this prediction for treatment decisions.')
        farm=st.session_state.setdefault('farm',demo_farm())
        available=[(r,c) for r in range(farm.rows) for c in range(farm.cols) if farm.cells[r][c]!='obstacle' and (r,c)!=farm.rover]
        chosen=st.selectbox('Select associated field cell',available,format_func=lambda z:f'Row {z[0]+1}, Column {z[1]+1}')
        severity=st.selectbox('Observed severity (manual)',['Low','Medium','High'])
        if st.button('Assign diagnosis to zone',type='primary'):
            if label.lower()=='healthy':
                st.warning('Healthy prediction: no infected zone was created.')
            else:
                farm.paint(*chosen,'infected',severity)
                st.session_state.revision=st.session_state.get('revision',0)+1
                st.session_state.setdefault('zone_diagnoses',{})[farm.key(*chosen)]={'class':label,'probability':prob,'severity':severity,'model':'MobileNetV2'}
                st.success('Infected zone added. Open Mission Planner to calculate a route.')
    except Exception as exc:
        st.error(f'Prediction failed: {exc}')
