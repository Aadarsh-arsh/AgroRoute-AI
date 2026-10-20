import unittest
from agroroute.battery_planning import estimate_route_energy, is_mission_feasible

class BatteryPlanningTests(unittest.TestCase):
    def test_energy_estimate(self):
        self.assertEqual(estimate_route_energy([(0, 0), (0, 1)], targets=2), 5.0)

    def test_reserve_is_enforced(self):
        self.assertTrue(is_mission_feasible([(0, 0)], battery=20, reserve=15))
        self.assertFalse(is_mission_feasible([(0, 0), (0, 1)], battery=15, reserve=15))

    def test_invalid_energy_rejected(self):
        with self.assertRaises(ValueError):
            estimate_route_energy([(0, 0)], per_step=-1)

if __name__ == "__main__":
    unittest.main()
