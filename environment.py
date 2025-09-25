"""
Environment module for the autonomous delivery agent.
Models the grid world with static/dynamic obstacles and terrain costs.
"""
import numpy as np
from typing import List, Tuple, Dict, Set, Optional
from enum import Enum

class Terrain(Enum):
    ROAD = 1
    GRASS = 2
    MUD = 3
    WATER = 999  # Essentially impassable

class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    STAY = (0, 0)

class DynamicObstacle:
    """Represents a moving obstacle with a predictable pattern"""
    def __init__(self, name: str, start_pos: Tuple[int, int], 
                 pattern: List[Direction], interval: int = 1):
        self.name = name
        self.position = start_pos
        self.pattern = pattern
        self.interval = interval
        self.step_count = 0
        self.history = [start_pos]
    
    def move(self, time: int) -> Tuple[int, int]:
        """Move obstacle according to its pattern"""
        if time % self.interval == 0:
            pattern_index = (time // self.interval) % len(self.pattern)
            dx, dy = self.pattern[pattern_index].value
            new_x = self.position[0] + dx
            new_y = self.position[1] + dy
            self.position = (new_x, new_y)
            self.history.append(self.position)
        return self.position
    
    def get_position_at_time(self, time: int) -> Tuple[int, int]:
        """Predict position at future time (for planning)"""
        effective_time = time // self.interval
        pattern_index = effective_time % len(self.pattern)
        
        current_pos = self.history[0]
        for i in range(effective_time + 1):
            dx, dy = self.pattern[i % len(self.pattern)].value
            current_pos = (current_pos[0] + dx, current_pos[1] + dy)
        
        return current_pos

class GridEnvironment:
    """Main environment class representing the grid world"""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.grid = np.ones((height, width), dtype=int)  # Default to road
        self.static_obstacles: Set[Tuple[int, int]] = set()
        self.dynamic_obstacles: Dict[str, DynamicObstacle] = {}
        self.packages: Dict[int, Tuple[int, int]] = {}
        self.start_position: Tuple[int, int] = (0, 0)
        self.delivery_points: Set[Tuple[int, int]] = set()
        
    def load_from_file(self, filename: str):
        """Load environment configuration from file"""
        with open(filename, 'r') as f:
            lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        current_section = None
        for line in lines:
            if line.endswith(':'):
                current_section = line[:-1].upper()
                continue
                
            if current_section == 'SIZE':
                self.width, self.height = map(int, line.split())
                self.grid = np.ones((self.height, self.width), dtype=int)
                
            elif current_section == 'START':
                self.start_position = tuple(map(int, line.split()))
                
            elif current_section == 'PACKAGES':
                parts = line.split()
                for part in parts:
                    pkg_id, x, y = map(int, part.split(':'))
                    self.packages[pkg_id] = (x, y)
                    self.delivery_points.add((x, y))
                    
            elif current_section == 'TERRAIN':
                row_data = list(map(int, line.split()))
                if len(self.grid) > 0:
                    y = len([l for l in lines if l.startswith('TERRAIN:') or 
                           (current_section == 'TERRAIN' and not l.endswith(':'))]) - 1
                    if y < self.height:
                        for x, cost in enumerate(row_data[:self.width]):
                            self.grid[y, x] = cost
                            
            elif current_section == 'OBSTACLES':
                if line.startswith('STATIC:'):
                    obstacles = line[7:].strip().split()
                    for obstacle in obstacles:
                        x, y = map(int, obstacle.split(':'))
                        self.static_obstacles.add((x, y))
                        
                elif line.startswith('DYNAMIC:'):
                    parts = line[8:].strip().split(':')
                    name = parts[0]
                    x, y = map(int, parts[1:3])
                    direction = Direction[parts[3].upper()]
                    interval = int(parts[4]) if len(parts) > 4 else 1
                    self.dynamic_obstacles[name] = DynamicObstacle(
                        name, (x, y), [direction], interval
                    )
    
    def get_terrain_cost(self, x: int, y: int) -> int:
        """Get movement cost for a cell"""
        if not self.is_within_bounds(x, y):
            return 999
        return self.grid[y, x]
    
    def is_within_bounds(self, x: int, y: int) -> bool:
        """Check if coordinates are within grid bounds"""
        return 0 <= x < self.width and 0 <= y < self.height
    
    def is_obstructed(self, x: int, y: int, time: int) -> bool:
        """Check if cell is obstructed at given time"""
        # Check static obstacles
        if (x, y) in self.static_obstacles:
            return True
            
        # Check dynamic obstacles
        for obstacle in self.dynamic_obstacles.values():
            obs_pos = obstacle.get_position_at_time(time)
            if (x, y) == obs_pos:
                return True
                
        return False
    
    def get_valid_moves(self, x: int, y: int, time: int) -> List[Tuple[int, int, int]]:
        """Get valid moves from current position with their costs"""
        moves = []
        for direction in [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]:
            dx, dy = direction.value
            new_x, new_y = x + dx, y + dy
            
            if (self.is_within_bounds(new_x, new_y) and 
                not self.is_obstructed(new_x, new_y, time)):
                cost = self.get_terrain_cost(new_x, new_y)
                moves.append((new_x, new_y, cost))
                
        return moves
    
    def visualize(self, agent_pos: Tuple[int, int] = None, time: int = 0):
        """Simple text visualization of the environment"""
        grid_display = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                if agent_pos and (x, y) == agent_pos:
                    row.append('A')
                elif self.is_obstructed(x, y, time):
                    row.append('X')
                elif (x, y) in self.delivery_points:
                    row.append('D')
                elif (x, y) == self.start_position:
                    row.append('S')
                else:
                    cost = self.get_terrain_cost(x, y)
                    row.append(str(cost))
            grid_display.append(' '.join(row))
        return '\n'.join(grid_display)