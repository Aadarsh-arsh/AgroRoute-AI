"""Saved MobileNetV2 model results and integrated farm-zone prediction."""
from pathlib import Path
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from agroroute.farm import demo_farm
from agroroute.deep_learning import predict_image

from agroroute.ui import apply_theme, page_hero, info_strip, footer
st.set_page_config(page_title='AgroRoute | Model Comparison',page_icon='🧠',layout='wide')
apply_theme()
page_hero('Model Performance Studio', 'Compare MobileNetV2 and Decision Tree on a shared held-out test split, inspect training history and assign image predictions to zones.', icon='📈', eyebrow='MODEL EVALUATION • TOMATO DISEASES')
info_strip('Model results are loaded from saved training artifacts. Use train_mobilenet.py in the terminal to retrain.')
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
st.subheader('Model accuracy comparison')
comparison=pd.DataFrame({'Model':['Decision Tree','MobileNetV2'],'Accuracy (%)':[100*result['decision_tree']['accuracy'],100*result['mobilenet']['accuracy']]})
chart=px.bar(comparison,y='Model',x='Accuracy (%)',orientation='h',text='Accuracy (%)',color='Model',color_discrete_map={'Decision Tree':'#9bb9a4','MobileNetV2':'#218a56'})
chart.update_traces(texttemplate='%{text:.1f}%',textposition='inside',insidetextfont=dict(color='white',size=15))
chart.update_layout(height=250,showlegend=False,margin=dict(l=12,r=25,t=20,b=25),xaxis_range=[0,100],
  xaxis=dict(title='Held-out test accuracy (%)',gridcolor='#e5efe8',ticksuffix='%'),
  yaxis=dict(title=None,categoryorder='array',categoryarray=['MobileNetV2','Decision Tree']),
  paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='#ffffff',font=dict(color='#244e34',size=12),bargap=.36)
st.plotly_chart(chart,use_container_width=True)
st.caption('Both models were evaluated on the same held-out split. Model probability is not a calibrated confidence guarantee.')

st.download_button('⬇ Download model evaluation (JSON)',json.dumps(result,indent=2),file_name='agroroute_model_evaluation.json',mime='application/json')
for key,name in [('mobilenet','MobileNetV2'),('decision_tree','Decision Tree')]:
    with st.expander(f'{name} — Confusion matrix and classification report'):
        matrix=pd.DataFrame(result[key]['confusion'],index=result['classes'],columns=result['classes'])
        heat=go.Figure(go.Heatmap(z=matrix.values,x=result['classes'],y=result['classes'],
                    colorscale=[[0,'#eef7ef'],[1,'#166f45']],showscale=True,
                    text=matrix.values,texttemplate='%{text}',textfont=dict(size=13)))
        heat.update_layout(height=340,margin=dict(l=10,r=10,t=18,b=45),
                    xaxis=dict(title='Predicted label'),yaxis=dict(title='True label',autorange='reversed'),
                    paper_bgcolor='rgba(0,0,0,0)',font=dict(color='#21472f'))
        st.plotly_chart(heat,use_container_width=True)
        st.dataframe(pd.DataFrame(result[key]['report']).T,use_container_width=True)

st.subheader('Training history')
history=pd.DataFrame(result['history'])
history.index=history.index+1
history.index.name='Epoch'
st.line_chart(history)
st.caption('Training/validation metrics are displayed per epoch; compare trends rather than only the final values.')
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

footer()
