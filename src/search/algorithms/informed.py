"""Cost-based and heuristic search algorithms."""

from __future__ import annotations

import heapq

from search.algorithms.common import goal_step, make_step
from search.problem import SearchProblem
from search.types import SearchNode


def uniform_cost(problem: SearchProblem):
    return _priority_search(problem, "UCS", lambda node: node.g)


def greedy_best_first(problem: SearchProblem):
    return _priority_search(problem, "Greedy", lambda node: node.h)


def astar(problem: SearchProblem):
    return _priority_search(problem, "A*", lambda node: node.g + node.h)


def _priority_search(problem: SearchProblem, algorithm: str, priority_fn):
    start_h = problem.heuristic(problem.initial_state())
    start = SearchNode(problem.initial_state(), g=0, h=start_h, f=0, order=0)
    start.f = priority_fn(start)

    heap = [(start.f, start.order, start)]
    best_cost = {problem.state_key(start.state): 0}
    explored_keys = set()
    explored_states = []
    expanded = 0
    generated = 0
    order = 1

    while heap:
        _, _, node = heapq.heappop(heap)
        key = problem.state_key(node.state)

        if key in explored_keys:
            continue
        if node.g > best_cost.get(key, float("inf")):
            continue

        explored_keys.add(key)
        explored_states.append(node.state)
        expanded += 1
        frontier_nodes = [item[2] for item in sorted(heap)]

        yield make_step(node, frontier_nodes, explored_states, expanded, generated, algorithm)

        if problem.is_goal(node.state):
            yield goal_step(node, frontier_nodes, explored_states, expanded, generated, algorithm)
            return

        for action in problem.actions(node.state):
            child_state = problem.result(node.state, action)
            child_key = problem.state_key(child_state)
            step_cost = problem.step_cost(node.state, action, child_state)
            child_g = node.g + step_cost

            if child_key in explored_keys:
                continue
            if child_g >= best_cost.get(child_key, float("inf")):
                continue

            child_h = problem.heuristic(child_state)
            child = SearchNode(
                state=child_state,
                parent=node,
                action=action,
                g=child_g,
                h=child_h,
                depth=node.depth + 1,
                order=order,
            )
            child.f = priority_fn(child)
            order += 1
            generated += 1
            best_cost[child_key] = child_g
            heapq.heappush(heap, (child.f, child.order, child))
