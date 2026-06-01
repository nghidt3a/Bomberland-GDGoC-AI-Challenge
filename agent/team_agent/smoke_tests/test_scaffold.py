import sys
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
TEAM_DIR = ROOT / "agent" / "team_agent"
if str(TEAM_DIR) not in sys.path:
    sys.path.insert(0, str(TEAM_DIR))

from person_a_safety.constants import BOX, GRASS, ITEM_RADIUS, WALL
from person_a_safety.danger import blast_cells, compute_danger_map, compute_hazard_map
from person_a_safety.masks import safe_actions
from person_a_safety.obs import parse_obs


def make_obs():
    grid = np.full((13, 13), GRASS, dtype=np.int8)
    grid[0, :] = WALL
    grid[-1, :] = WALL
    grid[:, 0] = WALL
    grid[:, -1] = WALL
    grid[5, 7] = BOX
    grid[3, 5] = ITEM_RADIUS
    players = np.array(
        [
            [5, 5, 1, 1, 1],
            [1, 1, 1, 1, 0],
            [1, 11, 1, 1, 0],
            [11, 1, 1, 1, 0],
        ],
        dtype=np.int8,
    )
    bombs = np.array([[5, 5, 3, 0]], dtype=np.int8)
    return {"map": grid, "players": players, "bombs": bombs}


def test_parse_obs_and_danger_map():
    state = parse_obs(make_obs(), agent_id=0)
    danger = compute_danger_map(state)

    assert state.self_pos == (5, 5)
    assert state.self_radius == 2
    assert danger[5, 5] == 3
    assert danger[5, 7] == 3
    assert danger[5, 8] > 1000


def test_blast_cells_stop_at_box():
    state = parse_obs(make_obs(), agent_id=0)
    cells = blast_cells((5, 5), 4, state.walls, state.boxes)

    assert (5, 7) in cells
    assert (5, 8) not in cells


def test_safe_actions_shape():
    state = parse_obs(make_obs(), agent_id=0)
    mask = safe_actions(state, compute_hazard_map(state))

    assert mask.shape == (6,)
    assert mask.dtype == bool


def test_agent_act_returns_valid_action():
    from competition.evaluation.runtime_guard import load_agent_instance

    agent = load_agent_instance(str(TEAM_DIR / "agent.py"), agent_id=0)
    action = agent.act(make_obs())

    assert isinstance(action, int)
    assert 0 <= action <= 5
