import numpy as np

from .constants import FIRE_DURATION, HORIZON, INF, MAX_BOMB_RADIUS
from .state import BombInfo, Cell, GameState


def in_bounds(shape: tuple[int, int], cell: Cell) -> bool:
    return 0 <= cell[0] < shape[0] and 0 <= cell[1] < shape[1]


def bomb_radius(state: GameState, bomb: BombInfo) -> int:
    """Estimate a bomb's blast radius.

    The engine locks a bomb's radius at placement time and the observation does
    NOT expose it (obs bombs are [x, y, timer, owner_id]). We therefore infer it
    from the owner's CURRENT radius bonus. If the owner picked up a radius item
    after placing the bomb, this over-estimates the blast — which is a deliberate
    bias toward safety (we treat more cells as dangerous, never fewer).
    """
    if 0 <= bomb.owner_id < len(state.players):
        return max(1, min(MAX_BOMB_RADIUS, 1 + int(state.players[bomb.owner_id][4])))
    return 1


def blast_cells(pos: Cell, radius: int, walls: np.ndarray, boxes: np.ndarray) -> set[Cell]:
    """Return cells hit by a bomb. Walls block; boxes are included then block."""

    cells = {pos}
    shape = walls.shape
    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        row, col = pos
        for _ in range(int(radius)):
            row += dr
            col += dc
            cell = (row, col)
            if not in_bounds(shape, cell):
                break
            if bool(walls[cell]):
                break
            cells.add(cell)
            if bool(boxes[cell]):
                break
    return cells


def compute_explosion_times(state: GameState) -> list[int]:
    """Apply simple fixpoint chain reaction over current bombs.

    Blast cells are computed against the CURRENT grid; we do not model boxes
    destroyed by an earlier blast extending a later one. This is a safe
    approximation for a danger map (it never shrinks the danger horizon in a way
    that matters for escaping the bombs already on the field).
    """

    times = [max(0, int(bomb.timer)) for bomb in state.bombs]
    changed = True
    while changed:
        changed = False
        for i, bomb_i in enumerate(state.bombs):
            cells_i = blast_cells(bomb_i.pos, bomb_radius(state, bomb_i), state.walls, state.boxes)
            for j, bomb_j in enumerate(state.bombs):
                if i == j:
                    continue
                if bomb_j.pos in cells_i and times[i] < times[j]:
                    times[j] = times[i]
                    changed = True
    return times


def compute_danger_map(state: GameState, horizon: int = HORIZON) -> np.ndarray:
    """danger_time[r, c] is the earliest future step where cell is on fire."""

    danger_time = np.full(state.grid.shape, INF, dtype=np.int32)
    if not state.bombs:
        return danger_time

    explosion_times = compute_explosion_times(state)
    for bomb, explode_at in zip(state.bombs, explosion_times):
        if explode_at > horizon:
            continue
        cells = blast_cells(bomb.pos, bomb_radius(state, bomb), state.walls, state.boxes)
        for cell in cells:
            for offset in range(FIRE_DURATION):
                t = int(explode_at) + offset
                if t <= horizon and t < int(danger_time[cell]):
                    danger_time[cell] = t
    return danger_time
