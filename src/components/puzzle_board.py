"""
puzzle_board.py - Component giao diện bàn cờ 8-Puzzle trong Streamlit
"""

import streamlit as st
from styles.components import render_puzzle_board_html


def render_board(state: tuple, label: str = "", label_color: str = "#FFFFFF", path_states: list = None):
    """Render bàn cờ 8-puzzle trong Streamlit."""
    html = render_puzzle_board_html(state, label, label_color, path_states)
    st.markdown(html, unsafe_allow_html=True)
