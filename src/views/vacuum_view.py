"""
vacuum_view.py - Giao diện mô phỏng Robot Hút Bụi (Vacuum Agent) trong Streamlit
"""

import streamlit as st
import time

from config.settings import GRID_SIZE, DIRTY
from core.vacuum_logic import init_vacuum_state, step_vacuum
from styles.theme import COLORS
from styles.components import neo_panel
from components.vacuum_grid import _render_grid_html


def render(base_dir: str):
    """Render giao diện module Vacuum Agent."""

    # ── Header ────────────────────────────────────────────────────────────────
    st.html(f"""
<div style="
    background-color: {COLORS['accent_1']};
    border: 2.5px solid var(--neo-border);
    box-shadow: 5px 5px 0px var(--neo-shadow);
    padding: 1rem 1.5rem;
    margin-bottom: 1.5rem;
">
    <h1 style="margin: 0; font-size: 2rem; letter-spacing: -1px; color: var(--neo-text);">
        🤖 ROBOT HÚT BỤI (VACUUM AGENT)
    </h1>
    <p style="margin: 0; font-size: 0.9rem; color: var(--neo-muted); font-weight: 600;">
        Mô phỏng tác nhân dọn phòng thông minh — Simple Reflex vs Model-Based
    </p>
</div>
""")

    # ── Control Panel ──────────────────────────────────────────────────────────
    col_type, col_speed = st.columns([3, 3])
    with col_type:
        st.markdown("**🧠 Chọn loại Agent**")
        agent_type = st.selectbox(
            "Agent", ["Simple Reflex Agent", "Model-Based Agent"],
            key="va_type_select", label_visibility="collapsed"
        )
        # rút gọn về tên ngắn
        agent_type_key = "Simple Reflex" if "Simple" in agent_type else "Model-Based"

    with col_speed:
        st.markdown("**⚡ Tốc độ Auto Run (ms)**")
        speed_ms = st.slider("Speed VA", 100, 2000, 500, 100, label_visibility="collapsed")

    st.markdown("---")

    # ── Nút điều khiển ────────────────────────────────────────────────────────
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""<style>
            div[data-testid="column"]:nth-child(1) .stButton > button {{
                background-color: {COLORS['btn_run']} !important; width: 100%;
                color: #111 !important;
            }}
        </style>""", unsafe_allow_html=True)
        btn_start = st.button("▶ Bắt đầu / Reset", key="va_btn_start", use_container_width=True)
    with c2:
        st.markdown(f"""<style>
            div[data-testid="column"]:nth-child(2) .stButton > button {{
                background-color: {COLORS['btn_step']} !important; width: 100%;
                color: #111 !important;
            }}
        </style>""", unsafe_allow_html=True)
        btn_next = st.button("⏭ Next Step", key="va_btn_next", use_container_width=True)
    with c3:
        is_running = st.session_state.get("va_running", False)
        st.markdown(f"""<style>
            div[data-testid="column"]:nth-child(3) .stButton > button {{
                background-color: {COLORS['accent_4']} !important; width: 100%;
                color: #111 !important;
            }}
        </style>""", unsafe_allow_html=True)
        btn_auto = st.button(
            "⏸ Dừng (Pause)" if is_running else "🔄 Auto Run",
            key="va_btn_auto", use_container_width=True
        )

    # ── Xử lý sự kiện ─────────────────────────────────────────────────────────
    if btn_start:
        init_vacuum_state(agent_type_key)
        st.rerun()

    if btn_next and not st.session_state.get("va_done", True):
        step_vacuum()

    if btn_auto:
        st.session_state["va_running"] = not st.session_state.get("va_running", False)

    # ── Kiểm tra đã khởi tạo chưa ─────────────────────────────────────────────
    if "va_env" not in st.session_state:
        st.html(neo_panel(
            f'<p style="text-align: center; font-size: 1.1rem; font-weight: 700; color: var(--neo-muted);">'
            f'👆 Chọn loại Agent và nhấn <b>▶ Bắt đầu</b> để bắt đầu mô phỏng!</p>',
            bg_color="var(--neo-bg)"
        ))
        return



    # ── Lấy dữ liệu ───────────────────────────────────────────────────────────
    env        = st.session_state["va_env"]
    agent      = st.session_state["va_agent"]
    step       = st.session_state.get("va_step", 0)
    done       = st.session_state.get("va_done", False)
    log        = st.session_state.get("va_log", [])
    visited    = getattr(agent, "visited", None)
    atype      = st.session_state.get("va_agent_type", "Simple Reflex")

    # Đếm ô còn bẩn
    dirty_count = env.dirty_count()

    # ── Thanh trạng thái ──────────────────────────────────────────────────────
    status_bg = COLORS["accent_1"] if done else COLORS["accent_2"]
    status_txt = f"✅ Dọn sạch sau {step} bước!" if done else \
                 f"Bước: {step} | Còn {dirty_count} ô bẩn | Agent: {atype}"
    st.html(f"""
<div style="
    background-color: {status_bg}; border: 2.5px solid var(--neo-border);
    box-shadow: 4px 4px 0px var(--neo-shadow);
    padding: 0.6rem 1.2rem; margin-bottom: 1rem;
    font-weight: 700; font-size: 1rem; font-family: 'Outfit', sans-serif;
    color: #111;
">
    {status_txt}
</div>
""")

    # ── Layout: Grid + Log ────────────────────────────────────────────────────
    col_grid, col_log = st.columns([3, 2])

    with col_grid:
        grid_html = _render_grid_html(env, agent.x, agent.y, visited)
        st.html(f"""
<div style="
    background-color: var(--neo-panel);
    border: 2.5px solid var(--neo-border);
    box-shadow: 5px 5px 0px var(--neo-shadow);
    padding: 1rem;
">
    <div style="font-weight: 900; font-size: 1.1rem; margin-bottom: 0.8rem; color: var(--neo-text);">
        🗺️ Ma trận phòng ({GRID_SIZE}×{GRID_SIZE})
    </div>
    {grid_html}
    <div style="margin-top: 0.8rem; font-size: 0.8rem; font-weight: 600; color: var(--neo-muted);">
        🤖 Robot &nbsp;&nbsp; 
        <span style="background: {COLORS['accent_1']}; border: 1.5px solid var(--neo-border); padding: 1px 6px; color: #111;">Sạch (đã thăm)</span> &nbsp;&nbsp;
        <span style="background: #8B4513; border: 1.5px solid var(--neo-border); padding: 1px 6px; color: white;">Bẩn</span> &nbsp;&nbsp;
        <span style="background: var(--neo-bg); border: 1.5px solid var(--neo-border); padding: 1px 6px; color: var(--neo-text);">Chưa thăm</span>
    </div>
</div>
""")

    with col_log:
        recent_log = log[-20:] if len(log) > 20 else log
        log_items = "".join(
            f'<div style="padding: 3px 0; border-bottom: 1px solid var(--neo-border); font-size: 0.85rem; color: var(--neo-text);">{entry}</div>'
            for entry in reversed(recent_log)
        )
        st.html(f"""
<div style="
    background-color: var(--neo-panel);
    border: 2.5px solid var(--neo-border);
    box-shadow: 5px 5px 0px var(--neo-shadow);
    padding: 1rem; height: 350px; overflow-y: auto;
">
    <div style="font-weight: 900; font-size: 1.1rem; margin-bottom: 0.8rem; color: var(--neo-text);">
        📜 Nhật ký hành động
    </div>
    <div style="font-family: 'Outfit', sans-serif;">
        {log_items if log_items else
         f'<span style="color: var(--neo-muted); font-style: italic;">Chưa có hành động nào...</span>'}
    </div>
</div>
""")

    # Auto Run Loop (Đặt ở cuối cùng để Streamlit vẽ xong UI rồi mới Sleep & Rerun)
    if st.session_state.get("va_running") and not st.session_state.get("va_done"):
        time.sleep(speed_ms / 1000.0)
        step_vacuum()
        st.rerun()
