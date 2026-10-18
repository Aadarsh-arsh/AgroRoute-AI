import unittest
from io import BytesIO
import numpy as np
from PIL import Image
from agroroute.real_learning import extract_features,train_real,predict
class TestRealLearning(unittest.TestCase):
    def test_feature_length(self):
        b=BytesIO();Image.new('RGB',(30,30),(30,150,40)).save(b,format='PNG')
        self.assertEqual(len(extract_features(b.getvalue())),16)
    def test_train_predict(self):
        rng=np.random.default_rng(9)
        X=np.vstack([rng.normal(0,.1,(30,16)),rng.normal(1,.1,(30,16))]);y=np.array(['healthy']*30+['infected']*30)
        result=train_real(X,y)
        self.assertGreaterEqual(result['accuracy'],.8)
        self.assertEqual(len(result['classes']),2)
    def test_invalid_dataset(self):
        with self.assertRaises(ValueError):train_real(np.ones((3,16)),np.array(['a','a','b']))
if __name__=='__main__':unittest.main()
