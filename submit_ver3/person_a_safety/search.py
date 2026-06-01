from collections import deque
from dataclasses import dataclass

import numpy as np

from .constants import ACTION_DELTAS, HORIZON, INF, MOVE_ACTIONS, STOP
from .danger import earliest_at
from .state import Cell, GameState


@dataclass
class BFSResult:
    safe_targets: list[tuple[Cell, int]]
    parent: dict[tuple[Cell, int], tuple[Cell, int]]
    first_action: dict[tuple[Cell, int], int]
    distances: dict[Cell, int]


def _horizon_limit(hazard: np.ndarray, horizon: int) -> int:
    """Never look past the last simulated tick of the hazard tensor."""
    return min(int(horizon), int(hazard.shape[0]) - 1)


def safe_at(cell: Cell, t: int, hazard: np.ndarray) -> bool:
    """True when ``cell`` is NOT on fire at exactly tick ``t``.

    ``hazard`` is the per-time tensor from :func:`compute_hazard_map`. Ticks
    beyond the simulated horizon are treated as safe (no bomb reaches that far).
    """
    if t < 0:
        t = 0
    if t >= hazard.shape[0]:
        return True
    return not bool(hazard[t, cell[0], cell[1]])


def eventually_safe(cell: Cell, t: int, hazard: np.ndarray) -> bool:
    """True when ``cell`` stays clear for the rest of the horizon from tick ``t``.

    Unlike the old earliest-time check this inspects EVERY remaining tick, so a
    cell that burns again later is correctly rejected as an escape target.
    """
    if t >= hazard.shape[0]:
        return True
    if t < 0:
        t = 0
    return not bool(hazard[t:, cell[0], cell[1]].any())


def _eventual_clear_tensor(hazard: np.ndarray) -> np.ndarray:
    """eventual_clear[t, r, c] is True if cell stays clear from t onward."""

    return ~np.logical_or.accumulate(hazard[::-1], axis=0)[::-1]


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
    hazard: np.ndarray,
    horizon: int = HORIZON,
    start_time: int = 0,
) -> BFSResult:
    """BFS over (cell, t), allowing wait/move while avoiding timed fire.

    ``start_time`` is the move-frame clock value already elapsed at ``start``.
    It must be 1 when ``start`` is the cell reached AFTER a move action: getting
    there has already consumed one step, so the agent has one fewer step of
    escape budget than the hazard tensor (computed in the original frame)
    suggests. Starting the BFS at t=0 in that case is an unsafe off-by-one.
    """

    limit = _horizon_limit(hazard, horizon)
    eventual_clear = _eventual_clear_tensor(hazard)
    queue = deque([(start, start_time)])
    visited = {(start, start_time)}
    parent: dict[tuple[Cell, int], tuple[Cell, int]] = {}
    first_action: dict[tuple[Cell, int], int] = {(start, start_time): STOP}
    distances: dict[Cell, int] = {start: start_time}
    safe_targets: list[tuple[Cell, int]] = []

    while queue:
        cell, t = queue.popleft()
        if t >= hazard.shape[0] or bool(eventual_clear[t, cell[0], cell[1]]):
            safe_targets.append((cell, t))

        if t >= limit:
            continue

        for action in MOVE_ACTIONS:
            nxt = move(cell, action)
            if not passable(state, nxt, allow_start=start):
                continue
            nt = t + 1
            if not safe_at(nxt, nt, hazard):
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
    hazard: np.ndarray,
    horizon: int = HORIZON,
    start_time: int = 0,
) -> bool:
    start = state.self_pos if start is None else start
    if not passable(state, start, allow_start=start):
        return False
    if not safe_at(start, start_time, hazard):
        return False

    limit = _horizon_limit(hazard, horizon)
    eventual_clear = _eventual_clear_tensor(hazard)
    queue = deque([(start, start_time)])
    visited = {(start, start_time)}

    while queue:
        cell, t = queue.popleft()
        if t >= hazard.shape[0] or bool(eventual_clear[t, cell[0], cell[1]]):
            return True
        if t >= limit:
            continue

        nt = t + 1
        for action in MOVE_ACTIONS:
            nxt = move(cell, action)
            if not passable(state, nxt, allow_start=start):
                continue
            if not safe_at(nxt, nt, hazard):
                continue
            node = (nxt, nt)
            if node in visited:
                continue
            visited.add(node)
            queue.append(node)

    return False


def safe_distances(
    state: GameState,
    hazard: np.ndarray,
    start: Cell | None = None,
    horizon: int = HORIZON,
    start_time: int = 0,
) -> dict[Cell, int]:
    start = state.self_pos if start is None else start
    return time_expanded_bfs(state, start, hazard, horizon, start_time).distances


def safe_relative_distances(
    state: GameState,
    hazard: np.ndarray,
    start: Cell | None = None,
    horizon: int = HORIZON,
    start_time: int = 0,
) -> dict[Cell, int]:
    """Return safe travel distances relative to ``start_time``.

    ``safe_distances`` exposes absolute arrival times in the hazard map frame.
    Strategy code that needs ordinary path distances should use this helper.
    """

    absolute = safe_distances(state, hazard, start, horizon, start_time)
    return {cell: max(0, int(arrival) - int(start_time)) for cell, arrival in absolute.items()}


def first_escape_action(
    state: GameState,
    hazard: np.ndarray,
    start: Cell | None = None,
    horizon: int = HORIZON,
    start_time: int = 0,
) -> int | None:
    """Return the first move toward the nearest safe target, if one exists."""

    start = state.self_pos if start is None else start
    if not passable(state, start, allow_start=start):
        return None
    if not safe_at(start, start_time, hazard):
        return None

    result = time_expanded_bfs(state, start, hazard, horizon, start_time)
    if not result.safe_targets:
        return None

    target = min(
        result.safe_targets,
        key=lambda item: (
            int(item[1]),
            0 if earliest_at(hazard, item[0]) >= INF else 1,
            item[0],
        ),
    )
    return int(result.first_action.get(target, STOP))
