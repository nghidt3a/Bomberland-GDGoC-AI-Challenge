# submit_ver4_aggressive — tối đa kills (variance cao)

Một trong 3 version ver4 (cùng lõi an toàn ver3, khác **style** trong scoring).
Style = `aggressive`. Bundle one-file `agent.py` (không zip).

Đẩy mạnh `kill`/`trap`/`pressure` để thắng tie-break bằng Kills, NHƯNG vẫn giữ kỷ
luật vị trí (`enemy_risk`/`confine` gần balanced). Bài học từ bench: hạ né-địch quá
tay khiến nó liều và chết sớm trước khi kịp kill — kills đến từ *bẫy kiên nhẫn*, nên
bản aggressive tối ưu là "kill-seeking có kỷ luật", không phải "chen sát địch".

Đã thêm tuyệt chiêu (sau safe_mask, self-death=0): **02 seal/pincer** (bom cũ + bom
mới kẹp chết địch — `seal` weight cao), **04 item denial** (phá power-up địch sắp lấy),
**05 endgame** (ép kill khi thua / 1v1 hạ `enemy_risk`). Trần `offense` chung chống
double-count.

Bench (vs Tactical/Genius/AggressiveBomber, 20 trận/band) — sau tuyệt chiêu:
- seed 1: win 0.45, rank 1.00, survive500 0.80, **kills 0.50**
- seed 50: win 0.30, rank 1.10, survive500 0.80, kills 0.30

→ Net cải thiện so với trước tuyệt chiêu (kills 0.30→0.40 trung bình, band yếu seed50
khá hơn rõ: rank 1.35→1.10). Variance cao — best-case mạnh. Self-death = 0 (25+ seed),
max ~13 ms/step.

Build lại: `python -m scripts.participant.build_team_bundle --all`
So sánh: `python -m agent.team_agent.bench.tiebreak_metrics --style aggressive --num-episodes 20 --seed 1`
