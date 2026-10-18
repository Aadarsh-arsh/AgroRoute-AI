import streamlit as st
from agroroute.learning import train_demo,image_features
st.set_page_config(page_title='AgroRoute | AI Learning',page_icon='🧠',layout='wide')
st.title('🧠 Machine Learning Laboratory')
st.warning('The bundled Decision Tree and K-Means demonstration uses SYNTHETIC feature vectors, not actual plant-disease training data. It is NOT a validated disease detector.')
st.subheader('Unit 5: Decision Tree + K-Means')
if st.button('Train and evaluate synthetic example',type='primary'):
    with st.spinner('Training educational models...'):
        result=train_demo()
    st.metric('Synthetic held-out accuracy',f"{result['accuracy']:.1%}")
    st.write('Confusion matrix',result['confusion'])
    st.write('K-Means cluster sizes',result['clusters'])
    st.caption('Do not report these metrics as real crop disease performance.')
st.divider()
st.subheader('Leaf image feature extractor')
upload=st.file_uploader('Upload a leaf image (JPG/PNG)',type=['jpg','jpeg','png'])
if upload:
    st.image(upload,caption='Uploaded image',width=280)
    try:
        features=image_features(upload.getvalue())
        st.write({'RGB means':features[:3].round(3).tolist(),'RGB standard deviations':features[3:6].round(3).tolist(),'Green pixel fraction':round(float(features[6]),3),'Dark pixel fraction':round(float(features[7]),3)})
        st.info('Features extracted. A real disease classifier requires a labeled dataset, training, held-out evaluation and saved model. No diagnosis is made here.')
    except Exception as e:st.error(f'Could not read image: {e}')
