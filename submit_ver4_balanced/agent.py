from time import perf_counter

from person_a_safety.bomb_tracker import BombRadiusTracker
from person_a_safety.constants import STOP
from person_a_safety.danger import compute_hazard_map
from person_a_safety.masks import safe_actions
from person_a_safety.obs import parse_obs
from person_a_safety.shield import final_shield
from person_b_strategy.policy_rule import RulePolicy

# The engine gives each ``act`` call 100 ms. The safety gate (hazard + safe mask +
# final shield) is mandatory and always runs; only the OPTIONAL strategy
# simulations (bomb-trap / escape-quality / enemy-bomb threat) are skipped once
# this soft budget is spent, leaving head-room for the shield. Chosen well under
# 100 ms so even a slow evaluator host stays inside the hard limit.
ACT_BUDGET_MS = 75.0

# Scoring temperament for this build: "balanced" | "aggressive" | "safe". The
# safety core is identical across all three; only this preset differs. The bundle
# builder rewrites this line to produce the per-version submissions.
STYLE = "balanced"


class Agent:
    """Submit-compatible agent that wires A's safety core to B's policy."""

    team_id = "TeamABScaffoldAgent"

    def __init__(self, agent_id: int):
        self.agent_id = int(agent_id)
        self.policy = RulePolicy(style=STYLE)
        self.radius_tracker = BombRadiusTracker()

    def act(self, obs: dict) -> int:
        started = perf_counter()
        try:
            radius_lookup = self.radius_tracker.update_from_obs(obs)
            state = parse_obs(obs, self.agent_id, radius_lookup=radius_lookup)
            hazard = compute_hazard_map(state)
            mask = safe_actions(state, hazard)
            deadline = started + ACT_BUDGET_MS / 1000.0
            raw_action = self.policy.choose_action(state, mask, hazard, deadline=deadline)
            return int(final_shield(raw_action, state, hazard, mask))
        except Exception:
            return STOP
