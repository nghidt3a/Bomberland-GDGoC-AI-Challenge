"""Radius items stay desirable until the blast cap (top agents farm radius ~3.7).

The old curve lost interest after radius 3 (value 0.85); the new curve keeps
radius worth a detour through radius 4 (blast 5 == engine cap) and only then
drops off. Bigger blast => more boxes per bomb and a wider kill threat.
"""

from grid_helpers import empty_grid, make_obs, make_player
from person_a_safety.constants import ITEM_RADIUS
from person_a_safety.obs import parse_obs
from person_b_strategy.scoring import item_value


def _state(radius_bonus):
    grid = empty_grid()
    grid[5, 6] = ITEM_RADIUS
    players = [
        make_player(5, 5, radius_bonus=radius_bonus),
        make_player(1, 1, alive=0),
        make_player(11, 11, alive=0),
        make_player(11, 1, alive=0),
    ]
    return parse_obs(make_obs(grid, players), 0)


def test_radius_wanted_through_blast_four():
    # self_radius = 1 + radius_bonus
    v_r4 = item_value(_state(radius_bonus=3), (5, 6))  # self_radius 4
    assert v_r4 > 0.85  # used to be 0.85 (no longer worth it); now still wanted


def test_radius_falls_off_past_cap():
    v_r4 = item_value(_state(radius_bonus=3), (5, 6))  # self_radius 4
    v_r5 = item_value(_state(radius_bonus=4), (5, 6))  # self_radius 5 == blast cap
    assert v_r5 < v_r4


def test_low_radius_still_most_valued():
    v_low = item_value(_state(radius_bonus=0), (5, 6))   # self_radius 1
    v_r4 = item_value(_state(radius_bonus=3), (5, 6))    # self_radius 4
    assert v_low > v_r4
