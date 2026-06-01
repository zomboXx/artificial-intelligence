# AI Search Visualizer Architecture

This project is organized as a generic AI search visualization framework.

The central design rule is:

```text
Problem is independent from Algorithm.
Algorithm is independent from UI.
UI renders SearchStep traces.
```

## Runtime Flow

```text
src/main.py
  -> views/search_view.py
      -> problems/registry.py
          -> selected SearchProblem
      -> search/algorithms/*
          -> yields SearchStep
      -> selected problem renderer

  -> views/vacuum_view.py
      -> core/vacuum_logic.py
```

## Generic Search Core

The search engine lives in `src/search`.

- `search/problem.py`: common `SearchProblem` protocol.
- `search/types.py`: `SearchNode`, `SearchStep`, path reconstruction.
- `search/algorithms/uninformed.py`: BFS, DFS, IDS.
- `search/algorithms/informed.py`: UCS, Greedy Best-First Search, A*.

All algorithms consume the same problem interface:

```python
initial_state()
is_goal(state)
actions(state)
result(state, action)
step_cost(state, action, next_state)
heuristic(state)
state_key(state)
```

All algorithms yield the same trace shape:

```python
SearchStep(
    current=...,
    frontier=[...],
    explored=[...],
    path=[...] | None,
    metrics={...},
)
```

## Problem Modules

Problem implementations live in `src/problems`.

- `problems/puzzle8`: 8-Puzzle.
- `problems/pathfinding`: grid pathfinding, similar to map route planning.
- `problems/queens8`: 8-Queens.

Each problem owns:

- `problem.py`: state model and search rules.
- `renderer.py`: HTML visualization for that problem's states.

## Vacuum Agent

The Vacuum Agent module remains separate because it is an agent simulation, not a generic search tree problem.

It lives in:

```text
src/views/vacuum_view.py
src/core/vacuum_logic.py
src/components/vacuum_grid.py
```

## Notebook Role

Notebooks are now learning artifacts only. The running app no longer loads algorithms from `.ipynb` files.

The active runtime algorithms are plain Python modules under `src/search/algorithms`.
