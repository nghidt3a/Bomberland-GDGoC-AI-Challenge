from dataclasses import replace

from .constants import BOMB_TIMER, HORIZON, INF
from .danger import compute_danger_map
from .search import safe_at, time_expanded_bfs
from .state import BombInfo, GameState


def copy_state_with_new_bomb_at_self(state: GameState, timer: int = BOMB_TIMER) -> GameState:
    new_bomb = BombInfo(pos=state.self_pos, timer=int(timer), owner_id=state.agent_id)
    return replace(
        state,
        bombs=[*state.bombs, new_bomb],
        bomb_positions={*state.bomb_positions, state.self_pos},
    )


def can_place_bomb_safely(state: GameState, horizon: int = HORIZON) -> bool:
    if not state.self_alive:
        return False
    if state.self_bombs_left <= 0:
        return False
    if state.self_pos in state.bomb_positions:
        return False

    simulated = copy_state_with_new_bomb_at_self(state)
    danger_time = compute_danger_map(simulated, horizon)
    # Placing a bomb consumes a full turn during which the agent CANNOT move:
    # it stays on its own cell while every existing bomb ticks down once. So the
    # escape search must start at t=1 (the first real move happens next step),
    # exactly like the post-move escape check. Starting at t=0 hands the agent a
    # phantom extra step of budget and was letting it bury itself next to its
    # own large-radius bombs (engine-verified self-destruct).
    return has_permanent_escape_after_bomb(simulated, danger_time, horizon)


def has_permanent_escape_after_bomb(
    simulated: GameState,
    danger_time,
    horizon: int = HORIZON,
) -> bool:
    """Require an escape target that does not burn in the current danger model."""

    if not safe_at(simulated.self_pos, 1, danger_time):
        return False

    bfs = time_expanded_bfs(simulated, simulated.self_pos, danger_time, horizon, start_time=1)
    return any(int(danger_time[cell]) >= INF for cell, _time in bfs.safe_targets)
