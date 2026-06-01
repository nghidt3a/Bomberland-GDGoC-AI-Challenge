import numpy as np

from .constants import INF
from .danger import compute_danger_map
from .state import GameState


def encode_features(state: GameState, danger_time: np.ndarray | None = None) -> np.ndarray:
    """Starter feature encoder for optional BC/PPO work."""

    danger_time = compute_danger_map(state) if danger_time is None else danger_time
    danger_norm = np.where(danger_time >= INF, 0.0, 1.0 / np.maximum(1.0, danger_time)).astype(np.float32)

    channels = [
        state.walls.astype(np.float32),
        state.boxes.astype(np.float32),
        state.item_radius.astype(np.float32),
        state.item_capacity.astype(np.float32),
        _one_hot(state.grid.shape, state.self_pos),
        _positions_channel(state.grid.shape, state.opponents),
        _positions_channel(state.grid.shape, state.bomb_positions),
        danger_norm,
    ]
    return np.stack(channels, axis=0)


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
