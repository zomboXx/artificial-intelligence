"""Problem-independent search algorithms."""

from search.algorithms.informed import astar, greedy_best_first, uniform_cost
from search.algorithms.uninformed import bfs, dfs, ids


ALGORITHMS = {
    "BFS": bfs,
    "DFS": dfs,
    "IDS": ids,
    "UCS": uniform_cost,
    "Greedy": greedy_best_first,
    "A*": astar,
}

ALGORITHM_LABELS = {
    "BFS": "BFS (Breadth-First Search)",
    "DFS": "DFS (Depth-First Search)",
    "IDS": "IDS (Iterative Deepening Search)",
    "UCS": "UCS (Uniform Cost Search)",
    "Greedy": "Greedy Best-First Search",
    "A*": "A* Search",
}
