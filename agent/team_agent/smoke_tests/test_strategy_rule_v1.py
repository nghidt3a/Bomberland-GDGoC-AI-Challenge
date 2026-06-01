import sys
from math import inf
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
TEAM_DIR = ROOT / "agent" / "team_agent"
if str(TEAM_DIR) not in sys.path:
    sys.path.insert(0, str(TEAM_DIR))

from person_a_safety.constants import (
    BOX,
    GRASS,
    ITEM_CAPACITY,
    ITEM_RADIUS,
    PLACE_BOMB,
    RIGHT,
    STOP,
    WALL,
)
from person_a_safety.danger import compute_hazard_map
from person_a_safety.obs import parse_obs
from person_b_strategy.loop_tracker import AntiLoopTracker
from person_b_strategy.scoring import (
    bomb_escape_quality,
    box_gain,
    box_move_score,
    farm_targets,
    item_value,
    phase_profile,
    score_action_components,
    score_actions,
)


def make_grid():
    grid = np.full((13, 13), GRASS, dtype=np.int8)
    grid[0, :] = WALL
    grid[-1, :] = WALL
    grid[:, 0] = WALL
    grid[:, -1] = WALL
    return grid


def make_state(grid=None, self_pos=(5, 5), bombs_left=1, radius_bonus=2, opponents=None):
    grid = make_grid() if grid is None else grid
    players = np.array(
        [
            [self_pos[0], self_pos[1], 1, bombs_left, radius_bonus],
            [1, 1, 0, 0, 0],
            [1, 11, 0, 0, 0],
            [11, 1, 0, 0, 0],
        ],
        dtype=np.int8,
    )
    for idx, pos in enumerate(opponents or [], start=1):
        players[idx] = [pos[0], pos[1], 1, 1, 0]
    return parse_obs({"map": grid, "players": players, "bombs": np.zeros((0, 4), dtype=np.int8)}, 0)


def test_score_actions_never_scores_unsafe_action():
    state = make_state()
    hazard = compute_hazard_map(state)
    safe_mask = np.zeros(6, dtype=bool)
    safe_mask[RIGHT] = True

    scores = score_actions(state, safe_mask, hazard)

    assert scores[RIGHT] > -inf
    assert all(score == -inf for action, score in scores.items() if action != RIGHT)


def test_box_gain_stops_at_first_box_and_wall():
    grid = make_grid()
    grid[5, 6] = BOX
    grid[5, 7] = BOX
    grid[6, 5] = BOX
    grid[5, 4] = WALL
    grid[5, 3] = BOX
    state = make_state(grid=grid, radius_bonus=4)

    assert box_gain(state, (5, 5)) == 2


def test_farm_targets_use_gain_over_safe_distance():
    grid = make_grid()
    grid[3, 4] = BOX
    grid[7, 8] = BOX
    grid[7, 6] = BOX
    grid[8, 7] = BOX
    grid[6, 7] = BOX
    state = make_state(grid=grid, self_pos=(1, 1), radius_bonus=4)
    distances = {(1, 1): 0, (3, 3): 1, (7, 7): 3}

    targets = farm_targets(state, distances)

    assert targets[0].cell == (7, 7)
    assert targets[0].gain == 4


def test_item_value_tracks_radius_and_capacity_needs():
    grid = make_grid()
    grid[5, 6] = ITEM_RADIUS
    grid[6, 5] = ITEM_CAPACITY

    low_radius = make_state(grid=grid, bombs_left=3, radius_bonus=0)
    assert item_value(low_radius, (5, 6)) > item_value(low_radius, (6, 5))

    low_capacity = make_state(grid=grid, bombs_left=1, radius_bonus=4)
    assert item_value(low_capacity, (6, 5)) > item_value(low_capacity, (5, 6))


def test_useless_bomb_is_penalized():
    state = make_state()
    hazard = compute_hazard_map(state)

    components = score_action_components(state, PLACE_BOMB, hazard)

    assert components["box_bomb"] == 0
    assert components["pressure"] == 0
    assert components["bomb_escape_quality"] == 0
    assert components["useless_bomb_penalty"] < 0


def test_stop_not_rewarded_as_farm():
    # Standing next to boxes whose blast our radius would clear must NOT credit
    # STOP with box-farming value; only PLACE_BOMB destroys boxes.
    grid = make_grid()
    grid[5, 6] = BOX
    grid[5, 7] = BOX
    state = make_state(grid=grid, self_pos=(5, 5), radius_bonus=4)

    assert box_gain(state, (5, 5)) > 0  # the cell's blast does cover boxes
    assert box_move_score(state, STOP, (5, 5), (), {}, {}) == 0.0


def test_bomb_escape_quality_requires_permanent_escape_cell():
    grid = np.ones((13, 13), dtype=np.int8)
    grid[5, 1:5] = GRASS
    state = make_state(grid=grid, self_pos=(5, 2), radius_bonus=4)

    assert bomb_escape_quality(state) == 0.0


def test_loop_tracker_penalizes_stop_and_abab_return():
    tracker = AntiLoopTracker()
    tracker.update((5, 5), 0)
    tracker.update((5, 6), 1)
    tracker.update((5, 5), 2)

    assert tracker.action_penalty((5, 5), 0) >= 7.0
    assert tracker.action_penalty((5, 6), 1) >= 8.0


def test_phase_profile_changes_weights_by_turn():
    early = phase_profile(0)
    mid = phase_profile(200)
    late = phase_profile(400)

    assert early.name == "early"
    assert mid.name == "mid"
    assert late.name in {"late_leading", "late_chasing"}
    assert early.weights.pressure < mid.weights.pressure
