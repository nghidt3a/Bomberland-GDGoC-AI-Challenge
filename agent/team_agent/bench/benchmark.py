import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
AGENT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def run_benchmark(num_matches: int = 20, max_steps: int = 500) -> None:
    from scripts.participant.estimate_rankings import estimate_rankings

    estimate_rankings(str(AGENT_DIR), num_matches=num_matches, max_steps=max_steps)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--num-matches", type=int, default=20)
    parser.add_argument("--max-steps", type=int, default=500)
    args = parser.parse_args()
    run_benchmark(num_matches=args.num_matches, max_steps=args.max_steps)
