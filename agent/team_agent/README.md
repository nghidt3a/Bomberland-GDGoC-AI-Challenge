# Team A/B agent scaffold

Thư mục này là scaffold để 2 người làm song song theo `docs/bomberman_agent_guides_md/08_CHIA_TASK_2_NGUOI.md`.

File tiếp theo nên đọc: `HUONG_DAN_TIEP_THEO_A_B.md`.

Chạy thử:

```bash
python -m scripts.participant.run_local_match --agent_paths agent/team_agent None None None --num_episodes 3 --visualize false
python -m scripts.participant.estimate_agent_time agent/team_agent --opponents None None None --num_matches 3
```

## Người A - Safety/Engine

Làm trong `person_a_safety/`:

- `constants.py`: action ids, tile ids, horizon. `ACTION_DELTAS` đã được khoá đúng
  theo engine thật (xem `smoke_tests/test_action_mapping.py`) — KHÔNG sửa theo
  kiểu row-col trong tài liệu fix vì engine này map LEFT/RIGHT vào trục row.
- `obs.py`: `parse_obs(obs, agent_id)`.
- `danger.py`: `blast_cells`, `compute_hazard_map` (hazard theo từng time-step
  `hazard[t, r, c]`, có chain reaction + box biến mất theo thời gian),
  `hazard_to_earliest`/`earliest_at`, và `compute_danger_map` (bản earliest-time
  suy ra từ hazard, dùng cho scoring).
- `search.py`: time-expanded BFS, `safe_at`/`eventually_safe` đọc hazard tensor,
  escape check (start_time=1 sau khi move).
- `masks.py`: `legal_actions`, `safe_actions`.
- `bomb.py`: `can_place_bomb_safely`.
- `shield.py`: `final_shield`.
- `features.py`: `encode_features` cho BC/PPO sau này.

> Bản nâng cấp (ver3) đổi danger map earliest-only → hazard theo time-step để vá
> bug "ô nổ 2 lần", thêm chain reaction + box-removal theo thời gian. Bản đóng gói
> để nộp nằm ở `submit_ver3/` (đọc `submit_ver3/README.md`).

## Người B - Strategy/Scoring/ML

Làm trong `person_b_strategy/`:

- `scoring.py`: farm/item/attack/mobility/loop scoring. Ver3 thêm:
  - vá bug STOP được thưởng farming (`box_move_score` trả 0 cho STOP),
  - `positional_risk`/`enemy_risk_penalty` + `enemy_contest_risk` (né hẻm cụt gần
    địch, không tranh item thua),
  - `trap_score`/`enemy_escape_count` (đặt bomb trap/kill khi giảm đường thoát địch),
  - phase weights theo tie-break (`late_leading`/`late_chasing`).
- `loop_tracker.py`: anti-loop state + proxy stats (boxes/items/bombs + số địch đã
  bị loại) để chọn late-game profile.
- `policy_rule.py`: rule policy gọi scoring và chỉ chọn trong safe mask.
- `policy_bc.py`, `policy_ppo.py`: stub cho model inference sau này.

Quy tắc bắt buộc: policy của B chỉ đề xuất action; action cuối luôn đi qua `final_shield`.
