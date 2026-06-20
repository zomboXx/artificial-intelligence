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
        col = len(state)
        actions = []
        for row in range(self.size):
            if _safe_position(state, col, row):
                actions.append(row)
        return actions

    def result(self, state, action):
        return tuple(list(state) + [action])

    def step_cost(self, state, action, next_state) -> float:
        return 1

    def heuristic(self, state) -> float:
        return self.size - len(state)

    def state_key(self, state):
        return state

    def local_initial_state(self):
        return tuple(0 for _ in range(self.size))

    def local_is_goal(self, state) -> bool:
        return self.local_heuristic(state) == 0

    def local_heuristic(self, state) -> float:
        conflicts = 0
        for col_a in range(self.size):
            for col_b in range(col_a + 1, self.size):
                row_a = state[col_a]
                row_b = state[col_b]
                if row_a == row_b or abs(row_a - row_b) == abs(col_a - col_b):
                    conflicts += 1
        return conflicts

    def local_neighbors(self, state):
        neighbors = []
        for col in range(self.size):
            for row in range(self.size):
                if state[col] == row:
                    continue
                next_state = list(state)
                next_state[col] = row
                neighbors.append((f"col {col} -> row {row}", tuple(next_state)))
        return neighbors


def _safe_position(state, col: int, row: int) -> bool:
    for prev_col, prev_row in enumerate(state):
        if prev_row == row:
            return False
        if abs(prev_col - col) == abs(prev_row - row):
            return False
    return True


def _is_valid(state) -> bool:
    return all(_safe_position(state[:col], col, row) for col, row in enumerate(state))
