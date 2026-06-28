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

    col_mode, col_sym = st.columns(2)
    with col_mode:
        game_mode = st.selectbox(
            "Game Mode",
            ("Debug Recursion", "Play vs AI"),
            key=f"{PREFIX}_game_mode"
        )
    with col_sym:
        human_player = st.selectbox(
            "Your Symbol (Human)",
            ("O", "X"),
            key=f"{PREFIX}_human_player",
            disabled=(game_mode != "Play vs AI")
        )

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

    if game_mode == "Play vs AI" and winner(board) is None and turn != human_player:
        with st.spinner("AI đang tính toán nước đi..."):
            _run_ai_turn(board, turn, algorithm, opponent_mode)
            board = st.session_state[f"{PREFIX}_board"]
            turn = st.session_state[f"{PREFIX}_turn"]

    preview = evaluate(board, algorithm) if winner(board) is None else {"move": None, "value": 0, "candidates": [], "nodes": 0, "pruned": 0}
    event = _current_event()

    if game_mode == "Play vs AI":
        ai_stats = st.session_state.get(f"{PREFIX}_ai_stats")
        last_nodes = ai_stats["nodes"] if ai_stats else 0
        last_pruned = ai_stats["pruned"] if ai_stats else 0
        last_time = f"{ai_stats['elapsed_ms']:.1f}ms" if ai_stats else "-"
        
        # Calculate hint
        from adversarial.core import MOVE_PRIORITY
        hint_move = None
        if winner(board) is None:
            if turn == MAX_PLAYER:
                hint_move = preview["move"]
            else:
                moves = legal_moves(board)
                if moves:
                    scored = []
                    for m in moves:
                        next_state = board_after(board, m, MIN_PLAYER)
                        res = evaluate(next_state, algorithm)
                        scored.append((m, res["value"]))
                    scored.sort(key=lambda item: (item[1], MOVE_PRIORITY[item[0]]))
                    hint_move = scored[0][0]

        metrics = st.columns(6)
        values = (
            ("Lượt đi (Turn)", turn),
            ("Kết quả (Winner)", winner(board) or "Đang chơi"),
            ("Gợi ý (Hint)", move_label(hint_move) if hint_move is not None else "-"),
            ("AI Nodes", last_nodes),
            ("AI Pruned", last_pruned),
            ("AI Time", last_time),
        )
        for column, (label, value) in zip(metrics, values):
            column.metric(label, value)
    else:
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
        if game_mode == "Play vs AI":
            game_winner = winner(board)
            if game_winner is not None:
                if game_winner == "Draw":
                    st.info("Trận đấu kết thúc với kết quả Hòa! 🤝")
                elif game_winner == human_player:
                    st.success("Chúc mừng! Bạn đã thắng AI! 🎉")
                else:
                    st.error("AI đã giành chiến thắng! 🤖")
        else:
            _root_candidates(preview)
    with right:
        if game_mode == "Play vs AI":
            _render_ai_decision_panel()
        else:
            _debug_event(event)


def _ensure_state():
    st.session_state.setdefault(f"{PREFIX}_board", empty_board())
    st.session_state.setdefault(f"{PREFIX}_turn", MAX_PLAYER)
    st.session_state.setdefault(f"{PREFIX}_events", [])
    st.session_state.setdefault(f"{PREFIX}_index", 0)
    st.session_state.setdefault(f"{PREFIX}_history", [])
    st.session_state.setdefault(f"{PREFIX}_game_mode", "Debug Recursion")
    st.session_state.setdefault(f"{PREFIX}_human_player", "O")
    st.session_state.setdefault(f"{PREFIX}_ai_stats", None)
    st.session_state.setdefault(f"{PREFIX}_last_move", None)


def _header():
    st.html(f"""
<div style="background:{COLORS['accent_3']};border:2.5px solid #111;box-shadow:5px 5px 0 #111;padding:1rem 1.4rem;margin-bottom:1.2rem;">
  <h1 style="margin:0;font-size:1.9rem;">Adversarial Search - Buổi 14</h1>
  <div style="font-weight:700;color:#222;">Step-debug Minimax, Alpha-Beta and Expectimax</div>
</div>
""")


def _controls(algorithm, opponent_mode, debug_depth):
    game_mode = st.session_state.get(f"{PREFIX}_game_mode", "Debug Recursion")
    
    if game_mode == "Play vs AI":
        columns = st.columns(2)
        with columns[0]:
            if st.button("Reset Game", use_container_width=True, key=f"{PREFIX}_reset"):
                st.session_state[f"{PREFIX}_board"] = empty_board()
                st.session_state[f"{PREFIX}_turn"] = MAX_PLAYER
                st.session_state[f"{PREFIX}_events"] = []
                st.session_state[f"{PREFIX}_index"] = 0
                st.session_state[f"{PREFIX}_history"] = []
                st.session_state[f"{PREFIX}_ai_stats"] = None
                st.session_state[f"{PREFIX}_last_move"] = None
                st.rerun()
        with columns[1]:
            if st.button("Undo Move", use_container_width=True, key=f"{PREFIX}_undo"):
                history = st.session_state[f"{PREFIX}_history"]
                if history:
                    board, turn = history.pop()
                    human_player = st.session_state.get(f"{PREFIX}_human_player", "O")
                    if history and turn != human_player:
                        board, turn = history.pop()
                    st.session_state[f"{PREFIX}_board"] = board
                    st.session_state[f"{PREFIX}_turn"] = turn
                    st.session_state[f"{PREFIX}_events"] = []
                    st.session_state[f"{PREFIX}_index"] = 0
                    st.session_state[f"{PREFIX}_ai_stats"] = None
                    st.session_state[f"{PREFIX}_last_move"] = None
                    st.rerun()
    else:
        columns = st.columns(6)
        with columns[0]:
            if st.button("Reset Game", use_container_width=True, key=f"{PREFIX}_reset"):
                st.session_state[f"{PREFIX}_board"] = empty_board()
                st.session_state[f"{PREFIX}_turn"] = MAX_PLAYER
                st.session_state[f"{PREFIX}_events"] = []
                st.session_state[f"{PREFIX}_index"] = 0
                st.session_state[f"{PREFIX}_history"] = []
                st.session_state[f"{PREFIX}_ai_stats"] = None
                st.session_state[f"{PREFIX}_last_move"] = None
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
                    st.session_state[f"{PREFIX}_last_move"] = None
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
    st.subheader("Bàn cờ Tic-Tac-Toe")
    
    game_mode = st.session_state.get(f"{PREFIX}_game_mode", "Debug Recursion")
    human_player = st.session_state.get(f"{PREFIX}_human_player", "O")
    
    if game_mode == "Play vs AI":
        st.markdown(f"Bạn đang cầm quân: **{human_player}**. Click vào ô trống khi đến lượt.")
        disabled_cond = lambda idx: (board[idx] != EMPTY or turn != human_player or winner(board) is not None)
    else:
        st.markdown("X là MAX; O là MIN/chance. Bấm vào ô trống khi đến lượt của O.")
        disabled_cond = lambda idx: (board[idx] != EMPTY or turn != MIN_PLAYER or winner(board) is not None)

    st.markdown("""
<style>
div[data-testid="stHorizontalBlock"] .stButton button[kind="secondary"] {min-height:72px;font-size:1.45rem;}
</style>
""", unsafe_allow_html=True)
    
    last_move = st.session_state.get(f"{PREFIX}_last_move")
    for row in range(3):
        columns = st.columns(3)
        for col in range(3):
            index = row * 3 + col
            label = board[index] if board[index] != EMPTY else "·"
            
            if last_move == index:
                st.markdown(f"""<style>
                    button[key="{PREFIX}_cell_{index}"] {{
                        background-color: {COLORS['accent_2']} !important;
                        border: 2.5px solid #111111 !important;
                    }}
                </style>""", unsafe_allow_html=True)
                
            with columns[col]:
                if st.button(label, key=f"{PREFIX}_cell_{index}", use_container_width=True, disabled=disabled_cond(index)):
                    _push_history()
                    player_to_move = human_player if game_mode == "Play vs AI" else MIN_PLAYER
                    st.session_state[f"{PREFIX}_board"] = board_after(board, index, player_to_move)
                    st.session_state[f"{PREFIX}_turn"] = opponent(player_to_move)
                    st.session_state[f"{PREFIX}_events"] = []
                    st.session_state[f"{PREFIX}_index"] = 0
                    st.session_state[f"{PREFIX}_last_move"] = index
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


def _run_ai_turn(board, turn, algorithm, opponent_mode):
    import time
    from adversarial.core import MOVE_PRIORITY
    start_time = time.perf_counter()
    
    if turn == MAX_PLAYER:
        res = evaluate(board, algorithm)
        move = res["move"]
        nodes = res["nodes"]
        pruned = res["pruned"]
        candidates = res["candidates"]
    else:
        # AI is MIN (O)
        moves = legal_moves(board)
        if not moves:
            return
        nodes = 0
        pruned = 0
        candidates = []
        for m in moves:
            next_state = board_after(board, m, MIN_PLAYER)
            res = evaluate(next_state, algorithm)
            nodes += res["nodes"] + 1
            pruned += res["pruned"]
            candidates.append((m, res["value"]))
            
        if opponent_mode == "Random":
            import random
            move = random.choice(moves)
        else:
            candidates.sort(key=lambda item: (item[1], MOVE_PRIORITY[item[0]]))
            move = candidates[0][0]
            
    elapsed = (time.perf_counter() - start_time) * 1000.0
    
    st.session_state[f"{PREFIX}_ai_stats"] = {
        "move": move,
        "nodes": nodes,
        "pruned": pruned,
        "elapsed_ms": elapsed,
        "candidates": candidates,
        "algorithm": algorithm
    }
    
    _push_history()
    st.session_state[f"{PREFIX}_board"] = board_after(board, move, turn)
    st.session_state[f"{PREFIX}_turn"] = opponent(turn)
    st.session_state[f"{PREFIX}_last_move"] = move


def _render_ai_decision_panel():
    st.subheader("Bảng tính toán quyết định của AI")
    ai_stats = st.session_state.get(f"{PREFIX}_ai_stats")
    if ai_stats is None:
        st.info("Chưa có lượt tính toán nào từ AI. Hãy đi một nước để kích hoạt AI!")
        return
        
    st.html(f"""
<div style="border:2.5px solid #111;box-shadow:4px 4px 0 #111;background:{COLORS['accent_4']};padding:1rem;margin-bottom:1rem;">
  <div style="font-weight:900;font-size:1.1rem;">AI Decision (Thuật toán: {ai_stats['algorithm']})</div>
  <div style="margin-top:.45rem;">
    Quyết định đi nước: <b>{move_label(ai_stats['move'])}</b>
  </div>
  <hr style="border:0;border-top:2px solid #111;margin:8px 0;">
  <div><b>Tổng số nút duyệt:</b> {ai_stats['nodes']}</div>
  <div><b>Số nhánh bị tỉa:</b> {ai_stats['pruned']}</div>
  <div><b>Thời gian chạy:</b> {ai_stats['elapsed_ms']:.2f} ms</div>
</div>
""")
    
    st.markdown("**Bảng điểm các nước đi ứng viên:**")
    candidates = ai_stats.get("candidates", [])
    if not candidates:
        st.caption("Không có nước đi khả dụng.")
    else:
        rows = [
            {
                "Nước đi": move_label(move),
                "Điểm đánh giá": round(score, 3),
                "Quyết định": "Chọn ⭐" if move == ai_stats["move"] else ""
            }
            for move, score in candidates
        ]
        st.dataframe(rows, use_container_width=True, hide_index=True)


import math


def opponent(player):
    return MIN_PLAYER if player == MAX_PLAYER else MAX_PLAYER


def _reconstruct_stack_frames(event, root_board, root_player, algorithm):
    path = event["path"]
    current_board = root_board
    current_player = root_player
    
    frames = []
    for i in range(len(path) + 1):
        is_chance = (algorithm == "Expectimax" and current_player == MIN_PLAYER)
        role = "CHANCE" if is_chance else ("MAX" if current_player == MAX_PLAYER else "MIN")
        
        # Next move chosen on path (if any)
        next_move = path[i] if i < len(path) else event.get("current_move")
        is_active = (i == len(path))
        
        frame_data = {
            "depth": i,
            "board": current_board,
            "player": current_player,
            "role": role,
            "next_move": next_move,
            "is_active": is_active,
            "alpha": event.get("alpha") if is_active else None,
            "beta": event.get("beta") if is_active else None,
            "value": event.get("value") if is_active else None,
        }
        frames.append(frame_data)
        
        if i < len(path):
            current_board = board_after(current_board, path[i], current_player)
            current_player = opponent(current_player)
            
    return frames


def _get_frame_description(frame, phase, event, algorithm):
    depth = frame["depth"]
    role = frame["role"]
    player = frame["player"]
    next_move_lbl = move_label(frame["next_move"]) if frame["next_move"] is not None else None
    
    if not frame["is_active"]:
        return f"Đang đợi kết quả từ các nhánh con. Đã chọn đi thử nước <b>{next_move_lbl}</b>."
        
    if phase == "ENTER":
        desc = f"Bắt đầu duyệt nút <b>{role}</b> ({player}) ở độ sâu {depth}."
        if algorithm == "Alpha-Beta":
            alpha_str = f"{event.get('alpha'):.2f}" if isinstance(event.get('alpha'), (int, float)) and abs(event.get('alpha')) != math.inf else str(event.get('alpha'))
            beta_str = f"{event.get('beta'):.2f}" if isinstance(event.get('beta'), (int, float)) and abs(event.get('beta')) != math.inf else str(event.get('beta'))
            desc += f"<br>Nhận giới hạn truyền xuống từ cha: &alpha; = <b>{alpha_str}</b>, &beta; = <b>{beta_str}</b>."
        return desc
        
    elif phase == "DESCEND":
        return f"Gọi đệ quy xuống cấp tiếp theo bằng nước đi thử <b>{next_move_lbl}</b>."
        
    elif phase == "UPDATE":
        val = event.get("value")
        val_str = f"{val:.2f}" if isinstance(val, (int, float)) and abs(val) != math.inf else str(val)
        desc = f"Nhận kết quả từ nhánh con trả về. Giá trị ước lượng tạm thời tại nút <b>{role}</b> này là <b>{val_str}</b>."
        if algorithm == "Alpha-Beta":
            alpha_str = f"{event.get('alpha'):.2f}" if isinstance(event.get('alpha'), (int, float)) and abs(event.get('alpha')) != math.inf else str(event.get('alpha'))
            beta_str = f"{event.get('beta'):.2f}" if isinstance(event.get('beta'), (int, float)) and abs(event.get('beta')) != math.inf else str(event.get('beta'))
            desc += f"<br>Cập nhật giới hạn: &alpha; = <b>{alpha_str}</b>, &beta; = <b>{beta_str}</b>."
        return desc
        
    elif phase == "LEAF":
        val = event.get("value")
        val_str = f"{val:.2f}" if isinstance(val, (int, float)) and abs(val) != math.inf else str(val)
        return f"Đã đạt nút lá (trạng thái kết thúc hoặc chạm độ sâu giới hạn). Trả giá trị đánh giá <b>{val_str}</b> về cho cha."
        
    elif phase == "PRUNE":
        pruned_lbls = ", ".join(move_label(m) for m in event.get("pruned_moves", []))
        alpha_str = f"{event.get('alpha'):.2f}" if isinstance(event.get('alpha'), (int, float)) and abs(event.get('alpha')) != math.inf else str(event.get('alpha'))
        beta_str = f"{event.get('beta'):.2f}" if isinstance(event.get('beta'), (int, float)) and abs(event.get('beta')) != math.inf else str(event.get('beta'))
        return f"⚠️ <b>CẮT NHÁNH {algorithm.upper()}!</b> Vì giới hạn &alpha; ({alpha_str}) &ge; &beta; ({beta_str}), thuật toán quyết định bỏ qua không cần tính các nhánh còn lại: <b>{pruned_lbls}</b>."
        
    elif phase == "RETURN":
        val = event.get("value")
        val_str = f"{val:.2f}" if isinstance(val, (int, float)) and abs(val) != math.inf else str(val)
        return f"Đã duyệt xong nút này. Trả giá trị tối ưu <b>{val_str}</b> về cho nút cha."
        
    return event["message"]


def _render_storyboard(event, root_board, root_player, algorithm):
    frames = _reconstruct_stack_frames(event, root_board, root_player, algorithm)
    
    html_parts = []
    for frame in frames:
        is_active = frame["is_active"]
        if is_active:
            phase_color = {
                "ENTER": COLORS["accent_4"],  # Blue
                "LEAF": COLORS["accent_5"],   # Purple
                "UPDATE": COLORS["accent_1"], # Green
                "PRUNE": COLORS["accent_3"],  # Red
                "RETURN": COLORS["accent_2"], # Yellow
            }.get(event["phase"], "#FFFFFF")
            border_style = "border: 2.5px solid #111111; box-shadow: 4px 4px 0px #111111;"
            active_badge = f"<span style='background:#111111;color:#FFFFFF;padding:2px 8px;font-size:0.7rem;font-weight:900;margin-left:8px;'>ĐANG CHẠY</span>"
        else:
            phase_color = "#FFFFFF"
            border_style = "border: 1.5px dashed #888888; opacity: 0.8;"
            active_badge = ""
            
        desc = _get_frame_description(frame, event["phase"], event, algorithm)
        mini_board_html = _mini_board(frame["board"])
        
        ab_info = ""
        if algorithm == "Alpha-Beta" and is_active:
            alpha = frame.get("alpha")
            beta = frame.get("beta")
            alpha_str = f"{alpha:.2f}" if isinstance(alpha, (int, float)) and abs(alpha) != math.inf else str(alpha)
            beta_str = f"{beta:.2f}" if isinstance(beta, (int, float)) and abs(beta) != math.inf else str(beta)
            ab_info = f"""
            <div style="font-size:0.75rem; margin-top:0.3rem; background:#FFFFFF; border:1.5px solid #111111; padding:2px 6px; display:inline-block; font-weight:700;">
                &alpha; = {alpha_str} &nbsp;|&nbsp; &beta; = {beta_str}
            </div>
            """
            
        role_label = f"Nút {frame['role']}"
        if frame['role'] == "MAX":
            role_badge_bg = COLORS["accent_1"]
        elif frame['role'] == "MIN":
            role_badge_bg = COLORS["accent_4"]
        else:
            role_badge_bg = COLORS["accent_2"]
            
        html_parts.append(f"""
<div style="background:{phase_color}; {border_style} padding: 0.8rem; margin-bottom: 0.8rem; display: flex; gap: 1rem; align-items: center;">
    <div style="flex-shrink: 0;">
        {mini_board_html}
    </div>
    <div style="flex-grow: 1; font-family: 'Outfit', sans-serif; color: #111111;">
        <div style="display: flex; align-items: center; margin-bottom: 0.2rem;">
            <span style="background:{role_badge_bg}; border: 1.5px solid #111111; font-weight:900; font-size:0.75rem; padding: 1px 6px;">
                {role_label} (Cấp {frame['depth']})
            </span>
            {active_badge}
        </div>
        <div style="font-size: 0.85rem; line-height: 1.4;">
            {desc}
        </div>
        {ab_info}
    </div>
</div>
""")
    return "\n".join(html_parts)


def _debug_event(event):
    st.subheader("Ngăn xếp Đệ quy Trực quan")
    if event is None:
        st.info("Nhấn 'Debug Reset', sau đó sử dụng 'Debug Step' để theo dõi từng bước chạy của thuật toán đệ quy.")
        return
        
    index = st.session_state[f"{PREFIX}_index"]
    total = len(st.session_state[f"{PREFIX}_events"])
    
    st.markdown(f"**Tiến trình đệ quy: Bước {index + 1} / {total}**")
    
    root_board = st.session_state[f"{PREFIX}_board"]
    root_player = st.session_state[f"{PREFIX}_turn"]
    algorithm = st.session_state[f"{PREFIX}_algorithm"]
    
    st.html(_render_storyboard(event, root_board, root_player, algorithm))
    
    # Show values already returned by children or pruned moves below
    if event.get("child_values") or event.get("pruned_moves"):
        col_c, col_p = st.columns(2)
        with col_c:
            if event.get("child_values"):
                st.markdown("**Giá trị con đã trả về:**")
                st.dataframe(
                    [{"Nước đi": move_label(move), "Giá trị": round(value, 3)} for move, value in event["child_values"]],
                    use_container_width=True,
                    hide_index=True
                )
        with col_p:
            if event.get("pruned_moves"):
                st.markdown("**Nước đi bị cắt nhánh:**")
                st.error(", ".join(move_label(move) for move in event["pruned_moves"]))


def _mini_board(board):
    cells = []
    for value in board:
        label = "" if value == EMPTY else value
        color = "#111111"
        if value == MAX_PLAYER:
            color = "#FF6B6B"
        elif value == MIN_PLAYER:
            color = "#74B9FF"
        cells.append(f"""
        <div style="
            width: 32px; height: 32px;
            background: #FFFFFF;
            border: 1.5px solid #111111;
            box-shadow: 1.5px 1.5px 0px #111111;
            display: flex; align-items: center; justify-content: center;
            font-size: 1rem; font-weight: 900;
            color: {color};
        ">{label}</div>
        """)
    return "<div style='display:grid;grid-template-columns:repeat(3,32px);gap:3px;justify-content:center;'>" + "".join(cells) + "</div>"
