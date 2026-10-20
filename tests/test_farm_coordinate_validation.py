import unittest

from agroroute.farm import Farm


class FarmCoordinateValidationTests(unittest.TestCase):
    def test_origin_is_in_bounds(self):
        farm = Farm(rows=5, cols=5)
        self.assertTrue(farm.in_bounds(0, 0))

    def test_last_cell_is_in_bounds(self):
        farm = Farm(rows=5, cols=5)
        self.assertTrue(farm.in_bounds(4, 4))

    def test_negative_coordinates_are_out_of_bounds(self):
        farm = Farm(rows=5, cols=5)
        self.assertFalse(farm.in_bounds(-1, 0))
        self.assertFalse(farm.in_bounds(0, -1))

    def test_coordinates_past_grid_are_out_of_bounds(self):
        farm = Farm(rows=5, cols=5)
        self.assertFalse(farm.in_bounds(5, 0))
        self.assertFalse(farm.in_bounds(0, 5))


if __name__ == "__main__":
    unittest.main()
