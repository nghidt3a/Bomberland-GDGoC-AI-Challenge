import numpy as np

from .constants import BOMB_TIMER, INF
from .danger import compute_danger_map
from .search import time_expanded_bfs
from .state import GameState


FEATURE_CHANNELS: tuple[str, ...] = (
    "wall",
    "box",
    "item_radius",
    "item_capacity",
    "self",
    "opponents",
    "bombs",
    "bomb_timer_norm",
    "danger_time_norm",
    "safe_reachable_cells",
)


def encode_features(state: GameState, danger_time: np.ndarray | None = None) -> np.ndarray:
    """Starter feature encoder for optional BC/PPO work."""

    danger_time = compute_danger_map(state) if danger_time is None else danger_time
    danger_norm = np.where(danger_time >= INF, 0.0, 1.0 / np.maximum(1.0, danger_time)).astype(np.float32)
    bomb_timer_norm = _bomb_timer_channel(state)
    safe_reachable = _safe_reachable_channel(state, danger_time)

    channels = [
        state.walls.astype(np.float32),
        state.boxes.astype(np.float32),
        state.item_radius.astype(np.float32),
        state.item_capacity.astype(np.float32),
        _one_hot(state.grid.shape, state.self_pos),
        _positions_channel(state.grid.shape, state.opponents),
        _positions_channel(state.grid.shape, state.bomb_positions),
        bomb_timer_norm,
        danger_norm,
        safe_reachable,
    ]
    features = np.stack(channels, axis=0).astype(np.float32, copy=False)
    if features.shape[0] != len(FEATURE_CHANNELS):
        raise RuntimeError("FEATURE_CHANNELS does not match encoded feature count")
    return features


def _one_hot(shape: tuple[int, int], cell: tuple[int, int]) -> np.ndarray:
    arr = np.zeros(shape, dtype=np.float32)
    if 0 <= cell[0] < shape[0] and 0 <= cell[1] < shape[1]:
        arr[cell] = 1.0
    return arr


def _positions_channel(shape: tuple[int, int], cells) -> np.ndarray:
    arr = np.zeros(shape, dtype=np.float32)
    for cell in cells:
        if 0 <= cell[0] < shape[0] and 0 <= cell[1] < shape[1]:
            arr[cell] = 1.0
    return arr


def _bomb_timer_channel(state: GameState) -> np.ndarray:
    arr = np.zeros(state.grid.shape, dtype=np.float32)
    for bomb in state.bombs:
        if 0 <= bomb.pos[0] < state.height and 0 <= bomb.pos[1] < state.width:
            arr[bomb.pos] = max(0.0, min(1.0, float(bomb.timer) / float(BOMB_TIMER)))
    return arr


def _safe_reachable_channel(state: GameState, danger_time: np.ndarray) -> np.ndarray:
    arr = np.zeros(state.grid.shape, dtype=np.float32)
    if not state.self_alive:
        return arr
    for cell in time_expanded_bfs(state, state.self_pos, danger_time).distances:
        arr[cell] = 1.0
    return arr
