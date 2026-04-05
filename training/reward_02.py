"""ICEC 2019 Bomberman-style rewards (Goulart et al., Table 1).

Scaled to this engine's observations. Kill credit is approximate: the env does
not attribute deaths to a specific bomb owner, so we use +1.0 per net enemy
death while the learner remains alive (same pragmatic choice as reward.py).

Reference: Learning How to Play Bomberman with Deep RL and IL (hal-03652029).
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Tuple

import numpy as np

parent_dir = Path(__file__).resolve().parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from engine import Map

from training.reward import (
    _any_bombs,
    _blast_status_at,
    _bomb_radius_from_obs,
    _enemy_alive_count,
    _explosion_tiles_for_bomb,
    _manhattan_to_nearest_alive_enemy,
    _parse_bomb_row,
)

# Table 1 (paper) — numeric values as published
R_AGENT_DEATH = -0.5
R_ENEMY_DEATH = 1.0
R_LAST_ALIVE = 1.0
R_BLOCK_DESTROYED = 0.1
R_CLOSEST_SO_FAR = 0.1
R_CLOSER_STEP = 0.002
R_FARTHER_STEP = -0.002
R_TIME_STEP = -0.01
R_IN_BLAST = -0.000666
R_SAFE_NEAR_BOMB = 0.002

# Manhattan distance to nearest bomb center to count as "bomb nearby" when safe
SAFE_NEAR_BOMB_RADIUS = 4


@dataclass
class EpisodeRewardState:
    """Mutable per-episode state for closest-enemy-so-far shaping."""

    best_dist: Optional[float] = None

    def reset(self) -> None:
        self.best_dist = None


def _box_count(obs) -> int:
    return int(np.sum(obs["map"] == Map.BOX))


def _min_manhattan_to_bomb_center(obs, x: int, y: int) -> Optional[int]:
    bombs = obs["bombs"]
    if bombs is None or np.asarray(bombs).size == 0:
        return None
    arr = np.asarray(bombs)
    if arr.ndim == 1:
        arr = arr.reshape(1, -1)
    best = None
    for i in range(arr.shape[0]):
        parsed = _parse_bomb_row(arr[i])
        if parsed is None:
            continue
        bx, by, _, _ = parsed
        d = abs(int(x) - int(bx)) + abs(int(y) - int(by))
        best = d if best is None else min(best, d)
    return best


def compute_reward_icec(
    prev_obs,
    curr_obs,
    agent_id: int,
    episode_state: EpisodeRewardState,
) -> Tuple[float, EpisodeRewardState]:
    """Return (reward, episode_state). Mutates ``episode_state`` in place."""
    if prev_obs is None:
        return 0.0, episode_state

    prev_players = prev_obs["players"]
    curr_players = curr_obs["players"]
    prev_alive = int(prev_players[agent_id][2])
    curr_alive = int(curr_players[agent_id][2])

    if prev_alive == 1 and curr_alive == 0:
        return float(R_AGENT_DEATH), episode_state

    reward = 0.0

    prev_enemies_alive = _enemy_alive_count(prev_players, agent_id)
    curr_enemies_alive = _enemy_alive_count(curr_players, agent_id)

    if curr_alive == 1 and curr_enemies_alive < prev_enemies_alive:
        reward += R_ENEMY_DEATH * float(prev_enemies_alive - curr_enemies_alive)
    if (
        curr_alive == 1
        and curr_enemies_alive == 0
        and prev_enemies_alive > 0
    ):
        reward += R_LAST_ALIVE

    prev_boxes = _box_count(prev_obs)
    curr_boxes = _box_count(curr_obs)
    if curr_boxes < prev_boxes:
        reward += R_BLOCK_DESTROYED * float(prev_boxes - curr_boxes)

    reward += R_TIME_STEP

    prev_x = int(prev_players[agent_id][0])
    prev_y = int(prev_players[agent_id][1])
    curr_x = int(curr_players[agent_id][0])
    curr_y = int(curr_players[agent_id][1])
    moved = prev_x != curr_x or prev_y != curr_y

    if curr_alive == 1 and moved:
        prev_d = _manhattan_to_nearest_alive_enemy(prev_players, agent_id, prev_x, prev_y)
        curr_d = _manhattan_to_nearest_alive_enemy(curr_players, agent_id, curr_x, curr_y)
        if prev_d is not None and curr_d is not None:
            if curr_d < prev_d:
                reward += R_CLOSER_STEP
            elif curr_d > prev_d:
                reward += R_FARTHER_STEP

            if episode_state.best_dist is None or curr_d < episode_state.best_dist:
                reward += R_CLOSEST_SO_FAR
                episode_state.best_dist = float(curr_d)

    if curr_alive == 1:
        in_blast, _ = _blast_status_at(curr_obs, curr_x, curr_y)
        if in_blast:
            reward += R_IN_BLAST
        elif _any_bombs(curr_obs):
            dbomb = _min_manhattan_to_bomb_center(curr_obs, curr_x, curr_y)
            if dbomb is not None and dbomb <= SAFE_NEAR_BOMB_RADIUS:
                reward += R_SAFE_NEAR_BOMB

    return float(reward), episode_state


if __name__ == "__main__":
    es = EpisodeRewardState()

    # Death
    po = {"map": np.zeros((3, 3), dtype=np.int8), "players": np.array([[1, 1, 1, 1, 0]], dtype=np.int8), "bombs": np.zeros((0, 4), dtype=np.int8)}
    co = {"map": np.zeros((3, 3), dtype=np.int8), "players": np.array([[1, 1, 0, 1, 0]], dtype=np.int8), "bombs": np.zeros((0, 4), dtype=np.int8)}
    r, _ = compute_reward_icec(po, co, 0, es)
    assert abs(r - R_AGENT_DEATH) < 1e-9, r

    # Time step only (standing still, alive, no bombs)
    es2 = EpisodeRewardState()
    r, _ = compute_reward_icec(po, po, 0, es2)
    assert abs(r - R_TIME_STEP) < 1e-9, r

    # Movement + closer enemy (two players)
    m = np.zeros((5, 5), dtype=np.int8)
    po3 = {
        "map": m,
        "players": np.array([[1, 2, 1, 1, 0], [3, 2, 1, 1, 0]], dtype=np.int8),
        "bombs": np.zeros((0, 4), dtype=np.int8),
    }
    co3 = {
        "map": m,
        "players": np.array([[2, 2, 1, 1, 0], [3, 2, 1, 1, 0]], dtype=np.int8),
        "bombs": np.zeros((0, 4), dtype=np.int8),
    }
    es3 = EpisodeRewardState()
    r, _ = compute_reward_icec(po3, co3, 0, es3)
    # time + closer (+0.002) + closest so far (+0.1) — prev dist 2, curr 1
    assert abs(r - (R_TIME_STEP + R_CLOSER_STEP + R_CLOSEST_SO_FAR)) < 1e-9, r

    print("reward_02 self-tests passed.")
