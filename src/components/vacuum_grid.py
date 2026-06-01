"""
vacuum_grid.py - Component ma trận phòng cho Robot Hút Bụi trong Streamlit
"""

import streamlit as st
from config.settings import GRID_SIZE, DIRTY, CLEAN
from styles.theme import COLORS, BORDER


def _render_grid_html(env, agent_x: int, agent_y: int, visited: set = None) -> str:
    """Tạo chuỗi HTML Neobrutalism ma trận phòng 4x4."""
    CELL_PX = 80
    rows_html = ""
    for i in range(GRID_SIZE):
        cells_html = ""
        for j in range(GRID_SIZE):
            is_agent   = (i == agent_x and j == agent_y)
            is_dirty   = (env.grid[i][j] == DIRTY)
            is_visited = visited and (i, j) in visited

            if is_agent:
                bg   = COLORS["accent_1"]
                text = "🤖"
                fs   = "1.8rem"
            elif is_dirty:
                bg   = "#8B4513"
                text = "💩"
                fs   = "1.5rem"
            elif is_visited:
                bg   = COLORS["accent_4"]
                text = "✓"
                fs   = "1.2rem"
            else:
                bg   = "var(--neo-bg)"  # Nền trống thích ứng với màu nền tối/sáng
                text = ""
                fs   = "1rem"

            cells_html += f"""
            <div style="
                width:{CELL_PX}px; height:{CELL_PX}px;
                background-color:{bg};
                border:{BORDER};
                display:flex; align-items:center; justify-content:center;
                font-size:{fs}; font-weight:900;
                font-family:'Outfit',sans-serif;
            ">{text}</div>
            """
        rows_html += f'<div style="display:flex;">{cells_html}</div>'

    return f"""
    <div style="
        border:{BORDER};
        box-shadow:5px 5px 0px var(--neo-shadow);
        display:inline-block;
    ">{rows_html}</div>
    """


def render_grid(env, agent_x: int, agent_y: int, visited: set = None):
    """Render ma trận phòng Robot hút bụi trong Streamlit."""
    html = _render_grid_html(env, agent_x, agent_y, visited)
    st.markdown(html, unsafe_allow_html=True)
