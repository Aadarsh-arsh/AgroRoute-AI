import unittest
from agroroute.farm import demo_farm
from agroroute.treatment import build_zone_plans, mission_feasibility

class TestTreatment(unittest.TestCase):
    def setUp(self):
        self.farm=demo_farm()
    def test_all_zones(self):
        self.assertEqual(len(build_zone_plans(self.farm)),4)
    def test_high_priority_first(self):
        self.assertEqual([p.priority for p in build_zone_plans(self.farm)][:2],['High','High'])
    def test_low_confidence_review(self):
        p=build_zone_plans(self.farm,{'2,2':{'disease':'Early_blight','probability':0.5}})
        self.assertTrue(next(x for x in p if (x.row,x.column)==(3,3)).manual_review)
    def test_high_confidence(self):
        p=build_zone_plans(self.farm,{'2,2':{'disease':'Early_blight','probability':0.9}})
        self.assertFalse(next(x for x in p if (x.row,x.column)==(3,3)).manual_review)
    def test_rain(self):
        self.assertFalse(build_zone_plans(self.farm,rain=True)[0].spraying_allowed)
    def test_battery(self):
        self.assertTrue(mission_feasibility(40,100,0.4,15,4,20)['feasible'])
        self.assertFalse(mission_feasibility(100,30,0.4,15,4,20)['feasible'])
    def test_capacity(self):
        self.assertFalse(mission_feasibility(10,100,0.4,15,4,2)['feasible'])
    def test_invalid_threshold(self):
        with self.assertRaises(ValueError):build_zone_plans(self.farm,confidence_threshold=1.1)

if __name__=='__main__':unittest.main()
