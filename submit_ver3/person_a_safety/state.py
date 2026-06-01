from dataclasses import dataclass
from typing import List, Set, Tuple

import numpy as np

Cell = Tuple[int, int]


@dataclass(frozen=True)
class BombInfo:
    pos: Cell
    timer: int
    owner_id: int


@dataclass
class GameState:
    grid: np.ndarray
    players: np.ndarray
    agent_id: int
    bombs: List[BombInfo]
    walls: np.ndarray
    boxes: np.ndarray
    item_radius: np.ndarray
    item_capacity: np.ndarray
    bomb_positions: Set[Cell]
    self_pos: Cell
    self_alive: bool
    self_bombs_left: int
    self_radius: int
    opponents: List[Cell]
    alive_players: List[Cell]

    @property
    def height(self) -> int:
        return int(self.grid.shape[0])

    @property
    def width(self) -> int:
        return int(self.grid.shape[1])
