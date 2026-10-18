import unittest
from agroroute.farm import Farm, demo_farm

class TestFarm(unittest.TestCase):
    def test_default(self):
        farm = Farm()
        self.assertEqual(farm.counts()['crop'], 144)
    def test_paint_and_roundtrip(self):
        farm = Farm()
        farm.paint(2,3,'infected','High')
        restored = Farm.from_dict(farm.to_dict())
        self.assertEqual(restored.severities['2,3'],'High')
    def test_block_rover_cell(self):
        farm = Farm()
        with self.assertRaises(ValueError):
            farm.paint(0,0,'obstacle')
    def test_rover_cannot_enter_obstacle(self):
        farm = Farm()
        farm.paint(1,1,'obstacle')
        with self.assertRaises(ValueError):
            farm.paint(1,1,'rover')
    def test_demo(self):
        self.assertEqual(demo_farm().counts()['infected'],4)
    def test_bad_import(self):
        with self.assertRaises(ValueError):
            Farm.from_dict({'schema_version':2})

if __name__ == '__main__':
    unittest.main()
