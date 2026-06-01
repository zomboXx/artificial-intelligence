"""Main Streamlit entry point for the AI visualization project."""

import os
import sys

import streamlit as st

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SRC_DIR)

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from styles.theme import COLORS, apply_global_styles
from views import search_view, vacuum_view


st.set_page_config(
    page_title="AI Algorithm Visualizer",
    page_icon="AI",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_global_styles()

PAGES = {
    "Search Algorithms": "search",
    "Vacuum Agent": "vacuum",
}

with st.sidebar:
    st.html(f"""
<div style="
    background-color: {COLORS['accent_2']};
    border: 2.5px solid var(--neo-border);
    box-shadow: 4px 4px 0px var(--neo-shadow);
    padding: 1rem; margin-bottom: 1.5rem;
    text-align: center;
">
    <div style="font-size: 2.2rem; line-height: 1;">AI</div>
    <div style="font-weight: 900; font-size: 1.1rem; margin-top: 0.3rem; color: var(--neo-text);">
        AI ALGORITHM<br>VISUALIZER
    </div>
    <div style="font-size: 0.75rem; color: var(--neo-muted); font-weight: 600; margin-top: 0.2rem;">
        Generic search and agent simulation
    </div>
</div>
""")

    st.markdown("**Modules**")
    selected_page = st.radio(
        "Module",
        list(PAGES.keys()),
        key="nav_page",
        label_visibility="collapsed",
    )

    st.markdown("---")
    if PAGES[selected_page] == "search":
        st.html("""
<div style="
    background-color: var(--neo-panel);
    border: 2px solid var(--neo-border);
    padding: 0.8rem; font-size: 0.85rem; color: var(--neo-text);
">
    <b>Generic Search Core</b><br>
    - BFS, DFS, IDS<br>
    - UCS, Greedy, A*<br><br>
    <b>Problems</b><br>
    - 8-Puzzle<br>
    - Grid Pathfinding<br>
    - 8-Queens
</div>
""")
    else:
        st.html("""
<div style="
    background-color: var(--neo-panel);
    border: 2px solid var(--neo-border);
    padding: 0.8rem; font-size: 0.85rem; color: var(--neo-text);
">
    <b>Agent Simulation</b><br>
    - Simple Reflex<br>
    - Model-Based<br><br>
    4x4 random room environment
</div>
""")

    st.markdown("---")
    st.html("""
<div style="font-size: 0.75rem; color: var(--neo-muted); font-weight: 600; line-height: 1.6;">
    Nguyen Duc Phat<br>
    MSSV: 24110296<br>
    HCM-UTE - ARIN330585
</div>
""")

page_key = PAGES[selected_page]

if page_key == "search":
    search_view.render(BASE_DIR)
elif page_key == "vacuum":
    vacuum_view.render(BASE_DIR)
