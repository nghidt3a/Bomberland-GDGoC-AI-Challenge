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

- `constants.py`: action ids, tile ids, horizon.
- `obs.py`: `parse_obs(obs, agent_id)`.
- `danger.py`: `blast_cells`, chain reaction, `compute_danger_map`.
- `search.py`: time-expanded BFS, `safe_at`, escape check.
- `masks.py`: `legal_actions`, `safe_actions`.
- `bomb.py`: `can_place_bomb_safely`.
- `shield.py`: `final_shield`.
- `features.py`: `encode_features` cho BC/PPO sau này.

## Người B - Strategy/Scoring/ML

Làm trong `person_b_strategy/`:

- `scoring.py`: farm/item/attack/mobility/loop scoring.
- `loop_tracker.py`: anti-loop state.
- `policy_rule.py`: rule policy gọi scoring và chỉ chọn trong safe mask.
- `policy_bc.py`, `policy_ppo.py`: stub cho model inference sau này.

Quy tắc bắt buộc: policy của B chỉ đề xuất action; action cuối luôn đi qua `final_shield`.
