from person_a_safety.constants import STOP


class BehaviorCloningPolicy:
    """Placeholder for BC inference. Keep final shield in agent.py."""

    def __init__(self, model_path=None):
        self.model_path = model_path
        self.model = None

    def choose_action(self, state, safe_mask, danger_time) -> int:
        return first_safe_action(safe_mask)


def first_safe_action(safe_mask) -> int:
    for action, allowed in enumerate(safe_mask):
        if allowed:
            return int(action)
    return STOP
