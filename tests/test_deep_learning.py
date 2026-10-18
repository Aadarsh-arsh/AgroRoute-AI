import tempfile
import unittest
from pathlib import Path
from PIL import Image
from agroroute.deep_learning import image_manifest,split_manifest

class TestDeepLearning(unittest.TestCase):
    def test_manifest_and_split_no_overlap(self):
        with tempfile.TemporaryDirectory() as d:
            for label in ['Healthy','Late_blight']:
                folder=Path(d)/label;folder.mkdir()
                for i in range(20):Image.new('RGB',(12,12),(i,30,20)).save(folder/f'{i:02}.png')
            rows=image_manifest(d)
            split=split_manifest(rows)
            sets=[{p for p,_ in split[k]} for k in ('train','val','test')]
            self.assertEqual(sum(map(len,sets)),40)
            self.assertFalse(sets[0]&sets[1] or sets[0]&sets[2] or sets[1]&sets[2])
            for group in split.values():
                self.assertEqual(set(label for _,label in group),{'Healthy','Late_blight'})
    def test_insufficient_images(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d)/'Healthy').mkdir()
            with self.assertRaises(ValueError):image_manifest(d)
if __name__=='__main__':unittest.main()
