"""HTML renderer for 8-Queens states."""

from __future__ import annotations

from styles.theme import BORDER, COLORS, SHADOW_SM


def render_state(state, role: str = "normal", size: int = 8) -> str:
    return render_board_with_trace(
        current=state,
        frontier=[],
        explored=[],
        path=None,
        start=(),
        goal=None,
        size=size,
        compact=True,
    )


def render_board_with_trace(current, frontier, explored, path, start, goal, size: int = 8, compact: bool = False) -> str:
    state = current or ()
    path_set = set(path or [])
    rows = ""
    cell_px = 34 if compact else 46

    for r in range(size):
        cells = ""
        for c in range(size):
            has_queen = r < len(state) and state[r] == c
            bg = "#FFFFFF" if (r + c) % 2 == 0 else "#F4F0E6"
            text = ""
            color = COLORS["text"]

            if has_queen:
                bg = COLORS["accent_5"] if state in path_set else COLORS["accent_4"]
                text = "Q"
                color = "#111111"
            elif r == len(state):
                bg = COLORS["accent_2"] + "66"

            cells += f"""
            <div style="
                width:{cell_px}px; height:{cell_px}px;
                background:{bg};
                color:{color};
                border:{BORDER};
                display:flex; align-items:center; justify-content:center;
                font-weight:900;
                box-shadow:{SHADOW_SM if not compact else 'none'};
                margin:1px;
            ">{text}</div>
            """
        rows += f'<div style="display:flex;">{cells}</div>'

    return f"""
    <div style="
        display:inline-block;
        background:var(--neo-panel);
        border:{BORDER};
        box-shadow:{SHADOW_SM};
        padding:0.6rem;
        margin:4px;
    ">{rows}</div>
    """
