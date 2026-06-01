"""Shared data types for problem-independent search visualization."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SearchNode:
    state: Any
    parent: "SearchNode | None" = None
    action: Any = None
    g: float = 0
    h: float = 0
    f: float = 0
    depth: int = 0
    order: int = 0


@dataclass
class SearchStep:
    current: Any
    frontier: list[Any]
    explored: list[Any]
    path: list[Any] | None
    metrics: dict[str, Any] = field(default_factory=dict)
    message: str = ""


def reconstruct_path(node: SearchNode | None) -> list[Any]:
    path = []
    while node is not None:
        path.append(node.state)
        node = node.parent
    return list(reversed(path))
