import unittest
from collections import deque
from agroroute.farm import Farm, demo_farm
from agroroute.pathfinding import ALGORITHMS, search, compare, neighbours

class TestPathfinding(unittest.TestCase):
    def test_start_equals_goal(self):
        for alg in ALGORITHMS:
            res = search(Farm(),(0,0),alg)
            self.assertTrue(res.found)
            self.assertEqual(res.path,[(0,0)])
            self.assertEqual(res.cost,0)
    def test_straight_route_is_contiguous(self):
        farm = Farm()
        for alg in ALGORITHMS:
            result = search(farm, (0, 6), alg)
            self.assertTrue(all(
                abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1
                for a, b in zip(result.path, result.path[1:])
            ))
    def test_straight_route(self):
        for alg in ALGORITHMS:
            res=search(Farm(),(0,4),alg)
            self.assertEqual(res.cost,4)
            self.assertEqual(res.path[0],(0,0))
            self.assertEqual(res.path[-1],(0,4))
    def test_invalid_start(self):
        farm = Farm()
        farm.paint(1, 1, 'obstacle')
        for alg in ALGORITHMS:
            with self.subTest(algorithm=alg):
                with self.assertRaises(ValueError):
                    search(farm, (1, 1), alg)

    def test_obstacle_detour(self):
        f=Farm(rows=5,cols=5)
        for r in range(4): f.paint(r,1,'obstacle')
        for alg in ALGORITHMS:
            res=search(f,(0,2),alg)
            self.assertTrue(res.found)
            self.assertEqual(res.cost,10)
            self.assertFalse(any(f.cells[r][c]=='obstacle' for r,c in res.path))
            self.assertTrue(all(abs(a[0]-b[0])+abs(a[1]-b[1])==1 for a,b in zip(res.path,res.path[1:])))

    def test_unreachable(self):
        f=Farm(rows=5,cols=5)
        f.paint(0,1,'obstacle')
        f.paint(1,0,'obstacle')
        for alg in ALGORITHMS:
            res=search(f,(2,2),alg)
            self.assertFalse(res.found)
            self.assertIsNone(res.cost)
            self.assertEqual(res.path,[])

    def test_invalid_goal(self):
        f=Farm()
        f.paint(2,2,'obstacle')
        with self.assertRaises(ValueError): search(f,(2,2))
        with self.assertRaises(ValueError): search(f,(100,100))
        with self.assertRaises(ValueError): search(f,(2,3),'Fake')

    def test_demo_comparison(self):
        results=compare(demo_farm(),(2,2))
        self.assertEqual(len(results),3)
        self.assertEqual(results[0].cost,results[1].cost)

    def test_shortest_path_against_bfs(self):
        f=demo_farm()
        for goal in [(2,2),(2,9),(8,9),(10,4),(11,11)]:
            q=deque([(f.rover,0)])
            seen={f.rover}
            optimal=None
            while q:
                pos,d=q.popleft()
                if pos==goal:
                    optimal=d;break
                for nxt in neighbours(f,pos):
                    if nxt not in seen:
                        seen.add(nxt);q.append((nxt,d+1))
            for alg in ('A*','UCS'):
                self.assertEqual(search(f,goal,alg).cost,optimal)

if __name__=='__main__': unittest.main()
