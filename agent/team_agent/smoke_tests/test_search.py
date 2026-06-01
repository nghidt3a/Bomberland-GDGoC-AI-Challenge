"""Time-expanded BFS: safe_at semantics and the post-move escape budget.

Includes a regression for Bug #1: the escape check after a move must start at
t=1, because reaching the cell already consumed one step of the danger budget.
Also covers the per-time hazard tensor: a cell that burns twice must stay unsafe
at BOTH ticks (the old earliest-only map silently lost the later burn).
"""

import numpy as np

from grid_helpers import make_obs, make_player
from person_a_safety.danger import compute_hazard_map
from person_a_safety.obs import parse_obs
from person_a_safety.search import (
    eventually_safe,
    first_escape_action,
    has_escape_path,
    safe_at,
    safe_distances,
    safe_relative_distances,
)


def _hazard(times: dict[tuple[int, int], list[int]], shape=(11, 3, 3)) -> np.ndarray:
    """Build a hazard tensor that burns each given cell at the listed ticks."""
    hazard = np.zeros(shape, dtype=bool)
    for (r, c), ticks in times.items():
        for t in ticks:
            hazard[t, r, c] = True
    return hazard


def test_safe_at_only_unsafe_at_exact_explosion():
    hazard = _hazard({(1, 1): [3]})
    assert safe_at((1, 1), 2, hazard) is True
    assert safe_at((1, 1), 3, hazard) is False  # on fire exactly at t=3
    assert safe_at((1, 1), 4, hazard) is True


def test_eventually_safe_after_fire_passes():
    hazard = _hazard({(1, 1): [3]})
    assert eventually_safe((1, 1), 2, hazard) is False  # fire still ahead
    assert eventually_safe((1, 1), 4, hazard) is True  # fire already passed


def test_cell_that_burns_twice_is_unsafe_at_both_ticks():
    # Regression for the earliest-only danger map: cell burns at t=2 AND t=6.
    hazard = _hazard({(1, 1): [2, 6]})
    assert safe_at((1, 1), 2, hazard) is False
    assert safe_at((1, 1), 3, hazard) is True  # gap between the two burns
    assert safe_at((1, 1), 6, hazard) is False  # the SECOND burn the old map lost
    # Standing there at t=3 is NOT eventually safe: fire returns at t=6.
    assert eventually_safe((1, 1), 3, hazard) is False
    assert eventually_safe((1, 1), 7, hazard) is True


def _single_row_corridor_state(bomb_timer, self_col):
    """Row-5 corridor (cols 1..11), walls elsewhere; bomb at (5,1) radius 4."""
    grid = np.ones((13, 13), dtype=np.int8)
    grid[5, 1:12] = 0
    players = [
        make_player(5, self_col, radius_bonus=3),  # bonus 3 -> radius 4
        make_player(1, 1),
        make_player(1, 2),
        make_player(1, 3),
    ]
    obs = make_obs(grid, players, bombs=[[5, 1, bomb_timer, 0]])
    return parse_obs(obs, agent_id=0)


def test_post_move_escape_off_by_one_regression():
    # Bomb covers cols 1..5 at t=3; the only exit is col 6 (3 moves from col 3).
    state = _single_row_corridor_state(bomb_timer=3, self_col=3)
    hazard = compute_hazard_map(state)

    # From t=0 there is just enough budget to reach safety.
    assert has_escape_path(state, (5, 3), hazard, start_time=0) is True
    # From t=1 (already used one step to get here) the budget is gone.
    assert has_escape_path(state, (5, 3), hazard, start_time=1) is False


def test_escape_exists_when_far_from_fire():
    state = _single_row_corridor_state(bomb_timer=6, self_col=8)
    hazard = compute_hazard_map(state)
    # col 8 is outside the radius-4 blast (cols 1..5) -> already safe.
    assert has_escape_path(state, (5, 8), hazard, start_time=0) is True


def test_dead_end_has_no_escape():
    # Pocket cell (5,1) with bomb on the only neighbour exit, surrounded by walls.
    grid = np.ones((13, 13), dtype=np.int8)
    grid[5, 1] = 0
    grid[5, 2] = 0
    players = [make_player(5, 1, radius_bonus=0)] + [make_player(1, i) for i in (1, 2, 3)]
    # Bomb at the exit (5,2) timer 1, radius 1 -> floods (5,1) and (5,2) at t=1.
    obs = make_obs(grid, players, bombs=[[5, 2, 1, 0]])
    state = parse_obs(obs, agent_id=0)
    hazard = compute_hazard_map(state)
    assert has_escape_path(state, (5, 1), hazard, start_time=0) is False


def test_safe_relative_distances_subtract_start_time():
    state = _single_row_corridor_state(bomb_timer=6, self_col=8)
    hazard = compute_hazard_map(state)

    absolute = safe_distances(state, hazard, start=(5, 8), start_time=1)
    relative = safe_relative_distances(state, hazard, start=(5, 8), start_time=1)

    assert absolute[(5, 8)] == 1
    assert relative[(5, 8)] == 0
    assert relative[(5, 9)] == absolute[(5, 9)] - 1


def test_first_escape_action_moves_toward_nearest_safety():
    state = _single_row_corridor_state(bomb_timer=3, self_col=3)
    hazard = compute_hazard_map(state)

    assert first_escape_action(state, hazard) == 4  # DOWN moves col 3 -> col 4 in this frame.


def test_first_escape_action_returns_none_when_no_escape():
    grid = np.ones((13, 13), dtype=np.int8)
    grid[5, 1] = 0
    players = [make_player(5, 1)] + [make_player(1, i) for i in (1, 2, 3)]
    obs = make_obs(grid, players, bombs=[[5, 1, 1, 0]])
    state = parse_obs(obs, agent_id=0)
    hazard = compute_hazard_map(state)

    assert first_escape_action(state, hazard) is None
