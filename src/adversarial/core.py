"""Tic-Tac-Toe adversarial search and bounded step-debug traces."""

from __future__ import annotations

import math


MAX_PLAYER = "X"
MIN_PLAYER = "O"
EMPTY = " "
WIN_LINES = (
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    (0, 3, 6), (1, 4, 7), (2, 5, 8),
    (0, 4, 8), (2, 4, 6),
)

MOVE_PRIORITY = {4: 0, 0: 1, 2: 1, 6: 1, 8: 1, 1: 2, 3: 2, 5: 2, 7: 2}


def empty_board():
    return tuple(EMPTY for _ in range(9))


def board_after(board, move, player):
    values = list(board)
    values[move] = player
    return tuple(values)


def legal_moves(board):
    return [index for index, value in enumerate(board) if value == EMPTY]


def winner(board):
    for left, middle, right in WIN_LINES:
        if board[left] != EMPTY and board[left] == board[middle] == board[right]:
            return board[left]
    return "Draw" if EMPTY not in board else None


def utility(board, depth=0):
    result = winner(board)
    if result == MAX_PLAYER:
        return 10 - depth
    if result == MIN_PLAYER:
        return depth - 10
    return 0


def opponent(player):
    return MIN_PLAYER if player == MAX_PLAYER else MAX_PLAYER


def move_label(move):
    return f"r{move // 3 + 1}c{move % 3 + 1}"


def evaluate(board, algorithm):
    if algorithm == "Alpha-Beta":
        return _root_alpha_beta(board)
    if algorithm == "Expectimax":
        return _root_expectimax(board)
    return _root_minimax(board)


def _root_minimax(board):
    stats = {"nodes": 0, "pruned": 0}
    memo = {}

    def value(state, player, depth):
        stats["nodes"] += 1
        key = (state, player, depth)
        if key in memo:
            return memo[key]
        if winner(state) is not None:
            result = utility(state, depth)
        else:
            values = [value(board_after(state, move, player), opponent(player), depth + 1) for move in legal_moves(state)]
            result = max(values) if player == MAX_PLAYER else min(values)
        memo[key] = result
        return result

    candidates = [(move, value(board_after(board, move, MAX_PLAYER), MIN_PLAYER, 1)) for move in legal_moves(board)]
    candidates.sort(key=lambda item: (-item[1], MOVE_PRIORITY[item[0]]))
    move, score = candidates[0] if candidates else (None, utility(board))
    return {"move": move, "value": score, "candidates": candidates, **stats}


def _root_alpha_beta(board):
    stats = {"nodes": 0, "pruned": 0}

    def value(state, player, depth, alpha, beta):
        stats["nodes"] += 1
        if winner(state) is not None:
            return utility(state, depth)
        if player == MAX_PLAYER:
            result = -math.inf
            for move in legal_moves(state):
                result = max(result, value(board_after(state, move, player), MIN_PLAYER, depth + 1, alpha, beta))
                alpha = max(alpha, result)
                if alpha >= beta:
                    stats["pruned"] += 1
                    break
            return result
        result = math.inf
        for move in legal_moves(state):
            result = min(result, value(board_after(state, move, player), MAX_PLAYER, depth + 1, alpha, beta))
            beta = min(beta, result)
            if alpha >= beta:
                stats["pruned"] += 1
                break
        return result

    candidates = []
    alpha = -math.inf
    for move in legal_moves(board):
        score = value(board_after(board, move, MAX_PLAYER), MIN_PLAYER, 1, alpha, math.inf)
        candidates.append((move, score))
        alpha = max(alpha, score)
    candidates.sort(key=lambda item: (-item[1], MOVE_PRIORITY[item[0]]))
    move, score = candidates[0] if candidates else (None, utility(board))
    return {"move": move, "value": score, "candidates": candidates, **stats}


def _root_expectimax(board):
    stats = {"nodes": 0, "pruned": 0}
    memo = {}

    def value(state, player, depth):
        stats["nodes"] += 1
        key = (state, player, depth)
        if key in memo:
            return memo[key]
        if winner(state) is not None:
            result = utility(state, depth)
        else:
            values = [value(board_after(state, move, player), opponent(player), depth + 1) for move in legal_moves(state)]
            result = max(values) if player == MAX_PLAYER else sum(values) / len(values)
        memo[key] = result
        return result

    candidates = [(move, value(board_after(board, move, MAX_PLAYER), MIN_PLAYER, 1)) for move in legal_moves(board)]
    candidates.sort(key=lambda item: (-item[1], MOVE_PRIORITY[item[0]]))
    move, score = candidates[0] if candidates else (None, utility(board))
    return {"move": move, "value": score, "candidates": candidates, **stats}


def heuristic_value(board):
    result = winner(board)
    if result is not None:
        return utility(board)
    weights = {0: 0, 1: 1, 2: 4, 3: 10}
    score = 0
    for line in WIN_LINES:
        values = [board[index] for index in line]
        x_count = values.count(MAX_PLAYER)
        o_count = values.count(MIN_PLAYER)
        if o_count == 0:
            score += weights[x_count]
        if x_count == 0:
            score -= weights[o_count]
    return score


def _event(phase, board, player, depth, path, message, **extra):
    return {
        "phase": phase,
        "board": board,
        "player": player,
        "role": extra.pop("role", "MAX" if player == MAX_PLAYER else "MIN"),
        "depth": depth,
        "path": list(path),
        "message": message,
        **extra,
    }


def build_debug_events(board, algorithm, root_player=MAX_PLAYER, max_depth=3):
    if algorithm == "Alpha-Beta":
        return _trace_alpha_beta(board, root_player, max_depth)
    return _trace_tree(board, root_player, max_depth, chance=algorithm == "Expectimax")


def _trace_tree(board, root_player, max_depth, chance=False):
    events = []

    def recurse(state, player, depth, path):
        role = "CHANCE" if chance and player == MIN_PLAYER else ("MAX" if player == MAX_PLAYER else "MIN")
        events.append(_event("ENTER", state, player, depth, path, f"Enter {role} node.", role=role))
        terminal = winner(state)
        if terminal is not None or depth >= max_depth:
            score = utility(state, depth) if terminal is not None else heuristic_value(state)
            events.append(_event("LEAF", state, player, depth, path, f"Return leaf value {score:.3f}.", role=role, value=score))
            return score
        values = []
        for move in legal_moves(state):
            events.append(_event("DESCEND", state, player, depth, path, f"Inspect {move_label(move)}.", role=role, current_move=move, child_values=list(values)))
            score = recurse(board_after(state, move, player), opponent(player), depth + 1, path + [move])
            values.append((move, score))
            if role == "MAX":
                current = max(item[1] for item in values)
            elif role == "MIN":
                current = min(item[1] for item in values)
            else:
                current = sum(item[1] for item in values) / len(values)
            events.append(_event("UPDATE", state, player, depth, path, f"{role} aggregate is {current:.3f}.", role=role, value=current, current_move=move, child_values=list(values)))
        result = max(item[1] for item in values) if role == "MAX" else (min(item[1] for item in values) if role == "MIN" else sum(item[1] for item in values) / len(values))
        events.append(_event("RETURN", state, player, depth, path, f"Return {result:.3f} to parent.", role=role, value=result, child_values=list(values)))
        return result

    recurse(board, root_player, 0, [])
    return events


def _trace_alpha_beta(board, root_player, max_depth):
    events = []

    def recurse(state, player, depth, path, alpha, beta):
        role = "MAX" if player == MAX_PLAYER else "MIN"
        events.append(_event("ENTER", state, player, depth, path, f"Enter {role}: alpha={alpha:.3f}, beta={beta:.3f}.", role=role, alpha=alpha, beta=beta))
        terminal = winner(state)
        if terminal is not None or depth >= max_depth:
            score = utility(state, depth) if terminal is not None else heuristic_value(state)
            events.append(_event("LEAF", state, player, depth, path, f"Return leaf value {score:.3f}.", role=role, value=score, alpha=alpha, beta=beta))
            return score
        moves = legal_moves(state)
        values = []
        result = -math.inf if player == MAX_PLAYER else math.inf
        for index, move in enumerate(moves):
            events.append(_event("DESCEND", state, player, depth, path, f"Inspect {move_label(move)}.", role=role, current_move=move, alpha=alpha, beta=beta, child_values=list(values)))
            score = recurse(board_after(state, move, player), opponent(player), depth + 1, path + [move], alpha, beta)
            values.append((move, score))
            if player == MAX_PLAYER:
                result = max(result, score)
                alpha = max(alpha, result)
            else:
                result = min(result, score)
                beta = min(beta, result)
            events.append(_event("UPDATE", state, player, depth, path, f"Update alpha={alpha:.3f}, beta={beta:.3f}.", role=role, value=result, current_move=move, alpha=alpha, beta=beta, child_values=list(values)))
            if alpha >= beta:
                pruned = moves[index + 1:]
                events.append(_event("PRUNE", state, player, depth, path, f"Prune {len(pruned)} moves because alpha >= beta.", role=role, value=result, alpha=alpha, beta=beta, pruned_moves=pruned, child_values=list(values)))
                break
        events.append(_event("RETURN", state, player, depth, path, f"Return {result:.3f} to parent.", role=role, value=result, alpha=alpha, beta=beta, child_values=list(values)))
        return result

    recurse(board, root_player, 0, [], -math.inf, math.inf)
    return events
