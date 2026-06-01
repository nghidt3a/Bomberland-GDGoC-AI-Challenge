"""Danger map: blast shape, radius source, and chain-reaction timing."""

import numpy as np

from grid_helpers import empty_grid, make_obs, make_player
from person_a_safety.constants import BOX, ITEM_RADIUS, WALL
from person_a_safety.danger import blast_cells, compute_danger_map
from person_a_safety.obs import parse_obs


def _state(grid, bombs, radius_bonus=0):
    # Single owner (player 0) whose radius_bonus drives every bomb's radius.
    players = [
        make_player(5, 5, radius_bonus=radius_bonus),
        make_player(1, 11),
        make_player(11, 11),
        make_player(11, 1),
    ]
    return parse_obs(make_obs(grid, players, bombs=bombs), agent_id=0)


# --- blast_cells geometry -------------------------------------------------

def test_blast_wall_blocks_and_is_excluded():
    grid = empty_grid()
    grid[5, 7] = WALL
    state = _state(grid, bombs=[[5, 5, 3, 0]])
    cells = blast_cells((5, 5), 3, state.walls, state.boxes)
    assert (5, 6) in cells
    assert (5, 7) not in cells  # wall itself not hit
    assert (5, 8) not in cells  # blocked beyond wall


def test_blast_box_is_hit_then_blocks():
    grid = empty_grid()
    grid[5, 7] = BOX
    state = _state(grid, bombs=[[5, 5, 3, 0]])
    cells = blast_cells((5, 5), 3, state.walls, state.boxes)
    assert (5, 7) in cells  # box tile is destroyed (hit)
    assert (5, 8) not in cells  # but blocks further travel


def test_blast_item_and_grass_do_not_block():
    grid = empty_grid()
    grid[5, 6] = ITEM_RADIUS
    state = _state(grid, bombs=[[5, 5, 3, 0]])
    cells = blast_cells((5, 5), 3, state.walls, state.boxes)
    assert {(5, 6), (5, 7), (5, 8)} <= cells


def test_radius_comes_from_owner_bonus():
    grid = empty_grid()
    # owner bonus 2 -> radius 3; reaches exactly 3 tiles, not 4.
    state = _state(grid, bombs=[[5, 5, 3, 0]], radius_bonus=2)
    danger = compute_danger_map(state)
    assert danger[5, 8] == 3  # distance 3 hit
    assert danger[5, 9] > 1000  # distance 4 safe


# --- chain reaction timing ------------------------------------------------

def test_chain_two_bombs_explode_at_earliest():
    grid = empty_grid()
    # A timer 2 at (5,5), B timer 6 at (5,7); radius 2 so A reaches B.
    bombs = [[5, 5, 2, 0], [5, 7, 6, 0]]
    state = _state(grid, bombs=bombs, radius_bonus=1)
    danger = compute_danger_map(state)
    assert danger[5, 7] == 2  # B dragged forward to A's time
    assert danger[5, 9] == 2  # B's own blast also fires at t=2


def test_chain_three_bombs_propagates():
    grid = empty_grid()
    bombs = [[5, 5, 2, 0], [5, 7, 6, 0], [5, 9, 6, 0]]
    state = _state(grid, bombs=bombs, radius_bonus=1)
    danger = compute_danger_map(state)
    assert danger[5, 7] == 2
    assert danger[5, 9] == 2
    assert danger[5, 11] == 2  # C's blast fires at t=2 too


def test_chain_blocked_by_wall_does_not_trigger():
    grid = empty_grid()
    grid[5, 6] = WALL  # wall between A and B
    bombs = [[5, 5, 2, 0], [5, 7, 6, 0]]
    state = _state(grid, bombs=bombs, radius_bonus=1)
    danger = compute_danger_map(state)
    # A cannot reach B: B keeps its own timer.
    assert danger[5, 7] == 6


def test_no_bombs_is_all_safe():
    grid = empty_grid()
    state = _state(grid, bombs=[])
    danger = compute_danger_map(state)
    assert np.all(danger > 1000)
