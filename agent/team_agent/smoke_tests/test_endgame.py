"""Endgame mode (technique 05): close the game by the step-500 tie-break — defend
the rank when leading near 500, force kills when losing / finishing / in a 1v1.
"""

from types import SimpleNamespace

from grid_helpers import empty_grid, make_obs, make_player
from person_a_safety.obs import parse_obs
from person_b_strategy.scoring import endgame_adjust, phase_profile


def _weights():
    return phase_profile(200, style="balanced").weights  # mid base


def _state(n_alive_opponents):
    players = [make_player(6, 6)]
    for i in range(3):
        players.append(make_player(1, 1 + i, alive=1 if i < n_alive_opponents else 0))
    return parse_obs(make_obs(empty_grid(), players), 0)


def test_defend_when_leading_near_500():
    w = _weights()
    out = endgame_adjust(w, _state(3), SimpleNamespace(proxy_kills=1, proxy_score=5.0), turn_index=450)
    assert out.survival > w.survival
    assert out.danger > w.danger
    assert out.pressure < w.pressure


def test_force_kill_when_losing_near_500():
    w = _weights()
    out = endgame_adjust(w, _state(3), SimpleNamespace(proxy_kills=0, proxy_score=0.0), turn_index=450)
    assert out.pressure > w.pressure
    assert out.kill > w.kill
    assert out.seal > w.seal


def test_duel_lowers_enemy_risk():
    w = _weights()
    duel = endgame_adjust(w, _state(1), SimpleNamespace(proxy_kills=0, proxy_score=0.0), turn_index=450)
    assert duel.enemy_risk < w.enemy_risk


def test_no_endgame_in_midgame():
    w = _weights()
    out = endgame_adjust(w, _state(3), SimpleNamespace(proxy_kills=0, proxy_score=0.0), turn_index=200)
    assert out == w  # not near 500 and 4 players alive -> untouched
