# Team A/B agent scaffold

Thu muc nay la scaffold de 2 nguoi lam song song theo `docs/bomberman_agent_guides_md/08_CHIA_TASK_2_NGUOI.md`.

Chay thu:

```bash
python -m scripts.participant.run_local_match --agent_paths agent/team_agent None None None --num_episodes 3 --visualize false
python -m scripts.participant.estimate_agent_time agent/team_agent --opponents None None None --num_matches 3
```

## Nguoi A - Safety/Engine

Lam trong `person_a_safety/`:

- `constants.py`: action ids, tile ids, horizon.
- `obs.py`: `parse_obs(obs, agent_id)`.
- `danger.py`: `blast_cells`, chain reaction, `compute_danger_map`.
- `search.py`: time-expanded BFS, `safe_at`, escape check.
- `masks.py`: `legal_actions`, `safe_actions`.
- `bomb.py`: `can_place_bomb_safely`.
- `shield.py`: `final_shield`.
- `features.py`: `encode_features` cho BC/PPO sau nay.

## Nguoi B - Strategy/Scoring/ML

Lam trong `person_b_strategy/`:

- `scoring.py`: farm/item/attack/mobility/loop scoring.
- `loop_tracker.py`: anti-loop state.
- `policy_rule.py`: rule policy goi scoring va chi chon trong safe mask.
- `policy_bc.py`, `policy_ppo.py`: stub cho model inference sau nay.

Quy tac bat buoc: policy cua B chi de xuat action; action cuoi luon di qua `final_shield`.
