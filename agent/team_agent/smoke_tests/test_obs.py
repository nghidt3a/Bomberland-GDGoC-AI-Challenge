"""parse_obs: faithful translation of the raw engine observation."""

import numpy as np

from grid_helpers import empty_grid, make_obs, make_player
from person_a_safety.constants import BOX, ITEM_CAPACITY, ITEM_RADIUS
from person_a_safety.obs import parse_obs


def four_players():
    return [
        make_player(1, 1, bombs_left=1, radius_bonus=0),
        make_player(11, 11, bombs_left=2, radius_bonus=1),
        make_player(1, 11, bombs_left=1, radius_bonus=2),
        make_player(11, 1, bombs_left=0, radius_bonus=3),
    ]


def test_each_agent_id_parses_self():
    grid = empty_grid()
    obs = make_obs(grid, four_players())
    expected_pos = [(1, 1), (11, 11), (1, 11), (11, 1)]
    for agent_id, pos in enumerate(expected_pos):
        state = parse_obs(obs, agent_id)
        assert state.self_pos == pos
        assert state.self_alive is True
        # self_radius = 1 + radius_bonus
        assert state.self_radius == 1 + agent_id  # bonuses are 0,1,2,3


def test_opponents_exclude_self_and_dead():
    grid = empty_grid()
    players = four_players()
    players[2][2] = 0  # mark player 2 dead
    obs = make_obs(grid, players)
    state = parse_obs(obs, agent_id=0)
    assert (1, 1) not in state.opponents  # self excluded
    assert (1, 11) not in state.opponents  # dead excluded
    assert (11, 11) in state.opponents and (11, 1) in state.opponents


def test_dead_self_is_reported_not_alive():
    grid = empty_grid()
    players = four_players()
    players[0][2] = 0
    state = parse_obs(make_obs(grid, players), agent_id=0)
    assert state.self_alive is False


def test_bombs_empty_one_and_many():
    grid = empty_grid()
    players = four_players()

    s0 = parse_obs(make_obs(grid, players, bombs=[]), agent_id=0)
    assert s0.bombs == [] and s0.bomb_positions == set()

    s1 = parse_obs(make_obs(grid, players, bombs=[[5, 5, 3, 0]]), agent_id=0)
    assert len(s1.bombs) == 1
    assert s1.bombs[0].pos == (5, 5) and s1.bombs[0].timer == 3
    assert s1.bombs[0].owner_id == 0 and (5, 5) in s1.bomb_positions

    s2 = parse_obs(
        make_obs(grid, players, bombs=[[5, 5, 3, 0], [6, 6, 7, 1]]), agent_id=0
    )
    assert len(s2.bombs) == 2 and {(5, 5), (6, 6)} <= s2.bomb_positions


def test_tile_masks_match_grid():
    grid = empty_grid()
    grid[5, 7] = BOX
    grid[3, 5] = ITEM_RADIUS
    grid[8, 8] = ITEM_CAPACITY
    state = parse_obs(make_obs(grid, four_players()), agent_id=0)
    assert state.boxes[5, 7] and not state.boxes[3, 5]
    assert state.item_radius[3, 5] and state.item_capacity[8, 8]
    assert state.walls[0, 0]  # border ring is wall


def test_bombs_left_parsed():
    grid = empty_grid()
    players = four_players()
    assert parse_obs(make_obs(grid, players), 3).self_bombs_left == 0
    assert parse_obs(make_obs(grid, players), 1).self_bombs_left == 2


def test_out_of_range_agent_id_is_safe():
    grid = empty_grid()
    state = parse_obs(make_obs(grid, four_players()), agent_id=99)
    assert state.self_alive is False
    assert state.self_bombs_left == 0
