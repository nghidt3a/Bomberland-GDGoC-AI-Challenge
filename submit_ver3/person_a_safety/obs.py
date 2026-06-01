from typing import Any

import numpy as np

from .constants import BOX, GRASS, ITEM_CAPACITY, ITEM_RADIUS, WALL
from .state import BombInfo, GameState


def parse_obs(obs: dict[str, Any], agent_id: int) -> GameState:
    """Normalize raw observation into the shared internal state."""

    grid = np.asarray(obs.get("map"), dtype=np.int16)
    players = _normalize_players(obs.get("players"))
    bombs_arr = _normalize_bombs(obs.get("bombs"))

    bombs = [
        BombInfo(pos=(int(row), int(col)), timer=int(timer), owner_id=int(owner_id))
        for row, col, timer, owner_id in bombs_arr
    ]
    bomb_positions = {bomb.pos for bomb in bombs}

    agent_id = int(agent_id)
    if 0 <= agent_id < len(players):
        me = players[agent_id]
        self_pos = (int(me[0]), int(me[1]))
        self_alive = bool(int(me[2]))
        self_bombs_left = int(me[3])
        self_radius = 1 + int(me[4])
    else:
        self_pos = (0, 0)
        self_alive = False
        self_bombs_left = 0
        self_radius = 1

    opponents = []
    alive_players = []
    for idx, player in enumerate(players):
        if int(player[2]) != 1:
            continue
        pos = (int(player[0]), int(player[1]))
        alive_players.append(pos)
        if idx != agent_id:
            opponents.append(pos)

    return GameState(
        grid=grid,
        players=players,
        agent_id=agent_id,
        bombs=bombs,
        walls=grid == WALL,
        boxes=grid == BOX,
        item_radius=grid == ITEM_RADIUS,
        item_capacity=grid == ITEM_CAPACITY,
        bomb_positions=bomb_positions,
        self_pos=self_pos,
        self_alive=self_alive,
        self_bombs_left=self_bombs_left,
        self_radius=max(1, self_radius),
        opponents=opponents,
        alive_players=alive_players,
    )


def _normalize_players(raw_players: Any) -> np.ndarray:
    arr = np.asarray(raw_players, dtype=np.int16)
    if arr.size == 0:
        return np.zeros((0, 5), dtype=np.int16)
    return arr.reshape((-1, 5))


def _normalize_bombs(raw_bombs: Any) -> np.ndarray:
    arr = np.asarray(raw_bombs, dtype=np.int16)
    if arr.size == 0:
        return np.zeros((0, 4), dtype=np.int16)
    if arr.ndim == 1:
        arr = arr.reshape((1, -1))
    if arr.shape[1] < 4:
        padded = np.zeros((arr.shape[0], 4), dtype=np.int16)
        padded[:, : arr.shape[1]] = arr
        return padded
    return arr[:, :4]
