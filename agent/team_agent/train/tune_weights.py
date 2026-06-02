"""Offline weight tuner (cross-entropy method) for the rule policy.

The hand-set ``ScoreWeights`` and phase schedule in ``person_b_strategy/scoring.py``
are a sensible prior but are not proven near-optimal. This tool searches for a
single fixed ``ScoreWeights`` (injected via ``RulePolicy(weights=...)``) that
maximises a fitness built from the same signals ``bench/strategy_metrics.py``
reports — lower avg rank, more survival, fewer self-deaths, more boxes/items.

It evaluates in-process against the rule opponents and prints the best weights it
finds; it deliberately does NOT touch the shipped phased weights. A short run is
a smoke test that the loop improves the prior; a long run (large ``--pop`` /
``--iters`` / ``--episodes``) can produce a candidate to review and paste in.

    python -m agent.team_agent.train.tune_weights --iters 8 --pop 16 --episodes 12 --seed 1

Note: tuning maximises a *single* weight set for the whole game, so the result is
a global compromise, not a replacement for the per-phase schedule. Treat its
output as a tie-broken suggestion, validated afterwards with strategy_metrics.
"""

import argparse
import json
import sys
from dataclasses import fields
from math import inf
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
TEAM_DIR = Path(__file__).resolve().parents[1]
for path in (ROOT, TEAM_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from engine.game import BomberEnv
from agent import GeniusRuleAgent, SmarterRuleAgent, TacticalRuleAgent

from person_a_safety.bomb_tracker import BombRadiusTracker
from person_a_safety.danger import compute_hazard_map
from person_a_safety.masks import safe_actions
from person_a_safety.obs import parse_obs
from person_a_safety.shield import final_shield
from person_b_strategy.policy_rule import RulePolicy
from person_b_strategy.scoring import ScoreWeights
from agent.team_agent.bench.aggressive_bomber_agent import AggressiveBomberAgent
from agent.team_agent.bench.tiebreak_metrics import tiebreak_ranks

# Tunable fields, in a fixed order so a flat vector maps cleanly to ScoreWeights.
FIELDS = [f.name for f in fields(ScoreWeights)]
# Per-field upper bound for clipping sampled candidates (lower bound is 0).
UPPER = {
    "survival": 60.0, "box_move": 160.0, "box_bomb": 140.0, "item": 120.0,
    "pressure": 60.0, "trap": 60.0, "mobility": 30.0, "danger": 60.0,
    "enemy_risk": 40.0, "loop": 20.0, "useless_bomb": 160.0, "stop": 40.0,
    "confine": 60.0, "kill": 120.0,
}

OPPONENT_CLASSES = {
    "TacticalRuleAgent": TacticalRuleAgent,
    "SmarterRuleAgent": SmarterRuleAgent,
    "GeniusRuleAgent": GeniusRuleAgent,
    "AggressiveBomber": AggressiveBomberAgent,
}


class TunableTeamAgent:
    """Same safety pipeline as the shipped Agent but with injectable weights.

    No time budget here: tuning wants the policy's full-strength decisions, not
    its degraded-under-deadline fallback.
    """

    def __init__(self, agent_id: int, weights: ScoreWeights):
        self.agent_id = int(agent_id)
        self.policy = RulePolicy(weights=weights)
        self.radius_tracker = BombRadiusTracker()

    def act(self, obs: dict) -> int:
        try:
            lookup = self.radius_tracker.update_from_obs(obs)
            state = parse_obs(obs, self.agent_id, radius_lookup=lookup)
            hazard = compute_hazard_map(state)
            mask = safe_actions(state, hazard)
            raw = self.policy.choose_action(state, mask, hazard)
            return int(final_shield(raw, state, hazard, mask))
        except Exception:
            return 0


def vec_to_weights(vec: np.ndarray) -> ScoreWeights:
    return ScoreWeights(**{name: float(vec[i]) for i, name in enumerate(FIELDS)})


def weights_to_vec(weights: ScoreWeights) -> np.ndarray:
    return np.array([getattr(weights, name) for name in FIELDS], dtype=float)


def evaluate(weights: ScoreWeights, opponents, episodes, base_seed, max_steps) -> dict:
    """Run ``episodes`` matches (player 0 = tuned policy) and aggregate the
    tie-break-aligned metrics (rank via Kills>Boxes>Items>Bombs at step 500)."""
    totals = {"wins": 0, "self_deaths": 0, "rank": 0, "survive500": 0,
              "kills": 0, "boxes": 0, "items": 0, "bombs": 0}
    env = BomberEnv(max_steps=max_steps, seed=base_seed)

    for ep in range(episodes):
        seed = base_seed + ep
        agents = [TunableTeamAgent(0, weights)]
        agents += [OPPONENT_CLASSES[name](i + 1) for i, name in enumerate(opponents)]
        obs = env.reset(seed=seed)
        prev_alive = [bool(p[2]) for p in obs["players"]]
        death_steps = [max_steps] * 4
        step = 0
        done = False

        while not done and step < max_steps:
            actions = []
            for agent in agents:
                try:
                    actions.append(int(agent.act(obs)))
                except Exception:
                    actions.append(0)
            obs, terminated, truncated = env.step(actions)
            done = terminated or truncated
            step += 1
            alive_now = [bool(p[2]) for p in obs["players"]]
            for pid, was in enumerate(prev_alive):
                if was and not alive_now[pid]:
                    death_steps[pid] = step
            prev_alive = alive_now

        stats = [dict(env.players[i].stats) for i in range(4)]
        ranks = tiebreak_ranks(death_steps, stats, max_steps)
        if ranks[0] == 0 and ranks.count(0) == 1:
            totals["wins"] += 1
        if death_steps[0] < max_steps:
            totals["self_deaths"] += 1  # any death (proxy); engine harness proves self-bomb=0
        else:
            totals["survive500"] += 1
        totals["rank"] += ranks[0]
        for k in ("kills", "boxes", "items", "bombs"):
            totals[k] += int(stats[0].get(k, 0))

    n = float(episodes)
    return {
        "win_rate": totals["wins"] / n,
        "self_death_rate": totals["self_deaths"] / n,
        "avg_rank": totals["rank"] / n,
        "survive500_rate": totals["survive500"] / n,
        "avg_kills": totals["kills"] / n,
        "avg_boxes": totals["boxes"] / n,
        "avg_items": totals["items"] / n,
        "avg_bombs": totals["bombs"] / n,
    }


def fitness(metrics: dict) -> float:
    """Higher is better, aligned to the real ladder: low tie-break rank, then the
    Kills>Boxes>Items>Bombs chain, with survival gated hard (a death tanks μ)."""
    return (
        -10.0 * metrics["avg_rank"]
        + 6.0 * metrics["win_rate"]
        + 4.0 * metrics["survive500_rate"]
        - 12.0 * metrics["self_death_rate"]
        + 3.0 * metrics["avg_kills"]
        + 0.2 * metrics["avg_boxes"]
        + 0.3 * metrics["avg_items"]
        + 0.02 * metrics["avg_bombs"]
    )


def tune(opponents, iters, pop, episodes, max_steps, base_seed, elite_frac, init_std_frac):
    rng = np.random.default_rng(base_seed)
    upper = np.array([UPPER[name] for name in FIELDS], dtype=float)

    mean = weights_to_vec(ScoreWeights())  # start from the shipped defaults
    std = mean * init_std_frac + 5.0
    n_elite = max(2, int(round(pop * elite_frac)))

    baseline = evaluate(ScoreWeights(), opponents, episodes, base_seed, max_steps)
    best_fit = fitness(baseline)
    best_vec = mean.copy()
    best_metrics = baseline
    print(f"[tune] baseline fitness={best_fit:+.3f} metrics={_fmt(baseline)}")

    for it in range(iters):
        samples = rng.normal(mean, std, size=(pop, len(FIELDS)))
        samples = np.clip(samples, 0.0, upper)
        scored = []
        for vec in samples:
            metrics = evaluate(vec_to_weights(vec), opponents, episodes, base_seed, max_steps)
            fit = fitness(metrics)
            scored.append((fit, vec, metrics))
            if fit > best_fit:
                best_fit, best_vec, best_metrics = fit, vec.copy(), metrics

        scored.sort(key=lambda item: item[0], reverse=True)
        elite = np.array([vec for _f, vec, _m in scored[:n_elite]])
        mean = elite.mean(axis=0)
        std = elite.std(axis=0) + 1.0
        print(f"[tune] iter {it + 1}/{iters} best_fit={scored[0][0]:+.3f} "
              f"global_best={best_fit:+.3f}")

    print(f"\n[tune] BEST fitness={best_fit:+.3f} metrics={_fmt(best_metrics)}")
    print("[tune] BEST weights:")
    print(_weights_src(vec_to_weights(best_vec)))
    return vec_to_weights(best_vec), best_metrics


def _fmt(metrics: dict) -> str:
    return " ".join(f"{k}={v:.2f}" for k, v in metrics.items())


def _weights_src(weights: ScoreWeights) -> str:
    body = ",\n".join(f"    {name}={getattr(weights, name):.1f}" for name in FIELDS)
    return f"ScoreWeights(\n{body},\n)"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--opponents", nargs=3,
                        default=["TacticalRuleAgent", "GeniusRuleAgent", "AggressiveBomber"])
    parser.add_argument("--iters", type=int, default=8)
    parser.add_argument("--pop", type=int, default=16)
    parser.add_argument("--episodes", type=int, default=12)
    parser.add_argument("--max-steps", type=int, default=500)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--elite-frac", type=float, default=0.3)
    parser.add_argument("--init-std-frac", type=float, default=0.35)
    parser.add_argument("--out", type=str, default=None, help="optional JSON path for best weights")
    args = parser.parse_args()

    best, metrics = tune(
        opponents=args.opponents,
        iters=args.iters,
        pop=args.pop,
        episodes=args.episodes,
        max_steps=args.max_steps,
        base_seed=args.seed,
        elite_frac=args.elite_frac,
        init_std_frac=args.init_std_frac,
    )

    if args.out:
        Path(args.out).write_text(
            json.dumps({"weights": {n: getattr(best, n) for n in FIELDS}, "metrics": metrics}, indent=2),
            encoding="utf-8",
        )
        print(f"[tune] wrote {args.out}")


if __name__ == "__main__":
    main()
