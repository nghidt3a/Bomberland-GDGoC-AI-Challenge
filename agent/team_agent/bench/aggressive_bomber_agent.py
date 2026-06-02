"""Aggressive sparring opponent that mimics the top agents in data_top/.

The real active pool sends ~30% top-rated opponents that play very actively: low
STOP, 36-70 bombs/game, 50-76% of bombs placed next to an opponent, radius farmed
to near-max, 2-3 simultaneous bombs. To validate our submissions against that
style we reuse OUR OWN safety core (so the sparring bot never self-destructs and
the match stays a fair test) driven by a deliberately aggressive ``ScoreWeights``:
heavy pressure/trap/kill, cheap STOP/loop, low proximity aversion.

It is NOT a submission — it lives under bench/ purely as a benchmark opponent
(see ``tiebreak_metrics.py``).
"""

from person_a_safety.bomb_tracker import BombRadiusTracker
from person_a_safety.danger import compute_hazard_map
from person_a_safety.masks import safe_actions
from person_a_safety.obs import parse_obs
from person_a_safety.shield import final_shield
from person_b_strategy.policy_rule import RulePolicy
from person_b_strategy.scoring import ScoreWeights

# Constant aggressive weights (bypasses the phase schedule) — a consistent,
# strong, kill-hungry sparring partner that still hunts boxes/items hard.
AGGRO_WEIGHTS = ScoreWeights(
    survival=14.0,
    box_move=60.0,
    box_bomb=58.0,
    item=50.0,
    pressure=28.0,
    trap=30.0,
    mobility=4.0,
    danger=11.0,
    enemy_risk=3.0,
    loop=2.5,
    useless_bomb=52.0,
    stop=4.0,
    confine=8.0,
    kill=55.0,
)


class AggressiveBomberAgent:
    team_id = "AggressiveBomber"

    def __init__(self, agent_id: int):
        self.agent_id = int(agent_id)
        self.policy = RulePolicy(weights=AGGRO_WEIGHTS)
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
