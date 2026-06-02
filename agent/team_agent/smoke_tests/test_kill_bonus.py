"""kill_bonus rewards a bomb that corners an opponent — but only when WE escape.

A kill is the #1 tie-break at step 500, so a bomb that drives the nearest
opponent's escape count to zero is worth a large bonus. It is paid ONLY when we
keep an escape ourselves, so the agent never trades a kill for a suicide.
"""

import numpy as np

from grid_helpers import empty_grid, make_obs, make_player
from person_a_safety.constants import GRASS, PLACE_BOMB
from person_a_safety.danger import compute_hazard_map
from person_a_safety.obs import parse_obs
from person_b_strategy.scoring import bomb_escape_quality, offense_eval, score_action_components


def _kill_board():
    # Enemy is sealed in a 2-cell pocket (5,1)-(5,2); we sit at the mouth (5,3) with
    # a vertical escape branch below. Our own bomb at (5,3) both floods the pocket
    # AND blocks the enemy's only route to the shared escape, so the enemy is killed
    # while we flee straight down.
    grid = np.ones((13, 13), dtype=np.int8)
    grid[5, 1:3] = GRASS   # pocket cols 1,2
    grid[5, 3] = GRASS     # mouth = our cell
    grid[6:12, 3] = GRASS  # vertical escape under us
    players = [
        make_player(5, 3, bombs_left=1, radius_bonus=1),
        make_player(5, 1),
        make_player(11, 11, alive=0),
        make_player(11, 1, alive=0),
    ]
    return parse_obs(make_obs(grid, players), 0)


def test_offense_eval_flags_corner_kill():
    state = _kill_board()
    _value, is_kill, _is_pincer = offense_eval(state, compute_hazard_map(state))
    assert is_kill is True


def test_kill_bonus_awarded_when_we_escape():
    state = _kill_board()
    comps = score_action_components(state, PLACE_BOMB, compute_hazard_map(state))
    assert comps["kill_bonus"] > 0.0


def test_no_kill_bonus_when_we_cannot_escape():
    # Enemy and us share a flooded corridor: the bomb kills the enemy but also us,
    # so escape_quality is 0 and the kill must NOT be rewarded.
    grid = np.ones((13, 13), dtype=np.int8)
    grid[5, 1:7] = GRASS
    state = parse_obs(
        make_obs(
            grid,
            [make_player(5, 2, bombs_left=1, radius_bonus=3), make_player(5, 1),
             make_player(11, 11, alive=0), make_player(11, 1, alive=0)],
        ),
        0,
    )
    hazard = compute_hazard_map(state)
    assert offense_eval(state, hazard)[1] is True   # it IS a kill...
    assert bomb_escape_quality(state) == 0.0         # ...but we cannot escape
    assert score_action_components(state, PLACE_BOMB, hazard)["kill_bonus"] == 0.0


def test_no_kill_bonus_without_opponent():
    state = parse_obs(
        make_obs(
            empty_grid(),
            [make_player(6, 6, bombs_left=1), make_player(1, 1, alive=0),
             make_player(11, 11, alive=0), make_player(11, 1, alive=0)],
        ),
        0,
    )
    comps = score_action_components(state, PLACE_BOMB, compute_hazard_map(state))
    assert comps["kill_bonus"] == 0.0
