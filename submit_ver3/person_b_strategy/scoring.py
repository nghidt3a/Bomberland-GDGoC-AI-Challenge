from dataclasses import dataclass, replace
from math import inf

import numpy as np

from person_a_safety.constants import (
    ACTIONS,
    INF,
    ITEM_CAPACITY,
    ITEM_RADIUS,
    MOVE_ACTIONS,
    PLACE_BOMB,
    STOP,
)
from person_a_safety.bomb import copy_state_with_new_bomb_at_self
from person_a_safety.danger import blast_cells, compute_hazard_map, earliest_at, hazard_to_earliest
from person_a_safety.masks import action_destination
from person_a_safety.search import eventually_safe, passable, time_expanded_bfs
from person_a_safety.state import Cell, GameState


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
