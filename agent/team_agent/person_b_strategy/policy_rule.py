from math import inf

from person_a_safety.constants import ACTIONS, STOP

from .loop_tracker import AntiLoopTracker
from .scoring import action_progress_value, action_tie_break_score, score_actions


class RulePolicy:
    """Rule_v1 policy: score only actions allowed by A's safe mask."""

    def __init__(self):
        self.loop_tracker = AntiLoopTracker()
        self.turn_index = 0

    def choose_action(self, state, safe_mask, danger_time) -> int:
        self.loop_tracker.observe_state(state)
        scores = score_actions(
            state,
            safe_mask,
            danger_time,
            tracker=self.loop_tracker,
            turn_index=self.turn_index,
        )

        action = self._best_action(state, scores)
        action_value = action_progress_value(state, action, turn_index=self.turn_index)
        self.loop_tracker.update(state.self_pos, action, action_value=action_value)
        self.turn_index += 1
        return int(action)

    def _best_action(self, state, scores: dict[int, float]) -> int:
        if not scores:
            return STOP

        action = max(
            ACTIONS,
            key=lambda candidate: (
                scores.get(candidate, -inf),
                action_tie_break_score(state, candidate, turn_index=self.turn_index),
            ),
        )
        if scores.get(action, -inf) == -inf:
            return STOP
        return int(action)
