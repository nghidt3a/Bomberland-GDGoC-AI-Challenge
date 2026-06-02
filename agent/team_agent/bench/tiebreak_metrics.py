"""Benchmark that scores agents the way the real ladder does: survive to step 500,
then break ties by Kills > Boxes > Items > Bombs.

Match analysis of ``data_top/`` showed 22/27 matches are decided by this step-500
tie-break, so plain win-rate hides what actually moves rank. This bench reconstructs
the real per-match ranking and reports the tie-break chain, against a pool that
mimics the active pool (strong baselines + an ``AggressiveBomber`` stand-in for the
~30% top opponents).

    # compare the three styles in-process
    python -m agent.team_agent.bench.tiebreak_metrics --style balanced --num-episodes 20 --seed 1
    python -m agent.team_agent.bench.tiebreak_metrics --style aggressive --num-episodes 20 --seed 1
    python -m agent.team_agent.bench.tiebreak_metrics --style safe --num-episodes 20 --seed 1
    # or score a built bundle
    python -m agent.team_agent.bench.tiebreak_metrics --agent-path submit_ver4_balanced --num-episodes 20 --seed 1
"""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
AGENT_DIR = Path(__file__).resolve().parents[1]
for p in (ROOT, AGENT_DIR):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from engine.game import BomberEnv
from agent import GeniusRuleAgent, SmarterRuleAgent, TacticalRuleAgent, BoxFarmerAgent
from competition.evaluation.runtime_guard import load_agent_instance

from person_a_safety.bomb_tracker import BombRadiusTracker
from person_a_safety.danger import compute_hazard_map
from person_a_safety.masks import safe_actions
from person_a_safety.obs import parse_obs
from person_a_safety.shield import final_shield
from person_b_strategy.policy_rule import RulePolicy
from agent.team_agent.bench.aggressive_bomber_agent import AggressiveBomberAgent

OPPONENT_FACTORY = {
    "TacticalRuleAgent": TacticalRuleAgent,
    "SmarterRuleAgent": SmarterRuleAgent,
    "GeniusRuleAgent": GeniusRuleAgent,
    "BoxFarmerAgent": BoxFarmerAgent,
    "AggressiveBomber": AggressiveBomberAgent,
}


class StyledTeamAgent:
    """Our full safety pipeline driven by a chosen scoring style (in-process)."""

    def __init__(self, agent_id: int, style: str):
        self.agent_id = int(agent_id)
        self.policy = RulePolicy(style=style)
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


def tiebreak_ranks(death_steps: list[int], stats: list[dict], max_steps: int) -> list[int]:
    """Reconstruct the real ranking. 0 = best.

    Survivors to ``max_steps`` outrank anyone who died earlier; among survivors the
    chain Kills > Boxes > Items > Bombs breaks ties. Agents that died earlier are
    ordered by death step (later = better); equal death steps mid-game stay a draw
    (engagement only breaks ties at step 500, per the rules).
    """
    keys = []
    for i in range(len(death_steps)):
        if death_steps[i] >= max_steps:
            s = stats[i]
            keys.append((death_steps[i], s.get("kills", 0), s.get("boxes", 0), s.get("items", 0), s.get("bombs", 0)))
        else:
            keys.append((death_steps[i], 0, 0, 0, 0))

    order = sorted(range(len(keys)), key=lambda i: keys[i], reverse=True)
    ranks = [0] * len(keys)
    for idx, i in enumerate(order):
        if idx > 0 and keys[i] == keys[order[idx - 1]]:
            ranks[i] = ranks[order[idx - 1]]
        else:
            ranks[i] = idx
    return ranks


def make_target(agent_id, style, agent_path):
    if agent_path:
        return load_agent_instance(agent_path, agent_id)
    return StyledTeamAgent(agent_id, style)


def run(style, agent_path, opponents, num_episodes, max_steps, seed):
    env = BomberEnv(max_steps=max_steps, seed=seed)
    totals = {"win": 0, "draw": 0, "rank": 0, "survive500": 0,
              "kills": 0, "boxes": 0, "items": 0, "bombs": 0}

    for ep in range(num_episodes):
        episode_seed = seed + ep
        agents = [make_target(0, style, agent_path)]
        agents += [OPPONENT_FACTORY[name](i + 1) for i, name in enumerate(opponents)]
        obs = env.reset(seed=episode_seed)
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
        my_rank = ranks[0]
        totals["rank"] += my_rank
        if my_rank == 0 and ranks.count(0) == 1:
            totals["win"] += 1
        elif my_rank == 0:
            totals["draw"] += 1
        if death_steps[0] >= max_steps:
            totals["survive500"] += 1
        for k in ("kills", "boxes", "items", "bombs"):
            totals[k] += stats[0].get(k, 0)

    n = float(num_episodes)
    metrics = {
        "style/path": agent_path or style,
        "episodes": num_episodes,
        "win_rate": totals["win"] / n,
        "draw_rate": totals["draw"] / n,
        "avg_tiebreak_rank": totals["rank"] / n,
        "survive500_rate": totals["survive500"] / n,
        "avg_kills": totals["kills"] / n,
        "avg_boxes": totals["boxes"] / n,
        "avg_items": totals["items"] / n,
        "avg_bombs": totals["bombs"] / n,
    }
    print("=== Tie-break Metrics ===")
    print(f"target: {metrics['style/path']}  opponents: {opponents}")
    for k in ("episodes", "win_rate", "draw_rate", "avg_tiebreak_rank", "survive500_rate",
              "avg_kills", "avg_boxes", "avg_items", "avg_bombs"):
        v = metrics[k]
        print(f"{k}: {v:.3f}" if isinstance(v, float) else f"{k}: {v}")
    return metrics


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--style", default="balanced", choices=["balanced", "aggressive", "safe"])
    parser.add_argument("--agent-path", default=None, help="load a built bundle instead of --style")
    parser.add_argument("--opponents", nargs=3,
                        default=["TacticalRuleAgent", "GeniusRuleAgent", "AggressiveBomber"])
    parser.add_argument("--num-episodes", type=int, default=20)
    parser.add_argument("--max-steps", type=int, default=500)
    parser.add_argument("--seed", type=int, default=1)
    args = parser.parse_args()

    path = args.agent_path
    if path:
        p = Path(path)
        if p.is_dir():
            p = p / "agent.py"
        path = str(p)
    run(args.style, path, args.opponents, args.num_episodes, args.max_steps, args.seed)


if __name__ == "__main__":
    main()
