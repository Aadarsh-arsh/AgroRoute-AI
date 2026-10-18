"""Optional machine-learning tools; require scikit-learn and Pillow."""
from io import BytesIO
import numpy as np

def image_features(image_bytes: bytes):
    from PIL import Image
    img=Image.open(BytesIO(image_bytes)).convert('RGB').resize((96,96))
    a=np.asarray(img,dtype=float)/255.0
    means=a.mean(axis=(0,1)); stds=a.std(axis=(0,1))
    green=(a[:,:,1]>a[:,:,0]*1.1)&(a[:,:,1]>a[:,:,2]*1.05)
    dark=(a.mean(axis=2)<0.3)
    return np.r_[means,stds,green.mean(),dark.mean()]

def train_demo(seed=42):
    """Synthetic teaching data ONLY: never represent accuracy as real-world diagnosis."""
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.cluster import KMeans
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score,classification_report,confusion_matrix
    rng=np.random.default_rng(seed)
    x=np.vstack([rng.normal(loc=0.35,scale=.09,size=(100,8)),rng.normal(loc=.65,scale=.09,size=(100,8))]).clip(0,1)
    y=np.array(['Illustrative A']*100+['Illustrative B']*100)
    train_x,test_x,train_y,test_y=train_test_split(x,y,test_size=.25,stratify=y,random_state=seed)
    model=DecisionTreeClassifier(max_depth=4,random_state=seed).fit(train_x,train_y)
    pred=model.predict(test_x)
    cluster=KMeans(n_clusters=2,random_state=seed,n_init=10).fit(x)
    return {'accuracy':accuracy_score(test_y,pred),'report':classification_report(test_y,pred,output_dict=True), 'confusion':confusion_matrix(test_y,pred).tolist(),'clusters':np.bincount(cluster.labels_).tolist(),'x':x,'labels':cluster.labels_}
