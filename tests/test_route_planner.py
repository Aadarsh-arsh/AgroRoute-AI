import unittest
from agroroute.farm import Farm
from agroroute.route_planner import plan_inspection_route

class RoutePlannerTests(unittest.TestCase):
    def test_empty_targets_returns_start(self):
        farm = Farm(rows=5, cols=5)
        route = plan_inspection_route(farm, targets=[])
        self.assertEqual(route.path, (tuple(farm.rover),))
        self.assertEqual(route.total_steps, 0)

    def test_duplicate_targets_rejected(self):
        farm = Farm(rows=5, cols=5)
        with self.assertRaises(ValueError):
            plan_inspection_route(farm, targets=[(1, 1), (1, 1)])

if __name__ == "__main__":
    unittest.main()
