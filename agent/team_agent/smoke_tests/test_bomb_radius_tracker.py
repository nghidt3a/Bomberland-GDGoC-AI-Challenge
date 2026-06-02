"""BombRadiusTracker locks a bomb's blast radius at first sighting.

The observation never exposes a bomb's radius, and a player's radius bonus only
ever grows. Snapshotting the owner's bonus the first turn a bomb appears keeps
the (correct, engine-locked) radius even after the owner grabs more radius items,
instead of over-estimating the blast forever. The snapshot is never an
under-estimate, so the self-death safety invariant is preserved.
"""

from grid_helpers import empty_grid, make_obs, make_player
from person_a_safety.bomb_tracker import BombRadiusTracker
from person_a_safety.constants import BOMB_TIMER
from person_a_safety.danger import bomb_radius
from person_a_safety.obs import parse_obs


def _players(self_cell, enemy_cell, enemy_bonus):
    return [
        make_player(*self_cell),
        make_player(*enemy_cell, radius_bonus=enemy_bonus),
        make_player(11, 11, alive=0),
        make_player(11, 1, alive=0),
    ]


def test_radius_locked_at_first_sighting():
    grid = empty_grid()
    obs1 = make_obs(grid, _players((6, 6), (1, 1), 1), bombs=[[1, 1, BOMB_TIMER, 1]])
    tracker = BombRadiusTracker()

    lookup1 = tracker.update_from_obs(obs1)
    assert lookup1[(1, 1)] == 2  # 1 + bonus(1)

    # The owner later collects radius items (bonus 1 -> 3) but the live bomb must
    # keep the radius it was placed with.
    obs2 = make_obs(grid, _players((6, 6), (1, 1), 3), bombs=[[1, 1, BOMB_TIMER - 1, 1]])
    lookup2 = tracker.update_from_obs(obs2)
    assert lookup2[(1, 1)] == 2  # locked, NOT 4

    state = parse_obs(obs2, 0, radius_lookup=lookup2)
    assert state.bombs[0].radius == 2
    assert bomb_radius(state, state.bombs[0]) == 2


def test_entry_dropped_then_resnapshot_on_same_cell():
    grid = empty_grid()
    tracker = BombRadiusTracker()
    tracker.update_from_obs(make_obs(grid, _players((6, 6), (1, 1), 0), bombs=[[1, 1, 3, 1]]))

    # Bomb gone -> the locked entry is forgotten.
    lookup = tracker.update_from_obs(make_obs(grid, _players((6, 6), (1, 1), 0), bombs=None))
    assert (1, 1) not in lookup

    # A new bomb later placed on the same cell after the owner upgraded must be
    # re-snapshotted to the new (higher) radius, not the stale one.
    lookup2 = tracker.update_from_obs(
        make_obs(grid, _players((6, 6), (1, 1), 2), bombs=[[1, 1, BOMB_TIMER, 1]])
    )
    assert lookup2[(1, 1)] == 3  # 1 + bonus(2)


def test_fallback_inference_without_lookup():
    grid = empty_grid()
    obs = make_obs(grid, _players((6, 6), (1, 1), 2), bombs=[[1, 1, 3, 1]])
    state = parse_obs(obs, 0)  # no radius_lookup

    assert state.bombs[0].radius is None
    assert bomb_radius(state, state.bombs[0]) == 3  # inferred 1 + bonus(2)
