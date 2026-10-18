import streamlit as st
from agroroute.learning import train_demo,image_features
from agroroute.ui import apply_theme, page_hero, info_strip, footer
st.set_page_config(page_title='AgroRoute | AI Learning',page_icon='🧠',layout='wide')
apply_theme()
page_hero('Machine Learning Laboratory', 'Explore Decision Trees, K-Means clustering and interpretable leaf-image features with educational demonstrations.', icon='🧠', eyebrow='UNIT 5 • SUPERVISED & UNSUPERVISED LEARNING')
st.warning('The bundled Decision Tree and K-Means demonstration uses SYNTHETIC feature vectors, not actual plant-disease training data. It is NOT a validated disease detector.')
st.subheader('Unit 5: Decision Tree + K-Means')
if st.button('Train and evaluate synthetic example',type='primary'):
    with st.spinner('Training educational models...'):
        result=train_demo()
    st.metric('Synthetic held-out accuracy',f"{result['accuracy']:.1%}")
    col_a,col_b=st.columns(2)
    with col_a:
        st.markdown('**Decision Tree confusion matrix**')
        st.dataframe(result['confusion'],use_container_width=True)
    with col_b:
        st.markdown('**K-Means cluster sizes**')
        st.dataframe([{'Cluster':i+1,'Observations':value} for i,value in enumerate(result['clusters'])],hide_index=True,use_container_width=True)
    st.caption('Do not report these metrics as real crop disease performance.')
st.divider()
st.subheader('Leaf image feature extractor')
upload=st.file_uploader('Upload a leaf image (JPG/PNG)',type=['jpg','jpeg','png'])
if upload:
    st.image(upload,caption='Uploaded image',width=280)
    try:
        features=image_features(upload.getvalue())
        a,b=st.columns(2)
        a.metric('Green pixel fraction',f'{float(features[6]):.1%}')
        b.metric('Dark pixel fraction',f'{float(features[7]):.1%}')
        with st.expander('View extracted RGB features'):
            st.json({'RGB means':features[:3].round(3).tolist(),
                     'RGB standard deviations':features[3:6].round(3).tolist()})
        st.info('Features extracted. A real disease classifier requires a labeled dataset, training, held-out evaluation and saved model. No diagnosis is made here.')
    except Exception as e:st.error(f'Could not read image: {e}')

footer()
