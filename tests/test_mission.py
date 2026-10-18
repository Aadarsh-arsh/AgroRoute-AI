import unittest
from agroroute.farm import Farm, demo_farm
from agroroute.mission import mission

class TestMission(unittest.TestCase):
    def setUp(self):
        self.f=demo_farm()
    def test_all_algorithms_complete_mission(self):
        for name in ('Nearest Neighbor','Genetic Algorithm','Exact Dynamic Programming'):
            with self.subTest(name=name):
                result=mission(self.f,name)
                self.assertTrue(result.found,result.message)
                self.assertEqual(result.path[0],self.f.rover)
                self.assertEqual(result.path[-1],self.f.rover)
                self.assertEqual(result.cost,len(result.path)-1)
                self.assertEqual(set(result.order[1:-1]),{(2,2),(2,9),(8,9),(10,4)})
                self.assertTrue(all(self.f.cells[r][c]!='obstacle' for r,c in result.path))
                self.assertTrue(all(abs(a[0]-b[0])+abs(a[1]-b[1])==1 for a,b in zip(result.path,result.path[1:])))
    def test_exact_no_worse_than_heuristics(self):
        optimal=mission(self.f,'Exact Dynamic Programming')
        for name in ('Nearest Neighbor','Genetic Algorithm'):
            self.assertGreaterEqual(mission(self.f,name).cost,optimal.cost)
    def test_seed_reproducible(self):
        a=mission(self.f,'Genetic Algorithm',seed=7)
        b=mission(self.f,'Genetic Algorithm',seed=7)
        self.assertEqual(a.order,b.order)
        self.assertEqual(a.cost,b.cost)
    def test_no_infected_zones(self):
        result=mission(Farm(),'Genetic Algorithm')
        self.assertFalse(result.found)
    def test_unreachable_zone(self):
        f=Farm(rows=5,cols=5)
        f.paint(2,2,'infected')
        for pos in ((1,2),(2,1),(2,3),(3,2)):
            f.paint(*pos,'obstacle')
        self.assertFalse(mission(f,'Exact Dynamic Programming').found)
    def test_one_zone_no_return(self):
        f=Farm(rows=5,cols=5)
        f.paint(1,1,'infected')
        r=mission(f,'Exact Dynamic Programming',return_to_base=False)
        self.assertEqual(r.cost,2)
        self.assertEqual(r.path[-1],(1,1))
    def test_exact_limit(self):
        f=Farm(rows=5,cols=5)
        for r in range(5):
            for c in range(5):
                if (r,c)!=(0,0) and (r,c)!=(4,4):f.paint(r,c,'infected')
        r=mission(f,'Exact Dynamic Programming')
        self.assertFalse(r.found)
        self.assertIn('limited',r.message)

if __name__=='__main__': unittest.main()
