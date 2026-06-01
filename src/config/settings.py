"""
settings.py - Cấu hình và hằng số dùng chung cho toàn dự án.
"""

# ── Cấu hình 8-Puzzle ──────────────────────────────────────────────────────────
# Trạng thái mặc định nếu không xáo trộn
DEFAULT_START_STATE = ((2, 8, 3), (1, 6, 4), (7, 0, 5))
GOAL_STATE          = ((1, 2, 3), (8, 0, 4), (7, 6, 5))

# ── Cấu hình Robot Hút Bụi (Vacuum Agent) ──────────────────────────────────────
GRID_SIZE = 4
DIRTY = 1
CLEAN = 0
