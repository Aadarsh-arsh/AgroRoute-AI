import unittest
from agroroute.farm import demo_farm
from agroroute.mission import mission
from agroroute.mission_control import preflight

class TestMissionControl(unittest.TestCase):
    def setUp(self):
        self.farm=demo_farm()
        self.route=mission(self.farm,'Nearest Neighbor',return_to_base=True).path
    def test_valid_round_trip(self):
        self.assertTrue(preflight(self.farm,self.route,0.4,20).feasible)
    def test_insufficient_battery(self):
        self.assertFalse(preflight(self.farm,self.route,3,20).feasible)
    def test_capacity(self):
        self.assertFalse(preflight(self.farm,self.route,0.4,1).feasible)
    def test_no_return(self):
        self.assertFalse(preflight(self.farm,self.route[:-1],0.4,20).feasible)
    def test_bad_step(self):
        self.assertFalse(preflight(self.farm,[self.farm.rover,(5,5),self.farm.rover],0.4,20).feasible)

if __name__=='__main__': unittest.main()
