"""Shared offense cap (00_README): stacking offense techniques (pressure + trap +
denial + seal/kill) must never produce a runaway / double-counted score, and a
productive bomb must still waive the useless-bomb penalty.
"""

from math import isfinite

import numpy as np

from grid_helpers import empty_grid, make_obs, make_player
from person_a_safety.constants import BOX, GRASS, ITEM_RADIUS, PLACE_BOMB
from person_a_safety.danger import compute_hazard_map
from person_a_safety.obs import parse_obs
from person_b_strategy.scoring import OFFENSE_CAP, score_action_components


def test_offense_cap_is_sane():
    assert 1.0 <= OFFENSE_CAP <= 5.0


def test_stacked_offense_stays_finite_and_bounded():
    # A bomb that simultaneously hits a box, threatens a nearby enemy, and a denial
    # item is on the board — many offense signals at once.
    grid = empty_grid()
    grid[5, 6] = BOX
    grid[5, 8] = ITEM_RADIUS
    players = [
        make_player(5, 5, bombs_left=2, radius_bonus=3),
        make_player(5, 7),  # enemy near our blast line
        make_player(11, 11, alive=0),
        make_player(11, 1, alive=0),
    ]
    state = parse_obs(make_obs(grid, players, bombs=[[5, 1, 6, 0]]), 0)  # own old bomb too
    comps = score_action_components(state, PLACE_BOMB, compute_hazard_map(state))

    assert all(isfinite(v) for v in comps.values())
    # Continuous offense components stay within their per-signal design caps * weight.
    assert 0.0 <= comps["pressure"] <= 3.0 * 30.0
    assert 0.0 <= comps["trap_bonus"] <= 2.0 * 30.0
    assert 0.0 <= comps["deny_bonus"] <= 2.0 * 40.0


def test_productive_bomb_not_useless():
    grid = empty_grid()
    grid[5, 6] = BOX
    state = parse_obs(
        make_obs(grid, [make_player(5, 5, bombs_left=1, radius_bonus=3),
                        make_player(1, 1, alive=0), make_player(11, 11, alive=0), make_player(11, 1, alive=0)]),
        0,
    )
    comps = score_action_components(state, PLACE_BOMB, compute_hazard_map(state))
    assert comps["box_bomb"] > 0.0
    assert comps["useless_bomb_penalty"] == 0.0
