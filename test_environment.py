"""Unit tests for environment module"""
import unittest
import os
from src.environment import GridEnvironment, Terrain, DynamicObstacle, Direction

class TestEnvironment(unittest.TestCase):
    
    def setUp(self):
        self.env = GridEnvironment(10, 10)
        
    def test_initialization(self):
        self.assertEqual(self.env.width, 10)
        self.assertEqual(self.env.height, 10)
        self.assertEqual(self.env.grid.shape, (10, 10))
        
    def test_terrain_costs(self):
        self.assertEqual(self.env.get_terrain_cost(0, 0), 1)  # Default road
        
    def test_obstacle_detection(self):
        self.env.static_obstacles.add((5, 5))
        self.assertTrue(self.env.is_obstructed(5, 5, 0))
        self.assertFalse(self.env.is_obstructed(0, 0, 0))
        
    def test_boundary_check(self):
        self.assertTrue(self.env.is_within_bounds(0, 0))
        self.assertTrue(self.env.is_within_bounds(9, 9))
        self.assertFalse(self.env.is_within_bounds(10, 10))
        self.assertFalse(self.env.is_within_bounds(-1, -1))

if __name__ == '__main__':
    unittest.main()