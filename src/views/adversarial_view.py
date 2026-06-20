"""Streamlit step debugger for Buoi 14 adversarial search."""

from __future__ import annotations

import html
import random

import streamlit as st

from adversarial import (
    EMPTY,
    MAX_PLAYER,
    MIN_PLAYER,
    board_after,
    build_debug_events,
    empty_board,
    evaluate,
    legal_moves,
    move_label,
    winner,
)
from styles.theme import COLORS


PREFIX = "game_lab"
ALGORITHMS = ("Minimax", "Alpha-Beta", "Expectimax")


def render(_base_dir=None):
    _ensure_state()
    _header()

    col1, col2, col3 = st.columns([1.2, 1, 1])
    with col1:
        algorithm = st.selectbox("Algorithm", ALGORITHMS, key=f"{PREFIX}_algorithm")
    with col2:
        opponent_mode = st.selectbox("O opponent", ("Optimal", "Random"), key=f"{PREFIX}_opponent")
    with col3:
        debug_depth = st.slider("Debug depth", 1, 5, 3, key=f"{PREFIX}_depth")

    _controls(algorithm, opponent_mode, debug_depth)
    board = st.session_state[f"{PREFIX}_board"]
    turn = st.session_state[f"{PREFIX}_turn"]
    preview = evaluate(board, algorithm) if winner(board) is None else {"move": None, "value": 0, "candidates": [], "nodes": 0, "pruned": 0}
    event = _current_event()

    metrics = st.columns(6)
    values = (
        ("Turn", turn),
        ("Winner", winner(board) or "-"),
        ("Best move", move_label(preview["move"]) if preview["move"] is not None else "-"),
        ("Value", f"{preview['value']:.3f}"),
        ("Nodes", preview["nodes"]),
        ("Pruned", preview["pruned"]),
    )
    for column, (label, value) in zip(metrics, values):
        column.metric(label, value)

    left, right = st.columns([1, 1.35])
    with left:
        _board_controls(board, turn)
        _root_candidates(preview)
    with right:
        _debug_event(event)


def _ensure_state():
    st.session_state.setdefault(f"{PREFIX}_board", empty_board())
    st.session_state.setdefault(f"{PREFIX}_turn", MAX_PLAYER)
    st.session_state.setdefault(f"{PREFIX}_events", [])
    st.session_state.setdefault(f"{PREFIX}_index", 0)
    st.session_state.setdefault(f"{PREFIX}_history", [])


def _header():
    st.html(f"""
<div style="background:{COLORS['accent_3']};border:2.5px solid #111;box-shadow:5px 5px 0 #111;padding:1rem 1.4rem;margin-bottom:1.2rem;">
  <h1 style="margin:0;font-size:1.9rem;">Adversarial Search - Buổi 14</h1>
  <div style="font-weight:700;color:#222;">Step-debug Minimax, Alpha-Beta and Expectimax</div>
</div>
""")


def _controls(algorithm, opponent_mode, debug_depth):
    columns = st.columns(6)
    with columns[0]:
        if st.button("Reset Game", use_container_width=True, key=f"{PREFIX}_reset"):
            st.session_state[f"{PREFIX}_board"] = empty_board()
            st.session_state[f"{PREFIX}_turn"] = MAX_PLAYER
            st.session_state[f"{PREFIX}_events"] = []
            st.session_state[f"{PREFIX}_index"] = 0
            st.session_state[f"{PREFIX}_history"] = []
            st.rerun()
    with columns[1]:
        if st.button("Debug Reset", use_container_width=True, key=f"{PREFIX}_debug_reset"):
            board = st.session_state[f"{PREFIX}_board"]
            turn = st.session_state[f"{PREFIX}_turn"]
            st.session_state[f"{PREFIX}_events"] = build_debug_events(board, algorithm, turn, debug_depth)
            st.session_state[f"{PREFIX}_index"] = 0
            st.rerun()
    with columns[2]:
        if st.button("Debug Step", use_container_width=True, key=f"{PREFIX}_debug_step"):
            events = st.session_state[f"{PREFIX}_events"]
            if not events:
                board = st.session_state[f"{PREFIX}_board"]
                turn = st.session_state[f"{PREFIX}_turn"]
                events = build_debug_events(board, algorithm, turn, debug_depth)
                st.session_state[f"{PREFIX}_events"] = events
            st.session_state[f"{PREFIX}_index"] = min(st.session_state[f"{PREFIX}_index"] + 1, max(0, len(events) - 1))
            st.rerun()
    with columns[3]:
        if st.button("AI Move", use_container_width=True, key=f"{PREFIX}_ai"):
            _ai_move(algorithm)
            st.rerun()
    with columns[4]:
        if st.button("O Move", use_container_width=True, key=f"{PREFIX}_opponent_move"):
            _opponent_move(algorithm, opponent_mode)
            st.rerun()
    with columns[5]:
        if st.button("Undo", use_container_width=True, key=f"{PREFIX}_undo"):
            history = st.session_state[f"{PREFIX}_history"]
            if history:
                board, turn = history.pop()
                st.session_state[f"{PREFIX}_board"] = board
                st.session_state[f"{PREFIX}_turn"] = turn
                st.session_state[f"{PREFIX}_events"] = []
                st.session_state[f"{PREFIX}_index"] = 0
                st.rerun()


def _push_history():
    st.session_state[f"{PREFIX}_history"].append((st.session_state[f"{PREFIX}_board"], st.session_state[f"{PREFIX}_turn"]))


def _ai_move(algorithm):
    board = st.session_state[f"{PREFIX}_board"]
    if st.session_state[f"{PREFIX}_turn"] != MAX_PLAYER or winner(board) is not None:
        return
    result = evaluate(board, algorithm)
    if result["move"] is None:
        return
    _push_history()
    st.session_state[f"{PREFIX}_board"] = board_after(board, result["move"], MAX_PLAYER)
    st.session_state[f"{PREFIX}_turn"] = MIN_PLAYER
    st.session_state[f"{PREFIX}_events"] = []
    st.session_state[f"{PREFIX}_index"] = 0


def _opponent_move(algorithm, opponent_mode):
    board = st.session_state[f"{PREFIX}_board"]
    if st.session_state[f"{PREFIX}_turn"] != MIN_PLAYER or winner(board) is not None:
        return
    moves = legal_moves(board)
    if not moves:
        return
    if opponent_mode == "Random":
        move = random.choice(moves)
    else:
        scored = [(move, evaluate(board_after(board, move, MIN_PLAYER), algorithm)["value"]) for move in moves]
        move = min(scored, key=lambda item: (item[1], item[0]))[0]
    _push_history()
    st.session_state[f"{PREFIX}_board"] = board_after(board, move, MIN_PLAYER)
    st.session_state[f"{PREFIX}_turn"] = MAX_PLAYER
    st.session_state[f"{PREFIX}_events"] = []
    st.session_state[f"{PREFIX}_index"] = 0


def _board_controls(board, turn):
    st.subheader("Tic-Tac-Toe board")
    st.markdown("X is MAX; O is MIN/chance. Click an empty cell only on O's turn.")
    st.markdown("""
<style>
div[data-testid="stHorizontalBlock"] .stButton button[kind="secondary"] {min-height:72px;font-size:1.45rem;}
</style>
""", unsafe_allow_html=True)
    for row in range(3):
        columns = st.columns(3)
        for col in range(3):
            index = row * 3 + col
            label = board[index] if board[index] != EMPTY else "·"
            with columns[col]:
                if st.button(label, key=f"{PREFIX}_cell_{index}", use_container_width=True, disabled=board[index] != EMPTY or turn != MIN_PLAYER or winner(board) is not None):
                    _push_history()
                    st.session_state[f"{PREFIX}_board"] = board_after(board, index, MIN_PLAYER)
                    st.session_state[f"{PREFIX}_turn"] = MAX_PLAYER
                    st.session_state[f"{PREFIX}_events"] = []
                    st.session_state[f"{PREFIX}_index"] = 0
                    st.rerun()


def _root_candidates(preview):
    st.subheader("Root candidates")
    if not preview["candidates"]:
        st.caption("No legal root moves.")
        return
    rows = [
        {"Selected": "Yes" if move == preview["move"] else "", "Move": move_label(move), "Value": round(value, 3)}
        for move, value in preview["candidates"]
    ]
    st.dataframe(rows, use_container_width=True, hide_index=True)


def _current_event():
    events = st.session_state[f"{PREFIX}_events"]
    if not events:
        return None
    return events[st.session_state[f"{PREFIX}_index"]]


def _debug_event(event):
    st.subheader("Current recursive event")
    if event is None:
        st.info("Press Debug Reset, then use Debug Step to follow recursion node by node.")
        return
    index = st.session_state[f"{PREFIX}_index"]
    total = len(st.session_state[f"{PREFIX}_events"])
    color = {"ENTER": COLORS["accent_4"], "LEAF": COLORS["accent_5"], "UPDATE": COLORS["accent_1"], "PRUNE": COLORS["accent_3"], "RETURN": COLORS["accent_2"]}.get(event["phase"], "#FFFFFF")
    path = "ROOT" if not event["path"] else "ROOT -> " + " -> ".join(move_label(move) for move in event["path"])
    st.html(f"""
<div style="background:{color};border:2.5px solid #111;box-shadow:4px 4px 0 #111;padding:1rem;margin-bottom:1rem;">
  <div style="font-weight:900;font-size:1.15rem;">{index + 1}/{total} - {html.escape(event['phase'])}</div>
  <div><b>Role:</b> {html.escape(event['role'])} &nbsp; <b>Depth:</b> {event['depth']}</div>
  <div><b>Path:</b> {html.escape(path)}</div>
  <div style="margin-top:.4rem;">{html.escape(event['message'])}</div>
</div>
""")
    left, right = st.columns([1, 1.15])
    with left:
        st.markdown("**Node board**")
        st.html(_mini_board(event["board"]))
    with right:
        details = {
            "Player": event["player"],
            "Value": event.get("value", "-"),
            "Alpha": event.get("alpha", "-"),
            "Beta": event.get("beta", "-"),
            "Current move": move_label(event["current_move"]) if event.get("current_move") is not None else "-",
        }
        st.json(details)
    if event.get("child_values"):
        st.markdown("**Values already returned by children**")
        st.dataframe([{"Move": move_label(move), "Value": round(value, 3)} for move, value in event["child_values"]], use_container_width=True, hide_index=True)
    if event.get("pruned_moves"):
        st.error("Pruned moves: " + ", ".join(move_label(move) for move in event["pruned_moves"]))


def _mini_board(board):
    cells = []
    for value in board:
        label = "" if value == EMPTY else value
        color = "#2563EB" if value == MAX_PLAYER else ("#DC2626" if value == MIN_PLAYER else "#FFFFFF")
        cells.append(f"<div style='aspect-ratio:1;border:2px solid #111;display:flex;align-items:center;justify-content:center;font-size:1.4rem;font-weight:900;color:{color};'>{label}</div>")
    return "<div style='display:grid;grid-template-columns:repeat(3,58px);gap:4px;'>" + "".join(cells) + "</div>"
