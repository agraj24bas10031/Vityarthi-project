"""
Autonomous delivery agent that plans and executes delivery routes.
"""
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
from environment import GridEnvironment, Direction
from algorithms import BFS, UniformCostSearch, AStarSearch, HillClimbing, SimulatedAnnealing

@dataclass
class DeliveryStatus:
    """Track delivery progress"""
    packages_delivered: set
    total_cost: float
    total_time: int
    path_taken: List[Tuple[int, int]]

class DeliveryAgent:
    """Autonomous delivery agent"""
    
    def __init__(self, environment: GridEnvironment, fuel_capacity: int = 1000):
        self.env = environment
        self.position = environment.start_position
        self.fuel = fuel_capacity
        self.time = 0
        self.packages_delivered = set()
        self.path_history = [environment.start_position]
        self.status_log = []
        
    def plan_delivery_route(self, algorithm: str = 'astar', 
                          heuristic: str = 'manhattan') -> List[Tuple[int, int]]:
        """Plan route to deliver all packages"""
        if not self.env.packages:
            return []
            
        # For simplicity, find route to deliver packages in order of proximity
        current_pos = self.position
        remaining_packages = set(self.env.packages.keys()) - self.packages_delivered
        full_route = []
        
        while remaining_packages:
            # Find nearest undelivered package
            nearest_pkg = None
            min_distance = float('inf')
            nearest_path = []
            
            for pkg_id in remaining_packages:
                goal_pos = self.env.packages[pkg_id]
                path = self.find_path(current_pos, goal_pos, algorithm, heuristic)
                if path and len(path) < min_distance:
                    min_distance = len(path)
                    nearest_pkg = pkg_id
                    nearest_path = path
                    
            if nearest_pkg and nearest_path:
                full_route.extend(nearest_path[1:])  # Skip current position
                current_pos = self.env.packages[nearest_pkg]
                remaining_packages.remove(nearest_pkg)
            else:
                break
                
        return [self.position] + full_route
    
    def find_path(self, start: Tuple[int, int], goal: Tuple[int, int],
                 algorithm: str = 'astar', heuristic: str = 'manhattan') -> Optional[List[Tuple[int, int]]]:
        """Find path using specified algorithm"""
        if algorithm == 'bfs':
            search = BFS(self.env)
        elif algorithm == 'ucs':
            search = UniformCostSearch(self.env)
        elif algorithm == 'astar':
            search = AStarSearch(self.env, heuristic)
        else:
            search = AStarSearch(self.env, heuristic)
            
        return search.search(start, goal)
    
    def execute_route(self, route: List[Tuple[int, int]], 
                     max_steps: int = 1000) -> DeliveryStatus:
        """Execute planned route"""
        original_position = self.position
        
        for i, next_pos in enumerate(route[1:max_steps+1], 1):
            # Check if we need to replan due to dynamic obstacles
            if self.env.is_obstructed(*next_pos, self.time):
                print(f"Obstacle detected at {next_pos}, time to replan!")
                new_route = self.replan_route(route[i-1:])
                if new_route:
                    route = route[:i-1] + new_route
                    next_pos = route[i] if i < len(route) else next_pos
                else:
                    print("Replanning failed! Stopping.")
                    break
            
            # Move to next position
            move_cost = self.env.get_terrain_cost(*next_pos)
            if self.fuel >= move_cost:
                self.position = next_pos
                self.fuel -= move_cost
                self.time += 1
                self.path_history.append(next_pos)
                
                # Check if package delivered
                for pkg_id, delivery_pos in self.env.packages.items():
                    if next_pos == delivery_pos and pkg_id not in self.packages_delivered:
                        self.packages_delivered.add(pkg_id)
                        print(f"Package {pkg_id} delivered at {next_pos}!")
            else:
                print("Out of fuel! Stopping.")
                break
                
        status = DeliveryStatus(
            packages_delivered=self.packages_delivered.copy(),
            total_cost=sum(self.env.get_terrain_cost(*pos) for pos in self.path_history[1:]),
            total_time=self.time,
            path_taken=self.path_history.copy()
        )
        self.status_log.append(status)
        return status
    
    def replan_route(self, remaining_route: List[Tuple[int, int]]) -> Optional[List[Tuple[int, int]]]:
        """Replan route using local search when obstacles appear"""
        if len(remaining_route) < 2:
            return None
            
        current_pos = remaining_route[0]
        goal_pos = remaining_route[-1]
        
        # Try hill climbing first
        hill_climb = HillClimbing(self.env)
        new_path = hill_climb.search(current_pos, goal_pos, remaining_route)
        
        if not new_path or len(new_path) == 0:
            # Fall back to simulated annealing
            annealing = SimulatedAnnealing(self.env)
            new_path = annealing.search(current_pos, goal_pos, remaining_route)
            
        return new_path
    
    def reset(self):
        """Reset agent to initial state"""
        self.position = self.env.start_position
        self.fuel = 1000
        self.time = 0
        self.packages_delivered = set()
        self.path_history = [self.env.start_position]
        self.status_log = []