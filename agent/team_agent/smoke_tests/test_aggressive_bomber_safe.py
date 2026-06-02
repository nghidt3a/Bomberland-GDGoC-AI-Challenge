"""The aggressive sparring bot never self-destructs.

It reuses the shared safety core (safe mask + final shield), so despite hunting
hard it must satisfy the same invariant as the shipped agent: it never dies
inside the blast of a bomb it owns. This keeps the benchmark a fair test rather
than a suicide pact.
"""

from engine.game import BomberEnv

from agent.team_agent.bench.aggressive_bomber_agent import AggressiveBomberAgent

# Reuse the engine-safety helpers (non-bombing wanderers + blast reconstruction).
from test_engine_safety import Wanderer, _blast_tiles

SEEDS = 12
STEPS = 150


def test_aggressive_bomber_never_self_destructs():
    own_bomb_deaths = 0
    bad_actions = 0

    for seed in range(SEEDS):
        env = BomberEnv(max_steps=STEPS, seed=seed)
        team = AggressiveBomberAgent(0)
        agents = [team, *(Wanderer(i, seed) for i in (1, 2, 3))]
        obs = env.reset(seed=seed)

        for _ in range(STEPS):
            if not env.players[0].alive:
                break
            actions = []
            for i, ag in enumerate(agents):
                try:
                    a = int(ag.act(obs))
                except Exception:
                    a = 0
                if i == 0 and not (0 <= a <= 5):
                    bad_actions += 1
                    a = 0
                actions.append(a)

            pre_grid = env.map.grid.copy()
            bombs_before = {id(b): b for b in env.bombs}
            was_alive = env.players[0].alive
            obs, terminated, truncated = env.step(actions)

            if was_alive and not env.players[0].alive:
                bombs_after = set(id(b) for b in env.bombs)
                exploded = [bombs_before[bid] for bid in (set(bombs_before) - bombs_after)]
                died_cell = (env.players[0].x, env.players[0].y)
                own_blast = set()
                for b in exploded:
                    if b.owner_id == 0:
                        own_blast |= _blast_tiles(b, pre_grid)
                if died_cell in own_blast:
                    own_bomb_deaths += 1
                break
            if terminated or truncated:
                break

    assert bad_actions == 0
    assert own_bomb_deaths == 0
