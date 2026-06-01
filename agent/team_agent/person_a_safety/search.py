from collections import deque
from dataclasses import dataclass

import numpy as np

from .constants import ACTION_DELTAS, FIRE_DURATION, HORIZON, INF, MOVE_ACTIONS, STOP
from .state import Cell, GameState


@dataclass
class BFSResult:
    safe_targets: list[tuple[Cell, int]]
    parent: dict[tuple[Cell, int], tuple[Cell, int]]
    first_action: dict[tuple[Cell, int], int]
    distances: dict[Cell, int]


def safe_at(cell: Cell, t: int, danger_time: np.ndarray) -> bool:
    d = int(danger_time[cell])
    return d == INF or not (d <= t < d + FIRE_DURATION)


def eventually_safe(cell: Cell, t: int, danger_time: np.ndarray) -> bool:
    d = int(danger_time[cell])
    return d == INF or t >= d + FIRE_DURATION


def move(cell: Cell, action: int) -> Cell:
    dr, dc = ACTION_DELTAS[action]
    return cell[0] + dr, cell[1] + dc


def in_bounds(state: GameState, cell: Cell) -> bool:
    return 0 <= cell[0] < state.height and 0 <= cell[1] < state.width


def passable(state: GameState, cell: Cell, *, allow_start: Cell | None = None) -> bool:
    if not in_bounds(state, cell):
        return False
    if bool(state.walls[cell]) or bool(state.boxes[cell]):
        return False
    if cell in state.bomb_positions and cell != allow_start:
        return False
    return True


def time_expanded_bfs(
    state: GameState,
    start: Cell,
    danger_time: np.ndarray,
    horizon: int = HORIZON,
    start_time: int = 0,
) -> BFSResult:
    """BFS over (cell, t), allowing wait/move while avoiding timed fire.

    ``start_time`` is the move-frame clock value already elapsed at ``start``.
    It must be 1 when ``start`` is the cell reached AFTER a move action: getting
    there has already consumed one step, so the agent has one fewer step of
    escape budget than ``danger_time`` (computed in the original frame) suggests.
    Starting the BFS at t=0 in that case is an unsafe off-by-one.
    """

    queue = deque([(start, start_time)])
    visited = {(start, start_time)}
    parent: dict[tuple[Cell, int], tuple[Cell, int]] = {}
    first_action: dict[tuple[Cell, int], int] = {(start, start_time): STOP}
    distances: dict[Cell, int] = {start: start_time}
    safe_targets: list[tuple[Cell, int]] = []

    while queue:
        cell, t = queue.popleft()
        if eventually_safe(cell, t, danger_time):
            safe_targets.append((cell, t))

        if t >= horizon:
            continue

        for action in MOVE_ACTIONS:
            nxt = move(cell, action)
            if not passable(state, nxt, allow_start=start):
                continue
            nt = t + 1
            if not safe_at(nxt, nt, danger_time):
                continue
            node = (nxt, nt)
            if node in visited:
                continue
            visited.add(node)
            parent[node] = (cell, t)
            first_action[node] = action if t == start_time else first_action[(cell, t)]
            distances[nxt] = min(nt, distances.get(nxt, nt))
            queue.append(node)

    return BFSResult(
        safe_targets=safe_targets,
        parent=parent,
        first_action=first_action,
        distances=distances,
    )


def has_escape_path(
    state: GameState,
    start: Cell | None,
    danger_time: np.ndarray,
    horizon: int = HORIZON,
    start_time: int = 0,
) -> bool:
    start = state.self_pos if start is None else start
    if not passable(state, start, allow_start=start):
        return False
    if not safe_at(start, start_time, danger_time):
        return False
    return bool(
        time_expanded_bfs(state, start, danger_time, horizon, start_time).safe_targets
    )


def safe_distances(
    state: GameState,
    danger_time: np.ndarray,
    start: Cell | None = None,
    horizon: int = HORIZON,
    start_time: int = 0,
) -> dict[Cell, int]:
    start = state.self_pos if start is None else start
    return time_expanded_bfs(state, start, danger_time, horizon, start_time).distances
