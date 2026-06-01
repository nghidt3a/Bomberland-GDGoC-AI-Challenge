from pathlib import Path

from bench.analyze_data_logs import analyze_match


TEAM_ID = "948d41ec-3dbd-4840-9ee5-f0d01cc1b6c0"
LOG_DIR = Path(__file__).resolve().parents[2] / "data_logs"


def match_file(seed: int) -> Path:
    matches = list(LOG_DIR.glob(f"match_*_{seed}.json"))
    assert matches, f"missing data log for seed {seed}"
    return matches[0]


def test_priority_data_log_deaths_remain_replayable():
    expected = {
        109659: "own_bomb_escape_failure",
        225587: "own_bomb_escape_failure",
        648293: "own_bomb_escape_failure",
        836037: "enemy_bomb_trap",
    }

    for seed, death_class in expected.items():
        result = analyze_match(match_file(seed), TEAM_ID)
        assert result["has_target"] is True
        assert result["death"]["class"] == death_class
        assert result["safety_replay"]["available"] is True
        assert result["death_timeline"], f"missing death timeline for seed {seed}"


def test_step500_camping_regressions_are_tracked():
    result = analyze_match(match_file(609286), TEAM_ID)

    assert result["has_target"] is True
    assert result["final_alive"] is True
    assert result["max_stop_streak"] >= 100
    assert "long_stop_streak" in result["issues"]
    assert "low_mobility" in result["issues"]
