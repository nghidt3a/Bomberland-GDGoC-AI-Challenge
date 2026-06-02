from dataclasses import replace

import numpy as np

from .bomb import can_place_bomb_safely
from .constants import ACTIONS, ACTION_DELTAS, INF, PLACE_BOMB, STOP
from .danger import compute_hazard_map, earliest_at
from .search import has_escape_path, move, passable, safe_at
from .state import GameState


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
