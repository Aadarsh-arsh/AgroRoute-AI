import unittest
from agroroute.farm import demo_farm, Farm
from agroroute.dashboard import overview, prepare_mission

class TestUnifiedDashboard(unittest.TestCase):
    def test_counts_and_priority(self):
        result=overview(demo_farm())
        self.assertEqual(result['total_zones'],4)
        self.assertEqual(result['high_priority'],2)
        self.assertEqual(result['manual_review'],4)

    def test_diagnoses_reduce_manual_review(self):
        farm=demo_farm()
        diagnoses={'2,2':{'class':'Early_blight','probability':0.9}}
        self.assertEqual(overview(farm,diagnoses)['manual_review'],3)

    def test_route_preflight(self):
        result,check=prepare_mission(demo_farm(),'Nearest Neighbor')
        self.assertTrue(result.found)
        self.assertTrue(check.feasible)
        self.assertEqual(result.path[0],result.path[-1])

    def test_insufficient_battery_blocks(self):
        result,check=prepare_mission(demo_farm(),'Nearest Neighbor',battery_per_step=4)
        self.assertTrue(result.found)
        self.assertFalse(check.feasible)

    def test_empty_farm_no_mission(self):
        result,check=prepare_mission(Farm(),'Nearest Neighbor')
        self.assertFalse(result.found)
        self.assertIsNone(check)

if __name__=='__main__':unittest.main()
