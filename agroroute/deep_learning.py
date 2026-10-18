"""Optional MobileNetV2 pipeline. TensorFlow is imported lazily."""
from pathlib import Path
import json
import numpy as np
from PIL import Image

EXTS={'.jpg','.jpeg','.png','.webp'}
IMAGE_SIZE=(160,160)

def image_manifest(root,limit=1000):
    root=Path(root)
    if not root.is_dir(): raise ValueError(f'Dataset directory not found: {root}')
    folders=sorted(p for p in root.iterdir() if p.is_dir())
    rows=[]
    for folder in folders:
        files=sorted(p for p in folder.rglob('*') if p.is_file() and p.suffix.lower() in EXTS)
        rows.extend((str(p),folder.name) for p in files[:limit])
    if len(folders)<2 or any(sum(label==f.name for _,label in rows)<10 for f in folders):
        raise ValueError('Need at least two classes, each with 10 or more images')
    return rows

def split_manifest(rows,seed=42):
    """Fixed stratified 60/15/25 train/validation/test split, shared by models."""
    from sklearn.model_selection import train_test_split
    paths,labels=zip(*rows)
    trainval,test=train_test_split(np.arange(len(rows)),test_size=.25,random_state=seed,stratify=labels)
    train,val=train_test_split(trainval,test_size=.20,random_state=seed,stratify=np.array(labels)[trainval])
    return {'train':[rows[i] for i in train], 'val':[rows[i] for i in val], 'test':[rows[i] for i in test]}

def load_images(rows,classes):
    X=[];y=[]
    for path,label in rows:
        try:
            with Image.open(path) as img:
                X.append(np.asarray(img.convert('RGB').resize(IMAGE_SIZE),dtype=np.float32))
                y.append(classes.index(label))
        except (OSError,ValueError) as e:
            raise ValueError(f'Cannot read {path}: {e}') from e
    return np.stack(X),np.asarray(y,dtype=np.int32)

def build_model(n_classes,pretrained=True):
    import tensorflow as tf
    weights='imagenet' if pretrained else None
    backbone=tf.keras.applications.MobileNetV2(input_shape=(*IMAGE_SIZE,3),include_top=False,weights=weights)
    backbone.trainable=False
    inputs=tf.keras.Input(shape=(*IMAGE_SIZE,3))
    x=tf.keras.applications.mobilenet_v2.preprocess_input(inputs)
    x=backbone(x,training=False)
    x=tf.keras.layers.GlobalAveragePooling2D()(x)
    x=tf.keras.layers.Dropout(.25)(x)
    outputs=tf.keras.layers.Dense(n_classes,activation='softmax')(x)
    model=tf.keras.Model(inputs,outputs)
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),loss='sparse_categorical_crossentropy',metrics=['accuracy'])
    return model

def train_and_evaluate(root,model_dir='models/mobile_net_v2',epochs=8,batch_size=16,limit=1000,seed=42,pretrained=True):
    import tensorflow as tf
    from sklearn.metrics import accuracy_score,classification_report,confusion_matrix
    from sklearn.tree import DecisionTreeClassifier
    from .real_learning import extract_features
    tf.keras.utils.set_random_seed(seed)
    rows=image_manifest(root,limit)
    splits=split_manifest(rows,seed)
    classes=sorted(set(label for _,label in rows))
    xtr,ytr=load_images(splits['train'],classes)
    xv,yv=load_images(splits['val'],classes)
    xt,yt=load_images(splits['test'],classes)
    model=build_model(len(classes),pretrained=pretrained)
    callbacks=[tf.keras.callbacks.EarlyStopping(monitor='val_loss',patience=3,restore_best_weights=True)]
    hist=model.fit(xtr,ytr,validation_data=(xv,yv),epochs=epochs,batch_size=batch_size,callbacks=callbacks,verbose=0)
    predicted=np.argmax(model.predict(xt,batch_size=batch_size,verbose=0),axis=1)
    # Same split for a fair comparison. Decision Tree features are computed on original image bytes.
    def feature_set(part):
        return np.stack([extract_features(Path(path).read_bytes()) for path,_ in part])
    tree=DecisionTreeClassifier(max_depth=8,min_samples_leaf=2,random_state=seed)
    tree.fit(feature_set(splits['train']),ytr)
    tree_pred=tree.predict(feature_set(splits['test']))
    result={'classes':classes,'split_counts':{k:len(v) for k,v in splits.items()},
        'mobilenet':{'accuracy':float(accuracy_score(yt,predicted)), 'confusion':confusion_matrix(yt,predicted,labels=range(len(classes))).tolist(), 'report':classification_report(yt,predicted,target_names=classes,output_dict=True,zero_division=0)},
        'decision_tree':{'accuracy':float(accuracy_score(yt,tree_pred)), 'confusion':confusion_matrix(yt,tree_pred,labels=range(len(classes))).tolist(), 'report':classification_report(yt,tree_pred,target_names=classes,output_dict=True,zero_division=0)},
        'history':{k:[float(v) for v in values] for k,values in hist.history.items()},
        'seed':seed,'pretrained':pretrained,'epochs_run':len(hist.history['loss'])}
    out=Path(model_dir);out.mkdir(parents=True,exist_ok=True)
    model.save(out/'model.keras')
    (out/'metadata.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    return result

def predict_image(model_dir,content):
    import tensorflow as tf
    from io import BytesIO
    folder=Path(model_dir)
    metadata=json.loads((folder/'metadata.json').read_text(encoding='utf-8'))
    model=tf.keras.models.load_model(folder/'model.keras')
    with Image.open(BytesIO(content)) as img:
        x=np.asarray(img.convert('RGB').resize(IMAGE_SIZE),dtype=np.float32)[None,...]
    probabilities=model.predict(x,verbose=0)[0]
    i=int(np.argmax(probabilities))
    return metadata['classes'][i],float(probabilities[i]),dict(zip(metadata['classes'],[float(p) for p in probabilities]))
