import numpy as np

from .constants import ACTIONS, INF, PLACE_BOMB, STOP
from .danger import compute_danger_map
from .masks import action_destination, legal_actions, safe_actions
from .search import passable
from .state import Cell, GameState


def action_is_safe(action: int, state: GameState, danger_time: np.ndarray | None = None) -> bool:
    if action not in ACTIONS:
        return False
    mask = safe_actions(state, danger_time)
    return bool(mask[int(action)])


def final_shield(action: int, state: GameState, danger_time: np.ndarray | None = None) -> int:
    """Final safety gate. B's policy must pass through this before returning."""

    danger_time = compute_danger_map(state) if danger_time is None else danger_time
    try:
        action = int(action)
    except Exception:
        action = STOP

    if action_is_safe(action, state, danger_time):
        return action

    mask = safe_actions(state, danger_time)
    if mask.any():
        chosen = best_escape_action(state, mask, danger_time)
    else:
        chosen = least_bad_action(state, danger_time)

    # Final invariant: never hand the engine an out-of-range action.
    return chosen if chosen in ACTIONS else STOP


def best_escape_action(state: GameState, mask: np.ndarray, danger_time: np.ndarray) -> int:
    candidates = [action for action in ACTIONS if bool(mask[action]) and action != PLACE_BOMB]
    if not candidates:
        candidates = [action for action in ACTIONS if bool(mask[action])]
    if not candidates:
        return STOP

    return max(candidates, key=lambda action: _escape_score(state, action, danger_time))


def least_bad_action(state: GameState, danger_time: np.ndarray) -> int:
    legal = legal_actions(state)
    candidates = [action for action in ACTIONS if bool(legal[action]) and action != PLACE_BOMB]
    if not candidates:
        return STOP
    return max(candidates, key=lambda action: _escape_score(state, action, danger_time))


def _escape_score(state: GameState, action: int, danger_time: np.ndarray) -> float:
    cell = action_destination(state, action)
    danger = int(danger_time[cell])
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
