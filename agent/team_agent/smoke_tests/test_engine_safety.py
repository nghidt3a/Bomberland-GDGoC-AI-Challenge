"""Engine cross-validation harness — the strongest safety proof.

Runs the REAL BomberEnv across many seeds, drives the team agent, and asserts
the core safety invariant of Person A:

  1. Every action returned is in [0, 5].
  2. The agent NEVER dies inside the blast of a bomb it owns (self-death = 0).

Dying to an opponent's bomb is reported but NOT failed: per the agreed scope we
only harden against self-inflicted death, not against predicting enemy bombs.

Run more seeds manually when hardening:
    TEAM_SAFETY_SEEDS=300 python -m pytest agent/team_agent/smoke_tests/test_engine_safety.py -q -s
"""

import os

import numpy as np

from engine.game import BomberEnv
from engine.map import Map

# Imported via conftest path setup.
from competition.evaluation.runtime_guard import load_agent_instance

from conftest import TEAM_DIR

NUM_SEEDS = int(os.environ.get("TEAM_SAFETY_SEEDS", "40"))
MAX_STEPS = int(os.environ.get("TEAM_SAFETY_MAX_STEPS", "300"))
TEAM_SLOT = 0


class Wanderer:
    """Deterministic, seeded opponent that only MOVES and never places a bomb.

    Using non-bombing opponents makes the match fully reproducible and ensures
    the only bombs on the field belong to our team agent. Any death inside a
    blast is therefore unambiguously self-inflicted (in scope for Person A),
    not the result of an opponent sealing our escape (out of scope).
    """

    def __init__(self, agent_id, seed):
        self.id = int(agent_id)
        self.rng = np.random.default_rng(seed * 31 + agent_id)

    def act(self, obs):
        return int(self.rng.integers(0, 5))  # 0..4 -> never PLACE_BOMB


def _blast_tiles(bomb, grid):
    """Replicate engine/game.py::_get_explosion_tiles against a given grid."""
    height, width = grid.shape
    tiles = {(bomb.x, bomb.y)}
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        for r in range(1, bomb.radius + 1):
            tx, ty = bomb.x + dx * r, bomb.y + dy * r
            if 0 <= tx < height and 0 <= ty < width:
                if grid[tx, ty] == Map.WALL:
                    break
                tiles.add((tx, ty))
                if grid[tx, ty] == Map.BOX:
                    break
            else:
                break
    return tiles


def _make_opponents(seed):
    """Three deterministic, non-bombing wanderers."""
    return [Wanderer(i, seed) for i in (1, 2, 3)]


def _run_one_match(seed):
    """Return (own_bomb_deaths, enemy_deaths, bad_actions) for one match."""
    env = BomberEnv(max_steps=MAX_STEPS, seed=seed)
    team = load_agent_instance(str(TEAM_DIR / "agent.py"), agent_id=TEAM_SLOT)
    opponents = _make_opponents(seed)  # carry ids 1..3
    agents = [team, *opponents]

    obs = env.reset(seed=seed)
    own_bomb_deaths = 0
    enemy_deaths = 0
    bad_actions = 0

    for _ in range(MAX_STEPS):
        was_alive = env.players[TEAM_SLOT].alive
        if not was_alive:
            break

        actions = []
        for i, ag in enumerate(agents):
            try:
                a = int(ag.act(obs))
            except Exception:
                a = 0
            if i == TEAM_SLOT and not (0 <= a <= 5):
                bad_actions += 1
                a = 0
            actions.append(a)

        # Snapshot the world right before the engine resolves explosions.
        pre_grid = env.map.grid.copy()
        bombs_before = set(id(b) for b in env.bombs)
        bombs_by_id = {id(b): b for b in env.bombs}

        obs, terminated, truncated = env.step(actions)

        # Did our agent just die this step?
        if was_alive and not env.players[TEAM_SLOT].alive:
            bombs_after = set(id(b) for b in env.bombs)
            exploded = [bombs_by_id[bid] for bid in (bombs_before - bombs_after)]
            died_cell = (env.players[TEAM_SLOT].x, env.players[TEAM_SLOT].y)

            own_blast = set()
            any_blast = set()
            for b in exploded:
                tiles = _blast_tiles(b, pre_grid)
                any_blast |= tiles
                if b.owner_id == TEAM_SLOT:
                    own_blast |= tiles

            if died_cell in own_blast:
                own_bomb_deaths += 1
            elif died_cell in any_blast:
                enemy_deaths += 1
            break

        if terminated or truncated:
            break

    return own_bomb_deaths, enemy_deaths, bad_actions


def test_agent_never_self_destructs_across_seeds():
    total_own = 0
    total_enemy = 0
    total_bad = 0
    offending_seeds = []

    for seed in range(NUM_SEEDS):
        own, enemy, bad = _run_one_match(seed)
        total_own += own
        total_enemy += enemy
        total_bad += bad
        if own or bad:
            offending_seeds.append(seed)

    print(
        f"\n[engine-safety] seeds={NUM_SEEDS} "
        f"own_bomb_deaths={total_own} enemy_deaths={total_enemy} "
        f"bad_actions={total_bad} offenders={offending_seeds}"
    )

    assert total_bad == 0, f"agent returned out-of-range actions on seeds {offending_seeds}"
    assert total_own == 0, f"agent self-destructed with its own bomb on seeds {offending_seeds}"
