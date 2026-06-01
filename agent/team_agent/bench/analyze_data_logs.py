import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


AGENT_DIR = Path(__file__).resolve().parents[1]
if str(AGENT_DIR) not in sys.path:
    sys.path.insert(0, str(AGENT_DIR))


STOP = 0
LEFT = 1
RIGHT = 2
UP = 3
DOWN = 4
PLACE_BOMB = 5

ACTION_NAMES = {
    STOP: "STOP",
    LEFT: "LEFT",
    RIGHT: "RIGHT",
    UP: "UP",
    DOWN: "DOWN",
    PLACE_BOMB: "PLACE_BOMB",
}

WALL = 1
BOX = 2
ITEM_RADIUS = 3
ITEM_CAPACITY = 4
MAX_BOMB_RADIUS = 5

PHASES = {
    "early": (0, 149),
    "mid": (150, 349),
    "late": (350, 10**9),
}


def action_name(action: Any) -> str:
    try:
        return ACTION_NAMES.get(int(action), f"INVALID_{action}")
    except Exception:
        return "INVALID"


def phase_name(step: int) -> str:
    for name, (lo, hi) in PHASES.items():
        if lo <= int(step) <= hi:
            return name
    return "late"


def count_tiles(grid: list[list[int]], values: set[int]) -> int:
    return sum(1 for row in grid for tile in row if int(tile) in values)


def player_alive(history_row: dict[str, Any], player_idx: int) -> bool:
    return bool(history_row.get("alive", [False] * 4)[player_idx])


def player_row(history_row: dict[str, Any], player_idx: int) -> list[int]:
    return [int(value) for value in history_row["players"][player_idx]]


def player_pos(history_row: dict[str, Any], player_idx: int) -> tuple[int, int]:
    player = player_row(history_row, player_idx)
    return int(player[0]), int(player[1])


def manhattan(a: tuple[int, int], b: tuple[int, int]) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def in_bounds(grid: list[list[int]], cell: tuple[int, int]) -> bool:
    return 0 <= cell[0] < len(grid) and 0 <= cell[1] < len(grid[0])


def bomb_radius(players: list[list[int]], owner_id: int) -> int:
    if 0 <= owner_id < len(players):
        return max(1, min(MAX_BOMB_RADIUS, 1 + int(players[owner_id][4])))
    return 1


def blast_cells(grid: list[list[int]], pos: tuple[int, int], radius: int) -> set[tuple[int, int]]:
    cells = {pos}
    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        row, col = pos
        for _ in range(int(radius)):
            row += dr
            col += dc
            cell = (row, col)
            if not in_bounds(grid, cell):
                break
            tile = int(grid[row][col])
            if tile == WALL:
                break
            cells.add(cell)
            if tile == BOX:
                break
    return cells


def action_from_transition(history: list[dict[str, Any]], row_idx: int, player_idx: int) -> int | None:
    actions = history[row_idx].get("actions")
    if actions is None:
        return None
    try:
        return int(actions[player_idx])
    except Exception:
        return None


def bomb_key(bomb: list[Any]) -> tuple[int, int, int]:
    return int(bomb[0]), int(bomb[1]), int(bomb[3])


def find_death_step(history: list[dict[str, Any]], player_idx: int) -> int | None:
    previous_alive = player_alive(history[0], player_idx)
    for row in history[1:]:
        alive = player_alive(row, player_idx)
        if previous_alive and not alive:
            return int(row["step"])
        previous_alive = alive
    return None


def max_ping_pong_streak(positions: list[tuple[int, tuple[int, int]]]) -> tuple[int, int]:
    if len(positions) < 4:
        return 0, 0

    max_streak = 0
    occurrences = 0
    current = 0
    cells = [pos for _step, pos in positions]
    for idx in range(2, len(cells)):
        if cells[idx] == cells[idx - 2] and cells[idx] != cells[idx - 1]:
            current += 1
            occurrences += 1
            max_streak = max(max_streak, current + 2)
        else:
            current = 0
    return max_streak, occurrences


def init_phase_metrics() -> dict[str, dict[str, Any]]:
    return {
        phase: {
            "actions": {name: 0 for name in ACTION_NAMES.values()},
            "steps_alive": 0,
            "unique_cells": 0,
            "bombs": 0,
            "stop_streak_max": 0,
        }
        for phase in PHASES
    }


def near_bombs(history_row: dict[str, Any], player_idx: int, radius: int = 6) -> list[str]:
    pos = player_pos(history_row, player_idx)
    result = []
    for raw_bomb in history_row.get("bombs") or []:
        bomb = [int(value) for value in raw_bomb]
        bomb_pos = (bomb[0], bomb[1])
        if manhattan(pos, bomb_pos) <= radius:
            result.append(f"({bomb[0]},{bomb[1]},t{bomb[2]},o{bomb[3]})")
    return result


def timeline_issue_tags(
    history_row: dict[str, Any],
    player_idx: int,
    death_step: int | None,
    death_class: str,
) -> list[str]:
    tags = []
    step = int(history_row["step"])
    pos = player_pos(history_row, player_idx)
    action = None
    actions = history_row.get("actions")
    if actions is not None:
        action = int(actions[player_idx])

    if action == STOP:
        tags.append("stop")
    for raw_bomb in history_row.get("bombs") or []:
        bomb = [int(value) for value in raw_bomb]
        grid = history_row["map"]
        radius = bomb_radius(history_row["players"], int(bomb[3]))
        if int(bomb[2]) <= 2 and pos in blast_cells(grid, (bomb[0], bomb[1]), radius):
            tags.append("danger_line")
            if int(bomb[3]) == player_idx:
                tags.append("own_bomb_line")
            else:
                tags.append("enemy_bomb_line")
    if death_step is not None and step == death_step:
        tags.append(f"death:{death_class}")
    return tags


def classify_death(
    history: list[dict[str, Any]],
    player_idx: int,
    death_step: int | None,
    stop_streak_max: int,
) -> dict[str, Any]:
    if death_step is None:
        return {
            "class": "survived",
            "exploding_bombs": [],
            "reason": "Agent sống đến hết trận.",
        }

    index_by_step = {int(row["step"]): idx for idx, row in enumerate(history)}
    row_idx = index_by_step.get(int(death_step))
    if row_idx is None or row_idx == 0:
        return {
            "class": "unknown_death",
            "exploding_bombs": [],
            "reason": "Không tìm thấy state ngay trước khi chết.",
        }

    previous = history[row_idx - 1]
    current = history[row_idx]
    death_pos = player_pos(current, player_idx)
    current_keys = {bomb_key(bomb) for bomb in current.get("bombs") or []}
    exploding = []

    for raw_bomb in previous.get("bombs") or []:
        bomb = [int(value) for value in raw_bomb]
        key = bomb_key(bomb)
        if bomb[2] > 1 and key in current_keys:
            continue
        radius = bomb_radius(previous["players"], bomb[3])
        cells = blast_cells(previous["map"], (bomb[0], bomb[1]), radius)
        if death_pos in cells:
            exploding.append(
                {
                    "pos": [bomb[0], bomb[1]],
                    "timer": bomb[2],
                    "owner": bomb[3],
                    "radius": radius,
                }
            )

    if any(bomb["owner"] == player_idx for bomb in exploding):
        return {
            "class": "own_bomb_escape_failure",
            "exploding_bombs": exploding,
            "reason": "Chết trong blast line của bom mình gần thời điểm nổ.",
        }
    if exploding:
        return {
            "class": "enemy_bomb_trap",
            "exploding_bombs": exploding,
            "reason": "Chết trong blast line của bom đối thủ gần thời điểm nổ.",
        }

    local_stop = 0
    for row in history[max(1, row_idx - 8) : row_idx + 1]:
        action = action_from_transition(history, row_idx=history.index(row), player_idx=player_idx)
        if action == STOP:
            local_stop += 1
    if local_stop >= 4 or stop_streak_max >= 20:
        return {
            "class": "loop_or_camping_death",
            "exploding_bombs": exploding,
            "reason": "Chết sau chuỗi đứng yên/lặp lại dài, cần xem lại anti-loop và escape bias.",
        }

    return {
        "class": "unknown_death",
        "exploding_bombs": exploding,
        "reason": "Chưa phân loại được từ log heuristic.",
    }


def death_timeline(
    history: list[dict[str, Any]],
    player_idx: int,
    death_step: int | None,
    death_class: str,
) -> list[dict[str, Any]]:
    if death_step is None:
        return []

    rows = [
        row
        for row in history
        if int(death_step) - 8 <= int(row["step"]) <= int(death_step)
    ]
    timeline = []
    for row in rows:
        actions = row.get("actions")
        action = None if actions is None else int(actions[player_idx])
        timeline.append(
            {
                "step": int(row["step"]),
                "pos": list(player_pos(row, player_idx)),
                "action": action_name(action),
                "alive": player_alive(row, player_idx),
                "near_bombs": near_bombs(row, player_idx),
                "issue_tags": timeline_issue_tags(row, player_idx, death_step, death_class),
            }
        )
    return timeline


def analyze_bombs(history: list[dict[str, Any]], player_idx: int) -> dict[str, Any]:
    events = []
    previous_bombs: set[tuple[int, int, int]] = set()

    for row_idx, row in enumerate(history):
        current_bombs = {bomb_key(bomb) for bomb in row.get("bombs") or []}
        for raw_bomb in row.get("bombs") or []:
            bomb = [int(value) for value in raw_bomb]
            key = bomb_key(bomb)
            if key in previous_bombs or bomb[3] != player_idx:
                continue

            pos = (bomb[0], bomb[1])
            radius = bomb_radius(row["players"], player_idx)
            cells = blast_cells(row["map"], pos, radius)
            target_boxes = sorted([cell for cell in cells if int(row["map"][cell[0]][cell[1]]) == BOX])
            enemies_in_blast = []
            for opp_idx, player in enumerate(row["players"]):
                if opp_idx == player_idx or int(player[2]) != 1:
                    continue
                opp_pos = (int(player[0]), int(player[1]))
                if opp_pos in cells:
                    enemies_in_blast.append(opp_idx)

            destroyed = set()
            for future in history[row_idx + 1 : min(len(history), row_idx + 11)]:
                for cell in target_boxes:
                    if cell not in destroyed and int(future["map"][cell[0]][cell[1]]) != BOX:
                        destroyed.add(cell)

            events.append(
                {
                    "step": int(row["step"]),
                    "pos": [pos[0], pos[1]],
                    "timer": bomb[2],
                    "radius": radius,
                    "target_boxes": len(target_boxes),
                    "destroyed_boxes": len(destroyed),
                    "enemies_in_blast": enemies_in_blast,
                    "value": len(destroyed) + len(enemies_in_blast),
                }
            )
        previous_bombs = current_bombs

    no_value = [event for event in events if event["target_boxes"] == 0 and not event["enemies_in_blast"]]
    useful = [event for event in events if event["destroyed_boxes"] > 0 or event["enemies_in_blast"]]
    burst_pairs = 0
    for prev, cur in zip(events, events[1:]):
        if int(cur["step"]) - int(prev["step"]) <= 3:
            burst_pairs += 1

    return {
        "events": events,
        "own_bombs_observed": len(events),
        "useful_bombs": len(useful),
        "no_value_bombs": len(no_value),
        "destroyed_boxes_proxy": sum(event["destroyed_boxes"] for event in events),
        "burst_pairs_le_3_steps": burst_pairs,
    }


def safety_replay(history: list[dict[str, Any]], player_idx: int) -> dict[str, Any]:
    try:
        from person_a_safety.danger import compute_hazard_map
        from person_a_safety.masks import safe_actions
        from person_a_safety.obs import parse_obs
        from person_a_safety.shield import final_shield
    except Exception as exc:
        return {
            "available": False,
            "error": str(exc),
            "checked_actions": 0,
            "unsafe_actions": 0,
            "shield_changes": 0,
            "examples": [],
        }

    checked = 0
    unsafe = 0
    shield_changes = 0
    examples = []
    for row_idx in range(1, len(history)):
        previous = history[row_idx - 1]
        current = history[row_idx]
        if not player_alive(previous, player_idx):
            continue
        action = action_from_transition(history, row_idx, player_idx)
        if action is None:
            continue

        obs = {
            "map": previous["map"],
            "players": previous["players"],
            "bombs": previous.get("bombs") or [],
        }
        try:
            state = parse_obs(obs, player_idx)
            hazard = compute_hazard_map(state)
            mask = safe_actions(state, hazard)
            shielded = int(final_shield(action, state, hazard))
        except Exception as exc:
            return {
                "available": False,
                "error": f"Replay failed at step {current['step']}: {exc}",
                "checked_actions": checked,
                "unsafe_actions": unsafe,
                "shield_changes": shield_changes,
                "examples": examples,
            }

        checked += 1
        is_unsafe = not bool(mask[action]) if 0 <= action < len(mask) else True
        changed = shielded != action
        if is_unsafe:
            unsafe += 1
        if changed:
            shield_changes += 1
        if (is_unsafe or changed) and len(examples) < 20:
            examples.append(
                {
                    "step": int(current["step"]),
                    "pos": list(player_pos(previous, player_idx)),
                    "action": action_name(action),
                    "safe_actions": [ACTION_NAMES[a] for a in range(len(mask)) if bool(mask[a])],
                    "shielded": action_name(shielded),
                }
            )

    return {
        "available": True,
        "error": None,
        "checked_actions": checked,
        "unsafe_actions": unsafe,
        "shield_changes": shield_changes,
        "examples": examples,
    }


def analyze_match(path: Path, team_id: str) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    team_ids = list(data.get("team_ids") or data.get("meta", {}).get("agent_names") or [])
    if team_id not in team_ids:
        return {"file": path.name, "has_target": False}

    player_idx = team_ids.index(team_id)
    history = data.get("history", [])
    death_step = find_death_step(history, player_idx)
    action_counts = {name: 0 for name in ACTION_NAMES.values()}
    phase_metrics = init_phase_metrics()
    phase_cells = {phase: set() for phase in PHASES}
    positions: list[tuple[int, tuple[int, int]]] = []
    stop_streak = 0
    max_stop_streak = 0
    bomb_steps = []
    last_alive_row = history[0]

    for row_idx, row in enumerate(history):
        step = int(row["step"])
        alive = player_alive(row, player_idx)
        phase = phase_name(step)
        if alive:
            pos = player_pos(row, player_idx)
            positions.append((step, pos))
            phase_cells[phase].add(pos)
            phase_metrics[phase]["steps_alive"] += 1
            last_alive_row = row

        if row_idx == 0 or not player_alive(history[row_idx - 1], player_idx):
            continue

        action = action_from_transition(history, row_idx, player_idx)
        if action is None or action not in ACTION_NAMES:
            continue

        name = ACTION_NAMES[action]
        action_counts[name] += 1
        phase_metrics[phase]["actions"][name] += 1
        if action == PLACE_BOMB:
            bomb_steps.append(step)
            phase_metrics[phase]["bombs"] += 1
        if action == STOP:
            stop_streak += 1
            max_stop_streak = max(max_stop_streak, stop_streak)
            phase_metrics[phase]["stop_streak_max"] = max(
                int(phase_metrics[phase]["stop_streak_max"]),
                stop_streak,
            )
        else:
            stop_streak = 0

    for phase, cells in phase_cells.items():
        phase_metrics[phase]["unique_cells"] = len(cells)

    ping_pong_max, ping_pong_count = max_ping_pong_streak(positions)
    bomb_metrics = analyze_bombs(history, player_idx)
    death = classify_death(history, player_idx, death_step, max_stop_streak)
    timeline = death_timeline(history, player_idx, death_step, death["class"])
    replay = safety_replay(history, player_idx)

    start_row = history[0]
    start_player = player_row(start_row, player_idx)
    last_player = player_row(last_alive_row, player_idx)
    runtime = data.get("runtime_stats", {}).get(str(player_idx), {})
    survival_steps = int(data.get("survival_steps", [0, 0, 0, 0])[player_idx])
    unique_cells = len({pos for _step, pos in positions})
    mobility_rate = unique_cells / max(1, survival_steps)

    issues = []
    if death["class"] == "own_bomb_escape_failure":
        issues.append("own_bomb_escape_failure")
    elif death["class"] == "enemy_bomb_trap":
        issues.append("enemy_bomb_trap")
    elif death["class"] != "survived":
        issues.append(death["class"])
    if survival_steps < 150:
        issues.append("early_death")
    if max_stop_streak >= 20:
        issues.append("long_stop_streak")
    if ping_pong_max >= 8:
        issues.append("ping_pong_loop")
    if mobility_rate < 0.12:
        issues.append("low_mobility")
    if bomb_metrics["own_bombs_observed"] <= 3:
        issues.append("bomb_underuse")
    if bomb_metrics["no_value_bombs"] >= max(3, bomb_metrics["own_bombs_observed"] // 2):
        issues.append("low_value_bombs")
    if replay["available"] and replay["unsafe_actions"] > 0:
        issues.append("current_safety_replay_flags")
    if survival_steps >= 500 and int(data.get("ranks", [0, 0, 0, 0])[player_idx]) >= 2:
        issues.append("step500_tiebreak_weak")

    return {
        "file": path.name,
        "seed": data.get("seed"),
        "has_target": True,
        "player_index": player_idx,
        "rank": int(data.get("ranks", [0, 0, 0, 0])[player_idx]),
        "survival_steps": survival_steps,
        "death_step": death_step,
        "final_alive": player_alive(history[-1], player_idx),
        "action_counts": action_counts,
        "phase_metrics": phase_metrics,
        "max_stop_streak": max_stop_streak,
        "bomb_steps": bomb_steps,
        "bomb_count": len(bomb_steps),
        "unique_cells_while_alive": unique_cells,
        "mobility_rate": mobility_rate,
        "last_alive_pos": list(player_pos(last_alive_row, player_idx)),
        "start_radius": 1 + int(start_player[4]),
        "max_radius": max(1 + int(row["players"][player_idx][4]) for row in history if player_alive(row, player_idx)),
        "end_radius": 1 + int(last_player[4]),
        "start_bombs_left": int(start_player[3]),
        "max_bombs_left": max(int(row["players"][player_idx][3]) for row in history if player_alive(row, player_idx)),
        "end_bombs_left": int(last_player[3]),
        "start_boxes": count_tiles(start_row["map"], {BOX}),
        "end_boxes_while_alive": count_tiles(last_alive_row["map"], {BOX}),
        "start_items": count_tiles(start_row["map"], {ITEM_RADIUS, ITEM_CAPACITY}),
        "end_items_while_alive": count_tiles(last_alive_row["map"], {ITEM_RADIUS, ITEM_CAPACITY}),
        "ping_pong_max": ping_pong_max,
        "ping_pong_count": ping_pong_count,
        "bomb_metrics": bomb_metrics,
        "death": death,
        "death_timeline": timeline,
        "safety_replay": replay,
        "runtime": runtime,
        "issues": issues,
    }


def fmt_bool(value: bool) -> str:
    return "yes" if value else "no"


def md_table(headers: list[str], rows: list[list[Any]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(value) for value in row) + " |")
    return "\n".join(lines)


def issue_label(issue: str) -> str:
    labels = {
        "own_bomb_escape_failure": "chết do bom mình / thoát bom kém",
        "enemy_bomb_trap": "chết do bom đối thủ",
        "unknown_death": "death chưa phân loại",
        "early_death": "chết sớm",
        "long_stop_streak": "STOP quá dài",
        "ping_pong_loop": "lặp A-B-A-B",
        "low_mobility": "di chuyển ít",
        "bomb_underuse": "ít đặt bom",
        "low_value_bombs": "bom ít giá trị",
        "current_safety_replay_flags": "safety replay flag",
        "step500_tiebreak_weak": "sống 500 nhưng tie-break yếu",
    }
    return labels.get(issue, issue)


def render_summary(matches: list[dict[str, Any]], team_id: str, log_dir: Path) -> str:
    valid = [match for match in matches if match.get("has_target")]
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    avg_rank = sum(match["rank"] for match in valid) / max(1, len(valid))
    avg_survival = sum(match["survival_steps"] for match in valid) / max(1, len(valid))
    survived = sum(1 for match in valid if match["final_alive"])
    early_deaths = sum(1 for match in valid if match["survival_steps"] < 150)
    death_count = sum(1 for match in valid if not match["final_alive"])
    long_stop = [match for match in valid if match["max_stop_streak"] >= 20]

    rows = []
    for match in valid:
        rows.append(
            [
                match["file"],
                match["seed"],
                match["player_index"],
                match["rank"],
                match["survival_steps"],
                match["death_step"] if match["death_step"] is not None else "-",
                fmt_bool(match["final_alive"]),
                match["bomb_count"],
                match["max_stop_streak"],
                match["unique_cells_while_alive"],
                ", ".join(issue_label(issue) for issue in match["issues"][:4]) or "-",
            ]
        )

    issue_counts: dict[str, int] = {}
    for match in valid:
        for issue in match["issues"]:
            issue_counts[issue] = issue_counts.get(issue, 0) + 1
    issue_rows = [
        [issue_label(issue), count]
        for issue, count in sorted(issue_counts.items(), key=lambda item: (-item[1], item[0]))
    ]

    lines = [
        "# Báo Cáo Tổng Hợp Data Logs",
        "",
        f"- Team id: `{team_id}`",
        f"- Log dir: `{log_dir}`",
        f"- Generated at: `{generated_at}`",
        f"- Số trận có team id: {len(valid)}/{len(matches)}",
        f"- Average rank: {avg_rank:.2f} (rank càng nhỏ càng tốt)",
        f"- Average survival: {avg_survival:.1f} steps",
        f"- Sống tới step 500: {survived}/{len(valid)}",
        f"- Chết trước step 500: {death_count}/{len(valid)}",
        f"- Chết sớm trước step 150: {early_deaths}/{len(valid)}",
        f"- Trận có STOP streak >= 20: {len(long_stop)}/{len(valid)}",
        "",
        "## Bảng Tổng Hợp Trận",
        "",
        md_table(
            [
                "file",
                "seed",
                "idx",
                "rank",
                "survival",
                "death",
                "alive500",
                "bombs",
                "max STOP",
                "unique cells",
                "issues",
            ],
            rows,
        ),
        "",
        "## Tần Suất Vấn Đề",
        "",
        md_table(["issue", "matches"], issue_rows) if issue_rows else "Không có issue flag.",
        "",
        "## Nhận Định Nhanh",
        "",
        "- Runtime log hiện tại không ghi nhận timeout/error/invalid action nổi bật.",
        "- Vấn đề lớn nhất là survival không ổn định: một nửa số trận chết trước step 500.",
        "- Nhiều trận có STOP streak dài, làm giảm progress và có thể làm agent bị trap.",
        "- Một số trận sống đến step 500 nhưng rank vẫn thấp, cần cải thiện tie-break bằng box/item/kill/progress.",
        "",
    ]
    return "\n".join(lines)


def render_safety(matches: list[dict[str, Any]]) -> str:
    valid = [match for match in matches if match.get("has_target")]
    rows = []
    for match in valid:
        replay = match["safety_replay"]
        rows.append(
            [
                match["seed"],
                match["death"]["class"],
                match["death_step"] if match["death_step"] is not None else "-",
                match["last_alive_pos"],
                replay["checked_actions"],
                replay["unsafe_actions"],
                replay["shield_changes"],
            ]
        )

    lines = [
        "# Vấn Đề Person A Safety",
        "",
        "Báo cáo này tách 2 loại bằng chứng:",
        "",
        "- Death classification là heuristic từ log: xem bomb timer/blast line quanh death step.",
        "- Current-code replay check chạy lại `parse_obs`, `compute_danger_map`, `safe_actions`, `final_shield` trên code hiện tại; nó không đảm bảo giống 100% bản đã submit.",
        "",
        "## Tổng Hợp Safety",
        "",
        md_table(
            [
                "seed",
                "death class",
                "death step",
                "last alive pos",
                "checked",
                "unsafe replay",
                "shield changes",
            ],
            rows,
        ),
        "",
        "## Case Cần Ưu Tiên",
        "",
    ]

    priority = [
        match
        for match in valid
        if match["death"]["class"] in {"own_bomb_escape_failure", "enemy_bomb_trap"}
        or (match["safety_replay"]["available"] and match["safety_replay"]["unsafe_actions"] > 0)
    ]
    if not priority:
        lines.append("- Chưa có case safety ưu tiên cao theo heuristic.")
    for match in priority:
        lines.extend(
            [
                f"### Seed {match['seed']} - {match['death']['class']}",
                "",
                f"- File: `{match['file']}`",
                f"- Player index: {match['player_index']}",
                f"- Death step: {match['death_step']}",
                f"- Reason: {match['death']['reason']}",
                f"- Exploding bombs: `{json.dumps(match['death']['exploding_bombs'], ensure_ascii=False)}`",
                f"- Current replay unsafe actions: {match['safety_replay']['unsafe_actions']}/{match['safety_replay']['checked_actions']}",
                f"- Current replay shield changes: {match['safety_replay']['shield_changes']}",
                "",
            ]
        )
        examples = match["safety_replay"].get("examples", [])[:5]
        if examples:
            lines.append("Replay examples:")
            for example in examples:
                lines.append(
                    f"- step {example['step']}, pos {example['pos']}, action {example['action']}, "
                    f"safe={example['safe_actions']}, shielded={example['shielded']}"
                )
            lines.append("")

    lines.extend(
        [
            "## Đề Xuất Cho A",
            "",
            "- Thêm regression test từ các seed có `own_bomb_escape_failure` và `enemy_bomb_trap`.",
            "- Khi current replay flag nhiều unsafe action, cần replay bằng obs step trước action để xem `safe_actions` có quá chặt hay submit policy cũ đã khác code hiện tại.",
            "- Audit các case STOP liên tiếp trong blast line timer <= 2: final shield nên ưu tiên first escape action thay vì cho STOP nếu còn move hợp lệ.",
            "",
        ]
    )
    return "\n".join(lines)


def render_strategy(matches: list[dict[str, Any]]) -> str:
    valid = [match for match in matches if match.get("has_target")]
    rows = []
    for match in valid:
        bomb_metrics = match["bomb_metrics"]
        rows.append(
            [
                match["seed"],
                match["rank"],
                match["survival_steps"],
                match["unique_cells_while_alive"],
                f"{match['mobility_rate']:.3f}",
                match["max_stop_streak"],
                match["ping_pong_max"],
                match["bomb_count"],
                bomb_metrics["useful_bombs"],
                bomb_metrics["no_value_bombs"],
                ", ".join(issue_label(issue) for issue in match["issues"] if issue != "current_safety_replay_flags") or "-",
            ]
        )

    phase_rows = []
    for match in valid:
        for phase, metrics in match["phase_metrics"].items():
            phase_rows.append(
                [
                    match["seed"],
                    phase,
                    metrics["steps_alive"],
                    metrics["actions"]["STOP"],
                    metrics["actions"]["PLACE_BOMB"],
                    metrics["unique_cells"],
                    metrics["stop_streak_max"],
                ]
            )

    lines = [
        "# Vấn Đề Person B Strategy",
        "",
        "## Tổng Hợp Strategy",
        "",
        md_table(
            [
                "seed",
                "rank",
                "survival",
                "unique",
                "mobility",
                "max STOP",
                "pingpong",
                "bombs",
                "useful bombs",
                "no-value bombs",
                "issues",
            ],
            rows,
        ),
        "",
        "## Phase Metrics",
        "",
        md_table(
            ["seed", "phase", "alive steps", "STOP", "BOMB", "unique cells", "max STOP"],
            phase_rows,
        ),
        "",
        "## Vấn Đề Chính",
        "",
        "- STOP/camping quá dài xuất hiện ở nhiều seed, làm agent mất tempo và dễ bị trap khi bom đối thủ áp sát.",
        "- Có seed đặt rất ít bom hoặc bom giá trị thấp, nên step500 tie-break kém dù sống tới cuối trận.",
        "- Một số seed chết ngay sau khi đặt bom rồi không thoát đủ xa; B cần giảm scoring cho bomb nếu action sau đó bị ép STOP.",
        "- Mobility thấp trong các trận sống lâu là dấu hiệu target selection/anti-loop chưa đủ mạnh.",
        "",
        "## Đề Xuất Rule_v2",
        "",
        "- Giảm điểm STOP theo cấp số nhân khi `max_stop_streak` cục bộ >= 3, trừ khi STOP là action safe duy nhất.",
        "- Tăng bonus progress nếu action làm giảm distance tới farm/item target; phạt quay lại ô vừa đứng nếu không có danger.",
        "- Chỉ cộng `PLACE_BOMB` khi có `box_gain`, enemy pressure rõ ràng, hoặc current-code safety replay cho thấy có đường thoát sau bomb.",
        "- Thêm phase late tie-break: nếu sống sau step 350 mà rank proxy thấp, tăng farm/item/pressure có kiểm soát thay vì camping.",
        "",
    ]
    return "\n".join(lines)


def render_timeline(matches: list[dict[str, Any]]) -> str:
    valid = [match for match in matches if match.get("has_target")]
    interesting = [
        match
        for match in valid
        if match["death_timeline"]
        or match["max_stop_streak"] >= 20
        or match["ping_pong_max"] >= 8
    ]

    lines = [
        "# Timeline Các Trận Quan Trọng",
        "",
        "Format: `step`, `pos`, `action`, `alive`, `near bombs`, `issue tags`.",
        "",
    ]

    for match in interesting:
        lines.extend(
            [
                f"## Seed {match['seed']} - {match['file']}",
                "",
                f"- Player index: {match['player_index']}",
                f"- Rank/survival: {match['rank']} / {match['survival_steps']}",
                f"- Death class: {match['death']['class']}",
                f"- Max STOP streak: {match['max_stop_streak']}",
                f"- Ping-pong max: {match['ping_pong_max']}",
                "",
            ]
        )
        rows = [
            [
                row["step"],
                row["pos"],
                row["action"],
                fmt_bool(row["alive"]),
                " ".join(row["near_bombs"]) or "-",
                ", ".join(row["issue_tags"]) or "-",
            ]
            for row in match["death_timeline"]
        ]
        if rows:
            lines.append(md_table(["step", "pos", "action", "alive", "near bombs", "issue tags"], rows))
            lines.append("")
        else:
            lines.append("- Trận này không có death timeline; flag do loop/camping hoặc tie-break.\n")

    return "\n".join(lines)


def write_reports(matches: list[dict[str, Any]], team_id: str, log_dir: Path, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    short_id = team_id.split("-")[0]
    outputs = {
        f"BAO_CAO_TONG_HOP_{short_id}.md": render_summary(matches, team_id, log_dir),
        "VAN_DE_PERSON_A_SAFETY.md": render_safety(matches),
        "VAN_DE_PERSON_B_STRATEGY.md": render_strategy(matches),
        "TIMELINE_CAC_TRAN_QUAN_TRONG.md": render_timeline(matches),
        f"metrics_{short_id}.json": json.dumps(
            {
                "team_id": team_id,
                "log_dir": str(log_dir),
                "generated_at": datetime.now().isoformat(timespec="seconds"),
                "matches": matches,
            },
            indent=2,
            ensure_ascii=False,
        ),
    }
    for filename, content in outputs.items():
        (out_dir / filename).write_text(content.rstrip() + "\n", encoding="utf-8")


def analyze_logs(log_dir: Path, team_id: str, out_dir: Path) -> list[dict[str, Any]]:
    files = sorted(log_dir.glob("*.json"))
    matches = [analyze_match(path, team_id) for path in files]
    write_reports(matches, team_id, log_dir, out_dir)
    return matches


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze Bomberland data logs for one team id.")
    parser.add_argument("--log-dir", type=Path, default=Path("agent/data_logs"))
    parser.add_argument("--team-id", required=True)
    parser.add_argument("--out-dir", type=Path, default=Path("agent/team_agent/reports/data_logs"))
    args = parser.parse_args()

    matches = analyze_logs(args.log_dir, args.team_id, args.out_dir)
    valid = [match for match in matches if match.get("has_target")]
    avg_rank = sum(match["rank"] for match in valid) / max(1, len(valid))
    survived = sum(1 for match in valid if match["final_alive"])
    print(f"Analyzed {len(valid)}/{len(matches)} logs for team {args.team_id}")
    print(f"Average rank: {avg_rank:.2f}")
    print(f"Survived to step 500: {survived}/{len(valid)}")
    print(f"Wrote reports to: {args.out_dir}")


if __name__ == "__main__":
    main()
