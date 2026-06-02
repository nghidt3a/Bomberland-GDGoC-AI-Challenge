from dataclasses import dataclass
from typing import List, Optional, Set, Tuple

import numpy as np

Cell = Tuple[int, int]


@dataclass(frozen=True)
class BombInfo:
    pos: Cell
    timer: int
    owner_id: int
    # Blast radius LOCKED at placement time. The observation never exposes it, so
    # callers that know the true radius (the cross-turn radius tracker) pass it
    # here; ``None`` means "infer from the owner's current bonus" (see
    # ``danger.bomb_radius``). Kept last with a default so existing positional
    # constructions ``BombInfo(pos, timer, owner_id)`` stay valid.
    radius: Optional[int] = None


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
