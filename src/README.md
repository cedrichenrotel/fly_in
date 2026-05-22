# Fly-in

*This project has been created as part of the 42 curriculum by cehenrot.*

---

## Description

**Fly-in** is a drone routing simulation system written in Python. The goal is to move an entire fleet of drones from a start zone to an end zone in the fewest possible simulation turns, while respecting strict movement, capacity, and zone-type constraints.

The simulation operates on a graph of connected zones, each with its own type (normal, restricted, priority, blocked), capacity, and color. Drones navigate this graph turn by turn, and the system must schedule their paths to avoid conflicts, deadlocks, and capacity violations.

The project includes:
- A file parser for custom map formats
- A pathfinding engine combining Dijkstra and A* algorithms
- A spatio-temporal reservation system to coordinate multiple drones
- A graphical interface built with the `arcade` library

---

## Project Structure

The project is fully object-oriented. Each file is organized around one or more classes with a single responsibility:

| File | Role |
|------|------|
| `zone.py` | Defines the `Zone` class and the `ZoneType` enum. Contains all the data needed to represent a zone: name, coordinates, type (normal, restricted, priority, blocked), color, and drone capacity. |
| `connection.py` | Defines the `Connection` class, which represents a bidirectional link between two zones, including its maximum drone capacity. |
| `drone.py` | Defines the `Drone` class. Each drone has an ID, a current zone, and a pre-computed path (timeline) assigned before the simulation starts. |
| `graph.py` | Defines the `Graph` class, which ties zones and connections together into a navigable map. It stores the adjacency list and provides neighbor lookup. |
| `algos.py` | Contains the pathfinding algorithms. An abstract base class `Algo` enforces a common interface, with two concrete implementations: `AlgoDijkstra` and `AlgoAstar`. This file is a practical application of object-oriented design using abstract classes and inheritance. |
| `file_parser.py` | Parses the input map file and builds a `Graph` object. Acts as a security layer: it validates all input data (zone names, coordinates, types, capacities) and raises explicit errors on any malformed input to prevent runtime crashes. |
| `simulator.py` | Orchestrates the full simulation. Uses the algorithms on the graph with the drones: pre-computes heuristics, runs spatio-temporal A* for each drone, builds their timelines, and generates the turn-by-turn output. |
| `visualizer.py` | Handles the graphical interface using the `arcade` library. Provides a menu to select maps by difficulty and animates the simulation with drone sprites moving across the graph in real time. |
| `main.py` | Entry point of the program. Creates the window and prints the final simulation output to the terminal. |

---

## Instructions

### Requirements

- Python 3.10 or later
- `arcade` library (and other dependencies listed in `requirements.txt`)

### Installation

```bash
make install
```

This creates a virtual environment and installs all dependencies.

### Run

```bash
make run
```

This launches the graphical interface. A menu lets you select a map by difficulty level. The simulation starts automatically after map selection.

### Debug

```bash
make debug
```

Runs the main script using Python's built-in debugger (`pdb`).

### Lint

```bash
make lint
```

Runs `flake8` and `mypy` with standard type-checking flags.

```bash
make lint-strict
```

Runs `mypy` with `--strict` for enhanced checking.

### Clean

```bash
make clean
```

Removes caches and compiled Python files.

---

## Algorithm Choices and Implementation Strategy

### Step 1 — Reverse Dijkstra (heuristic pre-computation)

Before any drone is routed, a single Dijkstra run is executed **from the end zone backwards** through the entire graph. This produces a dictionary `distances_from_goal`, which stores the real minimum cost to reach the destination from every zone in the graph.

This step is critical: it provides A* with an **admissible heuristic** — one that never overestimates the remaining cost. Because it is computed from real graph distances (not straight-line approximations), it is both admissible and consistent, which guarantees A* finds the optimal path.

### Step 2 — Spatio-temporal A* (per-drone routing)

Each drone is then routed one by one using a **spatio-temporal A*** algorithm. Unlike classical A*, this version does not search in space alone — it searches in **space × time**: each node in the search is a pair `(zone_name, turn)`.

This allows the algorithm to:
- Respect zone capacity constraints at each specific turn
- Allow drones to wait in place when a zone ahead is occupied
- Coordinate multiple drones without conflicts or deadlocks

A global `space_time_reservation` dictionary tracks how many drones will occupy each `(zone, turn)` slot. After each drone's path is computed, its reservations are added to this table so the next drone's A* search avoids those slots.

### Step 3 — Timeline construction

Once a spatio-temporal path is computed for a drone, it is converted into a flat `timeline: List[str]` — a list where index `t` contains the zone (or connection name) the drone occupies at turn `t`. This format is then used by `run_drones` to produce the final turn-by-turn output.

### Visual Representation

The graphical interface is built with `arcade` and consists of two views:

- **MenuView**: displays available maps grouped by difficulty. The user clicks to select a difficulty, then a specific map.
- **SimulationView**: renders the graph (zones as colored ellipses, connections as lines) and animates each drone as a sprite moving turn by turn. When all drones reach the destination, a summary panel displays total drones, total turns, and the full trajectory log.

---

## Resources

### References

- [A* Search Algorithm — Wikipedia](https://en.wikipedia.org/wiki/A*_search_algorithm)
- [Dijkstra's Algorithm — Wikipedia](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm)
- [Spatio-Temporal A* for Multi-Agent Pathfinding](https://en.wikipedia.org/wiki/Multi-agent_pathfinding)
- [Python `heapq` module documentation](https://docs.python.org/3/library/heapq.html)
- [Python-Arcade library documentation](https://api.arcade.academy/)
- [PEP 257 — Docstring Conventions](https://peps.python.org/pep-0257/)
- [mypy documentation](https://mypy.readthedocs.io/)

### AI Usage

AI (Claude, Anthropic) was used during this project for the following purposes:
- Helping structure the overall architecture of the project (class design, file organization)
- Providing guidance when stuck on specific algorithmic problems (spatio-temporal reservation logic, heuristic design)
- Assisting with final code review and identifying inconsistencies (type hints, naming conventions)

All AI-generated suggestions were reviewed, understood, and validated before integration. The core logic, algorithmic choices, and implementation decisions were made independently.