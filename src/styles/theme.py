"""
theme.py - Hệ thống CSS Neobrutalism phong cách Light Mode duy nhất.
Loại bỏ hoàn toàn chế độ Dark Mode để giao diện luôn hiển thị đồng nhất.
"""

import streamlit as st


# ── Hằng số màu sắc Light Mode cố định ────────────────────────────────────────
COLORS = {
    "bg":         "#F4F0E6",  # Nền giấy tái chế nhẹ nhàng
    "panel":      "#FFFFFF",  # Khung panel trắng tinh
    "accent_1":   "#A8FF3E",  # Xanh Neon cực chất
    "accent_2":   "#FFE135",  # Vàng Neon sáng
    "accent_3":   "#FF6B6B",  # Đỏ Neon cảnh báo
    "accent_4":   "#74B9FF",  # Xanh dương nhẹ
    "accent_5":   "#A29BFE",  # Tím pastel ngọt ngào
    "tile_bg":    "#FFFFFF",  # Ô số puzzle trắng
    "tile_blank": "#A8FF3E",  # Ô trống màu xanh lá neon
    "text":       "#111111",  # Chữ đen rõ nét
    "black":      "#111111",  # Viền đen cứng cáp
    "muted":      "#666666",  # Chú thích xám đậm
    "btn_run":    "#A8FF3E",
    "btn_step":   "#FFE135",
    "btn_reset":  "#FF6B6B",
}

BORDER     = "2.5px solid #111111"
SHADOW     = "4px 4px 0px #111111"
SHADOW_SM  = "3px 3px 0px #111111"


def apply_global_styles():
    """Inject CSS Neobrutalism cố định Light Mode, ghi đè hoàn toàn Dark Mode của Streamlit."""
    css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;900&display=swap');

:root {
    --neo-bg: #F4F0E6;
    --neo-panel: #FFFFFF;
    --neo-text: #111111;
    --neo-border: #111111;
    --neo-shadow: #111111;
    --neo-muted: #666666;
}

/* Ép buộc mọi chế độ hiển thị (Dark Mode/Light Mode/System) đều dùng Light Mode theme */
html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
    background-color: #F4F0E6 !important;
    font-family: 'Outfit', sans-serif !important;
    color: #111111 !important;
}

[data-testid="stSidebar"] {
    background-color: #FFFFFF !important;
    border-right: 2.5px solid #111111 !important;
    padding-top: 1rem;
}

[data-testid="stSidebar"] * {
    font-family: 'Outfit', sans-serif !important;
    color: #111111 !important;
}

/* Các nhãn của radio button, selectbox, slider */
label, div[data-testid="stMarkdownContainer"] p, span, li, b, strong {
    color: #111111 !important;
}

h1, h2, h3, h4, h5, h6 {
    font-family: 'Outfit', sans-serif !important;
    font-weight: 900 !important;
    color: #111111 !important;
    letter-spacing: -0.5px;
}

/* Định dạng các nút bấm Neobrutalism */
.stButton > button {
    font-family: 'Outfit', sans-serif !important;
    font-weight: 700 !important;
    border: 2.5px solid #111111 !important;
    box-shadow: 3px 3px 0px #111111 !important;
    border-radius: 0px !important;
    transition: all 0.08s ease !important;
    padding: 0.4rem 1.2rem !important;
    background-color: #FFFFFF !important;
    color: #111111 !important;
}

.stButton > button:hover {
    transform: translate(2px, 2px) !important;
    box-shadow: 1px 1px 0px #111111 !important;
    background-color: #FFFFFF !important;
    color: #111111 !important;
    border-color: #111111 !important;
}

.stButton > button:active {
    transform: translate(4px, 4px) !important;
    box-shadow: none !important;
}

/* Selectbox Neobrutalism */
[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
    border: 2.5px solid #111111 !important;
    border-radius: 0 !important;
    box-shadow: 3px 3px 0px #111111 !important;
    background-color: #FFFFFF !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 600 !important;
    color: #111111 !important;
}

/* Khắc phục màu chữ dropdown selectbox */
div[role="listbox"] ul li {
    color: #111111 !important;
    background-color: #FFFFFF !important;
}

/* Slider Neobrutalism */
div[data-testid="stSlider"] * {
    color: #111111 !important;
}

hr {
    border: 1.5px solid #111111 !important;
    margin: 1rem 0 !important;
}

/* Custom Scrollbar */
::-webkit-scrollbar {
    width: 8px;
}
::-webkit-scrollbar-track {
    background: #F4F0E6;
}
::-webkit-scrollbar-thumb {
    background: #111111;
    border-radius: 0;
}
</style>
"""
    st.markdown(css, unsafe_allow_html=True)
