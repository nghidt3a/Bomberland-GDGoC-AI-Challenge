import numpy as np

from .constants import ACTIONS, INF, PLACE_BOMB, STOP
from .danger import compute_hazard_map, earliest_at
from .masks import action_destination, legal_actions, safe_actions
from .search import first_escape_action, passable
from .state import Cell, GameState


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
