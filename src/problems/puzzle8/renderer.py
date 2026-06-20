"""HTML renderer for 8-Puzzle states."""

from __future__ import annotations

from styles.theme import BORDER, COLORS, SHADOW_SM


def render_state(state, role: str = "normal") -> str:
    if state is None:
        return _empty("No state")

    if isinstance(state, dict) and "state" in state:
        state = state["state"]

    label_color = {
        "current": COLORS["accent_1"],
        "start": COLORS["accent_2"],
        "goal": COLORS["accent_5"],
        "path": COLORS["accent_5"],
    }.get(role, "#FFFFFF")

    rows = ""
    for row in state:
        cells = ""
        for value in row:
            is_unknown = value == "?"
            bg = "#FFF59D" if is_unknown else (COLORS["tile_blank"] if value == 0 else COLORS["tile_bg"])
            label = "?" if is_unknown else ("" if value == 0 else value)
            cells += f"""
            <div style="
                width:54px; height:54px;
                background:{bg};
                border:{BORDER};
                box-shadow:{SHADOW_SM};
                display:flex; align-items:center; justify-content:center;
                font-size:1.35rem; font-weight:900;
                color:var(--neo-text);
                margin:3px;
            ">{label}</div>
            """
        rows += f'<div style="display:flex;">{cells}</div>'

    return f"""
    <div style="display:inline-block; margin:5px;">
        <div style="
            display:inline-block;
            background:{label_color};
            border:{BORDER};
            padding:2px 8px;
            font-weight:800;
            font-size:0.68rem;
            margin-bottom:4px;
        ">{role.upper()}</div>
        <div style="
            background:var(--neo-bg);
            border:{BORDER};
            box-shadow:{SHADOW_SM};
            padding:6px;
            display:inline-block;
        ">{rows}</div>
    </div>
    """


def render_board_with_trace(current, frontier, explored, path, start, goal) -> str:
    return f"""
    <div style="display:flex; gap:1.5rem; align-items:flex-start; flex-wrap:wrap;">
        {render_state(start, "start")}
        <div style="font-size:2rem; padding-top:52px;">-></div>
        {render_state(current, "current")}
        <div style="font-size:2rem; padding-top:52px;">-></div>
        {render_state(goal, "goal")}
    </div>
    """


def _empty(text: str) -> str:
    return f'<div style="padding:1rem; color:var(--neo-muted);">{text}</div>'
