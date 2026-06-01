"""Uninformed search algorithms."""

from __future__ import annotations

from collections import deque

from search.algorithms.common import goal_step, make_step
from search.problem import SearchProblem
from search.types import SearchNode


def bfs(problem: SearchProblem):
    start = SearchNode(problem.initial_state(), order=0)
    frontier = deque([start])
    frontier_keys = {problem.state_key(start.state)}
    explored_keys = set()
    explored_states = []
    expanded = 0
    generated = 0
    order = 1

    while frontier:
        node = frontier.popleft()
        frontier_keys.discard(problem.state_key(node.state))
        key = problem.state_key(node.state)
        if key in explored_keys:
            continue

        explored_keys.add(key)
        explored_states.append(node.state)
        expanded += 1

        yield make_step(node, list(frontier), explored_states, expanded, generated, "BFS")

        if problem.is_goal(node.state):
            yield goal_step(node, list(frontier), explored_states, expanded, generated, "BFS")
            return

        for action in problem.actions(node.state):
            child_state = problem.result(node.state, action)
            child_key = problem.state_key(child_state)
            if child_key in explored_keys or child_key in frontier_keys:
                continue
            child = SearchNode(
                state=child_state,
                parent=node,
                action=action,
                g=node.g + problem.step_cost(node.state, action, child_state),
                depth=node.depth + 1,
                order=order,
            )
            order += 1
            generated += 1
            frontier.append(child)
            frontier_keys.add(child_key)


def dfs(problem: SearchProblem):
    start = SearchNode(problem.initial_state(), order=0)
    frontier = [start]
    frontier_keys = {problem.state_key(start.state)}
    explored_keys = set()
    explored_states = []
    expanded = 0
    generated = 0
    order = 1

    while frontier:
        node = frontier.pop()
        frontier_keys.discard(problem.state_key(node.state))
        key = problem.state_key(node.state)
        if key in explored_keys:
            continue

        explored_keys.add(key)
        explored_states.append(node.state)
        expanded += 1

        yield make_step(node, list(frontier), explored_states, expanded, generated, "DFS")

        if problem.is_goal(node.state):
            yield goal_step(node, list(frontier), explored_states, expanded, generated, "DFS")
            return

        children = []
        for action in problem.actions(node.state):
            child_state = problem.result(node.state, action)
            child_key = problem.state_key(child_state)
            if child_key in explored_keys or child_key in frontier_keys:
                continue
            child = SearchNode(
                state=child_state,
                parent=node,
                action=action,
                g=node.g + problem.step_cost(node.state, action, child_state),
                depth=node.depth + 1,
                order=order,
            )
            order += 1
            generated += 1
            children.append((child_key, child))

        for child_key, child in reversed(children):
            frontier.append(child)
            frontier_keys.add(child_key)


def ids(problem: SearchProblem, max_depth: int = 40):
    expanded_total = 0
    generated_total = 0
    order = 0

    for limit in range(max_depth + 1):
        start = SearchNode(problem.initial_state(), depth=0, order=order)
        order += 1
        stack = [(start, {problem.state_key(start.state)})]
        expanded_this_limit = 0

        while stack:
            node, path_keys = stack.pop()
            expanded_this_limit += 1
            expanded_total += 1
            frontier_nodes = [item[0] for item in stack]
            ancestors = _ancestor_states(node)

            yield make_step(
                node,
                frontier_nodes,
                ancestors,
                expanded_total,
                generated_total,
                "IDS",
                extra={"limit": limit, "depth": node.depth},
                message=f"Depth limit {limit}",
            )

            if problem.is_goal(node.state):
                yield goal_step(
                    node,
                    frontier_nodes,
                    ancestors,
                    expanded_total,
                    generated_total,
                    "IDS",
                    extra={"limit": limit, "depth": node.depth},
                )
                return

            if node.depth >= limit:
                continue

            children = []
            for action in problem.actions(node.state):
                child_state = problem.result(node.state, action)
                child_key = problem.state_key(child_state)
                if child_key in path_keys:
                    continue
                child = SearchNode(
                    state=child_state,
                    parent=node,
                    action=action,
                    g=node.g + problem.step_cost(node.state, action, child_state),
                    depth=node.depth + 1,
                    order=order,
                )
                order += 1
                generated_total += 1
                children.append((child, path_keys | {child_key}))

            for child in reversed(children):
                stack.append(child)

        if expanded_this_limit == 0:
            return


def _ancestor_states(node: SearchNode) -> list:
    states = []
    current = node.parent
    while current is not None:
        states.append(current.state)
        current = current.parent
    return list(reversed(states))
