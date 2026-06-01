"""8-Queens as an incremental SearchProblem."""

from __future__ import annotations


class Queens8Problem:
    name = "8-Queens"

    def __init__(self, size: int = 8):
        self.size = size

    def initial_state(self):
        return ()

    def is_goal(self, state) -> bool:
        return len(state) == self.size and _is_valid(state)

    def actions(self, state) -> list[int]:
        if len(state) >= self.size:
            return []
        row = len(state)
        actions = []
        for col in range(self.size):
            if _safe_position(state, row, col):
                actions.append(col)
        return actions

    def result(self, state, action):
        return tuple(list(state) + [action])

    def step_cost(self, state, action, next_state) -> float:
        return 1

    def heuristic(self, state) -> float:
        return self.size - len(state)

    def state_key(self, state):
        return state


def _safe_position(state, row: int, col: int) -> bool:
    for prev_row, prev_col in enumerate(state):
        if prev_col == col:
            return False
        if abs(prev_row - row) == abs(prev_col - col):
            return False
    return True


def _is_valid(state) -> bool:
    return all(_safe_position(state[:row], row, col) for row, col in enumerate(state))
