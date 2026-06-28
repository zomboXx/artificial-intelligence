"""Registry that connects problem factories with renderers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from problems.pathfinding.problem import GridPathfindingProblem
from problems.pathfinding import renderer as pathfinding_renderer
from problems.puzzle8.problem import DEFAULT_START_STATE, GOAL_STATE, Puzzle8Problem, generate_solvable_shuffle
from problems.puzzle8 import renderer as puzzle8_renderer
from problems.queens8.problem import Queens8Problem
from problems.queens8 import renderer as queens8_renderer


@dataclass(frozen=True)
class ProblemSpec:
    key: str
    label: str
    description: str
    algorithms: tuple[str, ...]
    factory: Callable[[dict], object]
    renderer: object
    default_options: dict


def _puzzle_factory(options: dict):
    start = generate_solvable_shuffle() if options.get("shuffle") else DEFAULT_START_STATE
    return Puzzle8Problem(
        start_state=start,
        goal_state=GOAL_STATE,
        weighted_cost=options.get("weighted_cost", False),
        heuristic_name=options.get("heuristic", "manhattan"),
    )


def _pathfinding_factory(options: dict):
    from problems.pathfinding.problem import DEFAULT_GRID
    grid = options.get("grid", DEFAULT_GRID)
    heuristic = options.get("heuristic", "manhattan")
    return GridPathfindingProblem(grid=grid, heuristic_name=heuristic)


def _queens_factory(options: dict):
    return Queens8Problem(size=int(options.get("size", 8)))


PROBLEMS = {
    "puzzle8": ProblemSpec(
        key="puzzle8",
        label="8-Puzzle",
        description="Classic sliding tile state-space search problem.",
        algorithms=(
            "BFS", "DFS", "IDS", "UCS", "Greedy", "A*", "IDA*",
            "Simple HC", "Steepest HC", "Stochastic HC", "Sideways HC",
            "Random Restart HC", "Local Beam Better", "Local Beam Best",
            "Simulated Annealing", "Sensorless Search", "Partial Observation",
            "AND-OR Graph", "Belief State Demo",
        ),
        factory=_puzzle_factory,
        renderer=puzzle8_renderer,
        default_options={"shuffle": False, "weighted_cost": False, "heuristic": "manhattan"},
    ),
    "pathfinding": ProblemSpec(
        key="pathfinding",
        label="Grid Pathfinding",
        description="Find a route across a blocked grid, similar to map path planning.",
        algorithms=("BFS", "DFS", "IDS", "UCS", "Greedy", "A*", "IDA*", "Simple HC", "Steepest HC", "Stochastic HC"),
        factory=_pathfinding_factory,
        renderer=pathfinding_renderer,
        default_options={"grid": None, "heuristic": "manhattan"},
    ),
    "queens8": ProblemSpec(
        key="queens8",
        label="8-Queens",
        description="Place 8 queens so no two attack each other.",
        algorithms=("BFS", "DFS", "IDS", "UCS", "Greedy", "A*", "IDA*", "Simple HC", "Steepest HC", "Stochastic HC"),
        factory=_queens_factory,
        renderer=queens8_renderer,
        default_options={"size": 8},
    ),
}
