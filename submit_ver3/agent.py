# Bundled one-file Bomberland submission. Generated from submit_ver3 packages.


# --- person_a_safety/constants.py ---

STOP = 0
LEFT = 1
RIGHT = 2
UP = 3
DOWN = 4
PLACE_BOMB = 5

ACTIONS = (STOP, LEFT, RIGHT, UP, DOWN, PLACE_BOMB)
MOVE_ACTIONS = (STOP, LEFT, RIGHT, UP, DOWN)

# Matches engine/player.py action semantics.
ACTION_DELTAS = {
    STOP: (0, 0),
    LEFT: (-1, 0),
    RIGHT: (1, 0),
    UP: (0, -1),
    DOWN: (0, 1),
}

GRASS = 0
WALL = 1
BOX = 2
ITEM_RADIUS = 3
ITEM_CAPACITY = 4
WALKABLE_TILES = (GRASS, ITEM_RADIUS, ITEM_CAPACITY)

BOARD_SIZE = 13
BOMB_TIMER = 7
MAX_BOMB_RADIUS = 5
HORIZON = 10
FIRE_DURATION = 1
INF = 10**9


# --- person_a_safety/state.py ---

from dataclasses import dataclass
from typing import List, Set, Tuple

import numpy as np

Cell = Tuple[int, int]


@dataclass(frozen=True)
class BombInfo:
    pos: Cell
    timer: int
    owner_id: int


@dataclass
class GameState:
    grid: np.ndarray
    players: np.ndarray
    agent_id: int
    bombs: List[BombInfo]
    walls: np.ndarray
    boxes: np.ndarray
    item_radius: np.ndarray
    item_capacity: np.ndarray
    bomb_positions: Set[Cell]
    self_pos: Cell
    self_alive: bool
    self_bombs_left: int
    self_radius: int
    opponents: List[Cell]
    alive_players: List[Cell]

    @property
    def height(self) -> int:
        return int(self.grid.shape[0])

    @property
    def width(self) -> int:
        return int(self.grid.shape[1])


# --- person_a_safety/danger.py ---

import numpy as np



def danger_in_bounds(shape: tuple[int, int], cell: Cell) -> bool:
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
            if not danger_in_bounds(shape, cell):
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


# --- person_a_safety/search.py ---

from collections import deque
from dataclasses import dataclass

import numpy as np



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


# --- person_a_safety/bomb.py ---

from dataclasses import replace

import numpy as np



def copy_state_with_new_bomb_at_self(state: GameState, timer: int = BOMB_TIMER) -> GameState:
    new_bomb = BombInfo(pos=state.self_pos, timer=int(timer), owner_id=state.agent_id)
    return replace(
        state,
        bombs=[*state.bombs, new_bomb],
        bomb_positions={*state.bomb_positions, state.self_pos},
    )


def can_place_bomb_safely(state: GameState, horizon: int = HORIZON) -> bool:
    if not state.self_alive:
        return False
    if state.self_bombs_left <= 0:
        return False
    if state.self_pos in state.bomb_positions:
        return False

    simulated = copy_state_with_new_bomb_at_self(state)
    hazard = compute_hazard_map(simulated, horizon)
    # Placing a bomb consumes a full turn during which the agent CANNOT move:
    # it stays on its own cell while every existing bomb ticks down once. So the
    # escape search must start at t=1 (the first real move happens next step),
    # exactly like the post-move escape check. Starting at t=0 hands the agent a
    # phantom extra step of budget and was letting it bury itself next to its
    # own large-radius bombs (engine-verified self-destruct).
    return has_permanent_escape_after_bomb(simulated, hazard, horizon)


def has_permanent_escape_after_bomb(
    simulated: GameState,
    hazard: np.ndarray,
    horizon: int = HORIZON,
) -> bool:
    """Require an escape target that never burns again inside the horizon."""

    if not safe_at(simulated.self_pos, 1, hazard):
        return False

    bfs = time_expanded_bfs(simulated, simulated.self_pos, hazard, horizon, start_time=1)
    return any(earliest_at(hazard, cell) >= INF for cell, _time in bfs.safe_targets)


# --- person_a_safety/masks.py ---

from dataclasses import replace

import numpy as np



def action_destination(state: GameState, action: int) -> tuple[int, int]:
    if action == PLACE_BOMB:
        return state.self_pos
    if action in ACTION_DELTAS:
        return move(state.self_pos, action)
    return state.self_pos


def legal_actions(state: GameState) -> np.ndarray:
    mask = np.zeros(len(ACTIONS), dtype=bool)
    if not state.self_alive:
        mask[STOP] = True
        return mask

    for action in ACTIONS:
        if action == PLACE_BOMB:
            mask[action] = state.self_bombs_left > 0 and state.self_pos not in state.bomb_positions
            continue
        if action == STOP:
            mask[action] = True
            continue
        nxt = action_destination(state, action)
        mask[action] = passable(state, nxt, allow_start=state.self_pos)
    return mask


def has_escape_after_action(state: GameState, action: int, hazard: np.ndarray) -> bool:
    nxt = action_destination(state, action)
    if action == PLACE_BOMB:
        return can_place_bomb_safely(state)
    next_state = replace(state, self_pos=nxt)
    # The move already consumed one step, so the escape BFS must start at t=1:
    # the hazard tensor is in the original ("now") frame and the agent now has
    # one fewer step of budget. Starting at t=0 here would be an unsafe off-by-one.
    return has_escape_path(next_state, nxt, hazard, start_time=1)


def safe_actions(state: GameState, hazard: np.ndarray | None = None) -> np.ndarray:
    hazard = compute_hazard_map(state) if hazard is None else hazard
    legal = legal_actions(state)
    mask = np.zeros(len(ACTIONS), dtype=bool)

    for action in ACTIONS:
        if not legal[action]:
            continue
        if action == PLACE_BOMB:
            mask[action] = can_place_bomb_safely(state)
            continue
        nxt = action_destination(state, action)
        if not safe_at(nxt, 1, hazard):
            continue
        if not has_escape_after_action(state, action, hazard):
            continue
        mask[action] = True

    if not mask.any() and legal.any():
        # No certified-safe action: fall back to the move that lands on the cell
        # that stays clear the longest, and only if it never burns in-horizon.
        def survivability(action: int) -> int:
            dest = action_destination(state, action)
            if dest != state.self_pos:
                return earliest_at(hazard, dest)
            return earliest_at(hazard, state.self_pos) - 1

        best_action = max(
            [action for action in ACTIONS if legal[action] and action != PLACE_BOMB],
            key=survivability,
            default=STOP,
        )
        if earliest_at(hazard, action_destination(state, best_action)) >= INF:
            mask[best_action] = True

    return mask


# --- person_a_safety/shield.py ---

import numpy as np



def action_is_safe(action: int, state: GameState, hazard: np.ndarray | None = None) -> bool:
    if action not in ACTIONS:
        return False
    mask = safe_actions(state, hazard)
    return bool(mask[int(action)])


def final_shield(
    action: int,
    state: GameState,
    hazard: np.ndarray | None = None,
    mask: np.ndarray | None = None,
) -> int:
    """Final safety gate. B's policy must pass through this before returning.

    ``mask`` is the safe-action mask already computed for this step (from
    ``safe_actions``). Passing it in avoids recomputing the mask here — that
    recompute re-ran a full bomb-placement hazard simulation plus several BFS
    every turn and was the main source of >100 ms latency spikes.
    """

    hazard = compute_hazard_map(state) if hazard is None else hazard
    if mask is None:
        mask = safe_actions(state, hazard)
    try:
        action = int(action)
    except Exception:
        action = STOP

    if action in ACTIONS and bool(mask[action]):
        return action

    if mask.any():
        chosen = best_escape_action(state, mask, hazard)
        if chosen is None:
            chosen = least_bad_action(state, hazard)
    else:
        chosen = least_bad_action(state, hazard)

    # Final invariant: never hand the engine an out-of-range action.
    return chosen if chosen in ACTIONS else STOP


def best_escape_action(state: GameState, mask: np.ndarray, hazard: np.ndarray) -> int | None:
    candidates = [action for action in ACTIONS if bool(mask[action]) and action != PLACE_BOMB]
    if not candidates:
        return None

    planned = first_escape_action(state, hazard)
    if planned in candidates:
        return int(planned)

    return max(candidates, key=lambda action: _escape_score(state, action, hazard))


def least_bad_action(state: GameState, hazard: np.ndarray) -> int:
    legal = legal_actions(state)
    candidates = [action for action in ACTIONS if bool(legal[action]) and action != PLACE_BOMB]
    if not candidates:
        return STOP
    return max(candidates, key=lambda action: _escape_score(state, action, hazard))


def _escape_score(state: GameState, action: int, hazard: np.ndarray) -> float:
    cell = action_destination(state, action)
    danger = earliest_at(hazard, cell)
    score = 0.0
    score += 1000.0 if danger >= INF else float(danger)
    score += 3.0 * _open_neighbors(state, cell)
    if action == STOP:
        score -= 2.0
    return score


def _open_neighbors(state: GameState, cell: Cell) -> int:
    count = 0
    for nbr in ((cell[0] + 1, cell[1]), (cell[0] - 1, cell[1]), (cell[0], cell[1] + 1), (cell[0], cell[1] - 1)):
        if passable(state, nbr, allow_start=state.self_pos):
            count += 1
    return count


# --- person_a_safety/obs.py ---

from typing import Any

import numpy as np



def parse_obs(obs: dict[str, Any], agent_id: int) -> GameState:
    """Normalize raw observation into the shared internal state."""

    grid = np.asarray(obs.get("map"), dtype=np.int16)
    players = _normalize_players(obs.get("players"))
    bombs_arr = _normalize_bombs(obs.get("bombs"))

    bombs = [
        BombInfo(pos=(int(row), int(col)), timer=int(timer), owner_id=int(owner_id))
        for row, col, timer, owner_id in bombs_arr
    ]
    bomb_positions = {bomb.pos for bomb in bombs}

    agent_id = int(agent_id)
    if 0 <= agent_id < len(players):
        me = players[agent_id]
        self_pos = (int(me[0]), int(me[1]))
        self_alive = bool(int(me[2]))
        self_bombs_left = int(me[3])
        self_radius = 1 + int(me[4])
    else:
        self_pos = (0, 0)
        self_alive = False
        self_bombs_left = 0
        self_radius = 1

    opponents = []
    alive_players = []
    for idx, player in enumerate(players):
        if int(player[2]) != 1:
            continue
        pos = (int(player[0]), int(player[1]))
        alive_players.append(pos)
        if idx != agent_id:
            opponents.append(pos)

    return GameState(
        grid=grid,
        players=players,
        agent_id=agent_id,
        bombs=bombs,
        walls=grid == WALL,
        boxes=grid == BOX,
        item_radius=grid == ITEM_RADIUS,
        item_capacity=grid == ITEM_CAPACITY,
        bomb_positions=bomb_positions,
        self_pos=self_pos,
        self_alive=self_alive,
        self_bombs_left=self_bombs_left,
        self_radius=max(1, self_radius),
        opponents=opponents,
        alive_players=alive_players,
    )


def _normalize_players(raw_players: Any) -> np.ndarray:
    arr = np.asarray(raw_players, dtype=np.int16)
    if arr.size == 0:
        return np.zeros((0, 5), dtype=np.int16)
    return arr.reshape((-1, 5))


def _normalize_bombs(raw_bombs: Any) -> np.ndarray:
    arr = np.asarray(raw_bombs, dtype=np.int16)
    if arr.size == 0:
        return np.zeros((0, 4), dtype=np.int16)
    if arr.ndim == 1:
        arr = arr.reshape((1, -1))
    if arr.shape[1] < 4:
        padded = np.zeros((arr.shape[0], 4), dtype=np.int16)
        padded[:, : arr.shape[1]] = arr
        return padded
    return arr[:, :4]


# --- person_b_strategy/loop_tracker.py ---

from collections import deque



class AntiLoopTracker:
    """Stateful helper for discouraging short loops and stale camping."""

    def __init__(self, maxlen: int = 16):
        self.recent_positions: deque[Cell] = deque(maxlen=maxlen)
        self.recent_actions: deque[int] = deque(maxlen=maxlen)
        self.turn_index = 0
        self.steps_without_progress = 0

        self.last_box_count: int | None = None
        self.last_visible_item_count: int | None = None
        self.last_self_radius: int | None = None
        self.last_estimated_capacity: int | None = None
        self.last_action: int | None = None
        self.last_action_value = 0.0

        self.proxy_boxes = 0
        self.proxy_items = 0
        self.proxy_bombs = 0
        self.proxy_kills = 0
        self.initial_opponent_count: int | None = None

    @property
    def proxy_score(self) -> float:
        return (
            self.proxy_boxes * 0.8
            + self.proxy_items * 1.2
            + self.proxy_bombs * 0.25
            + self.proxy_kills * 3.0
        )

    def observe_state(self, state: GameState) -> None:
        # Field-thinning proxy: how many opponents have been eliminated since the
        # game started. We can't reliably attribute a kill to our own bomb from
        # the observation alone, but "fewer opponents alive" is exactly the signal
        # the late-game profile needs to decide between defending a lead and
        # chasing activity (see scoring.phase_profile). Counting alive opponents
        # is robust; it never over-credits.
        opponent_count = len(state.opponents)
        if self.initial_opponent_count is None:
            self.initial_opponent_count = opponent_count
        else:
            self.proxy_kills = max(self.proxy_kills, self.initial_opponent_count - opponent_count)

        box_count = int(state.boxes.sum())
        visible_item_count = int(state.item_radius.sum() + state.item_capacity.sum())
        estimated_capacity = estimate_capacity(state)

        if self.last_box_count is None:
            self._store_snapshot(state, box_count, visible_item_count, estimated_capacity)
            return

        made_progress = False

        if box_count < self.last_box_count:
            self.proxy_boxes += self.last_box_count - box_count
            made_progress = True

        if state.self_radius > (self.last_self_radius or 0):
            self.proxy_items += 1
            made_progress = True

        if estimated_capacity > (self.last_estimated_capacity or 0):
            self.proxy_items += 1
            made_progress = True

        if self._reached_new_area(state.self_pos):
            made_progress = True

        if self.last_action == PLACE_BOMB and self.last_action_value > 0:
            made_progress = True

        if made_progress:
            self.steps_without_progress = 0
        else:
            self.steps_without_progress += 1

        self._store_snapshot(state, box_count, visible_item_count, estimated_capacity)

    def update(self, pos: Cell, action: int, action_value: float = 0.0) -> None:
        action = int(action)
        self.recent_positions.append(pos)
        self.recent_actions.append(action)
        self.last_action = action
        self.last_action_value = float(action_value)
        self.turn_index += 1

        if action == PLACE_BOMB and action_value > 0:
            self.proxy_bombs += 1
            self.steps_without_progress = 0

    def action_penalty(self, next_pos: Cell, action: int) -> float:
        recent_positions = list(self.recent_positions)
        recent_actions = list(self.recent_actions)
        penalty = 0.0

        if action == STOP:
            penalty += 5.0
            penalty += 1.8 * sum(1 for recent_action in recent_actions[-5:] if recent_action == STOP)

        if recent_positions and next_pos == recent_positions[-1]:
            penalty += 2.5

        if len(recent_positions) >= 2 and next_pos == recent_positions[-2]:
            penalty += 8.0

        if len(recent_positions) >= 4 and recent_positions[-1] == recent_positions[-3]:
            if next_pos == recent_positions[-2]:
                penalty += 10.0

        penalty += 0.7 * sum(1 for pos in recent_positions if pos == next_pos)

        window = recent_positions[-8:]
        if len(window) >= 6 and len(set(window)) <= 3 and next_pos in window:
            penalty += 5.0

        if self.steps_without_progress >= 12:
            if action == STOP:
                penalty += 10.0
            if next_pos in recent_positions[-6:]:
                penalty += 4.0

        return penalty

    def _store_snapshot(
        self,
        state: GameState,
        box_count: int,
        visible_item_count: int,
        estimated_capacity: int,
    ) -> None:
        self.last_box_count = box_count
        self.last_visible_item_count = visible_item_count
        self.last_self_radius = int(state.self_radius)
        self.last_estimated_capacity = int(estimated_capacity)

    def _reached_new_area(self, pos: Cell) -> bool:
        if not self.recent_positions:
            return False
        return pos not in list(self.recent_positions)[-6:]


def estimate_capacity(state: GameState) -> int:
    owned_active = sum(1 for bomb in state.bombs if bomb.owner_id == state.agent_id)
    item_on_self = int(state.grid[state.self_pos]) in (ITEM_RADIUS, ITEM_CAPACITY)
    bonus = 1 if item_on_self and int(state.grid[state.self_pos]) == ITEM_CAPACITY else 0
    return max(1, min(5, int(state.self_bombs_left) + owned_active + bonus))


# --- person_b_strategy/scoring.py ---

from dataclasses import dataclass, replace
from math import inf

import numpy as np



@dataclass(frozen=True)
class ScoreWeights:
    survival: float = 18.0
    box_move: float = 62.0
    box_bomb: float = 42.0
    item: float = 46.0
    pressure: float = 12.0
    trap: float = 10.0
    mobility: float = 4.0
    danger: float = 12.0
    enemy_risk: float = 6.0
    loop: float = 3.2
    useless_bomb: float = 58.0
    stop: float = 7.0


@dataclass(frozen=True)
class FarmTarget:
    cell: Cell
    gain: int
    distance: int
    score: float


@dataclass(frozen=True)
class ItemTarget:
    cell: Cell
    value: float
    distance: int
    score: float


@dataclass(frozen=True)
class PhaseProfile:
    name: str
    weights: ScoreWeights


@dataclass(frozen=True)
class ScoringContext:
    distances: dict[Cell, int]
    earliest: np.ndarray
    farm_targets: tuple[FarmTarget, ...]
    item_targets: tuple[ItemTarget, ...]
    next_distances: dict[int, dict[Cell, int]]
    first_actions: dict[Cell, int]
    profile: PhaseProfile


def score_actions(
    state: GameState,
    safe_mask: np.ndarray,
    hazard: np.ndarray,
    tracker=None,
    weights: ScoreWeights | None = None,
    turn_index: int = 0,
) -> dict[int, float]:
    context = build_scoring_context(state, safe_mask, hazard, tracker, weights, turn_index)
    scores = {}
    for action in ACTIONS:
        if not bool(safe_mask[action]):
            scores[action] = -inf
            continue
        scores[action] = score_action(
            state,
            action,
            hazard,
            context.distances,
            tracker=tracker,
            weights=context.profile.weights,
            turn_index=turn_index,
            context=context,
        )
    return scores


def explain_action_scores(
    state: GameState,
    safe_mask: np.ndarray,
    hazard: np.ndarray,
    tracker=None,
    weights: ScoreWeights | None = None,
    turn_index: int = 0,
) -> dict[int, dict[str, float]]:
    context = build_scoring_context(state, safe_mask, hazard, tracker, weights, turn_index)
    explanations = {}
    for action in ACTIONS:
        if not bool(safe_mask[action]):
            explanations[action] = {"unsafe": -inf, "total": -inf}
            continue
        components = score_action_components(
            state,
            action,
            hazard,
            context.distances,
            tracker=tracker,
            weights=context.profile.weights,
            turn_index=turn_index,
            context=context,
        )
        explanations[action] = {**components, "total": sum(components.values())}
    return explanations


def score_action(
    state: GameState,
    action: int,
    hazard: np.ndarray,
    distances: dict[Cell, int] | None = None,
    tracker=None,
    weights: ScoreWeights | None = None,
    turn_index: int = 0,
    context: ScoringContext | None = None,
) -> float:
    components = score_action_components(
        state,
        action,
        hazard,
        distances,
        tracker=tracker,
        weights=weights,
        turn_index=turn_index,
        context=context,
    )
    return sum(components.values())


def score_action_components(
    state: GameState,
    action: int,
    hazard: np.ndarray,
    distances: dict[Cell, int] | None = None,
    tracker=None,
    weights: ScoreWeights | None = None,
    turn_index: int = 0,
    context: ScoringContext | None = None,
) -> dict[str, float]:
    if context is None:
        safe_mask = np.ones(len(ACTIONS), dtype=bool)
        context = build_scoring_context(state, safe_mask, hazard, tracker, weights, turn_index)
    if distances is None:
        distances = context.distances
    weights = context.profile.weights if weights is None else weights
    earliest = context.earliest

    next_pos = action_destination(state, action)
    next_distances = context.next_distances.get(action, distances)
    pressure_raw = pressure_score(state, action, turn_index=turn_index)

    # The post-bomb hazard is the single most expensive thing we simulate; share
    # one copy between the escape-quality and trap evaluations for PLACE_BOMB.
    trap_raw = 0.0
    escape_quality = 0.0
    if action == PLACE_BOMB and _can_simulate_bomb(state):
        simulated = copy_state_with_new_bomb_at_self(state)
        sim_hazard = compute_hazard_map(simulated)
        escape_quality = bomb_escape_quality(state, simulated, sim_hazard)
        trap_raw = trap_score(state, hazard, simulated, sim_hazard)
    gain_here = box_gain(state)
    offense = pressure_raw + trap_raw

    components = {
        "survival": weights.survival * survival_score(next_pos, earliest),
        "box_move": weights.box_move
        * box_move_score(state, action, next_pos, context.farm_targets, next_distances, context.first_actions),
        "box_bomb": weights.box_bomb * box_bomb_score(action, gain_here),
        "item": weights.item
        * item_move_score(state, action, next_pos, context.item_targets, next_distances, context.first_actions),
        "pressure": weights.pressure * pressure_raw,
        "trap_bonus": weights.trap * trap_raw,
        "mobility": weights.mobility * mobility_score(state, next_pos),
        "bomb_escape_quality": 0.0,
        "danger_penalty": -weights.danger * danger_penalty(next_pos, earliest),
        "enemy_risk_penalty": enemy_risk_penalty(state, action, next_pos, weights, turn_index),
        "loop_penalty": 0.0,
        "stop_penalty": -weights.stop if action == STOP else 0.0,
        "useless_bomb_penalty": useless_bomb_penalty(
            action,
            gain_here,
            offense,
            weights,
            has_farm_targets=bool(context.farm_targets),
            turn_index=turn_index,
        ),
    }

    if action == PLACE_BOMB:
        if escape_quality <= 0.0:
            components["useless_bomb_penalty"] -= weights.useless_bomb
        elif gain_here > 0 or offense > 0:
            components["bomb_escape_quality"] = weights.survival * min(0.75, escape_quality)

    apply_escape_bias(components, state, action, next_pos, earliest, weights)

    if tracker is not None:
        components["loop_penalty"] = -weights.loop * min(12.0, tracker.action_penalty(next_pos, action))
    return components


def build_scoring_context(
    state: GameState,
    safe_mask: np.ndarray,
    hazard: np.ndarray,
    tracker=None,
    weights: ScoreWeights | None = None,
    turn_index: int = 0,
) -> ScoringContext:
    earliest = hazard_to_earliest(hazard)
    bfs = time_expanded_bfs(state, state.self_pos, hazard)
    distances = bfs.distances
    first_actions = first_actions_by_cell(bfs.first_action, distances)
    profile = PhaseProfile("custom", weights) if weights is not None else phase_profile(turn_index, tracker)
    profile = PhaseProfile(profile.name, adjusted_weights(profile.weights, tracker))

    farms = tuple(farm_targets(state, distances))
    items = tuple(item_targets(state, distances, earliest))
    next_distances = {STOP: distances, PLACE_BOMB: distances}

    for action in ACTIONS:
        if action in (STOP, PLACE_BOMB) or not bool(safe_mask[action]):
            continue
        next_pos = action_destination(state, action)
        next_distances[action] = estimate_distances_after_step(state.self_pos, next_pos, distances)

    return ScoringContext(
        distances=distances,
        earliest=earliest,
        farm_targets=farms,
        item_targets=items,
        next_distances=next_distances,
        profile=profile,
        first_actions=first_actions,
    )


def phase_profile(turn_index: int, tracker=None) -> PhaseProfile:
    if turn_index < 150:
        return PhaseProfile(
            "early",
            ScoreWeights(
                survival=17.0,
                box_move=84.0,
                box_bomb=70.0,
                item=38.0,
                pressure=2.0,
                trap=4.0,
                mobility=4.0,
                danger=12.0,
                enemy_risk=5.0,
                loop=3.4,
                useless_bomb=92.0,
                stop=8.0,
            ),
        )

    if turn_index < 350:
        return PhaseProfile(
            "mid",
            ScoreWeights(
                survival=18.0,
                box_move=68.0,
                box_bomb=56.0,
                item=42.0,
                pressure=6.0,
                trap=10.0,
                mobility=4.5,
                danger=12.0,
                enemy_risk=6.0,
                loop=3.2,
                useless_bomb=86.0,
                stop=7.0,
            ),
        )

    proxy_score = tracker.proxy_score if tracker is not None else 0.0
    if proxy_score >= 3.0:
        return PhaseProfile(
            "late_leading",
            ScoreWeights(
                survival=24.0,
                box_move=48.0,
                box_bomb=46.0,
                item=36.0,
                pressure=6.0,
                trap=8.0,
                mobility=6.0,
                danger=16.0,
                enemy_risk=9.0,
                loop=3.0,
                useless_bomb=92.0,
                stop=6.0,
            ),
        )

    return PhaseProfile(
        "late_chasing",
        ScoreWeights(
            survival=18.0,
            box_move=66.0,
            box_bomb=54.0,
            item=40.0,
            pressure=16.0,
            trap=18.0,
            mobility=5.0,
            danger=13.0,
            enemy_risk=4.0,
            loop=3.5,
            useless_bomb=74.0,
            stop=8.5,
        ),
    )


def adjusted_weights(weights: ScoreWeights, tracker=None) -> ScoreWeights:
    if tracker is None or tracker.steps_without_progress < 12:
        return weights
    return replace(
        weights,
        box_move=weights.box_move * 1.35,
        item=weights.item * 1.25,
        loop=weights.loop * 1.25,
        stop=weights.stop * 1.8,
    )


def farm_targets(state: GameState, distances: dict[Cell, int]) -> list[FarmTarget]:
    targets = []
    for cell, distance in distances.items():
        if distance < 0:
            continue
        if not passable(state, cell, allow_start=state.self_pos):
            continue
        gain = box_gain(state, cell)
        if gain <= 0:
            continue
        score = gain / (distance + 1.0)
        targets.append(FarmTarget(cell=cell, gain=gain, distance=int(distance), score=score))

    return sorted(targets, key=lambda target: (-target.score, target.distance, target.cell))


def item_targets(
    state: GameState,
    distances: dict[Cell, int],
    earliest: np.ndarray,
) -> list[ItemTarget]:
    targets = []
    for cell, distance in distances.items():
        tile = int(state.grid[cell])
        if tile not in (ITEM_RADIUS, ITEM_CAPACITY):
            continue
        danger = int(earliest[cell])
        if danger < INF and danger <= distance + 1:
            continue
        # Skip distant items an opponent reaches at least as fast: contesting it
        # usually just gets the item destroyed (two occupants) or loses the race.
        if distance >= 2 and enemy_contest_risk(state, cell, distance) >= 1.0:
            continue
        value = item_value(state, cell)
        score = value / (distance + 1.0)
        targets.append(ItemTarget(cell=cell, value=value, distance=int(distance), score=score))

    return sorted(targets, key=lambda target: (-target.score, target.distance, target.cell))


def survival_score(pos: Cell, earliest: np.ndarray) -> float:
    danger = int(earliest[pos])
    if danger >= INF:
        return 2.0
    return max(0.0, min(2.0, danger / 4.0))


def mobility_score(state: GameState, pos: Cell) -> float:
    return float(sum(1 for nbr in neighbors(pos) if passable(state, nbr, allow_start=state.self_pos)))


def item_value(state: GameState, cell: Cell) -> float:
    tile = int(state.grid[cell])
    capacity = estimated_bomb_capacity(state)

    if tile == ITEM_RADIUS:
        if state.self_radius <= 2:
            return 2.4
        if state.self_radius == 3:
            return 1.55
        return 0.85

    if tile == ITEM_CAPACITY:
        if capacity <= 1:
            return 2.5
        if capacity == 2:
            return 1.75
        return 1.0

    return 0.0


def item_move_score(
    state: GameState,
    action: int,
    next_pos: Cell,
    targets: tuple[ItemTarget, ...],
    next_distances: dict[Cell, int],
    first_actions: dict[Cell, int],
) -> float:
    if action == STOP:
        return 0.0
    if int(state.grid[next_pos]) in (ITEM_RADIUS, ITEM_CAPACITY):
        return item_value(state, next_pos) * 1.35
    return max(
        directional_target_score(targets, next_distances),
        first_action_target_score(targets, action, first_actions),
    )


def box_gain(state: GameState, cell: Cell | None = None) -> int:
    cell = state.self_pos if cell is None else cell
    cells = blast_cells(cell, state.self_radius, state.walls, state.boxes)
    return sum(1 for blast_cell in cells if bool(state.boxes[blast_cell]))


def box_move_score(
    state: GameState,
    action: int,
    next_pos: Cell,
    targets: tuple[FarmTarget, ...],
    next_distances: dict[Cell, int],
    first_actions: dict[Cell, int],
) -> float:
    # STOP must NOT earn farming credit: standing on a cell whose blast covers a
    # box is not the same as actually destroying it (that needs PLACE_BOMB). The
    # old code rewarded STOP via box_gain(self_pos) and made the agent camp next
    # to boxes instead of bombing them.
    if action in (STOP, PLACE_BOMB):
        return 0.0
    direct_gain = float(box_gain(state, next_pos))
    target_gain = directional_target_score(targets, next_distances)
    path_gain = first_action_target_score(targets, action, first_actions)
    return max(direct_gain, target_gain, path_gain)


def box_bomb_score(action: int, gain_here: int) -> float:
    if action != PLACE_BOMB or gain_here <= 0:
        return 0.0
    return float(gain_here)


def _can_simulate_bomb(state: GameState) -> bool:
    return (
        state.self_alive
        and state.self_bombs_left > 0
        and state.self_pos not in state.bomb_positions
    )


def bomb_escape_quality(
    state: GameState,
    simulated: GameState | None = None,
    sim_hazard: np.ndarray | None = None,
) -> float:
    if not _can_simulate_bomb(state):
        return 0.0

    if simulated is None:
        simulated = copy_state_with_new_bomb_at_self(state)
    hazard = compute_hazard_map(simulated) if sim_hazard is None else sim_hazard
    bfs = time_expanded_bfs(simulated, simulated.self_pos, hazard, start_time=1)
    permanent_targets = [(cell, t) for cell, t in bfs.safe_targets if earliest_at(hazard, cell) >= INF]
    if not permanent_targets:
        return 0.0

    best = 0.0
    for cell, arrival in permanent_targets:
        open_count = open_neighbors(simulated, cell)
        candidate = 1.0 / max(1.0, float(arrival))
        candidate += 0.18 * open_count
        if cell == state.self_pos:
            candidate *= 0.25
        best = max(best, candidate)
    return min(2.0, best)


def pressure_score(state: GameState, action: int, turn_index: int = 0) -> float:
    if action != PLACE_BOMB or not state.opponents:
        return 0.0

    blast = blast_cells(state.self_pos, state.self_radius, state.walls, state.boxes)
    score = 0.0
    for enemy in state.opponents:
        if enemy in blast:
            score += 1.4
            continue
        if aligned_and_clear(state, state.self_pos, enemy, state.self_radius + 2):
            score += 0.35
        elif manhattan(state.self_pos, enemy) <= 2 and open_neighbors(state, enemy) <= 2:
            score += 0.25

    if turn_index < 150:
        score *= 0.55
    elif turn_index >= 350:
        score *= 1.2
    return min(score, 2.8)


def trap_score(
    state: GameState,
    hazard: np.ndarray,
    simulated: GameState | None = None,
    sim_hazard: np.ndarray | None = None,
) -> float:
    """Value of trapping an opponent by placing a bomb now.

    Measures how many eventually-safe cells the NEAREST opponent loses once our
    bomb is on the board (a kill bomb drives the count to zero). Gated on having
    a bomb and an opponent within blast-ish range so the extra search only runs
    when it can matter, and only for the single closest opponent to bound cost.
    """

    if not _can_simulate_bomb(state) or not state.opponents:
        return 0.0

    reach = state.self_radius + 2
    enemy = min(state.opponents, key=lambda e: manhattan(state.self_pos, e))
    if manhattan(state.self_pos, enemy) > reach:
        return 0.0

    if simulated is None:
        simulated = copy_state_with_new_bomb_at_self(state)
    if sim_hazard is None:
        sim_hazard = compute_hazard_map(simulated)

    before = enemy_escape_count(state, enemy, hazard)
    if before <= 0:
        return 0.0
    after = enemy_escape_count(simulated, enemy, sim_hazard)
    if after == 0:
        return 1.5  # cornered: a likely kill
    return min(2.5, (before - after) / float(before))  # fraction of escapes removed


def enemy_escape_count(state: GameState, enemy_pos: Cell, hazard: np.ndarray, horizon: int = 6) -> int:
    """Distinct cells the opponent could flee to while dodging the timed fire."""

    bfs = time_expanded_bfs(state, enemy_pos, hazard, horizon=horizon, start_time=0)
    reachable = {cell for cell, t in bfs.safe_targets if eventually_safe(cell, t, hazard)}
    return len(reachable)


def enemy_contest_risk(state: GameState, item_cell: Cell, my_distance: int) -> float:
    risk = 0.0
    for enemy in state.opponents:
        enemy_dist = manhattan(enemy, item_cell)
        if enemy_dist <= my_distance:
            risk += 1.0
        elif enemy_dist == my_distance + 1:
            risk += 0.4
    return risk


def positional_risk(state: GameState, cell: Cell) -> float:
    """Soft penalty for sitting near an opponent, worse inside a tight corridor.

    Only reorders already-safe actions (the safe mask is the hard gate), so it
    nudges the agent away from spots where an opponent could seal an escape.
    """

    risk = 0.0
    cramped = open_neighbors(state, cell) <= 2
    for enemy in state.opponents:
        d = manhattan(cell, enemy)
        if d <= 1:
            risk += 3.0
        elif d == 2:
            risk += 1.0
        if d <= 3 and cramped:
            risk += 2.0
    return risk


def enemy_risk_penalty(
    state: GameState,
    action: int,
    next_pos: Cell,
    weights: ScoreWeights,
    turn_index: int,
) -> float:
    if action == PLACE_BOMB or not state.opponents:
        return 0.0
    risk = positional_risk(state, next_pos)
    if risk <= 0.0:
        return 0.0
    # When chasing late we accept more proximity to push for kills.
    scale = 0.5 if turn_index >= 350 else 1.0
    return -weights.enemy_risk * scale * min(risk, 6.0)


def useless_bomb_penalty(
    action: int,
    gain_here: int,
    offense: float,
    weights: ScoreWeights,
    has_farm_targets: bool = False,
    turn_index: int = 0,
) -> float:
    if action != PLACE_BOMB:
        return 0.0
    if gain_here > 0:
        return 0.0
    if offense > 0:
        if has_farm_targets and turn_index < 350:
            return -weights.useless_bomb * 0.65
        return 0.0
    return -weights.useless_bomb


def apply_escape_bias(
    components: dict[str, float],
    state: GameState,
    action: int,
    next_pos: Cell,
    earliest: np.ndarray,
    weights: ScoreWeights,
) -> None:
    current_danger = int(earliest[state.self_pos])
    if current_danger >= INF:
        return

    next_danger = int(earliest[next_pos])
    components["box_move"] *= 0.25
    components["item"] *= 0.30
    components["pressure"] *= 0.10
    components["trap_bonus"] *= 0.10

    if next_danger >= INF:
        components["survival"] += weights.survival * 1.5
    elif next_danger > current_danger:
        components["survival"] += weights.survival * 0.6
    else:
        components["danger_penalty"] -= weights.danger * 0.8

    if action == STOP:
        components["stop_penalty"] -= weights.stop


def danger_penalty(pos: Cell, earliest: np.ndarray) -> float:
    danger = int(earliest[pos])
    if danger >= INF:
        return 0.0
    return 1.0 / max(1.0, float(danger))


def directional_target_score(
    targets: tuple[FarmTarget, ...] | tuple[ItemTarget, ...],
    next_distances: dict[Cell, int],
) -> float:
    best = 0.0
    for target in targets[:8]:
        next_distance = next_distances.get(target.cell)
        if next_distance is None:
            continue
        value = target.gain if isinstance(target, FarmTarget) else target.value
        candidate = value / (next_distance + 1.0)
        if next_distance < target.distance:
            candidate *= 1.2
        elif next_distance == target.distance:
            candidate *= 0.35
        else:
            candidate *= 0.05
        best = max(best, candidate)
    return best


def first_action_target_score(
    targets: tuple[FarmTarget, ...] | tuple[ItemTarget, ...],
    action: int,
    first_actions: dict[Cell, int],
) -> float:
    if action in (STOP, PLACE_BOMB):
        return 0.0

    best = 0.0
    for target in targets[:8]:
        if first_actions.get(target.cell) != action:
            continue
        best = max(best, target.score * 1.8)
    return best


def first_actions_by_cell(
    first_action_nodes: dict[tuple[Cell, int], int],
    distances: dict[Cell, int],
) -> dict[Cell, int]:
    first_actions = {}
    for (cell, time), action in first_action_nodes.items():
        if time == 0:
            continue
        if distances.get(cell) != time:
            continue
        if action == STOP:
            continue
        first_actions[cell] = int(action)
    return first_actions


def estimate_distances_after_step(
    current_pos: Cell,
    next_pos: Cell,
    distances: dict[Cell, int],
) -> dict[Cell, int]:
    if next_pos == current_pos:
        return distances

    estimated = {}
    for cell, distance in distances.items():
        if cell == next_pos:
            estimated[cell] = 0
            continue
        current_manhattan = manhattan(current_pos, cell)
        next_manhattan = manhattan(next_pos, cell)
        if next_manhattan < current_manhattan:
            estimated[cell] = max(0, distance - 1)
        elif next_manhattan == current_manhattan:
            estimated[cell] = distance
        else:
            estimated[cell] = distance + 1
    return estimated


def estimated_bomb_capacity(state: GameState) -> int:
    owned_active = sum(1 for bomb in state.bombs if bomb.owner_id == state.agent_id)
    return max(1, min(5, int(state.self_bombs_left) + owned_active))


def action_progress_value(state: GameState, action: int, turn_index: int = 0) -> float:
    next_pos = action_destination(state, action)
    if action == PLACE_BOMB:
        return float(box_gain(state) + pressure_score(state, action, turn_index=turn_index))
    if int(state.grid[next_pos]) in (ITEM_RADIUS, ITEM_CAPACITY):
        return item_value(state, next_pos)
    if action != STOP and box_gain(state, next_pos) > 0:
        return 0.5
    return 0.0


def action_tie_break_score(state: GameState, action: int, turn_index: int = 0) -> float:
    if action == PLACE_BOMB:
        return 4.0 if action_progress_value(state, action, turn_index=turn_index) > 0 else 0.25
    if action == STOP:
        return -1.0
    return 2.0 + action * 0.01


def aligned_and_clear(state: GameState, start: Cell, target: Cell, max_distance: int) -> bool:
    if start[0] != target[0] and start[1] != target[1]:
        return False
    if manhattan(start, target) > max_distance:
        return False

    if start[0] == target[0]:
        step = 1 if target[1] > start[1] else -1
        for col in range(start[1] + step, target[1], step):
            if bool(state.walls[start[0], col]) or bool(state.boxes[start[0], col]):
                return False
        return True

    step = 1 if target[0] > start[0] else -1
    for row in range(start[0] + step, target[0], step):
        if bool(state.walls[row, start[1]]) or bool(state.boxes[row, start[1]]):
            return False
    return True


def open_neighbors(state: GameState, pos: Cell) -> int:
    return sum(1 for nbr in neighbors(pos) if passable(state, nbr, allow_start=state.self_pos))


def manhattan(a: Cell, b: Cell) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def neighbors(pos: Cell) -> tuple[Cell, Cell, Cell, Cell]:
    row, col = pos
    return (
        (row - 1, col),
        (row + 1, col),
        (row, col - 1),
        (row, col + 1),
    )


# --- person_b_strategy/policy_rule.py ---

from math import inf




class RulePolicy:
    """Rule_v1 policy: score only actions allowed by A's safe mask."""

    def __init__(self):
        self.loop_tracker = AntiLoopTracker()
        self.turn_index = 0

    def choose_action(self, state, safe_mask, hazard) -> int:
        self.loop_tracker.observe_state(state)
        scores = score_actions(
            state,
            safe_mask,
            hazard,
            tracker=self.loop_tracker,
            turn_index=self.turn_index,
        )

        action = self._best_action(state, scores)
        action_value = action_progress_value(state, action, turn_index=self.turn_index)
        self.loop_tracker.update(state.self_pos, action, action_value=action_value)
        self.turn_index += 1
        return int(action)

    def _best_action(self, state, scores: dict[int, float]) -> int:
        if not scores:
            return STOP

        action = max(
            ACTIONS,
            key=lambda candidate: (
                scores.get(candidate, -inf),
                action_tie_break_score(state, candidate, turn_index=self.turn_index),
            ),
        )
        if scores.get(action, -inf) == -inf:
            return STOP
        return int(action)


# --- Agent entrypoint ---



class Agent:
    """Submit-compatible agent that wires A's safety core to B's policy."""

    team_id = "TeamABScaffoldAgent"

    def __init__(self, agent_id: int):
        self.agent_id = int(agent_id)
        self.policy = RulePolicy()

    def act(self, obs: dict) -> int:
        try:
            state = parse_obs(obs, self.agent_id)
            hazard = compute_hazard_map(state)
            mask = safe_actions(state, hazard)
            raw_action = self.policy.choose_action(state, mask, hazard)
            return int(final_shield(raw_action, state, hazard, mask))
        except Exception:
            return STOP
