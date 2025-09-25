"""Unit tests for delivery agent"""
import unittest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.agent import DeliveryAgent
from src.environment import GridEnvironment

class TestDeliveryAgent(unittest.TestCase):
    
    def setUp(self):
        self.env = GridEnvironment(10, 10)
        self.env.load_from_file('maps/small.map')
        self.agent = DeliveryAgent(self.env)
        
    def test_agent_initialization(self):
        self.assertEqual(self.agent.position, self.env.start_position)
        self.assertEqual(self.agent.fuel, 1000)
        self.assertEqual(self.agent.time, 0)
        self.assertEqual(len(self.agent.packages_delivered), 0)
        
    def test_plan_delivery_route(self):
        route = self.agent.plan_delivery_route('astar', 'manhattan')
        self.assertIsInstance(route, list)
        self.assertTrue(len(route) > 0)
        self.assertEqual(route[0], self.env.start_position)
        
    def test_find_path(self):
        path = self.agent.find_path((0, 0), (5, 5), 'astar', 'manhattan')
        self.assertIsInstance(path, list)
        self.assertTrue(len(path) > 0)
        
    def test_execute_route(self):
        route = [(0, 0), (1, 0), (2, 0), (3, 0)]
        status = self.agent.execute_route(route, max_steps=10)
        self.assertEqual(status.total_time, 3)  # 3 moves from start
        self.assertEqual(len(status.path_taken), 4)
        
    def test_reset(self):
        self.agent.position = (5, 5)
        self.agent.fuel = 500
        self.agent.time = 10
        self.agent.packages_delivered.add(1)
        
        self.agent.reset()
        
        self.assertEqual(self.agent.position, self.env.start_position)
        self.assertEqual(self.agent.fuel, 1000)
        self.assertEqual(self.agent.time, 0)
        self.assertEqual(len(self.agent.packages_delivered), 0)

if __name__ == '__main__':
    unittest.main()