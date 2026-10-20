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
    def test_parse_key_valid_coordinates(self):
        self.assertEqual(Farm.parse_key('3,7'), (3, 7))
        self.assertEqual(Farm.parse_key(' 4, 9 '), (4, 9))

    def test_parse_key_rejects_invalid_coordinates(self):
        invalid_keys = ('3', '3,4,5', 'row,col', '', '3,')
        for key in invalid_keys:
            with self.subTest(key=key):
                with self.assertRaises(ValueError):
                    Farm.parse_key(key)
    def test_counts_update_after_painting(self):
        farm = Farm()
        farm.paint(1, 1, 'obstacle')
        farm.paint(2, 2, 'infected', 'High')
        self.assertEqual(farm.counts()['obstacle'], 1)
        self.assertEqual(farm.counts()['infected'], 1)
        self.assertEqual(farm.counts()['crop'], 142)

if __name__ == '__main__':
    unittest.main()
