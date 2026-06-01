"""Starter dataset generator for behavior cloning experiments.

This is intentionally light. Person B can extend it to save (features, action)
pairs once Person A's encoder is stable.
"""

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
AGENT_DIR = Path(__file__).resolve().parents[1]
if str(AGENT_DIR) not in sys.path:
    sys.path.insert(0, str(AGENT_DIR))
if str(ROOT) not in sys.path:
    sys.path.insert(1, str(ROOT))


def collect_rule_actions(num_episodes: int = 5, max_steps: int = 500) -> list[dict]:
    from agent import Agent
    from engine.game import BomberEnv

    env = BomberEnv(max_steps=max_steps)
    agents = [Agent(i) for i in range(4)]
    rows = []

    for episode in range(num_episodes):
        obs = env.reset(seed=episode)
        done = False
        step = 0
        while not done and step < max_steps:
            actions = [agent.act(obs) for agent in agents]
            rows.append({"episode": episode, "step": step, "actions": actions})
            obs, terminated, truncated = env.step(actions)
            done = terminated or truncated
            step += 1

    return rows


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--num-episodes", type=int, default=5)
    parser.add_argument("--max-steps", type=int, default=500)
    args = parser.parse_args()
    data = collect_rule_actions(args.num_episodes, args.max_steps)
    print(f"collected {len(data)} steps")
