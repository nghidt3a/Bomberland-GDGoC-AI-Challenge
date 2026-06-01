import numpy as np

from grid_helpers import empty_grid, make_obs, make_player
from person_a_safety.constants import BOX, ITEM_CAPACITY, ITEM_RADIUS, WALL
from person_a_safety.danger import compute_danger_map
from person_a_safety.features import FEATURE_CHANNELS, encode_features
from person_a_safety.obs import parse_obs


def players():
    return [
        make_player(5, 5, alive=1, bombs_left=1, radius_bonus=1),
        make_player(7, 5, alive=1, bombs_left=1, radius_bonus=0),
        make_player(1, 1, alive=0, bombs_left=1, radius_bonus=0),
        make_player(9, 9, alive=1, bombs_left=1, radius_bonus=2),
    ]


def test_feature_channels_shape_and_dtype():
    grid = empty_grid()
    grid[3, 3] = BOX
    grid[4, 4] = ITEM_RADIUS
    grid[6, 6] = ITEM_CAPACITY
    obs = make_obs(grid, players(), bombs=[[5, 7, 4, 0], [8, 9, 6, 3]])
    state = parse_obs(obs, agent_id=0)

    features = encode_features(state)

    assert features.shape == (len(FEATURE_CHANNELS), 13, 13)
    assert features.dtype == np.float32


def test_feature_channels_mark_core_entities():
    grid = empty_grid()
    grid[0, 0] = WALL
    grid[3, 3] = BOX
    grid[4, 4] = ITEM_RADIUS
    grid[6, 6] = ITEM_CAPACITY
    obs = make_obs(grid, players(), bombs=[[5, 7, 4, 0]])
    state = parse_obs(obs, agent_id=0)
    features = encode_features(state, compute_danger_map(state))
    channel = {name: idx for idx, name in enumerate(FEATURE_CHANNELS)}

    assert features[channel["wall"], 0, 0] == 1.0
    assert features[channel["box"], 3, 3] == 1.0
    assert features[channel["item_radius"], 4, 4] == 1.0
    assert features[channel["item_capacity"], 6, 6] == 1.0
    assert features[channel["self"], 5, 5] == 1.0
    assert features[channel["opponents"], 7, 5] == 1.0
    assert features[channel["opponents"], 1, 1] == 0.0
    assert features[channel["bombs"], 5, 7] == 1.0
    assert 0.0 < features[channel["bomb_timer_norm"], 5, 7] <= 1.0


def test_dead_agent_has_no_safe_reachable_features():
    grid = empty_grid()
    dead_players = players()
    dead_players[0][2] = 0
    state = parse_obs(make_obs(grid, dead_players), agent_id=0)
    features = encode_features(state)
    channel = {name: idx for idx, name in enumerate(FEATURE_CHANNELS)}

    assert features[channel["self"], 5, 5] == 1.0
    assert features[channel["safe_reachable_cells"]].sum() == 0.0


def test_feature_encoder_supports_all_agent_ids():
    grid = empty_grid()
    obs = make_obs(grid, players(), bombs=[])

    for agent_id in range(4):
        state = parse_obs(obs, agent_id=agent_id)
        features = encode_features(state)
        assert features.shape == (len(FEATURE_CHANNELS), 13, 13)
