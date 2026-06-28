"""Grid pathfinding problem for generic search algorithms."""

from __future__ import annotations


import math

DEFAULT_GRID = (
    "S..#.......",
    ".#.#.#####.",
    ".#...#.....",
    ".###.#.###.",
    "...#...#...",
    "##.#####.#.",
    "...#.....#.",
    ".#.#.###.#.",
    ".#.....#..G",
    "....##.....",
)


class GridPathfindingProblem:
    name = "Grid Pathfinding"

    def __init__(self, grid: tuple[str, ...] = DEFAULT_GRID, heuristic_name: str = "manhattan"):
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0])
        self.start = self._find("S")
        self.goal = self._find("G")
        self.heuristic_name = heuristic_name

    def initial_state(self):
        return self.start

    def is_goal(self, state) -> bool:
        return state == self.goal

    def actions(self, state) -> list[str]:
        r, c = state
        moves = []
        for name, dr, dc in (
            ("UP", -1, 0),
            ("DOWN", 1, 0),
            ("LEFT", 0, -1),
            ("RIGHT", 0, 1),
        ):
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.rows and 0 <= nc < self.cols and self.grid[nr][nc] != "#":
                moves.append(name)
        return moves

    def result(self, state, action):
        r, c = state
        dr, dc = {
            "UP": (-1, 0),
            "DOWN": (1, 0),
            "LEFT": (0, -1),
            "RIGHT": (0, 1),
        }[action]
        return r + dr, c + dc

    def step_cost(self, state, action, next_state) -> float:
        return 1

    def heuristic(self, state) -> float:
        r, c = state
        gr, gc = self.goal
        if self.heuristic_name == "euclidean":
            return math.sqrt((r - gr) ** 2 + (c - gc) ** 2)
        elif self.heuristic_name == "chebyshev":
            return max(abs(r - gr), abs(c - gc))
        elif self.heuristic_name == "dijkstra":
            return 0.0
        else:  # default is manhattan
            return abs(r - gr) + abs(c - gc)

    def state_key(self, state):
        return state

    def _find(self, marker: str) -> tuple[int, int]:
        for r, row in enumerate(self.grid):
            c = row.find(marker)
            if c >= 0:
                return r, c
        raise ValueError(f"Marker {marker!r} not found in grid.")
