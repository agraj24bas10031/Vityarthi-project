Autonomous Delivery Agent
An AI-powered delivery agent that navigates 2D grid cities using various path planning algorithms. This project implements and compares multiple AI search strategies for autonomous package delivery with static and dynamic obstacles.

Features
Multiple Path Planning Algorithms: BFS, UCS, A*, and Local Search
Dynamic Obstacle Avoidance: Real-time replanning for moving obstacles
Terrain Cost Modeling: Different movement costs (1-3) for various terrains
Fuel Constraints: Limited energy resources for realistic simulation
Performance Metrics: Comprehensive tracking of efficiency measures
4-Connected Movement: Up, down, left, right movements
Visualization: ASCII-based environment display
Algorithms Implemented
Algorithm	Type	Strengths	Best Use Case
BFS	Uninformed	Complete, simple	Small maps with uniform costs
UCS	Uninformed	Optimal for weighted graphs	Medium maps with varying terrain
A*	Informed	Optimal and efficient	Most static environments
Local Search	Local	Fast, adaptable	Dynamic environments with obstacles
Installation
# Clone the repository
git clone <repository-url>
cd autonomous_delivery_agent

# Install dependencies
pip install -r requirements.txt
# Run with A* planner on small map
python run_agent.py --map maps/small.map --planner astar --start 0 0

# Run with dynamic obstacles using local search
python run_agent.py --map maps/dynamic.map --planner local --start 0 0

# Custom packages and fuel capacity
python run_agent.py --map maps/medium.map --planner ucs --start 2 2 --packages 1 1 8 8 --fuel 150
autonomous_delivery_agent/
├── maps/                 # Grid map files
│   ├── small.map        # 10x10 - Basic testing
│   ├── medium.map       # 15x15 - Moderate complexity
│   ├── large.map        # 20x20 - Scalability testing
│   └── dynamic.map      # 10x10 - Moving obstacles
├── src/                  # Core source code
│   ├── environment.py   # Grid world modeling
│   ├── agent.py         # Delivery agent logic
│   ├── utils.py         # Utility functions
│   └── planners/        # Search algorithms
│       ├── uninformed.py # BFS, Uniform Cost Search
│       ├── informed.py   # A* Search
│       └── local_search.py # Local Search
├── tests/               # Unit tests
│   ├── test_environment.py
│   ├── test_planners.py
│   └── test_agent.py
├── run_agent.py         # Main execution script
├── requirements.txt     # Python dependencies
└── README.md           # This file
# Example: maps/small.map
10 10                    # Grid dimensions (width height)

TERRAIN
1 1 1 1 1 1 1 1 1 1     # Terrain costs matrix
1 2 2 1 3 3 1 2 2 1     # 1=plain, 2=grass, 3=sand
1 2 2 1 3 3 1 2 2 1
1 1 1 1 1 1 1 1 1 1
...                     # 10x10 grid

OBSTACLES
3 3                      # Static obstacle positions (x y)
3 4
4 3
4 4

PACKAGES
1 1 8 8                  # Package: pickup_x pickup_y delivery_x delivery_y

DYNAMIC_OBSTACLES
1 1 2 1 3 1 4 1         # Moving obstacle path coordinates
0 2 4 6 8               # Time steps when obstacle appears
# Run all tests
python -m pytest tests/

# Run specific test category with verbose output
python -m pytest tests/test_planners.py -v
python -m pytest tests/test_environment.py -v
python -m pytest tests/test_agent.py -v

# Run with coverage report
python -m pytest tests/ --cov=src

Starting delivery mission with astar planner...
Map: maps/small.map
Start position: (0, 0)
Fuel capacity: 100
Number of packages: 1
--------------------------------------------------
Package picked up at time step 12
Package delivered at time step 24

MISSION RESULTS
==================================================
Planner: ASTAR
Deliveries completed: 1/1
Total cost: 24
Total nodes expanded: 45
Total planning time: 0.015s
Replanning events: 0
Mission time: 0.235s
Final position: (8, 8)
Remaining fuel: 76
Final time step: 24
Key Features Implementation 🔧
Environment Modeling
Grid-based world with customizable dimensions

Terrain costs affecting movement efficiency

Static obstacles as permanent barriers

Dynamic obstacles with scheduled movements

Temporal planning for obstacle avoidance

Agent Capabilities
State management (Idle, Picking Up, Delivering, Replanning)

Fuel-aware navigation with energy constraints

Real-time replanning when encountering obstacles

Multiple package delivery in single mission

Search Algorithms
BFS: Complete but memory-intensive

UCS: Optimal for weighted graphs

A*: Optimal and efficient with admissible heuristic

Local Search: Fast adaptation to dynamic changes

Dependencies 📦
Python 3.8 or higher

pytest (for testing)

(Optional) matplotlib for advanced visualization
Add to requirements.txt:
pytest>=7.0.0
Usage Examples 💡
Example 1: Basic Delivery
bash
python run_agent.py --map maps/small.map --planner astar --start 0 0
Example 2: Multiple Packages
bash
python run_agent.py --map maps/medium.map --planner ucs --start 2 2 --packages 1 1 8 8 --packages 3 3 6 6
Example 3: Dynamic Environment
bash
python run_agent.py --map maps/dynamic.map --planner local --start 0 0 --fuel 200
Troubleshooting 🔧
Common Issues
Import errors: Make sure you're running from project root directory

Map file not found: Use relative paths from project root

No path found: Check if start/delivery points are not blocked by obstacles

Debug Mode
Add print statements in src/agent.py to track agent movement and decisions.
Contributing 🤝
Fork the repository

Create a feature branch (git checkout -b feature/amazing-feature)

Commit changes (git commit -m 'Add amazing feature')

Push to branch (git push origin feature/amazing-feature)

Open a Pull Request

License 📄
This project is licensed under the MIT License - see for educational and research purposes.

Course Information 🎓
Course: CSA2001 - Fundamentals of AI and ML
Project Type: Project-Based Learning
Academic Project: Autonomous Delivery Agent with Path Planning Algorithms

Support 💬
For issues or questions:

Check the test cases in /tests directory

Review map file format specifications

Examine example commands in this README

Run with simple configurations first
