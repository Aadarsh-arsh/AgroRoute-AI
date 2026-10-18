import unittest
from evaluation.benchmark import scenarios
from agroroute.pathfinding import search
from agroroute.mission import mission, infected_zones

class EvaluationRegressionTests(unittest.TestCase):
    def test_scenarios_have_four_infected_zones(self):
        for farm in scenarios().values():
            self.assertEqual(len(infected_zones(farm)),4)
    def test_optimal_pathfinding_matches_ucs(self):
        for farm in scenarios().values():
            for goal in infected_zones(farm):
                self.assertEqual(search(farm,goal,"A*").cost,search(farm,goal,"UCS").cost)
    def test_all_route_methods_cover_zones_and_return(self):
        for farm in scenarios().values():
            for algorithm in ("Nearest Neighbor","Genetic Algorithm","Exact Dynamic Programming"):
                route=mission(farm,algorithm)
                self.assertTrue(route.found)
                self.assertEqual(route.path[0],farm.rover)
                self.assertEqual(route.path[-1],farm.rover)
                self.assertTrue(set(infected_zones(farm)).issubset(route.path))
    def test_exact_never_worse_than_heuristics(self):
        for farm in scenarios().values():
            exact=mission(farm,"Exact Dynamic Programming").cost
            for algorithm in ("Nearest Neighbor","Genetic Algorithm"):
                self.assertGreaterEqual(mission(farm,algorithm).cost,exact)
