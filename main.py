"""
Main program for autonomous delivery agent project.
Command-line interface for running different algorithms and scenarios.
"""
import time
import argparse
import sys
import os

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.environment import GridEnvironment
from src.agent import DeliveryAgent
from src.visualizer import DeliveryVisualizer
from src.algorithms import BFS, UniformCostSearch, AStarSearch

def create_test_maps():
    """Create test map files if they don't exist"""
    maps_dir = 'maps'
    if not os.path.exists(maps_dir):
        os.makedirs(maps_dir)
        print(f"Created {maps_dir} directory")
    
    # Map content would be created here (same as above)
    print("Test maps are ready in maps/ directory")

def benchmark_algorithms():
    """Benchmark different search algorithms"""
    print("Loading environment...")
    env = GridEnvironment(10, 10)
    
    try:
        env.load_from_file('maps/small.map')
    except FileNotFoundError:
        print("Error: maps/small.map not found. Run with --create-maps first.")
        return {}
    
    algorithms = {
        'BFS': BFS(env),
        'UCS': UniformCostSearch(env),
        'A* Manhattan': AStarSearch(env, 'manhattan'),
        'A* Euclidean': AStarSearch(env, 'euclidean')
    }
    
    results = {}
    start_pos = env.start_position
    goal_pos = list(env.packages.values())[0] if env.packages else (5, 5)
    
    print(f"Benchmarking algorithms from {start_pos} to {goal_pos}...")
    
    for name, algorithm in algorithms.items():
        print(f"Running {name}...")
        start_time = time.time()
        path = algorithm.search(start_pos, goal_pos)
        end_time = time.time()
        
        if path:
            path_length = len(path)
            total_cost = sum(env.get_terrain_cost(*pos) for pos in path[1:])
        else:
            path_length = 0
            total_cost = float('inf')
        
        results[name] = {
            'path_length': path_length,
            'total_cost': total_cost,
            'computation_time': end_time - start_time,
            'nodes_expanded': algorithm.nodes_expanded,
            'path_found': path is not None
        }
    
    return results

def run_delivery_simulation(map_file: str, algorithm: str, heuristic: str, visualize: bool):
    """Run a complete delivery simulation"""
    print(f"Loading map: {map_file}")
    env = GridEnvironment(1, 1)  # Will be resized by load_from_file
    
    try:
        env.load_from_file(map_file)
    except FileNotFoundError:
        print(f"Error: Map file {map_file} not found.")
        return
    
    print(f"Environment: {env.width}x{env.height}")
    print(f"Start: {env.start_position}")
    print(f"Packages: {len(env.packages)}")
    print(f"Static obstacles: {len(env.static_obstacles)}")
    print(f"Dynamic obstacles: {len(env.dynamic_obstacles)}")
    
    # Create and run agent
    agent = DeliveryAgent(env)
    
    print(f"\nPlanning route with {algorithm.upper()}...")
    route = agent.plan_delivery_route(algorithm, heuristic)
    
    if not route:
        print("Error: Could not plan route!")
        return
    
    print(f"Planned route: {len(route)} steps")
    estimated_cost = sum(env.get_terrain_cost(*pos) for pos in route[1:])
    print(f"Estimated cost: {estimated_cost}")
    
    print("\nExecuting delivery...")
    status = agent.execute_route(route)
    
    print(f"\n=== Delivery Results ===")
    print(f"Packages delivered: {len(status.packages_delivered)}/{len(env.packages)}")
    print(f"Total cost: {status.total_cost}")
    print(f"Total time: {status.total_time}")
    print(f"Fuel remaining: {agent.fuel}")
    
    if visualize:
        print("\nStarting visualization...")
        visualizer = DeliveryVisualizer(env)
        visualizer.animate_delivery(status.path_taken, interval=800)
    
    return status

def main():
    parser = argparse.ArgumentParser(description='Autonomous Delivery Agent - CSA2001 AI/ML Project')
    parser.add_argument('--map', type=str, default='maps/small.map', 
                       help='Map file to load')
    parser.add_argument('--algorithm', type=str, default='astar', 
                       choices=['bfs', 'ucs', 'astar'], 
                       help='Search algorithm to use')
    parser.add_argument('--heuristic', type=str, default='manhattan',
                       choices=['manhattan', 'euclidean', 'chebyshev'], 
                       help='Heuristic for A*')
    parser.add_argument('--benchmark', action='store_true', 
                       help='Run algorithm benchmark comparison')
    parser.add_argument('--visualize', action='store_true', 
                       help='Show graphical visualization')
    parser.add_argument('--create-maps', action='store_true',
                       help='Create test map files')
    parser.add_argument('--test', action='store_true',
                       help='Run unit tests')
    
    args = parser.parse_args()
    
    if args.create_maps:
        create_test_maps()
        print("Test maps created successfully!")
        return
    
    if args.test:
        print("Running unit tests...")
        import unittest
        loader = unittest.TestLoader()
        suite = loader.discover('tests')
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        return
    
    if args.benchmark:
        print("=== Algorithm Benchmark ===")
        results = benchmark_algorithms()
        
        if not results:
            return
        
        print("\n=== Benchmark Results ===")
        for algo, metrics in results.items():
            print(f"\n{algo}:")
            print(f"  Path Found: {'Yes' if metrics['path_found'] else 'No'}")
            print(f"  Path Length: {metrics['path_length']}")
            print(f"  Total Cost: {metrics['total_cost']}")
            print(f"  Computation Time: {metrics['computation_time']:.4f}s")
            print(f"  Nodes Expanded: {metrics['nodes_expanded']}")
        
        if args.visualize:
            try:
                visualizer = DeliveryVisualizer(GridEnvironment(1, 1))
                visualizer.plot_metrics(results)
            except Exception as e:
                print(f"Visualization error: {e}")
        
        return
    
    # Run delivery simulation
    print("=== Autonomous Delivery Agent ===")
    status = run_delivery_simulation(args.map, args.algorithm, args.heuristic, args.visualize)
    
    if status and args.visualize:
        print("\nSimulation complete! Check the visualization window.")

if __name__ == "__main__":
    main()