"""Time-expanded BFS: safe_at semantics and the post-move escape budget.

Includes a regression for Bug #1: the escape check after a move must start at
t=1, because reaching the cell already consumed one step of the danger budget.
"""

import numpy as np

from grid_helpers import make_obs, make_player
from person_a_safety.constants import INF
from person_a_safety.danger import compute_danger_map
from person_a_safety.obs import parse_obs
from person_a_safety.search import eventually_safe, has_escape_path, safe_at


def test_safe_at_only_unsafe_at_exact_explosion():
    danger = np.full((3, 3), INF, dtype=np.int32)
    danger[1, 1] = 3
    assert safe_at((1, 1), 2, danger) is True
    assert safe_at((1, 1), 3, danger) is False  # on fire exactly at t=3
    assert safe_at((1, 1), 4, danger) is True


def test_eventually_safe_after_fire_passes():
    danger = np.full((3, 3), INF, dtype=np.int32)
    danger[1, 1] = 3
    assert eventually_safe((1, 1), 2, danger) is False  # fire still ahead
    assert eventually_safe((1, 1), 4, danger) is True  # fire already passed


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
    danger = compute_danger_map(state)
    assert danger[5, 3] == 3 and danger[5, 6] >= INF

    # From t=0 there is just enough budget to reach safety.
    assert has_escape_path(state, (5, 3), danger, start_time=0) is True
    # From t=1 (already used one step to get here) the budget is gone.
    assert has_escape_path(state, (5, 3), danger, start_time=1) is False


def test_escape_exists_when_far_from_fire():
    state = _single_row_corridor_state(bomb_timer=6, self_col=8)
    danger = compute_danger_map(state)
    # col 8 is outside the radius-4 blast (cols 1..5) -> already safe.
    assert danger[5, 8] >= INF
    assert has_escape_path(state, (5, 8), danger, start_time=0) is True


def test_dead_end_has_no_escape():
    # Pocket cell (5,1) with bomb on the only neighbour exit, surrounded by walls.
    grid = np.ones((13, 13), dtype=np.int8)
    grid[5, 1] = 0
    grid[5, 2] = 0
    players = [make_player(5, 1, radius_bonus=0)] + [make_player(1, i) for i in (1, 2, 3)]
    # Bomb at the exit (5,2) timer 1, radius 1 -> floods (5,1) and (5,2) at t=1.
    obs = make_obs(grid, players, bombs=[[5, 2, 1, 0]])
    state = parse_obs(obs, agent_id=0)
    danger = compute_danger_map(state)
    assert has_escape_path(state, (5, 1), danger, start_time=0) is False
