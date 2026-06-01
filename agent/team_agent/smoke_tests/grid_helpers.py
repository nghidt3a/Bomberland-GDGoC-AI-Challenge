"""Small builders for constructing engine-shaped observations in tests.

Observation contract (mirrors engine/game.py::_get_obs):
  - map:     int grid, 0 grass / 1 wall / 2 box / 3 item_radius / 4 item_capacity
  - players: rows of [row, col, alive, bombs_left, radius_bonus]
  - bombs:   rows of [row, col, timer, owner_id]
"""

import numpy as np

from person_a_safety.constants import GRASS, WALL


def empty_grid(size: int = 13) -> np.ndarray:
    """All-grass board ringed by the wall border the engine always has."""
    grid = np.full((size, size), GRASS, dtype=np.int8)
    grid[0, :] = WALL
    grid[-1, :] = WALL
    grid[:, 0] = WALL
    grid[:, -1] = WALL
    return grid


def make_player(row, col, alive=1, bombs_left=1, radius_bonus=0):
    return [int(row), int(col), int(alive), int(bombs_left), int(radius_bonus)]


def make_obs(grid, players, bombs=None):
    """Assemble an obs dict. ``bombs`` is a list of [row, col, timer, owner_id]."""
    players_arr = np.array(players, dtype=np.int8)
    if bombs:
        bombs_arr = np.array(bombs, dtype=np.int8)
    else:
        bombs_arr = np.zeros((0, 4), dtype=np.int8)
    return {"map": np.asarray(grid), "players": players_arr, "bombs": bombs_arr}
