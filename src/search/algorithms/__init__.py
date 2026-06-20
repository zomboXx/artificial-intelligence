"""Problem-independent search algorithms."""

from search.algorithms.informed import astar, greedy_best_first, ida_star, uniform_cost
from search.algorithms.local import (
    and_or_graph_search_demo,
    belief_state_demo,
    local_beam_best,
    local_beam_better,
    partial_observation_search,
    random_restart_hill_climbing,
    sensorless_belief_state_search,
    sideways_hill_climbing,
    simple_hill_climbing,
    simulated_annealing,
    steepest_ascent_hill_climbing,
    stochastic_hill_climbing,
)
from search.algorithms.uninformed import bfs, dfs, ids


ALGORITHMS = {
    "BFS": bfs,
    "DFS": dfs,
    "IDS": ids,
    "UCS": uniform_cost,
    "Greedy": greedy_best_first,
    "A*": astar,
    "IDA*": ida_star,
    "Simple HC": simple_hill_climbing,
    "Steepest HC": steepest_ascent_hill_climbing,
    "Stochastic HC": stochastic_hill_climbing,
    "Sideways HC": sideways_hill_climbing,
    "Random Restart HC": random_restart_hill_climbing,
    "Local Beam Better": local_beam_better,
    "Local Beam Best": local_beam_best,
    "Simulated Annealing": simulated_annealing,
    "Sensorless Search": sensorless_belief_state_search,
    "Partial Observation": partial_observation_search,
    "AND-OR Graph": and_or_graph_search_demo,
    "Belief State Demo": belief_state_demo,
}

ALGORITHM_LABELS = {
    "BFS": "BFS (Breadth-First Search)",
    "DFS": "DFS (Depth-First Search)",
    "IDS": "IDS (Iterative Deepening Search)",
    "UCS": "UCS (Uniform Cost Search)",
    "Greedy": "Greedy Best-First Search",
    "A*": "A* Search",
    "IDA*": "IDA* Search",
    "Simple HC": "Simple Hill Climbing",
    "Steepest HC": "Steepest-Ascent Hill Climbing",
    "Stochastic HC": "Stochastic Hill Climbing",
    "Sideways HC": "Sideways Hill Climbing",
    "Random Restart HC": "Random-Restart Hill Climbing",
    "Local Beam Better": "Local Beam Search (k better states)",
    "Local Beam Best": "Local Beam Search (k best states)",
    "Simulated Annealing": "Simulated Annealing",
    "Sensorless Search": "Sensorless / Belief State Search",
    "Partial Observation": "Partial Observation Search",
    "AND-OR Graph": "AND-OR Graph Search",
    "Belief State Demo": "Belief State Search Demo",
}
