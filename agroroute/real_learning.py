"""Real labeled image dataset workflow; no bundled/pretrained diagnosis claims."""
from pathlib import Path
from io import BytesIO
import numpy as np
from PIL import Image

SUPPORTED={'.jpg','.jpeg','.png','.webp'}

def extract_features(data: bytes):
    im=Image.open(BytesIO(data)).convert('RGB').resize((96,96))
    a=np.asarray(im,dtype=np.float32)/255.
    from PIL import Image as PILImage
    hsv=np.asarray(im.convert('HSV'),dtype=np.float32)/255.
    mean=a.mean((0,1)); std=a.std((0,1))
    hmean=hsv.mean((0,1)); hstd=hsv.std((0,1))
    gray=a.mean(2)
    dx=np.abs(np.diff(gray,axis=1)).mean(); dy=np.abs(np.diff(gray,axis=0)).mean()
    dark=(gray<.3).mean(); yellow=((a[:,:,0]>.4)&(a[:,:,1]>.4)&(a[:,:,2]<.35)).mean()
    return np.r_[mean,std,hmean,hstd,dx,dy,dark,yellow].astype(np.float32)

def collect_dataset(root, limit_per_class=300):
    """Root/class_name/image.jpg. Deterministic and bounded to keep UI responsive."""
    root=Path(root)
    if not root.is_dir(): raise ValueError('Dataset folder does not exist.')
    classes=sorted(p for p in root.iterdir() if p.is_dir())
    if len(classes)<2: raise ValueError('Provide at least two class folders.')
    X=[]; y=[]; errors=[]
    for folder in classes:
        files=sorted(p for p in folder.rglob('*') if p.is_file() and p.suffix.lower() in SUPPORTED)
        for file in files[:limit_per_class]:
            try:
                X.append(extract_features(file.read_bytes())); y.append(folder.name)
            except (OSError,ValueError) as exc: errors.append(f'{file.name}: {exc}')
    if not X: raise ValueError('No readable images found.')
    labels,counts=np.unique(y,return_counts=True)
    if len(labels)<2 or min(counts)<5: raise ValueError('Each class needs at least 5 readable images.')
    return np.stack(X),np.asarray(y),errors

def train_real(X,y,seed=42):
    from sklearn.model_selection import train_test_split
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.cluster import KMeans
    from sklearn.metrics import accuracy_score,classification_report,confusion_matrix,adjusted_rand_score
    X=np.asarray(X);y=np.asarray(y)
    if X.ndim!=2 or len(X)!=len(y):raise ValueError('Invalid training data')
    classes,counts=np.unique(y,return_counts=True)
    if len(classes)<2 or min(counts)<5:raise ValueError('Need at least two classes with five images each')
    Xtr,Xte,ytr,yte=train_test_split(X,y,test_size=.25,random_state=seed,stratify=y)
    model=DecisionTreeClassifier(max_depth=8,min_samples_leaf=2,random_state=seed).fit(Xtr,ytr)
    pred=model.predict(Xte)
    cluster=KMeans(n_clusters=len(classes),n_init=10,random_state=seed).fit(Xtr)
    return {'model':model,'accuracy':float(accuracy_score(yte,pred)),
            'report':classification_report(yte,pred,output_dict=True,zero_division=0),
            'confusion':confusion_matrix(yte,pred,labels=classes).tolist(),
            'classes':classes.tolist(),'n_train':len(Xtr),'n_test':len(Xte),
            'cluster_ari_train':float(adjusted_rand_score(ytr,cluster.labels_))}

def predict(model,content):
    feat=extract_features(content).reshape(1,-1)
    label=str(model.predict(feat)[0]); proba=model.predict_proba(feat)[0]
    return label,float(np.max(proba))
