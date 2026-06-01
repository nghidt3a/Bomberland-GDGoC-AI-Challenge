import numpy as np

from .constants import HORIZON, INF, MAX_BOMB_RADIUS
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
    """Return cells hit by a bomb. Walls block; boxes are included then block.

    Mirrors engine/game.py::_get_explosion_tiles exactly (origin + four arms,
    each arm stopped by a wall before the wall, or by a box after including it).
    """

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


def compute_hazard_map(state: GameState, horizon: int = HORIZON) -> np.ndarray:
    """Per-time-step fire map: ``hazard[t, r, c]`` is True when cell (r, c) is on
    fire at relative time ``t`` (t counts the agent's move-frame, so a bomb whose
    observed timer is T burns its cells at t == T — see search.py for why t=1 is
    the first post-move frame).

    Why a 3D tensor instead of a single earliest-burn time per cell: a cell can
    be swept by *several* bombs at *different* times (two independent bombs, or a
    chain). Storing only the earliest time made ``eventually_safe`` believe a
    cell was permanently clear once the first fire passed, so the agent would
    route through it and die to the *second* blast. The tensor records every
    burn moment, which is the correct model for escape search.

    The simulation also reproduces two engine behaviours the old earliest-only
    map ignored:

    * **Chain reactions** — a blast that reaches another live bomb detonates it
      in the same tick (fix-point), exactly like the engine's chain loop.
    * **Box removal over time** — a box destroyed at tick t is gone at tick t+1,
      so a *later* bomb on that line now blasts further. Within a single tick,
      blast tiles are computed against the boxes still standing (the engine
      collects all explosion tiles before removing any box), then the destroyed
      boxes are cleared after the tick.

    The map is tiny: ``(horizon + 1) * 13 * 13`` booleans, recomputed well inside
    the 100 ms ``act`` budget.
    """

    height, width = state.grid.shape
    hazard = np.zeros((horizon + 1, height, width), dtype=bool)
    if not state.bombs:
        return hazard

    walls = state.walls
    boxes = state.boxes.copy()
    bombs = [
        {
            "pos": bomb.pos,
            "radius": bomb_radius(state, bomb),
            "explode_at": max(0, int(bomb.timer)),
            "exploded": False,
        }
        for bomb in state.bombs
    ]

    # A bomb's blast depends only on its pos/radius and the current boxes. Boxes
    # change at most a handful of times across the horizon, so memoise each
    # bomb's blast and invalidate only when a box is actually destroyed. This
    # keeps the chain-reaction fix-point cheap when many bombs are on the field.
    blast_cache: dict[int, set[Cell]] = {}

    def blast_of(i: int) -> set[Cell]:
        cached = blast_cache.get(i)
        if cached is None:
            cached = blast_cells(bombs[i]["pos"], bombs[i]["radius"], walls, boxes)
            blast_cache[i] = cached
        return cached

    for t in range(horizon + 1):
        exploding = {
            i for i, bomb in enumerate(bombs)
            if not bomb["exploded"] and bomb["explode_at"] <= t
        }
        if not exploding:
            continue

        # Chain-reaction fix-point: detonate every live bomb whose cell is hit by
        # the current blast set. Boxes still stand for the whole fix-point (engine
        # removes them only after collecting all tiles), so the blast set is
        # computed against ``boxes`` unchanged here.
        changed = True
        while changed:
            changed = False
            blast: set[Cell] = set()
            for i in exploding:
                blast |= blast_of(i)
            for j, bomb in enumerate(bombs):
                if bomb["exploded"] or j in exploding:
                    continue
                if bomb["pos"] in blast:
                    exploding.add(j)
                    changed = True

        # Paint hazard for this tick and record which boxes are consumed.
        destroyed: set[Cell] = set()
        for i in exploding:
            for cell in blast_of(i):
                hazard[t, cell[0], cell[1]] = True
                if bool(boxes[cell]):
                    destroyed.add(cell)
            bombs[i]["exploded"] = True

        # Clear destroyed boxes only AFTER the tick so a later bomb's blast can
        # now reach through the gap on a future tick — and invalidate cached
        # blasts since a removed box lets later blasts travel further.
        if destroyed:
            for cell in destroyed:
                boxes[cell] = False
            blast_cache.clear()

    return hazard


def hazard_to_earliest(hazard: np.ndarray) -> np.ndarray:
    """Collapse the hazard tensor to the earliest-burn-time map used by scalar
    scoring heuristics (``INF`` where a cell never burns inside the horizon)."""

    any_fire = hazard.any(axis=0)
    first = np.argmax(hazard, axis=0)  # first True index, or 0 if all-False
    return np.where(any_fire, first, INF).astype(np.int32)


def earliest_at(hazard: np.ndarray, cell: Cell) -> int:
    """Earliest tick ``cell`` is on fire, or ``INF`` if it never burns."""

    column = hazard[:, cell[0], cell[1]]
    idx = int(np.argmax(column))
    return idx if bool(column[idx]) else INF


def compute_danger_map(state: GameState, horizon: int = HORIZON) -> np.ndarray:
    """Earliest-burn-time map, derived from the per-time hazard tensor.

    Kept for the scoring heuristics (which only need a scalar "how soon does this
    cell burn") and for callers that predate the tensor. Safety-critical code
    (search/masks/shield/bomb) consumes :func:`compute_hazard_map` directly so it
    sees every burn moment, not just the first.
    """

    return hazard_to_earliest(compute_hazard_map(state, horizon))
