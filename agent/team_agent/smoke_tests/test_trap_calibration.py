"""trap_score values a true corner kill far above a weak "trap ảo".

The calibrated score rewards a bomb that drives the nearest opponent's escape
count to zero (a likely kill) and heavily discounts a bomb that still leaves the
enemy several ways out. A deeper enemy lookahead horizon also removes the false
"kill" a short window used to report.
"""

import numpy as np

from grid_helpers import empty_grid, make_obs, make_player
from person_a_safety.constants import GRASS
from person_a_safety.danger import compute_hazard_map
from person_a_safety.obs import parse_obs
from person_b_strategy.scoring import trap_score


def _state(grid, players):
    return parse_obs(make_obs(grid, players), 0)


def _kill_state():
    # Enemy at the closed end (5,1) of a 1-wide corridor; our bomb at (5,2) with
    # radius 4 floods every cell the enemy can reach -> no escape.
    grid = np.ones((13, 13), dtype=np.int8)
    grid[5, 1:7] = GRASS
    players = [
        make_player(5, 2, bombs_left=1, radius_bonus=3),
        make_player(5, 1),
        make_player(11, 11, alive=0),
        make_player(11, 1, alive=0),
    ]
    return _state(grid, players)


def _weak_trap_state():
    # Enemy in the open with many escapes; a radius-1 bomb removes only a few.
    players = [
        make_player(6, 6, bombs_left=1, radius_bonus=0),
        make_player(6, 7),
        make_player(11, 11, alive=0),
        make_player(11, 1, alive=0),
    ]
    return _state(empty_grid(), players)


def test_corner_kill_scores_high():
    state = _kill_state()
    hazard = compute_hazard_map(state)
    assert trap_score(state, hazard) >= 1.4


def test_weak_trap_is_discounted():
    state = _weak_trap_state()
    hazard = compute_hazard_map(state)
    assert trap_score(state, hazard) < 0.5


def test_kill_beats_weak_trap():
    kill = trap_score(_kill_state(), compute_hazard_map(_kill_state()))
    weak = trap_score(_weak_trap_state(), compute_hazard_map(_weak_trap_state()))
    assert kill > weak
