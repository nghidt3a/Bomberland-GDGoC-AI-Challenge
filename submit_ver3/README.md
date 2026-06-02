# submit_ver3 — Bomberland agent (rule-based + safety shield, hazard theo time-step)

Bản đóng gói để nộp, build từ `agent/team_agent` sau khi áp dụng các hướng fix
trong `huong_dan_fix_agent_bomberland.md`. Giữ nguyên kiến trúc **rule-based +
safety shield** của `submit_rule_v1`, nâng cấp phần lõi an toàn và chiến lược.

Source trong thư mục vẫn giữ module `person_a_safety/` và `person_b_strategy/`
để dễ audit, nhưng `submission.zip` là bản **one-file**: chỉ có `agent.py` ở
root. File này đã bundle toàn bộ module nội bộ để tránh lỗi evaluator load
`agent.py` nhưng không thấy package cạnh file (`No module named
'person_a_safety'`).

`act()` luôn trả int trong `[0,5]`, không import thư viện ngoài ngoài `numpy`,
trung bình ~3.7 ms/step trong timing gate mới (max spike ~12 ms, giới hạn 100 ms)
— giảm mạnh so với trước nhờ time-budget guard + bomb-radius tracker.

> Bundle được sinh tái lập bằng `python -m scripts.participant.build_team_bundle`
> (ghép module theo thứ tự phụ thuộc, strip import nội bộ, **fail nếu hai module
> trùng tên top-level** — đúng loại lỗi từng làm hỏng bundle thủ công).

---

## Điểm khác so với submit_rule_v1 (map theo tài liệu fix)

### P0 — An toàn / luật game

1. **Action mapping (mục 2): đã xác minh, KHÔNG sửa.**
   Engine thật (`engine/game.py`) map `LEFT/RIGHT` vào trục **row** (toạ độ đầu),
   `UP/DOWN` vào trục **col**. `ACTION_DELTAS` hiện tại áp lên `(row, col)` đã
   khớp engine. Đề xuất "sửa sang row-col" trong tài liệu là **sai** cho engine
   này — nếu sửa sẽ làm agent đi nhầm hướng. Đã thêm test khoá mapping bằng
   engine thật: `smoke_tests/test_action_mapping.py`.

2. **Danger map earliest-time → hazard theo time-step (mục 3).**
   `danger.py` cũ lưu `danger_time[r,c]` = thời điểm sớm nhất ô bị lửa. Một ô có
   thể bị nhiều bom quét ở các thời điểm khác nhau ⇒ mô hình cũ tưởng ô đã "an
   toàn vĩnh viễn" sau lần lửa đầu và agent có thể đi vào lần nổ thứ hai mà chết.
   Ver3 dùng `compute_hazard_map(state) -> hazard[t, r, c]` (bool, ~11×13×13) ghi
   **mọi** thời điểm cháy. `safe_at`/`eventually_safe` đọc đúng từng tick.
   `compute_danger_map` vẫn còn (suy ra earliest từ hazard) cho scoring.

3. **Chain reaction + box biến mất theo thời gian (mục 4).**
   `compute_hazard_map` mô phỏng theo từng tick: gom toàn bộ blast cùng tick
   (fix-point chain reaction giống engine), rồi mới xoá box bị phá **sau** tick —
   nên một bom nổ muộn có thể lan xa hơn qua ô box đã bị phá trước đó.

4. **Off-by-one move/bomb timer (mục 5): giữ nguyên + khoá test.**
   Sau khi move/đặt bomb, escape BFS bắt đầu ở `t=1` (đã đúng từ trước). Có
   regression test trong `test_search.py`, `test_bomb_checker.py`.

5. **Tối ưu timing safety gate.**
   `final_shield` nhận lại `safe_mask` đã tính, `compute_hazard_map` cache blast
   theo tick, và `has_escape_path` short-circuit khi tìm thấy ô eventually-safe
   thay vì dựng full BFS cho từng action.

6. **Đóng gói one-file.**
   `submit_ver3/agent.py` đã được bundle từ các module nội bộ; zip nộp bài chỉ
   chứa đúng `agent.py`.

### P1/P2 — Chiến lược chủ động hơn

7. **Vá bug STOP được thưởng farming (mục 6).**
   `box_move_score` trả `0` cho cả `STOP` lẫn `PLACE_BOMB` — đứng cạnh box không
   còn được tính điểm phá box (chỉ `PLACE_BOMB` mới phá). Test:
   `test_stop_not_rewarded_as_farm`.

8. **Enemy-aware + corridor + item contest (mục 9, 10).**
   `positional_risk`/`enemy_risk_penalty` (phạt mềm khi ở sát địch, nặng hơn
   trong hẻm cụt) và `enemy_contest_risk` (bỏ qua item ở xa mà địch tới kịp/nhanh
   hơn). Chỉ sắp lại thứ tự trong các action **đã an toàn** — safe mask vẫn là
   cổng chặn cứng.

9. **Bomb trap/kill có mục đích (mục 8).**
   `enemy_escape_count` (BFS đếm ô địch còn thoát được) + `trap_score`: đo phần
   đường thoát của địch **gần nhất** bị mất sau khi đặt bom; địch bị dồn vào thế
   không còn ô thoát ⇒ coi như khả năng kill cao. Bomb trap được tính là "có ích"
   (không bị phạt useless).

10. **Late-game theo tie-break (mục 11).**
   `loop_tracker` đếm số địch đã bị loại (proxy đáng tin, không over-credit) cùng
   boxes/items/bombs để chọn `late_leading` (đang dẫn → thủ, mobility cao) hay
   `late_chasing` (đang đuổi → tăng pressure/trap, bomb có ích).

### Nâng cấp thêm (5 cải tiến mới)

11. **Bomb-radius tracker liên-turn** (`person_a_safety/bomb_tracker.py`).
   Observation không lộ bán kính bom, nhưng engine **khoá bán kính lúc đặt**.
   Tracker snapshot bonus của chủ bom **lần đầu** thấy bom và giữ nguyên — thôi
   over-estimate mỗi khi chủ bom nhặt thêm radius item. Vì bonus chỉ tăng, snapshot
   luôn ≥ bán kính thật ⇒ **không bao giờ under-estimate** ⇒ self-death vẫn = 0.

12. **Anti-trap (chống bị nhốt)** trong `scoring.py`. Hai tín hiệu mềm (chỉ sắp lại
   các action đã an toàn, không đụng hard mask), chỉ áp khi đang an toàn để không
   cản đường thoát: `confinement_penalty` (rẻ — phạt bước vào pocket/hẻm cụt cạnh
   địch) và `enemy_bomb_escape_penalty` (mô phỏng địch gần nhất đặt bom rồi kiểm tra
   ta còn `has_escape_path` không). Vá đúng lỗ hổng "đi vào ngõ cụt rồi bị bom bịt".

13. **Time-budget guard** (`agent.py` `ACT_BUDGET_MS=75`). Safety gate luôn chạy;
   chỉ các sim chiến lược đắt (trap / escape-quality / enemy-bomb) bị bỏ khi quá
   ngân sách. Biến spike ~70 ms → ~12 ms, cận trên cứng < 100 ms trên máy chậm.

14. **Calibrate `trap_score`** (giảm "trap ảo"). Mở rộng horizon lookahead của địch
   (`ENEMY_ESCAPE_HORIZON=8`, sát ngòi nổ 7) để bớt false-kill; chiết khấu giá trị
   bẫy theo độ "bị dồn" thực sự (`confinement = 2/(2+after)`) — chỉ near-kill mới
   điểm cao, bẫy còn nhiều đường thoát bị hạ điểm mạnh.

15. **CEM auto-tune harness** (`train/tune_weights.py`). Tìm `ScoreWeights` bằng
   cross-entropy method, objective từ `strategy_metrics` (rank thấp + self_death=0 +
   boxes/items). In ra bộ trọng số tốt nhất để review; **không tự đổi** weights đang
   ship. Chạy ngắn = smoke test (xác nhận vòng lặp cải thiện prior), chạy dài để ra
   ứng viên.

---

## Bằng chứng kiểm thử

- **79 unit test** (`agent/team_agent/smoke_tests`) pass, gồm các test mới của
  đợt nâng cấp: `test_bomb_radius_tracker`, `test_anti_trap`,
  `test_trap_calibration`, `test_time_budget` (15 test mới) — cùng bộ cũ
  (`test_action_mapping`, double-burn, box-removal, `test_stop_not_rewarded_as_farm`).
- **Engine cross-validation harness** (`test_engine_safety.py`, drive BomberEnv
  thật): 60 seed/500 step trên source, self-death = 0, bad-actions = 0. Bản
  **bundle one-file** (`submit_ver3/agent.py`) cũng được certify riêng: 40 seed,
  self-death = 0, bad-actions = 0.
- **Timing** (sau nâng cấp): seed 1/10 match avg 3.75 ms, max 11.10 ms; seed 50/10
  match avg 3.69 ms, max 11.97 ms — cách xa giới hạn 100 ms.
- **Strategy_metrics** (seed 1, 20 trận, vs Tactical/Smarter/Genius): win 0.10,
  draw 0.90, **self_death 0.00**, **avg_rank 0.00**, boxes 7.40, items 8.00,
  bombs 53.05 (bundle khớp y hệt source). So ver3 trước: win 0.05 → 0.10,
  self_death 0.05 → 0.00, avg_rank 0.05 → 0.00.

Chạy lại:

```powershell
python -m pytest agent/team_agent/smoke_tests -q
$env:TEAM_SAFETY_SEEDS='60'; $env:TEAM_SAFETY_MAX_STEPS='500'; python -m pytest agent/team_agent/smoke_tests/test_engine_safety.py -q -s
python -m scripts.participant.build_team_bundle   # đồng bộ submit_ver3 + bundle + zip
python -m scripts.participant.estimate_agent_time submit_ver3 --opponents TacticalRuleAgent SmarterRuleAgent GeniusRuleAgent --num_matches 10 --seed 1
python -m scripts.participant.estimate_agent_time submit_ver3 --opponents TacticalRuleAgent SmarterRuleAgent GeniusRuleAgent --num_matches 10 --seed 50
python -m agent.team_agent.bench.strategy_metrics --agent-path submit_ver3 --num-episodes 20 --seed 1
python -m agent.team_agent.train.tune_weights --iters 8 --pop 16 --episodes 12 --seed 1   # auto-tune (tuỳ chọn)
```

> Benchmark trước/sau (win/draw/self-death) xem mục dưới — đo bằng
> `agent/team_agent/bench/strategy_metrics.py`.

## Benchmark (strategy_metrics, vs Tactical/Smarter/Genius)

Đo bằng `agent/team_agent/bench/strategy_metrics.py`, mỗi bản chạy **process
riêng** (tránh module caching lẫn nhau). `death_rate` = tỉ lệ trận agent chết
(do bất kỳ nguyên nhân); riêng self-bomb death được chứng minh = 0 ở engine
harness bên dưới. `avg_rank`: 0 = winner, 3 = chết đầu.

Seed band 1 (20 trận):

| Bản | win | draw | death | rank | boxes | items | bombs | survive |
|---|---|---|---|---|---|---|---|---|
| rule_v1 | 0.00 | 0.00 | 1.00 | 2.20 | 0.0 | 0.0 | 0.0 | 81 |
| **ver3** | 0.05 | 0.90 | 0.05 | 0.05 | 7.55 | 8.35 | 49.3 | 464 |

Seed band 50 (16 trận):

| Bản | win | draw | death | rank | boxes | items | bombs | survive |
|---|---|---|---|---|---|---|---|---|
| rule_v1 | 0.00 | 0.00 | 1.00 | 1.88 | 0.0 | 0.0 | 0.0 | 113 |
| **ver3** | 0.19 | 0.69 | 0.12 | 0.31 | 8.25 | 7.75 | 49.8 | 427 |

Nhận xét: `rule_v1` cực kỳ thụ động (STOP ~96% số bước, gần như không đặt bomb /
phá box — đúng bệnh mà tài liệu fix mô tả). `ver3` chủ động phá box, nhặt item,
đặt bomb có ích, sống tới gần cuối trận và gần như luôn nằm trong nhóm sống sót
(avg_rank ≈ 0.05–0.31), trong khi self-bomb death vẫn = 0 (engine harness).
