from person_a_safety.constants import STOP

from .loop_tracker import AntiLoopTracker
from .scoring import score_actions


class RulePolicy:
    """Person B's first policy: score only actions allowed by A's safe mask."""

    def __init__(self):
        self.loop_tracker = AntiLoopTracker()

    def choose_action(self, state, safe_mask, danger_time) -> int:
        scores = score_actions(state, safe_mask, danger_time, tracker=self.loop_tracker)
        action = max(scores, key=scores.get) if scores else STOP
        if scores and scores[action] == float("-inf"):
            action = STOP
        self.loop_tracker.update(state.self_pos, action)
        return int(action)
