"""The three submission styles order their weights as intended.

Same safety core, different temperament: ``aggressive`` leans into kills/pressure
and tolerates proximity; ``safe`` leans into survival/farming and avoids fights;
``balanced`` sits between. The per-phase profile scales by style.
"""

from person_b_strategy.scoring import phase_profile


def _weights(style, turn=200):
    return phase_profile(turn, style=style).weights


def test_offense_ordered_aggressive_balanced_safe():
    agg, bal, safe = _weights("aggressive"), _weights("balanced"), _weights("safe")
    assert agg.pressure > bal.pressure > safe.pressure
    assert agg.trap > bal.trap > safe.trap
    assert agg.kill > bal.kill > safe.kill


def test_safety_ordered_safe_balanced_aggressive():
    agg, bal, safe = _weights("aggressive"), _weights("balanced"), _weights("safe")
    assert safe.survival > bal.survival
    assert safe.enemy_risk > bal.enemy_risk > agg.enemy_risk
    assert safe.danger > bal.danger
    assert agg.stop < bal.stop < safe.stop


def test_balanced_is_unscaled_base():
    # balanced applies no multiplier, so it equals the raw phase base.
    from person_b_strategy.scoring import _phase_base

    base = _phase_base(200).weights
    bal = _weights("balanced")
    assert bal == base


def test_style_holds_across_phases():
    for turn in (0, 200, 400):
        assert _weights("aggressive", turn).pressure > _weights("safe", turn).pressure
