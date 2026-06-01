"""Generic search visualizer view."""

from __future__ import annotations

import time

import streamlit as st

from problems.registry import PROBLEMS
from search.algorithms import ALGORITHM_LABELS, ALGORITHMS
from styles.components import neo_panel
from styles.theme import COLORS


SESSION_PREFIX = "search_lab"


def render(base_dir: str | None = None):
    """Render a problem-independent search visualizer."""
    _render_header()

    selected_key = st.selectbox(
        "Problem",
        options=list(PROBLEMS.keys()),
        format_func=lambda key: PROBLEMS[key].label,
        key=f"{SESSION_PREFIX}_problem",
    )
    spec = PROBLEMS[selected_key]

    options = _render_problem_options(spec)

    algo_key = st.selectbox(
        "Algorithm",
        options=list(spec.algorithms),
        format_func=lambda key: ALGORITHM_LABELS[key],
        key=f"{SESSION_PREFIX}_algo",
    )

    speed_ms = st.slider(
        "Auto run speed (ms)",
        min_value=50,
        max_value=2000,
        value=300,
        step=50,
        key=f"{SESSION_PREFIX}_speed",
    )

    st.markdown("---")
    _render_controls(spec, options, algo_key)

    if f"{SESSION_PREFIX}_runner" not in st.session_state:
        st.html(neo_panel(
            f"""
            <div style="text-align:center; font-weight:800; color:var(--neo-muted);">
                Choose a problem and algorithm, then press Start / Reset.
            </div>
            <div style="text-align:center; margin-top:0.4rem; color:var(--neo-muted);">
                Current module: {spec.description}
            </div>
            """,
            bg_color="var(--neo-bg)",
        ))
        return

    if st.session_state.get(f"{SESSION_PREFIX}_problem_active") != selected_key:
        st.html(neo_panel(
            """
            <div style="text-align:center; font-weight:800; color:var(--neo-muted);">
                Press Start / Reset to initialize the selected problem.
            </div>
            """,
            bg_color="var(--neo-bg)",
        ))
        return

    problem = st.session_state[f"{SESSION_PREFIX}_problem_obj"]
    step = st.session_state.get(f"{SESSION_PREFIX}_step")
    if step is None:
        return

    _render_status(step)
    _render_problem_surface(spec, problem, step)
    _render_collections(spec, step)

    if st.session_state.get(f"{SESSION_PREFIX}_running") and step.path is None:
        time.sleep(speed_ms / 1000.0)
        _advance()
        st.rerun()


def _render_header():
    st.html(f"""
<div style="
    background-color: {COLORS['accent_2']};
    border: 2.5px solid var(--neo-border);
    box-shadow: 5px 5px 0px var(--neo-shadow);
    padding: 1rem 1.5rem;
    margin-bottom: 1.5rem;
">
    <h1 style="margin:0; font-size:2rem; color:var(--neo-text);">AI Search Visualizer</h1>
    <p style="margin:0; font-size:0.9rem; color:var(--neo-muted); font-weight:700;">
        One generic search engine running on multiple AI problems.
    </p>
</div>
""")


def _render_problem_options(spec):
    options = dict(spec.default_options)

    if spec.key == "puzzle8":
        col1, col2 = st.columns(2)
        with col1:
            options["shuffle"] = st.checkbox(
                "Random solvable start state",
                value=options["shuffle"],
                key=f"{SESSION_PREFIX}_puzzle_shuffle",
            )
        with col2:
            options["weighted_cost"] = st.checkbox(
                "UCS uses moved tile value as step cost",
                value=options["weighted_cost"],
                key=f"{SESSION_PREFIX}_puzzle_weighted",
            )
    elif spec.key == "queens8":
        options["size"] = st.slider(
            "Board size",
            min_value=4,
            max_value=10,
            value=int(options["size"]),
            step=1,
            key=f"{SESSION_PREFIX}_queens_size",
        )

    return options


def _render_controls(spec, options, algo_key):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        _style_button(1, COLORS["btn_run"])
        if st.button("Start / Reset", use_container_width=True, key=f"{SESSION_PREFIX}_start"):
            problem = spec.factory(options)
            runner = ALGORITHMS[algo_key](problem)
            st.session_state[f"{SESSION_PREFIX}_problem_obj"] = problem
            st.session_state[f"{SESSION_PREFIX}_runner"] = runner
            st.session_state[f"{SESSION_PREFIX}_algo_active"] = algo_key
            st.session_state[f"{SESSION_PREFIX}_problem_active"] = spec.key
            st.session_state[f"{SESSION_PREFIX}_running"] = False
            st.session_state[f"{SESSION_PREFIX}_done"] = False
            _advance()
            st.rerun()

    with col2:
        _style_button(2, COLORS["btn_step"])
        if st.button("Next Step", use_container_width=True, key=f"{SESSION_PREFIX}_next"):
            _advance()

    with col3:
        _style_button(3, COLORS["accent_4"])
        running = st.session_state.get(f"{SESSION_PREFIX}_running", False)
        if st.button("Pause" if running else "Auto Run", use_container_width=True, key=f"{SESSION_PREFIX}_auto"):
            st.session_state[f"{SESSION_PREFIX}_running"] = not running

    with col4:
        _style_button(4, COLORS["btn_reset"])
        if st.button("Stop", use_container_width=True, key=f"{SESSION_PREFIX}_stop"):
            st.session_state[f"{SESSION_PREFIX}_running"] = False
            st.session_state[f"{SESSION_PREFIX}_done"] = True


def _advance():
    runner = st.session_state.get(f"{SESSION_PREFIX}_runner")
    if runner is None or st.session_state.get(f"{SESSION_PREFIX}_done"):
        return

    try:
        step = next(runner)
        st.session_state[f"{SESSION_PREFIX}_step"] = step
        if step.path is not None:
            st.session_state[f"{SESSION_PREFIX}_running"] = False
            st.session_state[f"{SESSION_PREFIX}_done"] = True
    except StopIteration:
        st.session_state[f"{SESSION_PREFIX}_running"] = False
        st.session_state[f"{SESSION_PREFIX}_done"] = True


def _render_status(step):
    metrics = step.metrics
    bg = COLORS["accent_5"] if step.path else COLORS["accent_1"]
    fields = [
        f"Algorithm: {metrics.get('algorithm', '-')}",
        f"Expanded: {metrics.get('expanded', 0)}",
        f"Generated: {metrics.get('generated', 0)}",
        f"Frontier: {metrics.get('frontier_size', 0)}",
        f"Depth: {metrics.get('depth', 0)}",
    ]
    if metrics.get("algorithm") in ("UCS", "Greedy", "A*"):
        fields.append(f"g={metrics.get('g', 0)}")
        fields.append(f"h={metrics.get('h', 0)}")
        fields.append(f"f={metrics.get('f', 0)}")
    if "limit" in metrics:
        fields.append(f"Limit: {metrics['limit']}")

    if step.path:
        fields.append(f"Path length: {len(step.path) - 1}")

    st.html(f"""
<div style="
    background-color:{bg};
    border:2.5px solid var(--neo-border);
    box-shadow:4px 4px 0px var(--neo-shadow);
    padding:0.65rem 1rem;
    margin:1rem 0;
    font-weight:800;
    color:#111;
">{' | '.join(fields)}</div>
""")


def _render_problem_surface(spec, problem, step):
    renderer = spec.renderer
    kwargs = {
        "current": step.current,
        "frontier": step.frontier,
        "explored": step.explored,
        "path": step.path,
        "start": problem.initial_state(),
        "goal": getattr(problem, "goal", getattr(problem, "goal_state", None)),
    }
    if spec.key == "pathfinding":
        kwargs["grid"] = problem.grid
    if spec.key == "queens8":
        kwargs["size"] = problem.size

    st.html(f"""
<div style="
    background-color:var(--neo-panel);
    border:2.5px solid var(--neo-border);
    box-shadow:5px 5px 0px var(--neo-shadow);
    padding:1rem;
    margin-bottom:1rem;
">
    <div style="font-weight:900; font-size:1.05rem; margin-bottom:0.8rem;">
        Problem Surface
    </div>
    {renderer.render_board_with_trace(**kwargs)}
</div>
""")

    if step.path:
        path_items = "".join(
            renderer.render_state(state, "path")
            for state in step.path[:18]
        )
        overflow = "" if len(step.path) <= 18 else f"<div>... {len(step.path) - 18} more states</div>"
        st.html(f"""
<div style="
    background-color:{COLORS['accent_5']};
    border:2.5px solid var(--neo-border);
    box-shadow:5px 5px 0px var(--neo-shadow);
    padding:1rem;
    margin-bottom:1rem;
">
    <div style="font-weight:900; margin-bottom:0.7rem;">Solution Path</div>
    <div style="overflow-x:auto;">
        <div style="display:flex; flex-wrap:nowrap; min-width:max-content;">{path_items}</div>
        {overflow}
    </div>
</div>
""")


def _render_collections(spec, step):
    if step.path:
        return

    renderer = spec.renderer
    col1, col2 = st.columns(2)
    with col1:
        _render_state_strip("Frontier", step.frontier, renderer, COLORS["accent_2"] + "44")
    with col2:
        _render_state_strip("Explored", step.explored, renderer, COLORS["accent_3"] + "44")


def _render_state_strip(title, states, renderer, bg):
    shown = list(states[-10:]) if len(states) > 10 else list(states)
    content = "".join(renderer.render_state(state, "normal") for state in shown)
    if not content:
        content = '<div style="padding:0.8rem; color:var(--neo-muted); font-style:italic;">Empty</div>'
    note = f"<div style='font-size:0.75rem; color:var(--neo-muted);'>Showing {len(shown)}/{len(states)}</div>"

    st.html(f"""
<div style="
    background-color:{bg};
    border:2.5px solid var(--neo-border);
    box-shadow:4px 4px 0px var(--neo-shadow);
    padding:0.8rem;
    margin-bottom:1rem;
    overflow-x:auto;
">
    <div style="font-weight:900; margin-bottom:0.5rem;">{title}</div>
    <div style="display:flex; flex-wrap:nowrap; min-width:max-content;">{content}</div>
    {note}
</div>
""")


def _style_button(column_index: int, color: str):
    st.markdown(f"""<style>
        div[data-testid="column"]:nth-child({column_index}) .stButton > button {{
            background-color: {color} !important;
            width: 100%;
            color: #111 !important;
        }}
    </style>""", unsafe_allow_html=True)
