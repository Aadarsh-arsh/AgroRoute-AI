import unittest

from agroroute.farm import Farm
from agroroute.pathfinding import search


class PathfindingEdgeCaseTests(unittest.TestCase):
    def test_start_equals_goal_returns_zero_step_path(self):
        farm = Farm(rows=5, cols=5)
        result = search(farm, goal=farm.rover)
        self.assertTrue(result.found)
        self.assertEqual(result.path, [farm.rover])
        self.assertEqual(result.steps, 0)

    def test_unknown_algorithm_is_rejected(self):
        farm = Farm(rows=5, cols=5)
        with self.assertRaises(ValueError):
            search(farm, goal=(4, 4), algorithm="Unknown")

    def test_out_of_bounds_goal_is_rejected(self):
        farm = Farm(rows=5, cols=5)
        with self.assertRaises(ValueError):
            search(farm, goal=(5, 5))

    def test_path_avoids_obstacles(self):
        farm = Farm(rows=5, cols=5)
        farm.paint(0, 1, "obstacle")
        result = search(farm, goal=(0, 2))
        self.assertTrue(result.found)
        self.assertNotIn((0, 1), result.path)


if __name__ == "__main__":
    unittest.main()
