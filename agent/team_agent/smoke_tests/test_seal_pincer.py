"""Seal / pincer kill (technique 02): an own existing bomb + the new one together
corner an opponent that neither could alone. ``offense_eval`` now considers every
opponent and ranges by distance to self OR any own live bomb, and flags the kill
as a pincer so the ``seal`` weight adds an extra bonus.
"""

import numpy as np

from grid_helpers import make_obs, make_player
from person_a_safety.constants import GRASS, PLACE_BOMB
from person_a_safety.danger import compute_hazard_map
from person_a_safety.obs import parse_obs
from person_b_strategy.scoring import offense_eval, score_action_components


def _pincer_board():
    # Corridor row 5 cols 1..5, enemy in the middle (5,3); we stand at (5,5) with a
    # vertical escape below. Our OLD bomb at (5,1) seals the left, the NEW bomb at
    # (5,5) seals the right -> the enemy is pincered.
    grid = np.ones((13, 13), dtype=np.int8)
    grid[5, 1:6] = GRASS
    grid[6:11, 5] = GRASS
    players = [
        make_player(5, 5, bombs_left=1, radius_bonus=1),
        make_player(5, 3),
        make_player(11, 11, alive=0),
        make_player(11, 1, alive=0),
    ]
    return parse_obs(make_obs(grid, players, bombs=[[5, 1, 6, 0]]), 0)  # own old bomb at (5,1)


def _single_kill_board():
    # Same kill geometry but NO own old bomb -> a plain (non-pincer) kill.
    grid = np.ones((13, 13), dtype=np.int8)
    grid[5, 1:3] = GRASS
    grid[5, 3] = GRASS
    grid[6:12, 3] = GRASS
    players = [
        make_player(5, 3, bombs_left=1, radius_bonus=1),
        make_player(5, 1),
        make_player(11, 11, alive=0),
        make_player(11, 1, alive=0),
    ]
    return parse_obs(make_obs(grid, players), 0)


def test_offense_eval_flags_pincer():
    state = _pincer_board()
    _value, is_kill, is_pincer = offense_eval(state, compute_hazard_map(state))
    assert is_kill is True
    assert is_pincer is True


def test_single_kill_is_not_pincer():
    state = _single_kill_board()
    _value, is_kill, is_pincer = offense_eval(state, compute_hazard_map(state))
    assert is_kill is True
    assert is_pincer is False


def test_seal_adds_bonus_over_plain_kill():
    # Both boards trigger the same endgame/phase scaling, so the pincer kill_bonus
    # (kill + seal) must exceed the plain kill_bonus (kill only).
    pincer = score_action_components(_pincer_board(), PLACE_BOMB, compute_hazard_map(_pincer_board()))
    plain = score_action_components(_single_kill_board(), PLACE_BOMB, compute_hazard_map(_single_kill_board()))
    assert pincer["kill_bonus"] > plain["kill_bonus"] > 0.0
