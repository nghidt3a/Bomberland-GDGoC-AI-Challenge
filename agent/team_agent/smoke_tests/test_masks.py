"""legal_actions / safe_actions contract handed to Person B."""

from grid_helpers import empty_grid, make_obs, make_player
from person_a_safety.constants import BOX, DOWN, LEFT, PLACE_BOMB, RIGHT, STOP, UP
from person_a_safety.danger import compute_danger_map
from person_a_safety.masks import legal_actions, safe_actions
from person_a_safety.obs import parse_obs


def _state(grid, players, bombs=None, agent_id=0):
    return parse_obs(make_obs(grid, players, bombs=bombs), agent_id=agent_id)


def four(p0):
    return [p0, make_player(1, 11), make_player(11, 11), make_player(11, 1)]


def test_legal_blocks_walls_allows_grass():
    grid = empty_grid()
    state = _state(grid, four(make_player(1, 1)))  # cornered by the wall ring
    legal = legal_actions(state)
    assert legal[STOP]
    assert not legal[LEFT]  # (0,1) wall
    assert not legal[UP]    # (1,0) wall
    assert legal[RIGHT]     # (2,1) grass
    assert legal[DOWN]      # (1,2) grass


def test_legal_blocks_box():
    grid = empty_grid()
    grid[2, 1] = BOX
    state = _state(grid, four(make_player(1, 1)))
    assert not legal_actions(state)[RIGHT]  # (2,1) is a box


def test_place_bomb_legality():
    grid = empty_grid()
    # No bombs left -> cannot place.
    s0 = _state(grid, four(make_player(6, 6, bombs_left=0)))
    assert not legal_actions(s0)[PLACE_BOMB]
    # Standing on an existing bomb -> cannot place a second one here.
    s1 = _state(grid, four(make_player(6, 6, bombs_left=1)), bombs=[[6, 6, 5, 0]])
    assert not legal_actions(s1)[PLACE_BOMB]
    # Bombs available, empty cell -> legal.
    s2 = _state(grid, four(make_player(6, 6, bombs_left=1)))
    assert legal_actions(s2)[PLACE_BOMB]


def test_can_leave_own_bomb_cell():
    grid = empty_grid()
    state = _state(grid, four(make_player(6, 6, bombs_left=0)), bombs=[[6, 6, 5, 0]])
    legal = legal_actions(state)
    # The bomb sits on our own cell; we must still be allowed to step off it.
    assert legal[LEFT] and legal[RIGHT] and legal[UP] and legal[DOWN]


def test_safe_actions_filter_move_into_fire():
    grid = empty_grid()
    # Bomb at (6,9) timer 1, owner radius bonus 1 -> radius 2 -> floods (6,7).
    p0 = make_player(6, 6, bombs_left=1, radius_bonus=1)
    state = _state(grid, four(p0), bombs=[[6, 9, 1, 0]])
    danger = compute_danger_map(state)
    assert danger[6, 7] == 1  # explodes next step
    mask = safe_actions(state, danger)
    assert not mask[DOWN]  # DOWN -> (6,7) is on fire at t=1
    assert mask[UP] or mask[LEFT] or mask[RIGHT]  # escape directions remain
