from person_a_safety.constants import STOP


class PPOPolicy:
    """Placeholder for PPO inference. Do not train inside act()."""

    def __init__(self, model_path=None):
        self.model_path = model_path
        self.model = None

    def choose_action(self, state, safe_mask, hazard) -> int:
        for action, allowed in enumerate(safe_mask):
            if allowed:
                return int(action)
        return STOP
