"""Cross-turn bomb-radius tracker.

The observation exposes bombs as ``[x, y, timer, owner_id]`` but never their
blast radius, even though the engine LOCKS that radius at placement time
(``engine/game.py``: ``radius = 1 + player.bomb_radius_bonus``). Inferring the
radius from the owner's *current* bonus over-estimates the blast every time the
owner later grabs a radius item — safe, but it makes the agent needlessly timid
around old bombs.

This tracker snapshots the owner's bonus the first turn a bomb appears at a cell
and remembers it for the bomb's whole life. Because a player's ``bomb_radius_bonus``
only ever increases, the first-sighting snapshot is always >= the true locked
radius (exact in the common case, at most +1 in the rare same-step pickup case),
so the result is never an under-estimate — the safety invariant is preserved.

The tracker is keyed by cell. Two live bombs can never share a cell (the engine
forbids placing on an occupied bomb cell), and an entry is dropped the moment its
cell no longer holds a bomb, so a new bomb later placed on a freed cell is
re-snapshotted correctly.
"""

from .constants import MAX_BOMB_RADIUS
from .obs import _normalize_bombs, _normalize_players
from .state import Cell


class BombRadiusTracker:
    def __init__(self) -> None:
        self._locked: dict[Cell, int] = {}

    def update_from_obs(self, obs: dict) -> dict[Cell, int]:
        """Refresh from a raw observation and return ``{cell: locked_radius}``.

        Pass the returned mapping to :func:`person_a_safety.obs.parse_obs` so every
        observed bomb carries its locked radius.
        """

        players = _normalize_players(obs.get("players"))
        bombs = _normalize_bombs(obs.get("bombs"))

        current: dict[Cell, int] = {}
        for row, col, _timer, owner in bombs:
            pos = (int(row), int(col))
            if pos in self._locked:
                # Already seen: keep the radius captured at first sighting.
                current[pos] = self._locked[pos]
                continue
            owner_id = int(owner)
            radius = 1
            if 0 <= owner_id < len(players):
                radius = 1 + int(players[owner_id][4])
            current[pos] = max(1, min(MAX_BOMB_RADIUS, radius))

        # Replacing the dict drops any cell that no longer holds a bomb.
        self._locked = current
        return dict(current)
