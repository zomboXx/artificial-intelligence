"""
components.py - Thư viện HTML templates Neobrutalism cho các UI widgets nhỏ
"""

from styles.theme import COLORS, BORDER, SHADOW, SHADOW_SM


def neo_panel(content_html: str, bg_color: str = "var(--neo-panel)", padding: str = "1.2rem") -> str:
    """Tạo HTML panel kiểu Neobrutalism."""
    return f"""
    <div style="
        background-color: {bg_color};
        border: {BORDER};
        box-shadow: {SHADOW};
        padding: {padding};
        margin-bottom: 1rem;
    ">
        {content_html}
    </div>
    """


def neo_badge(text: str, color: str) -> str:
    """Tạo HTML badge (nhãn nhỏ) Neobrutalism."""
    return f"""
    <span style="
        background-color: {color};
        border: 2px solid var(--neo-border);
        padding: 2px 10px;
        font-weight: 700;
        font-size: 0.75rem;
        font-family: 'Outfit', sans-serif;
        color: var(--neo-text);
    ">{text}</span>
    """


def render_puzzle_tile(value: int, highlight: bool = False) -> str:
    """Render một ô số của bàn cờ 8-Puzzle dạng HTML Neobrutalism."""
    if value == 0:
        bg = COLORS["tile_blank"]
        text = ""
    else:
        bg = COLORS["tile_bg"] if not highlight else COLORS["accent_5"]
        text = str(value)

    return f"""
    <div style="
        width: 64px; height: 64px;
        background-color: {bg};
        border: {BORDER};
        box-shadow: {SHADOW_SM};
        display: flex; align-items: center; justify-content: center;
        font-size: 1.6rem; font-weight: 900;
        font-family: 'Outfit', sans-serif;
        color: var(--neo-text);
        margin: 3px;
        flex-shrink: 0;
    ">{text}</div>
    """


def render_puzzle_board_html(state: tuple, label: str = "", label_color: str = "#FFFFFF",
                              path_states: list = None) -> str:
    """
    Render bàn cờ 3x3 của 8-Puzzle dưới dạng HTML.
    state: tuple 3x3 ((r0,r1,r2),(r0,r1,r2),(r0,r1,r2))
    """
    if isinstance(state, dict) and "state" in state:
        state = state["state"]

    in_path = path_states is not None and state in path_states
    rows_html = ""
    for row in state:
        cells = "".join(render_puzzle_tile(v, highlight=in_path) for v in row)
        rows_html += f'<div style="display:flex;">{cells}</div>'

    label_html = ""
    if label:
        label_html = f"""
        <div style="
            background-color: {label_color};
            border: {BORDER};
            padding: 2px 8px;
            font-weight: 700; font-size: 0.7rem;
            font-family: 'Outfit', sans-serif;
            color: var(--neo-text);
            margin-bottom: 4px; display: inline-block;
        ">{label}</div><br>
        """

    return f"""
    <div style="display: inline-block; margin: 6px; vertical-align: top;">
        {label_html}
        <div style="
            background-color: var(--neo-bg);
            border: {BORDER};
            box-shadow: {SHADOW_SM};
            padding: 6px;
            display: inline-block;
        ">
            {rows_html}
        </div>
    </div>
    """


def render_scrollable_states(states: list, section_color: str, max_show: int = 12) -> str:
    """Render hàng ngang các bàn cờ trong một vùng có thể scroll (Frontier / Explored)."""
    if not states:
        return f"""
        <div style="
            padding: 1rem;
            color: var(--neo-muted);
            font-style: italic;
            font-family: 'Outfit', sans-serif;
        ">— Trống —</div>
        """

    shown = states[-max_show:] if len(states) > max_show else states
    boards = "".join(render_puzzle_board_html(s) for s in shown)
    overflow_note = ""
    if len(states) > max_show:
        overflow_note = f"""
        <div style="font-size:0.75rem; color:var(--neo-muted); padding: 4px 8px; font-family:'Outfit',sans-serif;">
            ... (Hiển thị {max_show}/{len(states)} trạng thái cuối)
        </div>
        """

    return f"""
    <div style="
        overflow-x: auto;
        background-color: {section_color};
        border: {BORDER};
        box-shadow: {SHADOW};
        padding: 0.8rem;
        margin-bottom: 0.8rem;
    ">
        <div style="display: flex; flex-wrap: nowrap; align-items: flex-start; min-width: max-content;">
            {boards}
        </div>
        {overflow_note}
    </div>
    """
