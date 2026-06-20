"""Local search algorithms."""

from __future__ import annotations

import math
import random

from search.algorithms.common import goal_step, make_step
from search.problem import SearchProblem
from search.types import SearchNode, SearchStep


def simple_hill_climbing(problem: SearchProblem):
    return _hill_climbing(problem, "Simple HC", "simple")


def steepest_ascent_hill_climbing(problem: SearchProblem):
    return _hill_climbing(problem, "Steepest HC", "steepest")


def stochastic_hill_climbing(problem: SearchProblem):
    return _hill_climbing(problem, "Stochastic HC", "stochastic")


def sideways_hill_climbing(problem: SearchProblem):
    return _hill_climbing(problem, "Sideways HC", "sideways")


def random_restart_hill_climbing(problem: SearchProblem, max_restart: int = 25):
    expanded = 0
    generated = 0
    best_state = _local_initial_state(problem)
    best_h = _local_heuristic(problem, best_state)
    explored = []

    for restart in range(max_restart + 1):
        state = best_state if restart == 0 else _local_random_state(problem, restart)
        h = _local_heuristic(problem, state)
        node = SearchNode(state=state, h=h, f=h, order=restart)

        while True:
            current_h = _local_heuristic(problem, state)
            explored.append(state)
            if current_h < best_h:
                best_state = state
                best_h = current_h

            if _local_is_goal(problem, state):
                yield goal_step(
                    node,
                    [],
                    explored,
                    expanded,
                    generated,
                    "Random Restart HC",
                    extra={"restart": restart, "h": current_h, "local": True},
                )
                return

            neighbor_nodes = _build_local_neighbor_nodes(problem, node, order_offset=generated)
            generated += len(neighbor_nodes)
            better = [candidate for candidate in neighbor_nodes if candidate.h < current_h]

            if not better:
                yield make_step(
                    node,
                    neighbor_nodes,
                    explored,
                    expanded,
                    generated,
                    "Random Restart HC",
                    extra={
                        "restart": restart,
                        "h": current_h,
                        "best_h": best_h,
                        "candidate_count": len(neighbor_nodes),
                        "local": True,
                        "restart_stuck": True,
                    },
                    message=f"Restart {restart} stuck; trying another start.",
                )
                break

            chosen = min(better, key=lambda candidate: candidate.h)
            expanded += 1
            yield make_step(
                node,
                neighbor_nodes,
                explored,
                expanded,
                generated,
                "Random Restart HC",
                extra={
                    "restart": restart,
                    "h": current_h,
                    "chosen_h": chosen.h,
                    "candidate_count": len(neighbor_nodes),
                    "local": True,
                },
                message=f"Restart {restart}: climbing.",
            )
            node = chosen
            state = chosen.state

    yield make_step(
        SearchNode(state=best_state, h=best_h, f=best_h),
        [],
        explored,
        expanded,
        generated,
        "Random Restart HC",
        extra={"best_h": best_h, "local": True, "stuck": True},
        message=f"Max restart reached; best h={best_h}.",
    )


def simulated_annealing(
    problem: SearchProblem,
    initial_temperature: float = 2.0,
    cooling_rate: float = 0.94,
    min_temperature: float = 0.001,
    max_steps: int = 500,
):
    state = _local_initial_state(problem)
    h = _local_heuristic(problem, state)
    node = SearchNode(state=state, h=h, f=h, order=0)
    temperature = initial_temperature
    expanded = 0
    generated = 0
    explored = []
    order = 1

    for step_index in range(max_steps + 1):
        explored.append(state)

        if _local_is_goal(problem, state):
            yield goal_step(
                node,
                [],
                explored,
                expanded,
                generated,
                "Simulated Annealing",
                extra={
                    "temperature": round(temperature, 4),
                    "h": h,
                    "local": True,
                },
            )
            return

        if temperature <= min_temperature:
            yield make_step(
                node,
                [],
                explored,
                expanded,
                generated,
                "Simulated Annealing",
                extra={
                    "temperature": round(temperature, 4),
                    "h": h,
                    "local": True,
                    "stuck": True,
                },
                message="Temperature reached Tmin.",
            )
            return

        neighbor_nodes = _build_local_neighbor_nodes(problem, node, order)
        order += len(neighbor_nodes)
        generated += len(neighbor_nodes)

        if not neighbor_nodes:
            yield make_step(
                node,
                [],
                explored,
                expanded,
                generated,
                "Simulated Annealing",
                extra={"temperature": round(temperature, 4), "h": h, "local": True, "stuck": True},
                message="No neighbors available.",
            )
            return

        candidate = random.choice(neighbor_nodes)
        delta = candidate.h - h
        if delta < 0:
            probability = 1.0
            roll = None
            accepted = True
            decision = "accepted directly because delta < 0"
        else:
            probability = math.exp(-delta / temperature)
            roll = random.random()
            accepted = roll < probability
            decision = f"{'accepted' if accepted else 'rejected'} by probability"

        yield make_step(
            node,
            neighbor_nodes,
            explored,
            expanded,
            generated,
            "Simulated Annealing",
            extra={
                "temperature": round(temperature, 4),
                "alpha": cooling_rate,
                "tmin": min_temperature,
                "step": step_index,
                "h": h,
                "candidate_h": candidate.h,
                "delta": delta,
                "probability": round(probability, 4),
                "roll": None if roll is None else round(roll, 4),
                "accepted": accepted,
                "local": True,
            },
            message=f"Sampled {candidate.action}: {decision}.",
        )

        if accepted:
            node = candidate
            state = candidate.state
            h = candidate.h
            expanded += 1

        temperature *= cooling_rate

    yield make_step(
        node,
        [],
        explored,
        expanded,
        generated,
        "Simulated Annealing",
        extra={"temperature": round(temperature, 4), "h": h, "local": True, "stuck": True},
        message="Stopped at max_steps.",
    )


def sensorless_belief_state_search(problem: SearchProblem, max_steps: int = 12, sample_limit: int = 240):
    true_state = _local_initial_state(problem)
    known = {}
    belief = _belief_from_known(problem, known, limit=sample_limit)
    explored = []
    expanded = 0
    generated = 0
    hidden_goal = _unknown_pattern_state()

    for _ in range(max_steps + 1):
        pattern = _belief_pattern_state(known)
        stats = _belief_stats(problem, belief)
        explored.append(pattern)

        if _local_is_goal(problem, true_state):
            yield SearchStep(
                current=true_state,
                frontier=[],
                explored=explored,
                path=[true_state],
                metrics={
                    "algorithm": "Sensorless Search",
                    "expanded": expanded,
                    "generated": generated,
                    "depth": expanded,
                    "g": 0,
                    "h": 0,
                    "f": 0,
                    "frontier_size": 0,
                    "explored_size": len(explored),
                    "belief_size": len(belief),
                    "belief_theory": _belief_count_from_known(known),
                    "known_tiles": len(known),
                    "display_start": pattern,
                    "display_goal": hidden_goal,
                    "knowledge_model": "No visible start/goal; no observation after actions",
                },
                message="Hidden true state reached the goal.",
            )
            return

        possible_actions = _belief_union_actions(problem, belief)
        if not possible_actions:
            yield SearchStep(
                current=pattern,
                frontier=[],
                explored=explored,
                path=None,
                metrics={
                    "algorithm": "Sensorless Search",
                    "expanded": expanded,
                    "generated": generated,
                    "depth": expanded,
                    "g": 0,
                    "h": stats["min"],
                    "f": stats["min"],
                    "frontier_size": 0,
                    "explored_size": len(explored),
                    "belief_size": len(belief),
                    "belief_theory": _belief_count_from_known(known),
                    "known_tiles": len(known),
                    "display_start": pattern,
                    "display_goal": hidden_goal,
                    "knowledge_model": "No visible start/goal; no observation after actions",
                    "stuck": True,
                },
                message="No action can be generated from the current belief sample.",
            )
            return

        candidates = []
        for action in possible_actions:
            transitioned = _belief_attempt_transition(problem, belief, action)
            generated += len(transitioned)
            if not transitioned:
                continue

            next_stats = _belief_stats(problem, transitioned)
            representative = min(transitioned, key=lambda candidate: (problem.heuristic(candidate), candidate))
            candidates.append(
                {
                    "state": representative,
                    "action": action,
                    "belief": transitioned,
                    "avg_h": next_stats["avg"],
                    "min_h": next_stats["min"],
                    "max_h": next_stats["max"],
                }
            )

        if not candidates:
            yield SearchStep(
                current=pattern,
                frontier=[],
                explored=explored,
                path=None,
                metrics={
                    "algorithm": "Sensorless Search",
                    "expanded": expanded,
                    "generated": generated,
                    "depth": expanded,
                    "g": 0,
                    "h": stats["min"],
                    "f": stats["min"],
                    "frontier_size": 0,
                    "explored_size": len(explored),
                    "belief_size": len(belief),
                    "belief_theory": _belief_count_from_known(known),
                    "known_tiles": len(known),
                    "display_start": pattern,
                    "display_goal": hidden_goal,
                    "knowledge_model": "No visible start/goal; no observation after actions",
                    "stuck": True,
                },
                message="Every sampled candidate was removed.",
            )
            return

        candidates.sort(key=lambda item: (item["avg_h"], item["min_h"], item["action"]))
        chosen = candidates[0]
        frontier_states = [candidate["state"] for candidate in candidates]

        yield SearchStep(
            current=pattern,
            frontier=frontier_states,
            explored=explored,
            path=None,
            metrics={
                "algorithm": "Sensorless Search",
                "expanded": expanded,
                "generated": generated,
                "depth": expanded,
                "g": 0,
                "h": stats["min"],
                "f": stats["min"],
                "frontier_size": len(frontier_states),
                "explored_size": len(explored),
                "belief_size": len(belief),
                "belief_theory": _belief_count_from_known(known),
                "known_tiles": len(known),
                "display_start": pattern,
                "display_goal": hidden_goal,
                "knowledge_model": "No visible start/goal; no observation after actions",
                "chosen_action": chosen["action"],
                "belief_avg_h": round(chosen["avg_h"], 2),
                "local": True,
            },
            message=(
                f"Sensorless: try {chosen['action']} without observing any tile; "
                f"update only the belief sample of {len(belief)} states."
            ),
        )

        if chosen["action"] in problem.actions(true_state):
            true_state = problem.result(true_state, chosen["action"])
        belief = chosen["belief"]
        expanded += 1

    stats = _belief_stats(problem, belief)
    pattern = _belief_pattern_state(known)
    yield SearchStep(
        current=pattern,
        frontier=[],
        explored=explored,
        path=None,
        metrics={
            "algorithm": "Sensorless Search",
            "expanded": expanded,
            "generated": generated,
            "depth": expanded,
            "g": 0,
            "h": stats["min"],
            "f": stats["min"],
            "frontier_size": 0,
            "explored_size": len(explored),
            "belief_size": len(belief),
            "belief_theory": _belief_count_from_known(known),
            "known_tiles": len(known),
            "display_start": pattern,
            "display_goal": hidden_goal,
            "knowledge_model": "No visible start/goal; no observation after actions",
            "stuck": True,
        },
        message="Stopped at max_steps.",
    )


def partial_observation_search(problem: SearchProblem, max_steps: int = 20):
    yield from _belief_state_demo(problem, max_steps=max_steps, algorithm="Partial Observation")


def and_or_graph_search_demo(problem: SearchProblem, max_steps: int = 18):
    state = _local_initial_state(problem)
    explored = [state]
    expanded = 0
    generated = 0
    plan = _and_or_plan(problem, state, depth_limit=5)

    yield SearchStep(
        current=state,
        frontier=[],
        explored=explored,
        path=None,
        metrics={
            "algorithm": "AND-OR Graph",
            "expanded": expanded,
            "generated": generated,
            "depth": 0,
            "g": 0,
            "h": _local_heuristic(problem, state),
            "f": _local_heuristic(problem, state),
            "frontier_size": 0,
            "explored_size": len(explored),
            "plan_found": plan is not None,
        },
        message="OR node is the agent action; AND node is the set of possible outcomes.",
    )

    for depth in range(1, max_steps + 1):
        if _local_is_goal(problem, state):
            yield SearchStep(
                current=state,
                frontier=[],
                explored=explored,
                path=explored,
                metrics={
                    "algorithm": "AND-OR Graph",
                    "expanded": expanded,
                    "generated": generated,
                    "depth": depth,
                    "g": depth,
                    "h": 0,
                    "f": depth,
                    "frontier_size": 0,
                    "explored_size": len(explored),
                    "plan_found": plan is not None,
                },
                message="Goal reached under one sampled nondeterministic execution.",
            )
            return

        action_rows = []
        for action in problem.actions(state):
            outcomes = _nondeterministic_results(problem, state, action)
            generated += len(outcomes)
            worst_h = max(_local_heuristic(problem, outcome) for outcome in outcomes)
            best_h = min(_local_heuristic(problem, outcome) for outcome in outcomes)
            action_rows.append((action, worst_h, best_h, outcomes))

        if not action_rows:
            yield SearchStep(
                current=state,
                frontier=[],
                explored=explored,
                path=None,
                metrics={
                    "algorithm": "AND-OR Graph",
                    "expanded": expanded,
                    "generated": generated,
                    "depth": depth,
                    "g": depth,
                    "h": _local_heuristic(problem, state),
                    "f": depth + _local_heuristic(problem, state),
                    "frontier_size": 0,
                    "explored_size": len(explored),
                    "plan_found": plan is not None,
                    "stuck": True,
                },
                message="No action is available.",
            )
            return

        action_rows.sort(key=lambda item: (item[1], item[2], item[0]))
        selected_action, worst_h, _, outcomes = action_rows[0]
        frontier_states = []
        for _, _, _, row_outcomes in action_rows:
            frontier_states.extend(row_outcomes)

        yield SearchStep(
            current=state,
            frontier=frontier_states,
            explored=explored,
            path=None,
            metrics={
                "algorithm": "AND-OR Graph",
                "expanded": expanded,
                "generated": generated,
                "depth": depth,
                "g": depth,
                "h": _local_heuristic(problem, state),
                "f": depth + _local_heuristic(problem, state),
                "frontier_size": len(frontier_states),
                "explored_size": len(explored),
                "chosen_action": selected_action,
                "and_outcomes": len(outcomes),
                "worst_h": worst_h,
                "plan_found": plan is not None,
                "local": True,
            },
            message=(
                f"OR chooses {selected_action}; AND node contains {len(outcomes)} possible outcomes. "
                "The demo samples one environment result."
            ),
        )

        state = random.choice(outcomes)
        explored.append(state)
        expanded += 1

    yield SearchStep(
        current=state,
        frontier=[],
        explored=explored,
        path=None,
        metrics={
            "algorithm": "AND-OR Graph",
            "expanded": expanded,
            "generated": generated,
            "depth": max_steps,
            "g": max_steps,
            "h": _local_heuristic(problem, state),
            "f": max_steps + _local_heuristic(problem, state),
            "frontier_size": 0,
            "explored_size": len(explored),
            "plan_found": plan is not None,
            "stuck": True,
        },
        message="Stopped at max_steps.",
    )


def belief_state_demo(problem: SearchProblem, max_steps: int = 20):
    yield from _belief_state_demo(problem, max_steps=max_steps, algorithm="Belief State Demo")


def _belief_state_demo(problem: SearchProblem, max_steps: int = 20, algorithm: str = "Belief State Demo"):
    state = _local_initial_state(problem)
    observed_tiles = _belief_observed_tiles(state)
    known = _belief_observation(state, observed_tiles)
    belief = _belief_from_known(problem, known)
    true_state = state
    start_pattern = _belief_pattern_state(known)
    goal_known = _belief_observation(getattr(problem, "goal_state", state), observed_tiles)
    goal_pattern = _belief_pattern_state(goal_known)

    expanded = 0
    generated = 0
    explored = []

    for _ in range(max_steps + 1):
        explored.append(_belief_pattern_state(known))
        stats = _belief_stats(problem, belief)
        current_pattern = _belief_pattern_state(known)
        current_h = stats["min"]

        if _local_is_goal(problem, true_state):
            yield SearchStep(
                current=true_state,
                frontier=[],
                explored=explored,
                path=[true_state],
                metrics={
                    "algorithm": algorithm,
                    "expanded": expanded,
                    "generated": generated,
                    "depth": expanded,
                    "g": 0,
                    "h": 0,
                    "f": 0,
                    "frontier_size": 0,
                    "explored_size": len(explored),
                    "belief_size": len(belief),
                    "belief_theory": _belief_count_from_known(known),
                    "known_tiles": len(known),
                    "display_start": start_pattern,
                    "display_goal": goal_pattern,
                    "knowledge_model": "Partial observation; reveal the moved tile after each action",
                },
                message="Hidden true state reached the goal.",
            )
            return

        common_actions = _belief_common_actions(problem, belief)
        true_actions = set(problem.actions(true_state))
        actions = [action for action in common_actions if action in true_actions]

        if not actions:
            yield SearchStep(
                current=current_pattern,
                frontier=[],
                explored=explored,
                path=None,
                metrics={
                    "algorithm": algorithm,
                    "expanded": expanded,
                    "generated": generated,
                    "depth": expanded,
                    "g": 0,
                    "h": current_h,
                    "f": current_h,
                    "frontier_size": 0,
                    "explored_size": len(explored),
                    "belief_size": len(belief),
                    "belief_theory": _belief_count_from_known(known),
                    "known_tiles": len(known),
                    "display_start": start_pattern,
                    "display_goal": goal_pattern,
                    "knowledge_model": "Partial observation; reveal the moved tile after each action",
                    "stuck": True,
                },
                message="No action is legal for both the belief state and hidden true state.",
            )
            return

        candidates = []
        for action in actions:
            transitioned = _belief_transition(problem, belief, action)
            generated += len(transitioned)
            next_true = problem.result(true_state, action)
            moved_tile = _moved_tile(problem, true_state, action)
            next_known = dict(known)
            next_known.update(_belief_observation(next_true, (0, moved_tile)))
            filtered = _belief_filter(transitioned, next_known)
            if not filtered:
                continue

            next_stats = _belief_stats(problem, filtered)
            representative = min(filtered, key=lambda candidate_state: (problem.heuristic(candidate_state), candidate_state))
            candidates.append(
                {
                    "state": representative,
                    "action": action,
                    "belief": filtered,
                    "true_state": next_true,
                    "known": next_known,
                    "moved_tile": moved_tile,
                    "before": len(transitioned),
                    "after": len(filtered),
                    "min_h": next_stats["min"],
                    "avg_h": next_stats["avg"],
                    "max_h": next_stats["max"],
                }
            )

        if not candidates:
            yield SearchStep(
                current=current_pattern,
                frontier=[],
                explored=explored,
                path=None,
                metrics={
                    "algorithm": algorithm,
                    "expanded": expanded,
                    "generated": generated,
                    "depth": expanded,
                    "g": 0,
                    "h": current_h,
                    "f": current_h,
                    "frontier_size": 0,
                    "explored_size": len(explored),
                    "belief_size": len(belief),
                    "belief_theory": _belief_count_from_known(known),
                    "known_tiles": len(known),
                    "display_start": start_pattern,
                    "display_goal": goal_pattern,
                    "knowledge_model": "Partial observation; reveal the moved tile after each action",
                    "stuck": True,
                },
                message="Observation removed every candidate state.",
            )
            return

        candidates.sort(key=lambda item: (item["avg_h"], item["min_h"], item["after"], item["action"]))
        chosen = candidates[0]
        frontier_states = [candidate["state"] for candidate in candidates]

        yield SearchStep(
            current=current_pattern,
            frontier=frontier_states,
            explored=explored,
            path=None,
            metrics={
                "algorithm": algorithm,
                "expanded": expanded,
                "generated": generated,
                "depth": expanded,
                "g": 0,
                "h": current_h,
                "f": current_h,
                "frontier_size": len(frontier_states),
                "explored_size": len(explored),
                "belief_size": len(belief),
                "belief_theory": _belief_count_from_known(known),
                "known_tiles": len(known),
                "display_start": start_pattern,
                "display_goal": goal_pattern,
                "knowledge_model": "Partial observation; reveal the moved tile after each action",
                "chosen_action": chosen["action"],
                "revealed_tile": chosen["moved_tile"],
                "belief_after": chosen["after"],
                "belief_before_filter": chosen["before"],
                "belief_avg_h": round(chosen["avg_h"], 2),
                "local": True,
            },
            message=(
                f"Choose {chosen['action']}; reveal tile {chosen['moved_tile']}; "
                f"belief {chosen['before']} -> {chosen['after']}."
            ),
        )

        belief = chosen["belief"]
        known = chosen["known"]
        true_state = chosen["true_state"]
        expanded += 1

    stats = _belief_stats(problem, belief)
    yield SearchStep(
        current=_belief_pattern_state(known),
        frontier=[],
        explored=explored,
        path=None,
        metrics={
            "algorithm": algorithm,
            "expanded": expanded,
            "generated": generated,
            "depth": expanded,
            "g": 0,
            "h": stats["min"],
            "f": stats["min"],
            "frontier_size": 0,
            "explored_size": len(explored),
            "belief_size": len(belief),
            "belief_theory": _belief_count_from_known(known),
            "known_tiles": len(known),
            "display_start": start_pattern,
            "display_goal": goal_pattern,
            "knowledge_model": "Partial observation; reveal the moved tile after each action",
            "stuck": True,
        },
        message="Stopped at max_steps.",
    )


def local_beam_best(problem: SearchProblem, beam_width: int = 2):
    return _local_beam(problem, "Local Beam Best", beam_width, better_only=False)


def local_beam_better(problem: SearchProblem, beam_width: int = 2):
    return _local_beam(problem, "Local Beam Better", beam_width, better_only=True)


def _hill_climbing(problem: SearchProblem, algorithm: str, variant: str, sideways_limit: int = 20):
    state = _local_initial_state(problem)
    h = _local_heuristic(problem, state)
    node = SearchNode(state=state, h=h, f=h, order=0)
    expanded = 0
    generated = 0
    order = 1
    sideways_used = 0

    yield make_step(node, [], [], expanded, generated, algorithm, extra={"h": h, "local": True})

    while True:
        if _local_is_goal(problem, state):
            yield goal_step(node, [], [], expanded, generated, algorithm, extra={"local": True})
            return

        expanded += 1
        neighbor_nodes = _build_local_neighbor_nodes(problem, node, order)
        order += len(neighbor_nodes)

        generated += len(neighbor_nodes)
        current_h = node.h
        better = [candidate for candidate in neighbor_nodes if candidate.h < current_h]
        equal = [candidate for candidate in neighbor_nodes if candidate.h == current_h]

        if variant == "simple":
            chosen = better[0] if better else None
        elif variant == "stochastic":
            chosen = random.choice(better) if better else None
        elif variant == "sideways":
            if better:
                chosen = random.choice(better)
            elif sideways_used < sideways_limit and equal:
                chosen = random.choice(equal)
            else:
                chosen = None
        else:
            chosen = min(better, key=lambda candidate: candidate.h, default=None)

        yield make_step(
            node,
            neighbor_nodes,
            [],
            expanded,
            generated,
            algorithm,
            extra={
                "h": current_h,
                "candidate_count": len(neighbor_nodes),
                "chosen_h": chosen.h if chosen else None,
                "sideways": sideways_used,
                "sideways_limit": sideways_limit if variant == "sideways" else None,
                "local": True,
            },
            message="Evaluating local neighbors.",
        )

        if chosen is None:
            yield make_step(
                node,
                neighbor_nodes,
                [],
                expanded,
                generated,
                algorithm,
                extra={"h": current_h, "local": True, "stuck": True},
                message="Stuck at a local optimum or plateau.",
            )
            return

        node = chosen
        state = node.state
        if variant == "sideways" and node.h == current_h:
            sideways_used += 1
        else:
            sideways_used = 0


def _local_beam(problem: SearchProblem, algorithm: str, beam_width: int, better_only: bool):
    start_state = _local_initial_state(problem)
    start_h = _local_heuristic(problem, start_state)
    beam_nodes = [SearchNode(state=start_state, h=start_h, f=start_h, order=0)]
    expanded = 0
    generated = 0
    explored = []
    seen_beams = {tuple(problem.state_key(node.state) for node in beam_nodes)}
    order = 1

    while True:
        explored.extend(node.state for node in beam_nodes)
        goal_node = next((node for node in beam_nodes if _local_is_goal(problem, node.state)), None)
        current_node = goal_node or beam_nodes[0]

        if goal_node is not None:
            yield goal_step(
                goal_node,
                beam_nodes,
                explored,
                expanded,
                generated,
                algorithm,
                extra={"beam_width": beam_width, "beam_size": len(beam_nodes), "local": True},
            )
            return

        candidates = []
        for parent_index, parent_node in enumerate(beam_nodes):
            parent_h = parent_node.h
            for action, child_state in _local_neighbors(problem, parent_node.state):
                child_h = _local_heuristic(problem, child_state)
                if better_only and child_h >= parent_h:
                    continue
                candidates.append(
                    SearchNode(
                        state=child_state,
                        parent=parent_node,
                        action=action,
                        h=child_h,
                        f=child_h,
                        depth=parent_node.depth + 1,
                        order=order,
                    )
                )
                order += 1

        generated += len(candidates)
        if not candidates:
            yield make_step(
                current_node,
                [],
                explored,
                expanded,
                generated,
                algorithm,
                extra={"beam_width": beam_width, "beam_size": len(beam_nodes), "local": True, "stuck": True},
                message="Beam has no candidates.",
            )
            return

        candidates.sort(key=lambda node: (node.h, node.order))
        chosen = []
        chosen_keys = set()
        for candidate in candidates:
            key = problem.state_key(candidate.state)
            if key in chosen_keys:
                continue
            chosen.append(candidate)
            chosen_keys.add(key)
            if len(chosen) == beam_width:
                break

        signature = tuple(problem.state_key(node.state) for node in chosen)
        expanded += len(beam_nodes)

        yield make_step(
            current_node,
            candidates,
            explored,
            expanded,
            generated,
            algorithm,
            extra={
                "beam_width": beam_width,
                "beam_size": len(chosen),
                "candidate_count": len(candidates),
                "best_h": chosen[0].h if chosen else None,
                "local": True,
            },
            message=f"Selected {len(chosen)}/{beam_width} beam states.",
        )

        if signature in seen_beams:
            yield make_step(
                current_node,
                candidates,
                explored,
                expanded,
                generated,
                algorithm,
                extra={"beam_width": beam_width, "beam_size": len(chosen), "local": True, "stuck": True},
                message="Beam repeated; stopping.",
            )
            return

        seen_beams.add(signature)
        beam_nodes = chosen


def _build_local_neighbor_nodes(problem, node: SearchNode, order_offset: int):
    neighbor_nodes = []
    order = order_offset
    for action, neighbor_state in _local_neighbors(problem, node.state):
        nh = _local_heuristic(problem, neighbor_state)
        neighbor_nodes.append(
            SearchNode(
                state=neighbor_state,
                parent=node,
                action=action,
                h=nh,
                f=nh,
                depth=node.depth + 1,
                order=order,
            )
        )
        order += 1
    return neighbor_nodes


def _local_initial_state(problem):
    if hasattr(problem, "local_initial_state"):
        return problem.local_initial_state()
    return problem.initial_state()


def _local_is_goal(problem, state) -> bool:
    if hasattr(problem, "local_is_goal"):
        return problem.local_is_goal(state)
    return problem.is_goal(state)


def _local_heuristic(problem, state) -> float:
    if hasattr(problem, "local_heuristic"):
        return problem.local_heuristic(state)
    return problem.heuristic(state)


def _local_neighbors(problem, state):
    if hasattr(problem, "local_neighbors"):
        return problem.local_neighbors(state)
    return [(action, problem.result(state, action)) for action in problem.actions(state)]


def _local_random_state(problem, restart_index: int):
    if hasattr(problem, "local_random_state"):
        return problem.local_random_state(restart_index)
    return problem.initial_state()


def _belief_observed_tiles(state):
    first_row = tuple(value for value in state[0] if value != 0)
    return tuple(dict.fromkeys(first_row + (0,)))


def _belief_observation(state, tiles):
    positions = {}
    for row_index, row in enumerate(state):
        for col_index, value in enumerate(row):
            if value in tiles:
                positions[value] = (row_index, col_index)
    return positions


def _belief_pattern_state(known):
    size = 3
    grid = [["?" for _ in range(size)] for _ in range(size)]
    for value, (row, col) in known.items():
        grid[row][col] = value
    return tuple(tuple(row) for row in grid)


def _unknown_pattern_state(size: int = 3):
    return tuple(tuple("?" for _ in range(size)) for _ in range(size))


def _belief_from_known(problem, known, limit: int | None = None):
    values = set(range(9))
    used_values = set(known)
    used_cells = set(known.values())
    remaining_values = sorted(values - used_values)
    remaining_cells = [
        (row, col)
        for row in range(3)
        for col in range(3)
        if (row, col) not in used_cells
    ]

    import itertools

    belief = []
    for permutation in itertools.permutations(remaining_values):
        grid = [[None for _ in range(3)] for _ in range(3)]
        for value, (row, col) in known.items():
            grid[row][col] = value
        for value, (row, col) in zip(permutation, remaining_cells):
            grid[row][col] = value
        belief.append(tuple(tuple(row) for row in grid))
        if limit is not None and len(belief) >= limit:
            break
    return belief


def _belief_count_from_known(known):
    remaining = 9 - len(known)
    total = 1
    for value in range(2, remaining + 1):
        total *= value
    return total


def _belief_filter(states, known):
    return [state for state in states if all(_tile_position(state, tile) == cell for tile, cell in known.items())]


def _belief_common_actions(problem, states):
    common = None
    for state in states:
        actions = set(problem.actions(state))
        common = actions if common is None else common & actions
    return list(common or [])


def _belief_union_actions(problem, states):
    actions = set()
    for state in states:
        actions.update(problem.actions(state))
    return sorted(actions)


def _belief_transition(problem, states, action):
    return [problem.result(state, action) for state in states if action in problem.actions(state)]


def _belief_attempt_transition(problem, states, action):
    transitioned = []
    for state in states:
        next_state = problem.result(state, action) if action in problem.actions(state) else state
        if next_state not in transitioned:
            transitioned.append(next_state)
    return transitioned


def _belief_stats(problem, states):
    values = [problem.heuristic(state) for state in states]
    return {
        "min": min(values),
        "avg": sum(values) / len(values),
        "max": max(values),
    }


def _moved_tile(problem, state, action):
    next_state = problem.result(state, action)
    blank_before = _tile_position(state, 0)
    return next_state[blank_before[0]][blank_before[1]]


def _nondeterministic_results(problem, state, action):
    intended = problem.result(state, action)
    actions = list(problem.actions(state))
    if action not in actions:
        return []

    slip_action = actions[(actions.index(action) + 1) % len(actions)]
    slip = problem.result(state, slip_action)

    outcomes = []
    for candidate in (intended, slip):
        if candidate not in outcomes:
            outcomes.append(candidate)
    return outcomes


def _and_or_plan(problem, start_state, depth_limit: int = 8):
    def or_search(state, path, depth):
        if _local_is_goal(problem, state):
            return {"type": "goal"}
        if depth == 0 or state in path:
            return None

        actions = sorted(
            problem.actions(state),
            key=lambda action: min(
                _local_heuristic(problem, outcome)
                for outcome in _nondeterministic_results(problem, state, action)
            ),
        )
        for action in actions:
            branches = {}
            failed = False
            for outcome in _nondeterministic_results(problem, state, action):
                subplan = or_search(outcome, path + (state,), depth - 1)
                if subplan is None:
                    failed = True
                    break
                branches[outcome] = subplan
            if not failed:
                return {"type": "action", "action": action, "branches": branches}
        return None

    return or_search(start_state, tuple(), depth_limit)


def _tile_position(state, tile):
    for row_index, row in enumerate(state):
        for col_index, value in enumerate(row):
            if value == tile:
                return (row_index, col_index)
    raise ValueError(f"Tile {tile!r} is not in state.")
