"""Streamlit visualization for Buoi 13 constraint satisfaction problems."""

from __future__ import annotations

import html
import time

import streamlit as st

from csp import make_map_coloring_csp, make_puzzle_csp, make_solver
from styles.theme import COLORS


PREFIX = "csp_lab"
ALGORITHMS = ("Backtracking", "Forward Checking", "AC-3 + Backtracking", "Min-Conflicts")
COLOR_HEX = {"Red": "#FF6B6B", "Green": "#A8FF3E", "Blue": "#74B9FF"}


def render(_base_dir=None):
    _header()
    col1, col2, col3 = st.columns([1.2, 1.4, 1])
    with col1:
        problem_key = st.selectbox("Problem", ("map", "puzzle"), format_func=lambda value: "Map Coloring" if value == "map" else "8-Puzzle as CSP", key=f"{PREFIX}_problem")
    with col2:
        algorithm = st.selectbox("Algorithm", ALGORITHMS, key=f"{PREFIX}_algorithm")
    with col3:
        speed = st.slider("Auto speed (ms)", 100, 1500, 450, 50, key=f"{PREFIX}_speed")

    _controls(problem_key, algorithm)
    step = st.session_state.get(f"{PREFIX}_step")
    csp = st.session_state.get(f"{PREFIX}_csp")
    if step is None or csp is None:
        st.info("Press Start / Reset to initialize the CSP debugger.")
        return

    _metrics(step)
    left, right = st.columns([1.25, 1])
    with left:
        if csp.kind == "map":
            _render_map(csp, step)
        else:
            _render_puzzle(csp, step)
    with right:
        _render_debug(step)
    _render_domains(csp, step)

    if st.session_state.get(f"{PREFIX}_running") and not step.terminal:
        time.sleep(speed / 1000)
        _advance()
        st.rerun()


def _header():
    st.html(f"""
<div style="background:{COLORS['accent_2']};border:2.5px solid #111;box-shadow:5px 5px 0 #111;padding:1rem 1.4rem;margin-bottom:1.2rem;">
  <h1 style="margin:0;font-size:1.9rem;">CSP Lab - Buổi 13</h1>
  <div style="font-weight:700;color:#444;">Backtracking, Forward Checking, AC-3 and Min-Conflicts</div>
</div>
""")


def _controls(problem_key, algorithm):
    columns = st.columns(4)
    with columns[0]:
        if st.button("Start / Reset", use_container_width=True, key=f"{PREFIX}_start"):
            csp = make_map_coloring_csp() if problem_key == "map" else make_puzzle_csp()
            st.session_state[f"{PREFIX}_csp"] = csp
            st.session_state[f"{PREFIX}_runner"] = make_solver(csp, algorithm)
            st.session_state[f"{PREFIX}_running"] = False
            st.session_state[f"{PREFIX}_done"] = False
            _advance()
            st.rerun()
    with columns[1]:
        if st.button("Next Step", use_container_width=True, key=f"{PREFIX}_next"):
            _advance()
            st.rerun()
    with columns[2]:
        running = st.session_state.get(f"{PREFIX}_running", False)
        if st.button("Pause" if running else "Auto Run", use_container_width=True, key=f"{PREFIX}_auto"):
            st.session_state[f"{PREFIX}_running"] = not running
            st.rerun()
    with columns[3]:
        if st.button("Stop", use_container_width=True, key=f"{PREFIX}_stop"):
            st.session_state[f"{PREFIX}_running"] = False
            st.session_state[f"{PREFIX}_done"] = True


def _advance():
    runner = st.session_state.get(f"{PREFIX}_runner")
    if runner is None or st.session_state.get(f"{PREFIX}_done"):
        return
    try:
        step = next(runner)
        st.session_state[f"{PREFIX}_step"] = step
        if step.terminal:
            st.session_state[f"{PREFIX}_running"] = False
            st.session_state[f"{PREFIX}_done"] = True
    except StopIteration:
        st.session_state[f"{PREFIX}_running"] = False
        st.session_state[f"{PREFIX}_done"] = True


def _metrics(step):
    values = (
        ("Status", step.status),
        ("Step", step.step_index),
        ("Checks", step.checks),
        ("Pruned", step.pruned),
        ("Backtracks", step.backtracks),
        ("Conflicts", len(step.conflicts)),
    )
    columns = st.columns(len(values))
    for column, (label, value) in zip(columns, values):
        column.metric(label, value)


def _render_map(csp, step):
    st.subheader("Map assignment")
    regions = []
    conflicted = {var for pair in step.conflicts for var in pair}
    for var in csp.variables:
        value = step.assignment.get(var)
        background = COLOR_HEX.get(value, "#FFFFFF")
        border = "#D7263D" if var in conflicted else "#111111"
        domain = ", ".join(map(str, step.domains[var]))
        regions.append(f"""
<div style="background:{background};border:3px solid {border};box-shadow:3px 3px 0 #111;padding:.7rem;min-height:78px;">
  <div style="font-size:1.1rem;font-weight:900;">{var}</div>
  <div style="font-size:.8rem;font-weight:700;">{html.escape(str(value)) if value is not None else 'Unassigned'}</div>
  <div style="font-size:.7rem;color:#444;">D={html.escape(domain)}</div>
</div>""")
    st.html(f"<div style='display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:.75rem;'>{''.join(regions)}</div>")
    st.caption("Adjacency constraints: " + ", ".join(f"{left}-{right}" for left, right in (("WA", "NT"), ("WA", "SA"), ("NT", "SA"), ("NT", "Q"), ("SA", "Q"), ("SA", "NSW"), ("SA", "V"), ("Q", "NSW"), ("NSW", "V"))))


def _render_puzzle(csp, step):
    st.subheader("8-Puzzle CSP assignment")
    cells = []
    conflicted = {var for pair in step.conflicts for var in pair}
    for var in csp.variables:
        value = step.assignment.get(var)
        border = "#D7263D" if var in conflicted else "#111111"
        background = COLORS["accent_4"] if var in csp.fixed else "#FFFFFF"
        label = "" if value == 0 else ("?" if value is None else str(value))
        cells.append(f"""
<div style="aspect-ratio:1;background:{background};border:3px solid {border};box-shadow:3px 3px 0 #111;display:flex;flex-direction:column;align-items:center;justify-content:center;">
  <div style="font-size:2rem;font-weight:900;">{label}</div>
  <div style="font-size:.65rem;color:#555;">{var}{' fixed' if var in csp.fixed else ''}</div>
</div>""")
    st.html(f"<div style='display:grid;grid-template-columns:repeat(3,110px);gap:.65rem;justify-content:center;'>{''.join(cells)}</div>")
    st.caption("CSP formulation: nine cell variables, tile domains 0..8, AllDifferent constraints and four fixed clues.")


def _render_debug(step):
    st.subheader("Current inference step")
    st.html(f"""
<div style="border:2.5px solid #111;box-shadow:4px 4px 0 #111;background:{COLORS['accent_1']};padding:1rem;">
  <div style="font-weight:900;font-size:1.1rem;">{html.escape(step.status)}</div>
  <div style="margin-top:.45rem;">{html.escape(step.message)}</div>
  <hr style="border:0;border-top:2px solid #111;">
  <div><b>Variable:</b> {html.escape(str(step.current_var or '-'))}</div>
  <div><b>Value:</b> {html.escape(str(step.current_value if step.current_value is not None else '-'))}</div>
  <div><b>Assigned:</b> {len(step.assignment)}</div>
</div>
""")
    st.markdown("**Assignment**")
    st.code("\n".join(f"{var} = {value}" for var, value in step.assignment.items()) or "<empty>", language="text")
    if step.conflicts:
        st.error("Conflicts: " + ", ".join(f"{left}-{right}" for left, right in step.conflicts))


def _render_domains(csp, step):
    st.subheader("Domains after inference")
    rows = [{"Variable": var, "Domain": str(step.domains[var]), "Size": len(step.domains[var]), "Assigned": step.assignment.get(var)} for var in csp.variables]
    st.dataframe(rows, use_container_width=True, hide_index=True)
