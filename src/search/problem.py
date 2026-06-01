"""Problem interface consumed by generic search algorithms."""

from __future__ import annotations

from typing import Any, Protocol


class SearchProblem(Protocol):
    name: str

    def initial_state(self) -> Any:
        ...

    def is_goal(self, state: Any) -> bool:
        ...

    def actions(self, state: Any) -> list[Any]:
        ...

    def result(self, state: Any, action: Any) -> Any:
        ...

    def step_cost(self, state: Any, action: Any, next_state: Any) -> float:
        ...

    def heuristic(self, state: Any) -> float:
        return 0

    def state_key(self, state: Any) -> Any:
        return state
