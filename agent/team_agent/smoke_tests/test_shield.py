"""final_shield: the last gate that vetoes any unsafe action from Person B."""

from grid_helpers import empty_grid, make_obs, make_player
from person_a_safety.constants import ACTIONS, DOWN, PLACE_BOMB, STOP, UP
from person_a_safety.danger import compute_danger_map
from person_a_safety.masks import safe_actions
from person_a_safety.obs import parse_obs
from person_a_safety.shield import final_shield


def _state(grid, players, bombs=None, agent_id=0):
    return parse_obs(make_obs(grid, players, bombs=bombs), agent_id=agent_id)


def four(p0):
    return [p0, make_player(1, 11), make_player(11, 11), make_player(11, 1)]


def test_safe_action_passes_through_unchanged():
    grid = empty_grid()
    state = _state(grid, four(make_player(6, 6, bombs_left=1)))
    danger = compute_danger_map(state)
    assert safe_actions(state, danger)[UP]
    assert final_shield(UP, state, danger) == UP


def test_unsafe_move_is_overridden_to_a_safe_one():
    grid = empty_grid()
    p0 = make_player(6, 6, bombs_left=1, radius_bonus=1)
    state = _state(grid, four(p0), bombs=[[6, 9, 1, 0]])  # DOWN -> (6,7) on fire
    danger = compute_danger_map(state)
    chosen = final_shield(DOWN, state, danger)  # B insists on the unsafe move
    assert chosen in ACTIONS
    assert safe_actions(state, danger)[chosen]  # replaced by an actually-safe action


def test_unsafe_bomb_is_overridden():
    # Dead-end pocket: placing a bomb is suicide; shield must not return it.
    import numpy as np

    grid = np.ones((13, 13), dtype=np.int8)
    grid[5, 1] = 0
    grid[5, 2] = 0
    state = _state(grid, four(make_player(5, 1, bombs_left=1)))
    chosen = final_shield(PLACE_BOMB, state)
    assert chosen != PLACE_BOMB
    assert chosen in ACTIONS


def test_invalid_action_is_sanitised():
    grid = empty_grid()
    state = _state(grid, four(make_player(6, 6, bombs_left=1)))
    assert final_shield(99, state) in ACTIONS
    assert final_shield(-1, state) in ACTIONS


def test_dead_agent_returns_stop():
    grid = empty_grid()
    state = _state(grid, four(make_player(6, 6, alive=0)))
    assert final_shield(PLACE_BOMB, state) == STOP
