from dataclasses import dataclass
from math import inf

import numpy as np

from person_a_safety.constants import (
    ACTIONS,
    INF,
    ITEM_CAPACITY,
    ITEM_RADIUS,
    PLACE_BOMB,
    STOP,
)
from person_a_safety.danger import blast_cells
from person_a_safety.masks import action_destination
from person_a_safety.search import passable, safe_distances
from person_a_safety.state import Cell, GameState


@dataclass(frozen=True)
class ScoreWeights:
    survival: float = 20.0
    box: float = 50.0
    item: float = 40.0
    pressure: float = 20.0
    mobility: float = 8.0
    useful_bomb: float = 8.0
    danger: float = 12.0
    loop: float = 10.0
    useless_bomb: float = 35.0
    stop: float = 3.0


def score_actions(
    state: GameState,
    safe_mask: np.ndarray,
    danger_time: np.ndarray,
    tracker=None,
    weights: ScoreWeights = ScoreWeights(),
) -> dict[int, float]:
    distances = safe_distances(state, danger_time)
    scores = {}
    for action in ACTIONS:
        if not bool(safe_mask[action]):
            scores[action] = -inf
            continue
        scores[action] = score_action(state, action, danger_time, distances, tracker, weights)
    return scores


def score_action(
    state: GameState,
    action: int,
    danger_time: np.ndarray,
    distances: dict[Cell, int],
    tracker=None,
    weights: ScoreWeights = ScoreWeights(),
) -> float:
    next_pos = action_destination(state, action)
    score = 0.0

    score += weights.survival * survival_score(state, next_pos, danger_time)
    score += weights.mobility * mobility_score(state, next_pos)
    score += weights.item * item_score(state, next_pos, distances)
    score += weights.box * box_move_score(state, next_pos, distances)
    score += weights.pressure * pressure_score(state, action)
    score += useful_bomb_score(state, action, weights)
    score -= weights.danger * danger_penalty(next_pos, danger_time)

    if action == STOP:
        score -= weights.stop
    if tracker is not None:
        score -= weights.loop * tracker.action_penalty(next_pos, action)
    return score


def survival_score(state: GameState, pos: Cell, danger_time: np.ndarray) -> float:
    danger = int(danger_time[pos])
    if danger >= INF:
        return 2.0
    return max(0.0, min(2.0, danger / 4.0))


def mobility_score(state: GameState, pos: Cell) -> float:
    return float(sum(1 for nbr in neighbors(pos) if passable(state, nbr, allow_start=state.self_pos)))


def item_score(state: GameState, pos: Cell, distances: dict[Cell, int]) -> float:
    if int(state.grid[pos]) == ITEM_RADIUS:
        return 1.2
    if int(state.grid[pos]) == ITEM_CAPACITY:
        return 1.3

    targets = [
        cell
        for cell, dist in distances.items()
        if int(state.grid[cell]) in (ITEM_RADIUS, ITEM_CAPACITY) and dist >= 0
    ]
    if not targets:
        return 0.0
    best = min(distances[cell] for cell in targets)
    return 1.0 / (best + 1.0)


def box_gain(state: GameState, cell: Cell | None = None) -> int:
    cell = state.self_pos if cell is None else cell
    cells = blast_cells(cell, state.self_radius, state.walls, state.boxes)
    return sum(1 for blast_cell in cells if bool(state.boxes[blast_cell]))


def box_move_score(state: GameState, pos: Cell, distances: dict[Cell, int]) -> float:
    if box_gain(state, pos) > 0:
        return float(box_gain(state, pos))

    best = 0.0
    for cell, dist in distances.items():
        if dist <= 0:
            continue
        gain = box_gain(state, cell)
        if gain <= 0:
            continue
        best = max(best, gain / (dist + 1.0))
    return best


def pressure_score(state: GameState, action: int) -> float:
    if action != PLACE_BOMB or not state.opponents:
        return 0.0
    blast = blast_cells(state.self_pos, state.self_radius, state.walls, state.boxes)
    return float(sum(1 for enemy in state.opponents if enemy in blast))


def useful_bomb_score(state: GameState, action: int, weights: ScoreWeights) -> float:
    if action != PLACE_BOMB:
        return 0.0
    gain = box_gain(state)
    pressure = pressure_score(state, action)
    if gain > 0 or pressure > 0:
        return weights.useful_bomb * (gain + pressure)
    return -weights.useless_bomb


def danger_penalty(pos: Cell, danger_time: np.ndarray) -> float:
    danger = int(danger_time[pos])
    if danger >= INF:
        return 0.0
    return 1.0 / max(1.0, float(danger))


def neighbors(pos: Cell) -> tuple[Cell, Cell, Cell, Cell]:
    row, col = pos
    return (
        (row - 1, col),
        (row + 1, col),
        (row, col - 1),
        (row, col + 1),
    )
