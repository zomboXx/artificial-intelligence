"""
vacuum_logic.py - Business logic cho Robot Hút Bụi (Vacuum Agent)
Environment, Agent classes, Session State management.
"""

import random
import streamlit as st

from config.settings import GRID_SIZE, DIRTY, CLEAN


# ── Môi trường ──────────────────────────────────────────────────────────────────

class Environment:
    def __init__(self, grid: list[list[int]]):
        self.grid = [row[:] for row in grid]

    def is_dirty(self, x, y):
        return self.grid[x][y] == DIRTY

    def clean(self, x, y):
        self.grid[x][y] = CLEAN

    def all_clean(self):
        return all(
            self.grid[i][j] == CLEAN
            for i in range(GRID_SIZE) for j in range(GRID_SIZE)
        )

    def dirty_count(self):
        return sum(
            self.grid[i][j] == DIRTY
            for i in range(GRID_SIZE) for j in range(GRID_SIZE)
        )


# ── Tác nhân phản xạ đơn giản ──────────────────────────────────────────────────

class SimpleReflexAgent:
    """Chỉ biết trạng thái ô hiện tại, di chuyển ngẫu nhiên."""

    def __init__(self, env: Environment, x: int = 0, y: int = 0):
        self.env = env
        self.x = x
        self.y = y
        self.log = []

    def _possible_moves(self):
        moves = []
        if self.x > 0:            moves.append(("UP",    self.x-1, self.y))
        if self.x < GRID_SIZE-1:  moves.append(("DOWN",  self.x+1, self.y))
        if self.y > 0:            moves.append(("LEFT",  self.x, self.y-1))
        if self.y < GRID_SIZE-1:  moves.append(("RIGHT", self.x, self.y+1))
        return moves

    def act(self):
        if self.env.grid[self.x][self.y] == DIRTY:
            self.env.clean(self.x, self.y)
            self.log.append(f"🧹 SUCK tại ({self.x},{self.y})")
        else:
            moves = self._possible_moves()
            if moves:
                action, nx, ny = random.choice(moves)
                self.x, self.y = nx, ny
                self.log.append(f"→ MOVE {action} → ({self.x},{self.y})")


# ── Tác nhân dựa trên mô hình ──────────────────────────────────────────────────

class ModelBasedAgent:
    """Lưu tập ô đã thăm, ưu tiên ô chưa thăm."""

    def __init__(self, env: Environment, x: int = 0, y: int = 0):
        self.env = env
        self.x = x
        self.y = y
        self.visited = {(x, y)}
        self.log = []

    def _possible_moves(self):
        moves = []
        if self.x > 0:            moves.append(("UP",    self.x-1, self.y))
        if self.x < GRID_SIZE-1:  moves.append(("DOWN",  self.x+1, self.y))
        if self.y > 0:            moves.append(("LEFT",  self.x, self.y-1))
        if self.y < GRID_SIZE-1:  moves.append(("RIGHT", self.x, self.y+1))
        return moves

    def act(self):
        if self.env.grid[self.x][self.y] == DIRTY:
            self.env.clean(self.x, self.y)
            self.log.append(f"🧹 SUCK tại ({self.x},{self.y})")
        else:
            all_moves = self._possible_moves()
            unvisited = [(a, nx, ny) for a, nx, ny in all_moves
                         if (nx, ny) not in self.visited]
            chosen = random.choice(unvisited if unvisited else all_moves)
            _, nx, ny = chosen
            self.x, self.y = nx, ny
            self.visited.add((nx, ny))
            self.log.append(f"→ MOVE {chosen[0]} → ({self.x},{self.y})")


# ── Session State ───────────────────────────────────────────────────────────────

def init_vacuum_state(agent_type: str):
    """Khởi tạo môi trường và agent mới."""
    grid = [
        [random.choice([DIRTY, CLEAN]) for _ in range(GRID_SIZE)]
        for _ in range(GRID_SIZE)
    ]
    env = Environment(grid)

    if agent_type == "Simple Reflex":
        agent = SimpleReflexAgent(env)
    else:
        agent = ModelBasedAgent(env)

    ss = st.session_state
    ss["va_env"]        = env
    ss["va_agent"]      = agent
    ss["va_agent_type"] = agent_type
    ss["va_step"]       = 0
    ss["va_done"]       = False
    ss["va_running"]    = False
    ss["va_log"]        = []


def step_vacuum():
    """Thực hiện một bước hành động của Agent."""
    ss = st.session_state
    if ss.get("va_done"):
        return

    agent = ss["va_agent"]
    env   = ss["va_env"]

    if env.all_clean():
        ss["va_done"]    = True
        ss["va_running"] = False
        ss["va_log"].append("✅ ĐÃ DỌN SẠCH TOÀN BỘ!")
        return

    agent.act()
    ss["va_step"] += 1

    if agent.log:
        ss["va_log"].append(agent.log[-1])

    if env.all_clean():
        ss["va_done"]    = True
        ss["va_running"] = False
        ss["va_log"].append("✅ ĐÃ DỌN SẠCH TOÀN BỘ!")
