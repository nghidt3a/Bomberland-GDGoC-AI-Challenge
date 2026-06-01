"""Lock ACTION_DELTAS to the REAL engine movement semantics (doc P0 #1).

The uploaded fix doc proposed "correcting" ACTION_DELTAS to a row-col scheme.
That would be WRONG for this engine: engine/game.py maps LEFT/RIGHT to the FIRST
coordinate (x == row) and UP/DOWN to the SECOND (y == col):

    LEFT  -> dx=-1   RIGHT -> dx=+1   UP -> dy=-1   DOWN -> dy=+1   (x=row, y=col)

so the existing ACTION_DELTAS (applied to a (row, col) cell) is already correct.
This test drives the actual engine so any future "fix" that breaks the mapping
fails loudly instead of silently making the agent walk into fire.
"""

from engine.game import BomberEnv
from engine.map import Map

from person_a_safety.constants import ACTION_DELTAS, DOWN, LEFT, RIGHT, STOP, UP


def _engine_destination(action: int) -> tuple[int, int]:
    env = BomberEnv(seed=0)
    env.reset(seed=0)

    player = env.players[0]
    player.x, player.y = 6, 6
    # Open the centre cell and its four neighbours so the move is never blocked.
    for cell in ((6, 6), (5, 6), (7, 6), (6, 5), (6, 7)):
        env.map.grid[cell] = Map.GRASS
    env.bombs = []

    env.step([action, STOP, STOP, STOP])
    return (env.players[0].x, env.players[0].y)


def test_action_deltas_match_real_engine():
    for action in (LEFT, RIGHT, UP, DOWN):
        dr, dc = ACTION_DELTAS[action]
        expected = (6 + dr, 6 + dc)
        assert _engine_destination(action) == expected, (
            f"ACTION_DELTAS[{action}] disagrees with the engine"
        )


def test_engine_uses_row_for_left_right_and_col_for_up_down():
    # Explicit, human-readable spelling of the (quirky) engine convention.
    assert _engine_destination(RIGHT) == (7, 6)  # row + 1
    assert _engine_destination(LEFT) == (5, 6)   # row - 1
    assert _engine_destination(DOWN) == (6, 7)   # col + 1
    assert _engine_destination(UP) == (6, 5)     # col - 1
