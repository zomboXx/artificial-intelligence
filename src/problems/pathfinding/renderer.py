"""HTML renderer for grid pathfinding."""

from __future__ import annotations

from styles.theme import BORDER, COLORS, SHADOW_SM


def render_state(state, role: str = "normal") -> str:
    if state is None:
        return '<div style="padding:1rem; color:var(--neo-muted);">No coordinate</div>'
    return f"""
    <div style="
        display:inline-flex; align-items:center; justify-content:center;
        min-width:96px; height:46px;
        background:{COLORS['panel']};
        border:{BORDER};
        box-shadow:{SHADOW_SM};
        font-weight:900;
    ">{role.upper()}: {state}</div>
    """


def render_board_with_trace(current, frontier, explored, path, start, goal, grid) -> str:
    frontier_set = set(frontier or [])
    explored_set = set(explored or [])
    path_set = set(path or [])

    rows = ""
    for r, row in enumerate(grid):
        cells = ""
        for c, raw in enumerate(row):
            pos = (r, c)
            text = ""
            bg = COLORS["panel"]
            color = COLORS["text"]

            if raw == "#":
                bg = "#111111"
                color = "#FFFFFF"
            elif pos == start:
                bg = COLORS["accent_2"]
                text = "S"
            elif pos == goal:
                bg = COLORS["accent_5"]
                text = "G"
            elif pos == current:
                bg = COLORS["accent_1"]
                text = "C"
            elif pos in path_set:
                bg = COLORS["accent_5"]
                text = "*"
            elif pos in frontier_set:
                bg = COLORS["accent_2"]
                text = "F"
            elif pos in explored_set:
                bg = COLORS["accent_3"]
                text = "E"

            cells += f"""
            <div style="
                width:42px; height:42px;
                background:{bg};
                color:{color};
                border:{BORDER};
                box-shadow:{SHADOW_SM};
                display:flex; align-items:center; justify-content:center;
                font-size:0.85rem; font-weight:900;
                margin:2px;
            ">{text}</div>
            """
        rows += f'<div style="display:flex;">{cells}</div>'

    return f"""
    <div style="
        background:var(--neo-panel);
        border:{BORDER};
        box-shadow:5px 5px 0px var(--neo-shadow);
        padding:1rem;
        display:inline-block;
    ">{rows}</div>
    """
