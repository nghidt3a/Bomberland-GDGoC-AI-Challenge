"""Generate behavior-cloning samples from the shielded rule agent."""

import argparse
import sys
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
AGENT_DIR = Path(__file__).resolve().parents[1]
if str(AGENT_DIR) not in sys.path:
    sys.path.insert(0, str(AGENT_DIR))
if str(ROOT) not in sys.path:
    sys.path.insert(1, str(ROOT))


def collect_rule_samples(
    num_episodes: int = 5,
    max_steps: int = 500,
    seed: int = 1,
) -> dict[str, np.ndarray]:
    from agent import Agent
    from engine.game import BomberEnv
    from person_a_safety.danger import compute_hazard_map
    from person_a_safety.features import encode_features
    from person_a_safety.masks import safe_actions
    from person_a_safety.obs import parse_obs

    env = BomberEnv(max_steps=max_steps, seed=seed)
    features = []
    teacher_actions = []
    safe_masks = []
    agent_ids = []
    steps = []
    episodes = []

    for episode in range(num_episodes):
        episode_seed = seed + episode
        agents = [Agent(i) for i in range(4)]
        obs = env.reset(seed=episode_seed)
        done = False
        step = 0

        while not done and step < max_steps:
            step_features = []
            step_masks = []
            actions = []

            for agent_id, agent in enumerate(agents):
                state = parse_obs(obs, agent_id)
                hazard = compute_hazard_map(state)
                mask = safe_actions(state, hazard)
                action = int(agent.act(obs))
                actions.append(action)

                if not state.self_alive:
                    continue

                step_features.append(encode_features(state, hazard))
                step_masks.append(mask.astype(np.bool_))
                teacher_actions.append(action)
                agent_ids.append(agent_id)
                steps.append(step)
                episodes.append(episode_seed)

            features.extend(step_features)
            safe_masks.extend(step_masks)
            obs, terminated, truncated = env.step(actions)
            done = terminated or truncated
            step += 1

    return {
        "features": np.asarray(features, dtype=np.float32),
        "teacher_action": np.asarray(teacher_actions, dtype=np.int64),
        "safe_mask": np.asarray(safe_masks, dtype=np.bool_),
        "agent_id": np.asarray(agent_ids, dtype=np.int64),
        "step": np.asarray(steps, dtype=np.int64),
        "episode_seed": np.asarray(episodes, dtype=np.int64),
    }


def save_dataset(samples: dict[str, np.ndarray], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(output_path, **samples)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--num-episodes", type=int, default=5)
    parser.add_argument("--max-steps", type=int, default=500)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    data = collect_rule_samples(
        num_episodes=args.num_episodes,
        max_steps=args.max_steps,
        seed=args.seed,
    )
    print(f"collected {len(data['teacher_action'])} samples")
    if args.out is not None:
        save_dataset(data, args.out)
        print(f"saved dataset to {args.out}")


if __name__ == "__main__":
    main()
