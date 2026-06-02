"""The time-budget guard skips the expensive strategy simulations once the soft
per-step budget is spent, without ever raising or returning a non-finite score.

The mandatory safety work (hazard map + safe mask + final shield) is unaffected
and still runs in the agent; only the OPTIONAL bomb-trap / escape-quality /
enemy-bomb simulations inside scoring are dropped under deadline pressure.
"""

import time
from math import isfinite

import numpy as np

from grid_helpers import make_obs, make_player
from person_a_safety.constants import GRASS, PLACE_BOMB
from person_a_safety.danger import compute_hazard_map
from person_a_safety.obs import parse_obs
from person_b_strategy.scoring import score_action_components


def _kill_state():
    grid = np.ones((13, 13), dtype=np.int8)
    grid[5, 1:7] = GRASS
    players = [
        make_player(5, 2, bombs_left=1, radius_bonus=3),
        make_player(5, 1),
        make_player(11, 11, alive=0),
        make_player(11, 1, alive=0),
    ]
    return parse_obs(make_obs(grid, players), 0)


def test_deadline_skips_bomb_trap_simulation():
    state = _kill_state()
    hazard = compute_hazard_map(state)

    live = score_action_components(state, PLACE_BOMB, hazard, deadline=None)
    skipped = score_action_components(state, PLACE_BOMB, hazard, deadline=time.perf_counter() - 1.0)

    # With time, the corner kill earns a trap bonus; out of time, the sim is
    # skipped so the trap/escape-quality components collapse to zero.
    assert live["trap_bonus"] > 0.0
    assert skipped["trap_bonus"] == 0.0
    assert skipped["bomb_escape_quality"] == 0.0


def test_skipped_scores_stay_finite():
    state = _kill_state()
    hazard = compute_hazard_map(state)
    components = score_action_components(state, PLACE_BOMB, hazard, deadline=time.perf_counter() - 1.0)
    assert all(isfinite(value) for value in components.values())
