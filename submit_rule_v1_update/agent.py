from person_a_safety.constants import STOP
from person_a_safety.danger import compute_danger_map
from person_a_safety.masks import safe_actions
from person_a_safety.obs import parse_obs
from person_a_safety.shield import final_shield
from person_b_strategy.policy_rule import RulePolicy


class Agent:
    """Submit-compatible agent that wires A's safety core to B's policy."""

    team_id = "TeamAB_rule_v1_update"

    def __init__(self, agent_id: int):
        self.agent_id = int(agent_id)
        self.policy = RulePolicy()

    def act(self, obs: dict) -> int:
        try:
            state = parse_obs(obs, self.agent_id)
            danger_time = compute_danger_map(state)
            mask = safe_actions(state, danger_time)
            raw_action = self.policy.choose_action(state, mask, danger_time)
            return int(final_shield(raw_action, state, danger_time))
        except Exception:
            return STOP
