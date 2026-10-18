import unittest
from agroroute.farm import demo_farm
from agroroute.rover import RoverState
from agroroute.expert import forward_chain,backward_chain
from agroroute.scheduler import schedule
class IntegrationTests(unittest.TestCase):
    def test_rover_moves(self):
        f=demo_farm();r=RoverState([(0,0),(0,1),(0,2)])
        self.assertTrue(r.tick(f));self.assertEqual(r.position,(0,1));self.assertEqual(r.battery,99.6)
    def test_rover_blocks_jump(self):
        f=demo_farm();r=RoverState([(0,0),(2,0)])
        self.assertFalse(r.tick(f));self.assertEqual(r.status,'Invalid route')
    def test_rover_completion(self):
        f=demo_farm();r=RoverState([(0,0),(0,1)])
        self.assertTrue(r.tick(f));self.assertEqual(r.status,'Completed')
    def test_forward(self):
        c=forward_chain('Late Blight','High',True)
        self.assertEqual(c.facts['priority'],'Urgent');self.assertFalse(c.facts['spraying_allowed'])
    def test_backward(self):
        c=forward_chain('Late Blight','High')
        self.assertTrue(backward_chain(c,'needs_inspection')[0])
    def test_csp_feasible(self):
        tasks=[{'id':'A','duration':2},{'id':'B','duration':2}]
        r=schedule(tasks,4)
        self.assertTrue(r.feasible);self.assertNotEqual(r.assignments['A'],r.assignments['B'])
    def test_csp_infeasible(self):
        tasks=[{'id':'A','duration':2},{'id':'B','duration':2}]
        self.assertFalse(schedule(tasks,3).feasible)
    def test_csp_invalid(self):
        with self.assertRaises(ValueError):schedule([{'id':'A','duration':0}],4)
if __name__=='__main__':unittest.main()
