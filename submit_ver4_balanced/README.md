# submit_ver4_balanced — safe-aggression + farm (KHUYẾN NGHỊ)

Một trong 3 version ver4 (cùng lõi an toàn ver3, khác **style** trong scoring).
Style = `balanced`. Bundle one-file `agent.py` (không zip).

Tie-break-aware: tận dụng meta "22/27 trận phân hạng ở step 500 theo Kills > Boxes >
Items > Bombs". So với ver3: thêm `kill_bonus` (thưởng lớn cho bom dồn địch về 0
đường thoát, chỉ khi ta còn thoát), farm radius tới blast 5, dùng multi-bomb, và
late-game vẫn giữ giao tranh (không lẩn trốn khi dẫn).

`balanced` = preset cân bằng: kill/pressure/trap vừa-cao, kỷ luật vị trí giữ nguyên.
Đã thêm tuyệt chiêu (sau safe_mask, self-death=0): **02 seal/pincer**, **04 item
denial**, **05 endgame** (giữ hạng khi gần 500 + dẫn / ép kill khi thua / 1v1) + trần
`offense` chống double-count — với weight vừa phải (aggressive đẩy mạnh hơn).

Bench (vs Tactical/Genius/AggressiveBomber, 20 trận/band) — sau tuyệt chiêu:
- seed 1: win 0.35, rank 1.20, survive500 0.80, kills 0.45
- seed 50: win 0.35, rank 0.90, survive500 0.85, kills 0.35

→ Trung tính so với trước tuyệt chiêu (không tụt, không thắng rõ ở mẫu 20 trận; thêm
năng lực pincer/denial/endgame). Vẫn ổn định nhất trong 3 bản. Self-death = 0 (25+
seed), max ~13 ms/step.

Build lại: `python -m scripts.participant.build_team_bundle --all`
So sánh: `python -m agent.team_agent.bench.tiebreak_metrics --style balanced --num-episodes 20 --seed 1`
