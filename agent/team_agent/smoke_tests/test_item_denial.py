"""Item denial (technique 04): deny a high-value power-up the enemy reaches first,
either by bombing the item cell or stomping it same-tick. Never fires for items we
win (``en_d >= my_d``), so it does not double-count with ``item_move_score``.
"""

from grid_helpers import empty_grid, make_obs, make_player
from person_a_safety.bomb import copy_state_with_new_bomb_at_self
from person_a_safety.constants import DOWN, ITEM_CAPACITY, ITEM_RADIUS, PLACE_BOMB
from person_a_safety.danger import compute_hazard_map
from person_a_safety.obs import parse_obs
from person_b_strategy.scoring import item_denial_score, score_action_components


def _state(item_cell, item_kind, self_cell, enemy_cell, bombs_left=1, radius_bonus=2):
    grid = empty_grid()
    grid[item_cell] = item_kind
    players = [
        make_player(*self_cell, bombs_left=bombs_left, radius_bonus=radius_bonus),
        make_player(*enemy_cell),
        make_player(11, 11, alive=0),
        make_player(11, 1, alive=0),
    ]
    return parse_obs(make_obs(grid, players), 0)


def test_deny_bomb_when_enemy_wins_item():
    # item (5,7); enemy adjacent (en_d=1); we are 2 away -> enemy wins -> deny.
    state = _state((5, 7), ITEM_RADIUS, (5, 5), (5, 8))
    sim_hazard = compute_hazard_map(copy_state_with_new_bomb_at_self(state))  # bomb covers (5,7)
    assert item_denial_score(state, PLACE_BOMB, state.self_pos, {(5, 7): 2}, sim_hazard) > 0.0


def test_no_deny_when_we_win_item():
    state = _state((5, 7), ITEM_RADIUS, (5, 6), (5, 11))
    sim_hazard = compute_hazard_map(copy_state_with_new_bomb_at_self(state))
    assert item_denial_score(state, PLACE_BOMB, state.self_pos, {(5, 7): 1}, sim_hazard) == 0.0


def test_deny_stomp_same_tick():
    # Moving onto the item while an enemy is adjacent destroys it (>=2 occupants).
    state = _state((5, 7), ITEM_CAPACITY, (5, 5), (5, 8))
    assert item_denial_score(state, DOWN, (5, 7), {(5, 7): 2}, None) > 0.0


def test_deny_bomb_waives_useless_penalty():
    # A bomb that denies an enemy item must not be dismissed as useless.
    state = _state((5, 7), ITEM_RADIUS, (5, 5), (5, 8))
    comps = score_action_components(state, PLACE_BOMB, compute_hazard_map(state))
    assert comps["deny_bonus"] > 0.0
    assert comps["useless_bomb_penalty"] == 0.0
