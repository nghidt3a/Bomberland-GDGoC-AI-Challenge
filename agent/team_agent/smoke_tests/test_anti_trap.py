"""Anti-trap penalties keep the agent out of cells an opponent can seal.

These are SOFT scoring signals (the safe mask is still the hard gate): a cheap
geometric ``confinement_penalty`` that always runs, and a simulated
``enemy_bomb_escape_penalty`` that places a hypothetical enemy bomb and checks we
would still have an escape. Both only fire when we are currently safe, so they
never block a needed escape.
"""

import time

import numpy as np

from grid_helpers import empty_grid, make_obs, make_player
from person_a_safety.constants import GRASS, PLACE_BOMB, STOP
from person_a_safety.danger import compute_hazard_map
from person_a_safety.obs import parse_obs
from person_b_strategy.scoring import (
    ScoreWeights,
    confinement_penalty,
    enemy_bomb_escape_penalty,
    score_action_components,
)


def _corridor(self_cell, enemy_cell, cols, enemy_bonus=0, self_bonus=0):
    """All-wall board with a 1-wide horizontal corridor on row 5 over ``cols``."""
    grid = np.ones((13, 13), dtype=np.int8)
    grid[5, cols] = GRASS
    players = [
        make_player(*self_cell, radius_bonus=self_bonus),
        make_player(*enemy_cell, radius_bonus=enemy_bonus),
        make_player(11, 11, alive=0),
        make_player(11, 1, alive=0),
    ]
    return parse_obs(make_obs(grid, players), 0)


def test_confinement_penalizes_pocket_near_enemy():
    state = _corridor((5, 3), (5, 4), slice(1, 6))
    weights = ScoreWeights()

    # (5,1) is a dead-end pocket (only exit back to (5,2)); enemy is 3 away.
    assert confinement_penalty(state, (5, 1), weights, turn_index=200) < 0.0


def test_confinement_ignores_open_ground():
    state = parse_obs(
        make_obs(
            empty_grid(),
            [make_player(6, 6), make_player(6, 9), make_player(11, 11, alive=0), make_player(11, 1, alive=0)],
        ),
        0,
    )
    assert confinement_penalty(state, (6, 7), ScoreWeights(), turn_index=200) == 0.0


def test_confinement_ignores_distant_enemy():
    state = _corridor((5, 3), (5, 5), slice(1, 6))  # enemy 4 away from the pocket (5,1)
    assert confinement_penalty(state, (5, 1), ScoreWeights(), turn_index=200) == 0.0


def test_enemy_bomb_penalty_flags_sealed_corridor():
    # Enemy with radius 5 standing at (5,4) can flood the whole corridor; stepping
    # into (5,1) leaves no cell that survives the blast -> a trap.
    state = _corridor((5, 2), (5, 4), slice(1, 7), enemy_bonus=4)
    assert enemy_bomb_escape_penalty(state, (5, 1), ScoreWeights(), turn_index=200) < 0.0


def test_enemy_bomb_penalty_zero_in_open_ground():
    state = parse_obs(
        make_obs(
            empty_grid(),
            [make_player(6, 6), make_player(6, 10), make_player(11, 11, alive=0), make_player(11, 1, alive=0)],
        ),
        0,
    )
    assert enemy_bomb_escape_penalty(state, (6, 7), ScoreWeights(), turn_index=200) == 0.0


def test_enemy_bomb_penalty_skipped_past_deadline():
    state = _corridor((5, 2), (5, 4), slice(1, 7), enemy_bonus=4)
    past = time.perf_counter() - 1.0
    assert enemy_bomb_escape_penalty(state, (5, 1), ScoreWeights(), turn_index=200, deadline=past) == 0.0


def test_components_apply_confinement_only_for_moves_when_safe():
    state = _corridor((5, 2), (5, 4), slice(1, 6))
    hazard = compute_hazard_map(state)

    # The corridor runs along the column axis, so UP (col-1) moves (5,2)->(5,1),
    # the dead-end pocket; that move earns a confinement penalty...
    from person_a_safety.constants import UP
    from person_a_safety.masks import action_destination

    assert action_destination(state, UP) == (5, 1)
    move_comps = score_action_components(state, UP, hazard)
    assert move_comps["confinement_penalty"] < 0.0

    # ...but PLACE_BOMB never gets a confinement penalty (it does not move us).
    bomb_comps = score_action_components(state, PLACE_BOMB, hazard)
    assert bomb_comps["confinement_penalty"] == 0.0
