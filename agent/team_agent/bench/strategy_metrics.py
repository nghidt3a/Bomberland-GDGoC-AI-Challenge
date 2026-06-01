import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
AGENT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.game import BomberEnv
from scripts.participant.run_local_match import make_agents


def run_strategy_metrics(
    agent_path: str,
    opponents: list[str],
    num_episodes: int = 20,
    max_steps: int = 500,
    seed: int = 1,
) -> dict[str, float]:
    env = BomberEnv(max_steps=max_steps, seed=seed)
    totals = {
        "wins": 0,
        "draws": 0,
        "self_deaths": 0,
        "survival_steps": 0,
        "rank": 0,
        "kills": 0,
        "boxes": 0,
        "items": 0,
        "bombs": 0,
    }

    for episode in range(num_episodes):
        episode_seed = seed + episode
        agents, _names = make_agents([agent_path, *opponents], seed=episode_seed)
        obs = env.reset(seed=episode_seed)
        done = False
        step = 0
        death_order = []
        prev_alive = [bool(player[2]) for player in obs["players"]]
        agent_death_step = max_steps

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

            alive_now = [bool(player[2]) for player in obs["players"]]
            for player_id, was_alive in enumerate(prev_alive):
                if was_alive and not alive_now[player_id]:
                    death_order.append(player_id)
                    if player_id == 0:
                        agent_death_step = step
            prev_alive = alive_now

        alive_final = [bool(player[2]) for player in obs["players"]]
        survivors = [player_id for player_id, alive in enumerate(alive_final) if alive]
        ranks = ranks_from_deaths(survivors, death_order)

        if len(survivors) == 1 and survivors[0] == 0:
            totals["wins"] += 1
        elif 0 in survivors:
            totals["draws"] += 1
        if not alive_final[0]:
            totals["self_deaths"] += 1

        totals["survival_steps"] += min(agent_death_step, step)
        totals["rank"] += ranks[0]

        stats = env.players[0].stats
        for key in ("kills", "boxes", "items", "bombs"):
            totals[key] += int(stats.get(key, 0))

    metrics = {
        "episodes": float(num_episodes),
        "win_rate": totals["wins"] / num_episodes,
        "draw_rate": totals["draws"] / num_episodes,
        "self_death_rate": totals["self_deaths"] / num_episodes,
        "avg_survival_steps": totals["survival_steps"] / num_episodes,
        "avg_rank": totals["rank"] / num_episodes,
        "avg_kills": totals["kills"] / num_episodes,
        "avg_boxes": totals["boxes"] / num_episodes,
        "avg_items": totals["items"] / num_episodes,
        "avg_bombs": totals["bombs"] / num_episodes,
    }
    print_metrics(metrics)
    return metrics


def ranks_from_deaths(survivors: list[int], death_order: list[int]) -> list[int]:
    ranks = [0, 0, 0, 0]
    for player_id in survivors:
        ranks[player_id] = 0
    current_rank = 1 if survivors else 0
    for player_id in reversed(death_order):
        ranks[player_id] = current_rank
        current_rank += 1
    return ranks


def print_metrics(metrics: dict[str, float]) -> None:
    print("=== Strategy Metrics ===")
    for key in (
        "episodes",
        "win_rate",
        "draw_rate",
        "self_death_rate",
        "avg_survival_steps",
        "avg_rank",
        "avg_kills",
        "avg_boxes",
        "avg_items",
        "avg_bombs",
    ):
        print(f"{key}: {metrics[key]:.3f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent-path", default=str(AGENT_DIR))
    parser.add_argument(
        "--opponents",
        nargs=3,
        default=["TacticalRuleAgent", "SmarterRuleAgent", "GeniusRuleAgent"],
    )
    parser.add_argument("--num-episodes", type=int, default=20)
    parser.add_argument("--max-steps", type=int, default=500)
    parser.add_argument("--seed", type=int, default=1)
    args = parser.parse_args()

    run_strategy_metrics(
        agent_path=args.agent_path,
        opponents=args.opponents,
        num_episodes=args.num_episodes,
        max_steps=args.max_steps,
        seed=args.seed,
    )
