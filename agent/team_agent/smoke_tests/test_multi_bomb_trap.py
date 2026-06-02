"""Multi-bomb: a 2nd live bomb is allowed and credited when productive.

Top agents keep 2-3 bombs out at once (capacity items) to farm faster and seal a
second escape. With spare ``bombs_left`` and an existing own bomb elsewhere, the
agent must still be allowed to place a productive 2nd bomb, and that bomb must be
credited (box_bomb) rather than dismissed as useless.
"""

import numpy as np

from grid_helpers import empty_grid, make_obs, make_player
from person_a_safety.bomb import can_place_bomb_safely
from person_a_safety.constants import BOX, PLACE_BOMB
from person_a_safety.danger import compute_hazard_map
from person_a_safety.obs import parse_obs
from person_b_strategy.scoring import score_action_components


def test_second_bomb_allowed_and_credited():
    grid = empty_grid()
    grid[6, 7] = BOX
    grid[6, 8] = BOX
    players = [
        make_player(6, 6, bombs_left=2, radius_bonus=2),  # holds a 2nd bomb
        make_player(1, 1, alive=0),
        make_player(11, 11, alive=0),
        make_player(11, 1, alive=0),
    ]
    # We already own a live bomb far away at (1,5); placing a 2nd next to boxes.
    state = parse_obs(make_obs(grid, players, bombs=[[1, 5, 5, 0]]), 0)
    hazard = compute_hazard_map(state)

    assert can_place_bomb_safely(state) is True  # the 2nd bomb is still escapable
    comps = score_action_components(state, PLACE_BOMB, hazard)
    assert comps["box_bomb"] > 0.0                # it destroys boxes
    assert comps["useless_bomb_penalty"] == 0.0   # productive -> not penalised
