"""
Search algorithms for path planning: BFS, Uniform-Cost, A*, and local search methods.
"""
import heapq
import math
import random
from typing import List, Tuple, Dict, Set, Optional, Callable
from collections import deque
from dataclasses import dataclass, field
from environment import GridEnvironment, Direction

@dataclass(order=True)
class SearchNode:
    """Node for search algorithms"""
    cost: float
    position: Tuple[int, int] = field(compare=False)
    time: int = field(compare=False)
    parent: Optional['SearchNode'] = field(compare=False)
    action: Optional[Direction] = field(compare=False)
    packages_delivered: Set[int] = field(compare=False)
    
    def __init__(self, position, time=0, parent=None, action=None, 
                 packages_delivered=None, cost=0):
        self.position = position
        self.time = time
        self.parent = parent
        self.action = action
        self.packages_delivered = packages_delivered or set()
        self.cost = cost

class SearchAlgorithm:
    """Base class for search algorithms"""
    
    def __init__(self, environment: GridEnvironment):
        self.env = environment
        self.nodes_expanded = 0
        
    def reconstruct_path(self, node: SearchNode) -> List[Tuple[int, int]]:
        """Reconstruct path from goal node to start"""
        path = []
        current = node
        while current:
            path.append(current.position)
            current = current.parent
        return path[::-1]
    
    def get_successors(self, node: SearchNode) -> List[SearchNode]:
        """Generate successor nodes"""
        self.nodes_expanded += 1
        x, y = node.position
        successors = []
        
        moves = self.env.get_valid_moves(x, y, node.time)
        for new_x, new_y, move_cost in moves:
            # Check if this move delivers a package
            new_packages = node.packages_delivered.copy()
            for pkg_id, delivery_pos in self.env.packages.items():
                if (new_x, new_y) == delivery_pos and pkg_id not in new_packages:
                    new_packages.add(pkg_id)
            
            new_node = SearchNode(
                position=(new_x, new_y),
                time=node.time + 1,
                parent=node,
                cost=node.cost + move_cost,
                packages_delivered=new_packages
            )
            successors.append(new_node)
            
        return successors

class BFS(SearchAlgorithm):
    """Breadth-First Search implementation"""
    
    def search(self, start: Tuple[int, int], goal: Tuple[int, int] = None) -> Optional[List[Tuple[int, int]]]:
        """BFS search for single goal"""
        queue = deque([SearchNode(start)])
        visited = set([start])
        
        while queue:
            current = queue.popleft()
            
            # Check if goal reached
            if current.position == goal:
                return self.reconstruct_path(current)
            
            for successor in self.get_successors(current):
                if successor.position not in visited:
                    visited.add(successor.position)
                    queue.append(successor)
                    
        return None

class UniformCostSearch(SearchAlgorithm):
    """Uniform-Cost Search implementation"""
    
    def search(self, start: Tuple[int, int], goal: Tuple[int, int] = None) -> Optional[List[Tuple[int, int]]]:
        """UCS search for single goal"""
        frontier = []
        heapq.heappush(frontier, (0, SearchNode(start)))
        visited_costs = {start: 0}
        
        while frontier:
            current_cost, current = heapq.heappop(frontier)
            
            if current_cost > visited_costs.get(current.position, float('inf')):
                continue
                
            if current.position == goal:
                return self.reconstruct_path(current)
            
            for successor in self.get_successors(current):
                if (successor.position not in visited_costs or 
                    successor.cost < visited_costs[successor.position]):
                    visited_costs[successor.position] = successor.cost
                    heapq.heappush(frontier, (successor.cost, successor))
                    
        return None

class AStarSearch(SearchAlgorithm):
    """A* Search implementation with configurable heuristics"""
    
    def __init__(self, environment: GridEnvironment, heuristic: str = 'manhattan'):
        super().__init__(environment)
        self.heuristic = heuristic
        
    def calculate_heuristic(self, pos: Tuple[int, int], goal: Tuple[int, int]) -> float:
        """Calculate heuristic value"""
        x1, y1 = pos
        x2, y2 = goal
        
        if self.heuristic == 'manhattan':
            return abs(x1 - x2) + abs(y1 - y2)
        elif self.heuristic == 'euclidean':
            return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
        elif self.heuristic == 'chebyshev':
            return max(abs(x1 - x2), abs(y1 - y2))
        else:
            return 0
    
    def search(self, start: Tuple[int, int], goal: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
        """A* search for single goal"""
        frontier = []
        start_node = SearchNode(start)
        start_f = self.calculate_heuristic(start, goal)
        heapq.heappush(frontier, (start_f, start_node))
        
        g_costs = {start: 0}
        visited = set()
        
        while frontier:
            current_f, current = heapq.heappop(frontier)
            
            if current.position in visited:
                continue
            visited.add(current.position)
            
            if current.position == goal:
                return self.reconstruct_path(current)
            
            for successor in self.get_successors(current):
                if successor.position in visited:
                    continue
                    
                new_g = current.cost + self.env.get_terrain_cost(*successor.position)
                if successor.position not in g_costs or new_g < g_costs[successor.position]:
                    g_costs[successor.position] = new_g
                    h = self.calculate_heuristic(successor.position, goal)
                    f = new_g + h
                    heapq.heappush(frontier, (f, successor))
                    
        return None

class HillClimbing:
    """Hill Climbing with Random Restarts for replanning"""
    
    def __init__(self, environment: GridEnvironment, max_restarts: int = 10):
        self.env = environment
        self.max_restarts = max_restarts
        
    def evaluate_path(self, path: List[Tuple[int, int]]) -> float:
        """Evaluate path quality (lower is better)"""
        if not path:
            return float('inf')
            
        total_cost = 0
        time = 0
        for i in range(1, len(path)):
            x, y = path[i]
            total_cost += self.env.get_terrain_cost(x, y)
            
            # Penalize paths that go through obstacles
            if self.env.is_obstructed(x, y, time):
                total_cost += 1000
            time += 1
            
        return total_cost
    
    def generate_neighbor(self, path: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """Generate a neighboring path by making a small change"""
        if len(path) <= 2:
            return path
            
        # Randomly modify a segment of the path
        new_path = path.copy()
        start_idx = random.randint(1, len(path) - 2)
        end_idx = min(start_idx + random.randint(1, 3), len(path) - 1)
        
        # Try to find an alternative route for this segment
        segment_start = path[start_idx - 1]
        segment_end = path[end_idx]
        
        # Use A* for the segment (simplified)
        try:
            alt_segment = self.find_alternative_route(segment_start, segment_end, 
                                                     path[start_idx:end_idx])
            if alt_segment:
                new_path = path[:start_idx] + alt_segment + path[end_idx:]
        except:
            pass
            
        return new_path
    
    def find_alternative_route(self, start: Tuple[int, int], end: Tuple[int, int],
                             original_segment: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """Find alternative route between two points"""
        # Simple BFS for alternative route
        queue = deque([(start, [start])])
        visited = set([start])
        
        while queue:
            current, path = queue.popleft()
            
            if current == end:
                return path[1:]  # Exclude start
                
            x, y = current
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                neighbor = (x + dx, y + dy)
                if (self.env.is_within_bounds(*neighbor) and 
                    neighbor not in visited and 
                    not self.env.is_obstructed(*neighbor, 0) and
                    neighbor not in original_segment):
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
                    
        return None
    
    def search(self, start: Tuple[int, int], goal: Tuple[int, int], 
               initial_path: List[Tuple[int, int]] = None) -> List[Tuple[int, int]]:
        """Hill climbing search with random restarts"""
        best_path = initial_path or []
        best_score = self.evaluate_path(best_path)
        
        for restart in range(self.max_restarts):
            if not best_path:
                # Generate initial path using A*
                astar = AStarSearch(self.env)
                current_path = astar.search(start, goal) or []
            else:
                current_path = best_path.copy()
                
            current_score = self.evaluate_path(current_path)
            improvements = 0
            
            for _ in range(100):  # Max iterations per restart
                neighbor = self.generate_neighbor(current_path)
                neighbor_score = self.evaluate_path(neighbor)
                
                if neighbor_score < current_score:
                    current_path, current_score = neighbor, neighbor_score
                    improvements += 1
                else:
                    # With small probability, accept worse solution
                    if random.random() < 0.1:
                        current_path, current_score = neighbor, neighbor_score
                
                if improvements >= 10:  # Stop if no improvement
                    break
            
            if current_score < best_score:
                best_path, best_score = current_path, current_score
                
        return best_path

class SimulatedAnnealing:
    """Simulated Annealing for path optimization"""
    
    def __init__(self, environment: GridEnvironment, initial_temp: float = 1000, 
                 cooling_rate: float = 0.95):
        self.env = environment
        self.initial_temp = initial_temp
        self.cooling_rate = cooling_rate
    
    def search(self, start: Tuple[int, int], goal: Tuple[int, int],
               initial_path: List[Tuple[int, int]] = None) -> List[Tuple[int, int]]:
        """Simulated annealing search"""
        current_path = initial_path or AStarSearch(self.env).search(start, goal) or []
        current_score = self.evaluate_path(current_path)
        
        best_path = current_path.copy()
        best_score = current_score
        
        temperature = self.initial_temp
        
        while temperature > 1:
            neighbor = self.generate_neighbor(current_path)
            neighbor_score = self.evaluate_path(neighbor)
            
            # Always accept better solutions
            if neighbor_score < current_score:
                current_path, current_score = neighbor, neighbor_score
                if current_score < best_score:
                    best_path, best_score = current_path.copy(), current_score
            else:
                # Accept worse solution with probability based on temperature
                probability = math.exp((current_score - neighbor_score) / temperature)
                if random.random() < probability:
                    current_path, current_score = neighbor, neighbor_score
            
            temperature *= self.cooling_rate
            
        return best_path
    
    def evaluate_path(self, path: List[Tuple[int, int]]) -> float:
        """Same evaluation as HillClimbing"""
        if not path:
            return float('inf')
        total_cost = sum(self.env.get_terrain_cost(x, y) for x, y in path[1:])
        return total_cost
    
    def generate_neighbor(self, path: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """Generate neighbor path (simplified version)"""
        if len(path) <= 3:
            return path
            
        new_path = path.copy()
        # Randomly swap two segments
        i, j = random.sample(range(1, len(path) - 1), 2)
        new_path[i], new_path[j] = new_path[j], new_path[i]
        return new_path