"""CSP models and step-based solvers for the web visualizer."""

from __future__ import annotations

from dataclasses import dataclass, field
import random
from typing import Any, Callable, Iterator


@dataclass(frozen=True)
class CSP:
    name: str
    variables: tuple[str, ...]
    domains: dict[str, tuple[Any, ...]]
    neighbors: dict[str, tuple[str, ...]]
    constraint: Callable[[str, Any, str, Any], bool]
    kind: str
    fixed: frozenset[str] = frozenset()


@dataclass
class CSPStep:
    assignment: dict[str, Any]
    domains: dict[str, list[Any]]
    status: str
    message: str
    current_var: str | None = None
    current_value: Any = None
    checks: int = 0
    backtracks: int = 0
    pruned: int = 0
    step_index: int = 0
    conflicts: list[tuple[str, str]] = field(default_factory=list)
    terminal: bool = False


MAP_EDGES = (
    ("WA", "NT"), ("WA", "SA"), ("NT", "SA"), ("NT", "Q"),
    ("SA", "Q"), ("SA", "NSW"), ("SA", "V"), ("Q", "NSW"),
    ("NSW", "V"),
)


def make_map_coloring_csp() -> CSP:
    variables = ("WA", "NT", "SA", "Q", "NSW", "V", "T")
    neighbors = {var: set() for var in variables}
    for left, right in MAP_EDGES:
        neighbors[left].add(right)
        neighbors[right].add(left)
    return CSP(
        name="Map Coloring - Australia",
        variables=variables,
        domains={var: ("Red", "Green", "Blue") for var in variables},
        neighbors={var: tuple(sorted(values)) for var, values in neighbors.items()},
        constraint=lambda _a, value_a, _b, value_b: value_a != value_b,
        kind="map",
    )


def make_puzzle_csp() -> CSP:
    variables = tuple(f"C{index}" for index in range(9))
    fixed_values = {"C0": 1, "C1": 2, "C2": 3, "C4": 0}
    domains = {
        var: (fixed_values[var],) if var in fixed_values else tuple(range(9))
        for var in variables
    }
    return CSP(
        name="8-Puzzle as CSP",
        variables=variables,
        domains=domains,
        neighbors={var: tuple(other for other in variables if other != var) for var in variables},
        constraint=lambda _a, value_a, _b, value_b: value_a != value_b,
        kind="puzzle",
        fixed=frozenset(fixed_values),
    )


def make_solver(csp: CSP, algorithm: str) -> Iterator[CSPStep]:
    if algorithm == "Backtracking":
        return backtracking_steps(csp, inference="none")
    if algorithm == "Forward Checking":
        return backtracking_steps(csp, inference="forward")
    if algorithm == "AC-3 + Backtracking":
        return backtracking_steps(csp, inference="ac3")
    return min_conflicts_steps(csp)


def _copy_domains(domains):
    return {var: list(values) for var, values in domains.items()}


def _conflicts(csp: CSP, assignment: dict[str, Any]):
    result = []
    for var in csp.variables:
        if var not in assignment:
            continue
        for other in csp.neighbors[var]:
            if other not in assignment or var > other:
                continue
            if not csp.constraint(var, assignment[var], other, assignment[other]):
                result.append((var, other))
    return result


def _consistent(csp, var, value, assignment):
    return all(
        other not in assignment or csp.constraint(var, value, other, assignment[other])
        for other in csp.neighbors[var]
    )


def _select_variable(csp, assignment, domains):
    remaining = [var for var in csp.variables if var not in assignment]
    return min(remaining, key=lambda var: (len(domains[var]), -len(csp.neighbors[var]), var))


def _ordered_values(csp, var, domains, assignment):
    def eliminated(value):
        return sum(
            not csp.constraint(var, value, other, other_value)
            for other in csp.neighbors[var]
            if other not in assignment
            for other_value in domains[other]
        )
    return sorted(domains[var], key=lambda value: (eliminated(value), str(value)))


def _forward_check(csp, var, value, domains, assignment):
    next_domains = _copy_domains(domains)
    next_domains[var] = [value]
    removed = []
    for other in csp.neighbors[var]:
        if other in assignment:
            continue
        for other_value in list(next_domains[other]):
            if not csp.constraint(var, value, other, other_value):
                next_domains[other].remove(other_value)
                removed.append((other, other_value))
        if not next_domains[other]:
            return False, next_domains, removed
    return True, next_domains, removed


def _revise(csp, domains, left, right):
    removed = []
    for value in list(domains[left]):
        if not any(csp.constraint(left, value, right, other) for other in domains[right]):
            domains[left].remove(value)
            removed.append((left, value))
    return removed


def ac3(csp: CSP, domains):
    queue = [(left, right) for left in csp.variables for right in csp.neighbors[left]]
    removed = []
    processed = 0
    while queue:
        left, right = queue.pop(0)
        processed += 1
        revised = _revise(csp, domains, left, right)
        if revised:
            removed.extend(revised)
            if not domains[left]:
                return False, removed, processed
            queue.extend((neighbor, left) for neighbor in csp.neighbors[left] if neighbor != right)
    return True, removed, processed


def _step(csp, assignment, domains, status, message, counters, **kwargs):
    return CSPStep(
        assignment=dict(assignment),
        domains=_copy_domains(domains),
        status=status,
        message=message,
        checks=counters["checks"],
        backtracks=counters["backtracks"],
        pruned=counters["pruned"],
        step_index=counters["steps"],
        conflicts=_conflicts(csp, assignment),
        **kwargs,
    )


def backtracking_steps(csp: CSP, inference="none"):
    counters = {"checks": 0, "backtracks": 0, "pruned": 0, "steps": 0}
    start_domains = _copy_domains(csp.domains)

    if inference == "ac3":
        ok, removed, processed = ac3(csp, start_domains)
        counters["pruned"] += len(removed)
        counters["steps"] += 1
        yield _step(csp, {}, start_domains, "AC-3 initialization", f"Processed {processed} arcs; pruned {len(removed)} values.", counters)
        if not ok:
            yield _step(csp, {}, start_domains, "Failure", "AC-3 emptied a domain.", counters, terminal=True)
            return

    def backtrack(assignment, domains):
        if len(assignment) == len(csp.variables):
            counters["steps"] += 1
            yield _step(csp, assignment, domains, "Solved", "All variables satisfy every constraint.", counters, terminal=True)
            return True

        var = _select_variable(csp, assignment, domains)
        counters["steps"] += 1
        yield _step(csp, assignment, domains, "Select variable", f"MRV selected {var}.", counters, current_var=var)

        for value in _ordered_values(csp, var, domains, assignment):
            counters["checks"] += 1
            if not _consistent(csp, var, value, assignment):
                counters["steps"] += 1
                yield _step(csp, assignment, domains, "Reject value", f"{var}={value} violates a constraint.", counters, current_var=var, current_value=value)
                continue

            next_assignment = dict(assignment)
            next_assignment[var] = value
            next_domains = _copy_domains(domains)
            next_domains[var] = [value]
            counters["steps"] += 1
            yield _step(csp, next_assignment, next_domains, "Assign", f"Try {var}={value}.", counters, current_var=var, current_value=value)

            ok = True
            if inference in ("forward", "ac3"):
                ok, next_domains, removed = _forward_check(csp, var, value, next_domains, next_assignment)
                counters["pruned"] += len(removed)
                counters["steps"] += 1
                yield _step(csp, next_assignment, next_domains, "Forward check", f"Pruned {len(removed)} values.", counters, current_var=var, current_value=value)
            if ok and inference == "ac3":
                ok, removed, processed = ac3(csp, next_domains)
                counters["pruned"] += len(removed)
                counters["steps"] += 1
                yield _step(csp, next_assignment, next_domains, "AC-3 propagation", f"Processed {processed} arcs; pruned {len(removed)} more values.", counters, current_var=var, current_value=value)

            if ok and (yield from backtrack(next_assignment, next_domains)):
                return True

            counters["backtracks"] += 1
            counters["steps"] += 1
            yield _step(csp, assignment, domains, "Backtrack", f"Backtrack from {var}={value}.", counters, current_var=var, current_value=value)
        return False

    solved = yield from backtrack({}, start_domains)
    if not solved:
        counters["steps"] += 1
        yield _step(csp, {}, start_domains, "Failure", "No satisfying assignment exists.", counters, terminal=True)


def min_conflicts_steps(csp: CSP, max_steps=250):
    counters = {"checks": 0, "backtracks": 0, "pruned": 0, "steps": 0}
    assignment = {
        var: csp.domains[var][0] if var in csp.fixed else random.choice(csp.domains[var])
        for var in csp.variables
    }
    domains = _copy_domains(csp.domains)
    yield _step(csp, assignment, domains, "Initialize", "Created a complete random assignment.", counters)

    for index in range(1, max_steps + 1):
        counters["steps"] = index
        conflicts = _conflicts(csp, assignment)
        if not conflicts:
            yield _step(csp, assignment, domains, "Solved", "No conflicts remain.", counters, terminal=True)
            return
        variables = sorted({var for pair in conflicts for var in pair if var not in csp.fixed})
        if not variables:
            yield _step(csp, assignment, domains, "Stuck", "Only fixed variables remain conflicted.", counters, terminal=True)
            return
        var = random.choice(variables)

        def score(value):
            return sum(
                not csp.constraint(var, value, other, assignment[other])
                for other in csp.neighbors[var]
            )

        scores = [(value, score(value)) for value in csp.domains[var]]
        best_score = min(item[1] for item in scores)
        value = random.choice([item[0] for item in scores if item[1] == best_score])
        previous = assignment[var]
        assignment[var] = value
        counters["checks"] += len(scores)
        yield _step(csp, assignment, domains, "Min-conflicts", f"Change {var}: {previous} -> {value}; local conflicts={best_score}.", counters, current_var=var, current_value=value)

    yield _step(csp, assignment, domains, "Stopped", "Reached the min-conflicts step limit.", counters, terminal=True)
