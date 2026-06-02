from collections import deque

from person_a_safety.constants import ITEM_CAPACITY, ITEM_RADIUS, PLACE_BOMB, STOP
from person_a_safety.state import Cell, GameState


class AntiLoopTracker:
    """Stateful helper for discouraging short loops and stale camping."""

    def __init__(self, maxlen: int = 16):
        self.recent_positions: deque[Cell] = deque(maxlen=maxlen)
        self.recent_actions: deque[int] = deque(maxlen=maxlen)
        self.turn_index = 0
        self.steps_without_progress = 0

        self.last_box_count: int | None = None
        self.last_visible_item_count: int | None = None
        self.last_self_radius: int | None = None
        self.last_estimated_capacity: int | None = None
        self.last_action: int | None = None
        self.last_action_value = 0.0

        self.proxy_boxes = 0
        self.proxy_items = 0
        self.proxy_bombs = 0
        self.proxy_kills = 0

    @property
    def proxy_score(self) -> float:
        return (
            self.proxy_boxes * 0.8
            + self.proxy_items * 1.2
            + self.proxy_bombs * 0.25
            + self.proxy_kills * 3.0
        )

    def observe_state(self, state: GameState) -> None:
        box_count = int(state.boxes.sum())
        visible_item_count = int(state.item_radius.sum() + state.item_capacity.sum())
        estimated_capacity = estimate_capacity(state)

        if self.last_box_count is None:
            self._store_snapshot(state, box_count, visible_item_count, estimated_capacity)
            return

        made_progress = False

        if box_count < self.last_box_count:
            self.proxy_boxes += self.last_box_count - box_count
            made_progress = True

        if state.self_radius > (self.last_self_radius or 0):
            self.proxy_items += 1
            made_progress = True

        if estimated_capacity > (self.last_estimated_capacity or 0):
            self.proxy_items += 1
            made_progress = True

        if self._reached_new_area(state.self_pos):
            made_progress = True

        if self.last_action == PLACE_BOMB and self.last_action_value > 0:
            made_progress = True

        if made_progress:
            self.steps_without_progress = 0
        else:
            self.steps_without_progress += 1

        self._store_snapshot(state, box_count, visible_item_count, estimated_capacity)

    def update(self, pos: Cell, action: int, action_value: float = 0.0) -> None:
        action = int(action)
        self.recent_positions.append(pos)
        self.recent_actions.append(action)
        self.last_action = action
        self.last_action_value = float(action_value)
        self.turn_index += 1

        if action == PLACE_BOMB and action_value > 0:
            self.proxy_bombs += 1
            self.steps_without_progress = 0

    def action_penalty(self, next_pos: Cell, action: int) -> float:
        recent_positions = list(self.recent_positions)
        recent_actions = list(self.recent_actions)
        penalty = 0.0

        if action == STOP:
            penalty += 5.0
            penalty += 1.8 * sum(1 for recent_action in recent_actions[-5:] if recent_action == STOP)

        if recent_positions and next_pos == recent_positions[-1]:
            penalty += 2.5

        if len(recent_positions) >= 2 and next_pos == recent_positions[-2]:
            penalty += 8.0

        if len(recent_positions) >= 4 and recent_positions[-1] == recent_positions[-3]:
            if next_pos == recent_positions[-2]:
                penalty += 10.0

        penalty += 0.7 * sum(1 for pos in recent_positions if pos == next_pos)

        window = recent_positions[-8:]
        if len(window) >= 6 and len(set(window)) <= 3 and next_pos in window:
            penalty += 5.0

        if self.steps_without_progress >= 12:
            if action == STOP:
                penalty += 10.0
            if next_pos in recent_positions[-6:]:
                penalty += 4.0

        return penalty

    def _store_snapshot(
        self,
        state: GameState,
        box_count: int,
        visible_item_count: int,
        estimated_capacity: int,
    ) -> None:
        self.last_box_count = box_count
        self.last_visible_item_count = visible_item_count
        self.last_self_radius = int(state.self_radius)
        self.last_estimated_capacity = int(estimated_capacity)

    def _reached_new_area(self, pos: Cell) -> bool:
        if not self.recent_positions:
            return False
        return pos not in list(self.recent_positions)[-6:]


def estimate_capacity(state: GameState) -> int:
    owned_active = sum(1 for bomb in state.bombs if bomb.owner_id == state.agent_id)
    item_on_self = int(state.grid[state.self_pos]) in (ITEM_RADIUS, ITEM_CAPACITY)
    bonus = 1 if item_on_self and int(state.grid[state.self_pos]) == ITEM_CAPACITY else 0
    return max(1, min(5, int(state.self_bombs_left) + owned_active + bonus))
