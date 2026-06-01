"""8-Puzzle as a generic SearchProblem."""

from __future__ import annotations

import random


DEFAULT_START_STATE = ((2, 8, 3), (1, 6, 4), (7, 0, 5))
GOAL_STATE = ((1, 2, 3), (8, 0, 4), (7, 6, 5))

MOVES = (
    ("UP", -1, 0),
    ("DOWN", 1, 0),
    ("LEFT", 0, -1),
    ("RIGHT", 0, 1),
)


class Puzzle8Problem:
    name = "8-Puzzle"

    def __init__(self, start_state=DEFAULT_START_STATE, goal_state=GOAL_STATE, weighted_cost=False):
        self.start_state = start_state
        self.goal_state = goal_state
        self.weighted_cost = weighted_cost
        self.goal_positions = {
            value: (r, c)
            for r, row in enumerate(goal_state)
            for c, value in enumerate(row)
        }

    def initial_state(self):
        return self.start_state

    def is_goal(self, state) -> bool:
        return state == self.goal_state

    def actions(self, state) -> list[str]:
        blank_r, blank_c = _find_blank(state)
        actions = []
        for name, dr, dc in MOVES:
            nr, nc = blank_r + dr, blank_c + dc
            if 0 <= nr < 3 and 0 <= nc < 3:
                actions.append(name)
        return actions

    def result(self, state, action):
        blank_r, blank_c = _find_blank(state)
        dr, dc = dict((name, (r, c)) for name, r, c in MOVES)[action]
        nr, nc = blank_r + dr, blank_c + dc
        grid = [list(row) for row in state]
        grid[blank_r][blank_c], grid[nr][nc] = grid[nr][nc], grid[blank_r][blank_c]
        return tuple(tuple(row) for row in grid)

    def step_cost(self, state, action, next_state) -> float:
        if not self.weighted_cost:
            return 1
        blank_r, blank_c = _find_blank(state)
        next_blank_r, next_blank_c = _find_blank(next_state)
        return state[next_blank_r][next_blank_c] or state[blank_r][blank_c]

    def heuristic(self, state) -> float:
        total = 0
        for r, row in enumerate(state):
            for c, value in enumerate(row):
                if value == 0:
                    continue
                gr, gc = self.goal_positions[value]
                total += abs(r - gr) + abs(c - gc)
        return total

    def state_key(self, state):
        return state


def generate_solvable_shuffle() -> tuple[tuple[int, ...], ...]:
    while True:
        nums = list(range(9))
        random.shuffle(nums)
        if _count_inversions(nums) % 2 == 0:
            non_zero = [idx for idx, value in enumerate(nums) if value != 0]
            nums[non_zero[0]], nums[non_zero[1]] = nums[non_zero[1]], nums[non_zero[0]]

        state = tuple(tuple(nums[r * 3 + c] for c in range(3)) for r in range(3))
        if is_solvable(state):
            return state


def is_solvable(state) -> bool:
    flat = [value for row in state for value in row]
    return _count_inversions(flat) % 2 == 1


def _count_inversions(flat: list[int]) -> int:
    values = [value for value in flat if value != 0]
    return sum(
        1
        for i in range(len(values))
        for j in range(i + 1, len(values))
        if values[i] > values[j]
    )


def _find_blank(state) -> tuple[int, int]:
    for r, row in enumerate(state):
        for c, value in enumerate(row):
            if value == 0:
                return r, c
    raise ValueError("Puzzle state has no blank tile.")
