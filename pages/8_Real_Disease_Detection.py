"""Real-data supervised learning and explicit zone assignment."""
import io
import streamlit as st
import pandas as pd
from agroroute.farm import demo_farm
from agroroute.real_learning import collect_dataset,train_real,predict
st.set_page_config(page_title='AgroRoute | Real Disease Data',page_icon='🍅',layout='wide')
st.title('🍅 Plant Disease Detection — Real Dataset Laboratory')
st.info('This module trains a Decision Tree on YOUR labeled images. No dataset or pretrained model is bundled. Predictions are experimental and are not verified agricultural diagnoses.')
st.markdown('**Dataset format:** `data/plant_leaves/Healthy/*.jpg`, `data/plant_leaves/Early_blight/*.jpg`, `data/plant_leaves/Late_blight/*.jpg` (at least 5 images per class).')
folder=st.text_input('Dataset directory (relative to project or absolute)',value='data/plant_leaves')
limit=st.slider('Maximum images per class',20,1000,200,20)
if st.button('Train Decision Tree and evaluate',type='primary'):
    try:
        with st.spinner('Reading images, extracting features and training...'):
            X,y,errors=collect_dataset(folder,limit)
            result=train_real(X,y)
        st.session_state.real_model=result['model']
        st.session_state.real_metrics={k:v for k,v in result.items() if k!='model'}
        st.success(f"Trained on {result['n_train']} images; evaluated on {result['n_test']} held-out images.")
        if errors:st.warning(f'Skipped {len(errors)} unreadable files.')
    except Exception as e:st.error(f'Training failed: {e}')
metrics=st.session_state.get('real_metrics')
if metrics:
    a,b,c=st.columns(3)
    a.metric('Held-out accuracy',f"{metrics['accuracy']:.1%}")
    b.metric('Test images',metrics['n_test'])
    c.metric('K-Means ARI (training)',f"{metrics['cluster_ari_train']:.3f}")
    st.caption('ARI compares unsupervised K-Means clusters against training labels; clusters are not disease predictions. This is an educational evaluation, not field validation.')
    st.write('Class confusion matrix (true rows, predicted columns):')
    st.dataframe(pd.DataFrame(metrics['confusion'],index=metrics['classes'],columns=metrics['classes']))
    st.dataframe(pd.DataFrame(metrics['report']).T)
st.divider()
st.subheader('Classify leaf and link to a farm zone')
file=st.file_uploader('Upload a leaf photo',type=['jpg','jpeg','png','webp'])
if file:
    st.image(file,width=270)
    if 'real_model' not in st.session_state:
        st.warning('Train a model with a labeled dataset first. No diagnosis is available yet.')
    else:
        try:
            label,confidence=predict(st.session_state.real_model,file.getvalue())
            st.write(f'**Predicted class:** {label}  ·  **Model probability:** {confidence:.1%}')
            st.caption('Model probability is not proof of correctness or a calibrated confidence estimate.')
            farm=st.session_state.setdefault('farm',demo_farm())
            targets=[(r,c) for r in range(farm.rows) for c in range(farm.cols) if farm.cells[r][c]!='obstacle' and (r,c)!=farm.rover]
            chosen=st.selectbox('Associate this image with a farm cell',targets,format_func=lambda z:f'Row {z[0]+1}, Column {z[1]+1}')
            severity=st.selectbox('Observed severity (manual assessment)',['Low','Medium','High'],index=1)
            st.caption('Severity is supplied by the user; the classifier does not estimate severity.')
            if st.button('Mark selected cell as infected'):
                farm.paint(*chosen,'infected',severity)
                st.session_state.revision=st.session_state.get('revision',0)+1
                st.session_state.setdefault('zone_diagnoses',{})[farm.key(*chosen)]={'class':label,'probability':confidence,'severity':severity}
                st.success('Zone updated. Open Farm Designer or Mission Planner to view and plan a route.')
        except Exception as exc:st.error(f'Prediction or zone assignment failed: {exc}')
