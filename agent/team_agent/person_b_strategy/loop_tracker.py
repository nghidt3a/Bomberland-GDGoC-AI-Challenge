from collections import deque

from person_a_safety.constants import STOP
from person_a_safety.state import Cell


class AntiLoopTracker:
    """Small stateful helper for discouraging A-B-A-B loops and camping."""

    def __init__(self, maxlen: int = 12):
        self.recent_positions: deque[Cell] = deque(maxlen=maxlen)
        self.recent_actions: deque[int] = deque(maxlen=maxlen)

    def update(self, pos: Cell, action: int) -> None:
        self.recent_positions.append(pos)
        self.recent_actions.append(int(action))

    def action_penalty(self, next_pos: Cell, action: int) -> float:
        penalty = 0.0
        if action == STOP:
            penalty += 3.0
        if self.recent_positions and next_pos == self.recent_positions[-1]:
            penalty += 2.0
        if len(self.recent_positions) >= 3 and next_pos == self.recent_positions[-3]:
            penalty += 6.0
        penalty += 0.5 * sum(1 for pos in self.recent_positions if pos == next_pos)
        return penalty
