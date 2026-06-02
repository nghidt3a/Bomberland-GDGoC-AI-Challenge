# submit_ver4_safe — sống tới 500 + farm tối đa (variance thấp)

Một trong 3 version ver4 (cùng lõi an toàn ver3, khác **style** trong scoring).
Style = `safe`. Bundle one-file `agent.py` (không zip).

Ưu tiên sống tới step 500 và farm thật nhiều box/item/bombs: nâng `survival`/`danger`/
`enemy_risk`/`confine`, hạ `kill`/`pressure`/`trap`. Mạnh khi tie-break nghiêng về
Boxes/Items/Bombs (sau Kills) và khi muốn tránh rủi ro chết sớm (rank-3 tụt μ TrueSkill).

Bench (vs Tactical/Genius/AggressiveBomber, 20 trận/band):
- seed 1: win 0.45, tie-break rank 1.05, survive500 0.80, kills 0.40, boxes 6.4
- seed 50: win 0.20, rank 1.30, survive500 0.70, kills 0.15, boxes 7.95

→ Chắc chắn, ít liều; điểm yếu là kills dao động (khi thấp dễ thua tie-break). Self-death
= 0 (engine harness 25+ seed), max ~9 ms/step (nhanh nhất).

Build lại: `python -m scripts.participant.build_team_bundle --all`
So sánh: `python -m agent.team_agent.bench.tiebreak_metrics --style safe --num-episodes 20 --seed 1`
