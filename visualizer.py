"""
Visualization utilities for the delivery agent.
"""
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation
from typing import List, Tuple
from src.environment import GridEnvironment

class DeliveryVisualizer:
    """Visualize the delivery agent's progress"""
    
    def __init__(self, environment: GridEnvironment):
        self.env = environment
        self.fig, self.ax = plt.subplots(figsize=(10, 10))
        
    def plot_environment(self, agent_pos: Tuple[int, int] = None, time: int = 0):
        """Plot the grid environment"""
        self.ax.clear()
        
        # Create grid visualization
        for y in range(self.env.height):
            for x in range(self.env.width):
                cost = self.env.get_terrain_cost(x, y)
                color = self.get_color_for_terrain(cost)
                
                rect = patches.Rectangle((x, y), 1, 1, linewidth=1, 
                                       edgecolor='black', facecolor=color, alpha=0.7)
                self.ax.add_patch(rect)
                
                # Add cost text
                self.ax.text(x + 0.5, y + 0.5, str(cost), ha='center', va='center', fontsize=8)
                
                # Mark obstacles
                if self.env.is_obstructed(x, y, time):
                    self.ax.text(x + 0.5, y + 0.5, 'X', ha='center', va='center', 
                               fontsize=12, fontweight='bold', color='red')
                
                # Mark delivery points
                if (x, y) in self.env.delivery_points:
                    circle = patches.Circle((x + 0.5, y + 0.5), 0.3, fill=True, color='green')
                    self.ax.add_patch(circle)
        
        # Mark agent position
        if agent_pos:
            agent_circle = patches.Circle((agent_pos[0] + 0.5, agent_pos[1] + 0.5), 
                                        0.4, fill=True, color='blue')
            self.ax.add_patch(agent_circle)
            self.ax.text(agent_pos[0] + 0.5, agent_pos[1] + 0.5, 'A', 
                        ha='center', va='center', fontweight='bold', color='white')
        
        self.ax.set_xlim(0, self.env.width)
        self.ax.set_ylim(0, self.env.height)
        self.ax.set_aspect('equal')
        self.ax.grid(True)
        self.ax.set_title(f'Delivery Environment (Time: {time})')
        
    def get_color_for_terrain(self, cost: int) -> str:
        """Get color representation for terrain cost"""
        if cost == 1: return 'lightgray'   # Road
        elif cost == 2: return 'lightgreen' # Grass
        elif cost == 3: return 'brown'      # Mud
        else: return 'lightblue'            # Water/other
    
    def animate_delivery(self, path: List[Tuple[int, int]], interval: int = 500):
        """Animate the delivery route"""
        def update(frame):
            if frame < len(path):
                self.plot_environment(path[frame], frame)
            return []
        
        anim = FuncAnimation(self.fig, update, frames=len(path), 
                           interval=interval, repeat=False)
        plt.show()
        return anim

    def plot_metrics(self, results: dict):
        """Plot comparative metrics for different algorithms"""
        algorithms = list(results.keys())
        costs = [results[algo]['total_cost'] for algo in algorithms]
        times = [results[algo]['computation_time'] for algo in algorithms]
        nodes_expanded = [results[algo]['nodes_expanded'] for algo in algorithms]
        
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        
        # Cost comparison
        axes[0].bar(algorithms, costs, color=['skyblue', 'lightgreen', 'lightcoral'])
        axes[0].set_title('Total Path Cost')
        axes[0].set_ylabel('Cost')
        
        # Time comparison
        axes[1].bar(algorithms, times, color=['skyblue', 'lightgreen', 'lightcoral'])
        axes[1].set_title('Computation Time')
        axes[1].set_ylabel('Time (seconds)')
        
        # Nodes expanded comparison
        axes[2].bar(algorithms, nodes_expanded, color=['skyblue', 'lightgreen', 'lightcoral'])
        axes[2].set_title('Nodes Expanded')
        axes[2].set_ylabel('Nodes')
        
        plt.tight_layout()
        plt.show()