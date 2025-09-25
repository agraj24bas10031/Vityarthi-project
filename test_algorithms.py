"""Unit tests for search algorithms"""
import unittest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.algorithms import BFS, UniformCostSearch, AStarSearch, HillClimbing, SimulatedAnnealing
from src.environment import GridEnvironment

class TestSearchAlgorithms(unittest.TestCase):
    
    def setUp(self):
        self.env = GridEnvironment(5, 5)
        # Create a simple grid for testing
        for y in range(5):
            for x in range(5):
                self.env.grid[y, x] = 1  # All roads
        
    def test_bfs_find_path(self):
        bfs = BFS(self.env)
        path = bfs.search((0, 0), (4, 4))
        self.assertIsNotNone(path)
        self.assertEqual(path[0], (0, 0))
        self.assertEqual(path[-1], (4, 4))
        self.assertTrue(len(path) > 0)
        
    def test_ucs_find_path(self):
        ucs = UniformCostSearch(self.env)
        path = ucs.search((0, 0), (4, 4))
        self.assertIsNotNone(path)
        self.assertEqual(path[0], (0, 0))
        self.assertEqual(path[-1], (4, 4))
        
    def test_astar_find_path(self):
        astar = AStarSearch(self.env, 'manhattan')
        path = astar.search((0, 0), (4, 4))
        self.assertIsNotNone(path)
        self.assertEqual(path[0], (0, 0))
        self.assertEqual(path[-1], (4, 4))
        
    def test_astar_heuristics(self):
        # Test different heuristics
        for heuristic in ['manhattan', 'euclidean', 'chebyshev']:
            astar = AStarSearch(self.env, heuristic)
            path = astar.search((0, 0), (4, 4))
            self.assertIsNotNone(path)
            
    def test_hill_climbing(self):
        hc = HillClimbing(self.env)
        initial_path = [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (4, 1), (4, 2), (4, 3), (4, 4)]
        optimized_path = hc.search((0, 0), (4, 4), initial_path)
        self.assertIsNotNone(optimized_path)
        self.assertEqual(optimized_path[0], (0, 0))
        self.assertEqual(optimized_path[-1], (4, 4))
        
    def test_simulated_annealing(self):
        sa = SimulatedAnnealing(self.env)
        initial_path = [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (4, 1), (4, 2), (4, 3), (4, 4)]
        optimized_path = sa.search((0, 0), (4, 4), initial_path)
        self.assertIsNotNone(optimized_path)
        self.assertEqual(optimized_path[0], (0, 0))
        self.assertEqual(optimized_path[-1], (4, 4))

if __name__ == '__main__':
    unittest.main()