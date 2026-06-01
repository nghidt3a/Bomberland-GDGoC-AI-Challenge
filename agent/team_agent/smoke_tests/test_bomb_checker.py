"""can_place_bomb_safely: never place a bomb we cannot escape.

Regression for Bug #2: placing a bomb consumes a turn the agent cannot move in
(it stays put while existing bombs tick once), so the escape search must start
at t=1. Otherwise the budget is over-estimated and the agent buries itself next
to its own large-radius bombs (caught by the engine harness).
"""

import numpy as np

from grid_helpers import empty_grid, make_obs, make_player
from person_a_safety.bomb import can_place_bomb_safely, copy_state_with_new_bomb_at_self
from person_a_safety.constants import BOMB_TIMER
from person_a_safety.obs import parse_obs


def _state(grid, players, bombs=None, agent_id=0):
    return parse_obs(make_obs(grid, players, bombs=bombs), agent_id=agent_id)


def four(p0):
    return [p0, make_player(1, 11), make_player(11, 11), make_player(11, 1)]


def test_simulated_bomb_is_placed_at_self():
    grid = empty_grid()
    state = _state(grid, four(make_player(6, 6)))
    simulated = copy_state_with_new_bomb_at_self(state)
    assert simulated.bombs[-1].timer == BOMB_TIMER
    assert simulated.bombs[-1].pos == (6, 6)
    assert simulated.bombs[-1].owner_id == state.agent_id


def test_placement_step_consumes_a_turn_regression():
    # Row-9 corridor (cols 1..11), walls above/below so escape is 1-D.
    # An enemy bomb at (9,1) radius 4 floods cols 1..5 at t=3. Standing at col 3,
    # placing a bomb costs the current turn (no move) -> only 2 real moves left,
    # not enough to clear col 5. With the old t=0 budget it looked escapable.
    grid = np.ones((13, 13), dtype=np.int8)
    grid[9, 1:12] = 0
    players = [
        make_player(9, 3, bombs_left=1, radius_bonus=0),  # our small-radius bomb
        make_player(1, 11, radius_bonus=3),  # enemy owns the radius-4 bomb
        make_player(11, 11),
        make_player(11, 1),
    ]
    state = _state(grid, players, bombs=[[9, 1, 3, 1]])
    assert can_place_bomb_safely(state) is False


def test_cannot_place_when_current_cell_burns_next_step():
    grid = empty_grid()
    players = four(make_player(5, 3, bombs_left=1, radius_bonus=4))
    state = _state(grid, players, bombs=[[5, 5, 1, 0]])

    assert can_place_bomb_safely(state) is False


def test_open_area_can_place_safely():
    grid = empty_grid()
    state = _state(grid, four(make_player(6, 6, bombs_left=1)))
    assert can_place_bomb_safely(state) is True


def test_dead_end_cannot_place():
    # Pocket of two cells (5,1)-(5,2); a bomb here floods both with no exit.
    grid = np.ones((13, 13), dtype=np.int8)
    grid[5, 1] = 0
    grid[5, 2] = 0
    players = four(make_player(5, 1, bombs_left=1))
    state = _state(grid, players)
    assert can_place_bomb_safely(state) is False


def test_no_bombs_left_cannot_place():
    grid = empty_grid()
    state = _state(grid, four(make_player(6, 6, bombs_left=0)))
    assert can_place_bomb_safely(state) is False


def test_existing_bomb_on_cell_cannot_place():
    grid = empty_grid()
    state = _state(grid, four(make_player(6, 6, bombs_left=1)), bombs=[[6, 6, 5, 0]])
    assert can_place_bomb_safely(state) is False
