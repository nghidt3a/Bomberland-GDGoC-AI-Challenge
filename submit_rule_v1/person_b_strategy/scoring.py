from dataclasses import dataclass, replace
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
from person_a_safety.search import passable, time_expanded_bfs
from person_a_safety.state import Cell, GameState


@dataclass(frozen=True)
class ScoreWeights:
    survival: float = 18.0
    box_move: float = 62.0
    box_bomb: float = 42.0
    item: float = 46.0
    pressure: float = 12.0
    mobility: float = 4.0
    danger: float = 12.0
    loop: float = 2.5
    useless_bomb: float = 58.0
    stop: float = 5.0


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
    farm_targets: tuple[FarmTarget, ...]
    item_targets: tuple[ItemTarget, ...]
    next_distances: dict[int, dict[Cell, int]]
    first_actions: dict[Cell, int]
    profile: PhaseProfile


def score_actions(
    state: GameState,
    safe_mask: np.ndarray,
    danger_time: np.ndarray,
    tracker=None,
    weights: ScoreWeights | None = None,
    turn_index: int = 0,
) -> dict[int, float]:
    context = build_scoring_context(state, safe_mask, danger_time, tracker, weights, turn_index)
    scores = {}
    for action in ACTIONS:
        if not bool(safe_mask[action]):
            scores[action] = -inf
            continue
        scores[action] = score_action(
            state,
            action,
            danger_time,
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
    danger_time: np.ndarray,
    tracker=None,
    weights: ScoreWeights | None = None,
    turn_index: int = 0,
) -> dict[int, dict[str, float]]:
    context = build_scoring_context(state, safe_mask, danger_time, tracker, weights, turn_index)
    explanations = {}
    for action in ACTIONS:
        if not bool(safe_mask[action]):
            explanations[action] = {"unsafe": -inf, "total": -inf}
            continue
        components = score_action_components(
            state,
            action,
            danger_time,
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
    danger_time: np.ndarray,
    distances: dict[Cell, int] | None = None,
    tracker=None,
    weights: ScoreWeights | None = None,
    turn_index: int = 0,
    context: ScoringContext | None = None,
) -> float:
    components = score_action_components(
        state,
        action,
        danger_time,
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
    danger_time: np.ndarray,
    distances: dict[Cell, int] | None = None,
    tracker=None,
    weights: ScoreWeights | None = None,
    turn_index: int = 0,
    context: ScoringContext | None = None,
) -> dict[str, float]:
    if context is None:
        safe_mask = np.ones(len(ACTIONS), dtype=bool)
        context = build_scoring_context(state, safe_mask, danger_time, tracker, weights, turn_index)
    if distances is None:
        distances = context.distances
    weights = context.profile.weights if weights is None else weights

    next_pos = action_destination(state, action)
    next_distances = context.next_distances.get(action, distances)
    pressure_raw = pressure_score(state, action, turn_index=turn_index)
    gain_here = box_gain(state)

    components = {
        "survival": weights.survival * survival_score(next_pos, danger_time),
        "box_move": weights.box_move
        * box_move_score(state, action, next_pos, context.farm_targets, next_distances, context.first_actions),
        "box_bomb": weights.box_bomb * box_bomb_score(action, gain_here),
        "item": weights.item
        * item_move_score(state, action, next_pos, context.item_targets, next_distances, context.first_actions),
        "pressure": weights.pressure * pressure_raw,
        "mobility": weights.mobility * mobility_score(state, next_pos),
        "danger_penalty": -weights.danger * danger_penalty(next_pos, danger_time),
        "loop_penalty": 0.0,
        "stop_penalty": -weights.stop if action == STOP else 0.0,
        "useless_bomb_penalty": useless_bomb_penalty(
            action,
            gain_here,
            pressure_raw,
            weights,
            has_farm_targets=bool(context.farm_targets),
            turn_index=turn_index,
        ),
    }

    apply_escape_bias(components, state, action, next_pos, danger_time, weights)

    if tracker is not None:
        components["loop_penalty"] = -weights.loop * min(12.0, tracker.action_penalty(next_pos, action))
    return components


def build_scoring_context(
    state: GameState,
    safe_mask: np.ndarray,
    danger_time: np.ndarray,
    tracker=None,
    weights: ScoreWeights | None = None,
    turn_index: int = 0,
) -> ScoringContext:
    bfs = time_expanded_bfs(state, state.self_pos, danger_time)
    distances = bfs.distances
    first_actions = first_actions_by_cell(bfs.first_action, distances)
    profile = PhaseProfile("custom", weights) if weights is not None else phase_profile(turn_index, tracker)
    profile = PhaseProfile(profile.name, adjusted_weights(profile.weights, tracker))

    farms = tuple(farm_targets(state, distances))
    items = tuple(item_targets(state, distances, danger_time))
    next_distances = {STOP: distances, PLACE_BOMB: distances}

    for action in ACTIONS:
        if action in (STOP, PLACE_BOMB) or not bool(safe_mask[action]):
            continue
        next_pos = action_destination(state, action)
        next_distances[action] = estimate_distances_after_step(state.self_pos, next_pos, distances)

    return ScoringContext(
        distances=distances,
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
                mobility=4.0,
                danger=12.0,
                loop=2.4,
                useless_bomb=92.0,
                stop=5.5,
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
                mobility=4.5,
                danger=12.0,
                loop=2.5,
                useless_bomb=86.0,
                stop=5.0,
            ),
        )

    proxy_score = tracker.proxy_score if tracker is not None else 0.0
    if proxy_score >= 4.0:
        return PhaseProfile(
            "late_leading",
            ScoreWeights(
                survival=24.0,
                box_move=48.0,
                box_bomb=46.0,
                item=36.0,
                pressure=6.0,
                mobility=6.0,
                danger=16.0,
                loop=2.2,
                useless_bomb=92.0,
                stop=4.0,
            ),
        )

    return PhaseProfile(
        "late_chasing",
        ScoreWeights(
            survival=18.0,
            box_move=66.0,
            box_bomb=54.0,
            item=40.0,
            pressure=14.0,
            mobility=5.0,
            danger=13.0,
            loop=2.7,
            useless_bomb=78.0,
            stop=6.0,
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
    danger_time: np.ndarray,
) -> list[ItemTarget]:
    targets = []
    for cell, distance in distances.items():
        tile = int(state.grid[cell])
        if tile not in (ITEM_RADIUS, ITEM_CAPACITY):
            continue
        danger = int(danger_time[cell])
        if danger < INF and danger <= distance + 1:
            continue
        value = item_value(state, cell)
        score = value / (distance + 1.0)
        targets.append(ItemTarget(cell=cell, value=value, distance=int(distance), score=score))

    return sorted(targets, key=lambda target: (-target.score, target.distance, target.cell))


def survival_score(pos: Cell, danger_time: np.ndarray) -> float:
    danger = int(danger_time[pos])
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
    if action == PLACE_BOMB:
        return 0.0
    direct_gain = float(box_gain(state, next_pos))
    target_gain = directional_target_score(targets, next_distances)
    path_gain = first_action_target_score(targets, action, first_actions)
    return max(direct_gain, target_gain, path_gain)


def box_bomb_score(action: int, gain_here: int) -> float:
    if action != PLACE_BOMB or gain_here <= 0:
        return 0.0
    return float(gain_here)


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


def useless_bomb_penalty(
    action: int,
    gain_here: int,
    pressure_raw: float,
    weights: ScoreWeights,
    has_farm_targets: bool = False,
    turn_index: int = 0,
) -> float:
    if action != PLACE_BOMB:
        return 0.0
    if gain_here > 0:
        return 0.0
    if pressure_raw > 0:
        if has_farm_targets and turn_index < 350:
            return -weights.useless_bomb * 0.65
        return 0.0
    return -weights.useless_bomb


def apply_escape_bias(
    components: dict[str, float],
    state: GameState,
    action: int,
    next_pos: Cell,
    danger_time: np.ndarray,
    weights: ScoreWeights,
) -> None:
    current_danger = int(danger_time[state.self_pos])
    if current_danger >= INF:
        return

    next_danger = int(danger_time[next_pos])
    components["box_move"] *= 0.25
    components["item"] *= 0.30
    components["pressure"] *= 0.10

    if next_danger >= INF:
        components["survival"] += weights.survival * 1.5
    elif next_danger > current_danger:
        components["survival"] += weights.survival * 0.6
    else:
        components["danger_penalty"] -= weights.danger * 0.8

    if action == STOP:
        components["stop_penalty"] -= weights.stop


def danger_penalty(pos: Cell, danger_time: np.ndarray) -> float:
    danger = int(danger_time[pos])
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
