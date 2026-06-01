"""Helpers shared by search algorithms."""

from __future__ import annotations

from search.types import SearchNode, SearchStep, reconstruct_path


def make_step(
    node: SearchNode,
    frontier_nodes: list[SearchNode],
    explored_states: list,
    expanded: int,
    generated: int,
    algorithm: str,
    path: list | None = None,
    extra: dict | None = None,
    message: str = "",
) -> SearchStep:
    metrics = {
        "algorithm": algorithm,
        "expanded": expanded,
        "generated": generated,
        "depth": node.depth,
        "g": node.g,
        "h": node.h,
        "f": node.f,
        "frontier_size": len(frontier_nodes),
        "explored_size": len(explored_states),
    }
    if extra:
        metrics.update(extra)

    return SearchStep(
        current=node.state,
        frontier=[n.state for n in frontier_nodes],
        explored=list(explored_states),
        path=path,
        metrics=metrics,
        message=message,
    )


def goal_step(
    node: SearchNode,
    frontier_nodes: list[SearchNode],
    explored_states: list,
    expanded: int,
    generated: int,
    algorithm: str,
    extra: dict | None = None,
) -> SearchStep:
    path = reconstruct_path(node)
    return make_step(
        node=node,
        frontier_nodes=frontier_nodes,
        explored_states=explored_states,
        expanded=expanded,
        generated=generated,
        algorithm=algorithm,
        path=path,
        extra=extra,
        message=f"Goal found in {len(path) - 1} moves.",
    )
