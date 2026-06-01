# Kế hoạch: Hiện trạng agent ver3 + Roadmap phát triển (ưu tiên ML: BC→PPO)

## Context — vì sao có tài liệu này

Nhóm đang thi **GDGoC-HCMUS AI Challenge 2026 (Bomberland)**: 4 agent đánh nhau (FFA) trên lưới 13×13, xếp hạng bằng **TrueSkill** `Score = μ − 3σ` (start μ=100, σ=33.33). Vài mốc luật quyết định cách ưu tiên:

- **Deadline nộp: 21/6** → hôm nay 2026-06-02, còn **~19 ngày**.
- **Cần ≥ 50 trận** mới đủ điều kiện vào Top 8 (nộp muộn = không đủ trận = loại bất kể điểm). 3 lần nộp/ngày.
- **Giới hạn 100ms/step**, startup ≤ 20s. Lib cho phép: numpy, scipy, torch, tensorflow, SB3, gymnasium, onnxruntime.
- **Tie-break khi sống tới step 500**: kills > boxes > items > bombs.
- Baseline mạnh (điểm cố định): tactical 114.7, genius 112.5, smarter 111.3, box_farmer 107.9, simple 107.8, random 99.

Bản agent **mới nhất = `submit_ver3`** (one-file bundle), build từ source `agent/team_agent/`, đã được khuyến nghị nộp thay cho bản thụ động `submit_rule_v1`. Tài liệu này: (1) chụp đầy đủ hiện trạng ver3 — chức năng/tính năng/thuật toán/điểm mạnh-yếu; (2) roadmap cải thiện lấy **ML (BC→PPO)** làm trục chính, kèm lan can để không lỡ deadline.

> Đây là tài liệu **đọc-để-định-hướng**. Mọi số liệu đều tái lập được bằng lệnh ở cuối file.

---

# PHẦN 1 — HIỆN TRẠNG AGENT `submit_ver3`

## 1.1 Kiến trúc tổng thể

Chia 2 người: **Person A (safety/engine)** trong [person_a_safety/](../agent/team_agent/person_a_safety/) và **Person B (strategy)** trong [person_b_strategy/](../agent/team_agent/person_b_strategy/).

Luồng mỗi lượt `act(obs)` trong [agent.py](../agent/team_agent/agent.py):

```
parse_obs → compute_hazard_map → safe_actions (mask an toàn)
          → RulePolicy.choose_action (chấm điểm trong mask) → final_shield → int [0,5]
```

- **Bất biến bắt buộc**: mọi action đi qua `final_shield` (cổng an toàn cứng). `act()` bọc try/except, lỗi → trả STOP.
- **Đóng gói**: `submit_ver3/agent.py` là **one-file bundle** (gộp toàn bộ module để tránh lỗi evaluator `No module named 'person_a_safety'`); `submission.zip` chỉ chứa `agent.py`. Chỉ dùng `numpy`.
- **Tốc độ**: ~6.8–8.1 ms/step trung bình, spike tối đa ~28–70 ms → **an toàn dưới 100ms**.

## 1.2 Safety core (Person A) — thuật toán

| File | Vai trò & thuật toán chính |
|---|---|
| [constants.py](../agent/team_agent/person_a_safety/constants.py) | Action id; `ACTION_DELTAS` **đã khoá đúng engine** (LEFT/RIGHT → trục row, UP/DOWN → trục col). `BOMB_TIMER=7`, `MAX_BOMB_RADIUS=5`, `HORIZON=10`. |
| [obs.py](../agent/team_agent/person_a_safety/obs.py) / [state.py](../agent/team_agent/person_a_safety/state.py) | `parse_obs` → `GameState`: walls/boxes/item_radius/item_capacity là grid bool; self pos/alive/bombs_left/radius; danh sách opponents. `radius = 1 + bonus`. |
| [danger.py](../agent/team_agent/person_a_safety/danger.py) | **Lõi mô hình lửa.** `blast_cells` mirror y hệt engine (gốc + 4 nhánh, wall chặn trước, box bị tính rồi chặn). `bomb_radius` suy từ radius **hiện tại** của owner (over-estimate = bias an toàn, vì obs không expose radius lúc đặt bom). **`compute_hazard_map → hazard[t,r,c]`**: tensor lửa theo từng tick — nâng cấp lớn nhất so với rule_v1. |
| [search.py](../agent/team_agent/person_a_safety/search.py) | **Time-expanded BFS** trên `(cell, t)`. `safe_at`/`eventually_safe` đọc tensor. Điểm tinh tế: sau move/đặt bom, BFS bắt đầu `start_time=1` (move đã tiêu 1 step) — để t=0 là off-by-one tự sát. |
| [masks.py](../agent/team_agent/person_a_safety/masks.py) | `legal_actions` + `safe_actions`: action an toàn ⇔ ô đích không cháy ở t=1 **và** còn đường thoát sau đó. Có fallback "ô sống lâu nhất" khi không có action chắc chắn an toàn. |
| [bomb.py](../agent/team_agent/person_a_safety/bomb.py) | `can_place_bomb_safely`: mô phỏng đặt bom rồi đòi **đường thoát vĩnh viễn** (ô không bao giờ cháy lại trong horizon) — chặt hơn rule_v1, chống tự chôn cạnh bom radius lớn. |
| [shield.py](../agent/team_agent/person_a_safety/shield.py) | `final_shield`: action trong mask thì giữ; không thì `best_escape_action` → `least_bad_action`; không bao giờ trả action ngoài [0,5]. Nhận lại mask/hazard đã tính để tránh spike latency. |

**Vì sao hazard tensor quan trọng (vá bug "ô nổ 2 lần"):** rule_v1 chỉ lưu thời điểm cháy *sớm nhất* mỗi ô. Một ô có thể bị nhiều bom/chain quét ở các tick khác nhau → mô hình cũ tưởng ô đã an toàn vĩnh viễn sau lần lửa đầu → agent đi vào lần nổ thứ 2 và chết. Tensor ghi **mọi** thời điểm cháy + mô phỏng **chain reaction** (fix-point) và **box biến mất theo thời gian** (bom nổ muộn lan xa hơn qua ô box đã bị phá). Có cache blast theo tick để nhanh.

## 1.3 Strategy core (Person B) — chấm điểm & policy

[scoring.py](../agent/team_agent/person_b_strategy/scoring.py): tổng có trọng số, **chỉ chấm trên các action đã an toàn**:

- **Tích cực**: `survival`, `box_move` (STOP/PLACE_BOMB = 0 — đã vá bug rule_v1 thưởng đứng yên cạnh box), `box_bomb`, `item`, `pressure`, `trap_bonus`, `bomb_escape_quality`, `mobility`.
- **Phạt**: `danger_penalty`, `enemy_risk_penalty` (`positional_risk` né hẻm cụt gần địch), `loop_penalty`, `stop_penalty`, `useless_bomb_penalty`.
- `trap_score`/`enemy_escape_count`: BFS đếm số ô địch gần nhất còn thoát được sau khi mình đặt bom (dồn về 0 ⇒ khả năng kill).
- `enemy_contest_risk`: bỏ qua item mà địch tới kịp/nhanh hơn.
- `apply_escape_bias`: khi ô hiện tại đang nguy hiểm → giảm mạnh farm/item/pressure, tăng survival.
- `phase_profile`: trọng số theo phase (early <150 / mid <350 / late ≥350); late tách **late_leading** (đang dẫn → thủ) vs **late_chasing** (đang đuổi → tăng pressure/trap) theo `tracker.proxy_score`.

[loop_tracker.py](../agent/team_agent/person_b_strategy/loop_tracker.py): chống lặp/camping + proxy stats (boxes/items/bombs/kills). `proxy_kills = sĩ số địch ban đầu − địch còn sống` (robust, không over-credit).

[policy_rule.py](../agent/team_agent/person_b_strategy/policy_rule.py): `RulePolicy` — argmax điểm trong mask, tie-break bằng `action_tie_break_score`, fallback STOP.

## 1.4 ⚠️ Hạ tầng ML — ĐÃ CÓ KHUNG NHƯNG CHƯA NỐI

Đây là vùng tiềm năng lớn nhất chưa khai thác:

- [features.py](../agent/team_agent/person_a_safety/features.py): `encode_features` → tensor **10 kênh × 13×13** (walls, boxes, item_radius, item_capacity, self, opponents, bombs, bomb_timer_norm, danger_time_norm, safe_reachable). **Sẵn sàng cho BC/PPO.**
- [train/gen_dataset.py](../agent/team_agent/train/gen_dataset.py): thu (features, teacher_action từ rule agent đã shield, safe_mask, agent_id, step, seed) → `.npz`. **Bộ sinh dataset BC đã xong.**
- [policy_bc.py](../agent/team_agent/person_b_strategy/policy_bc.py) & [policy_ppo.py](../agent/team_agent/person_b_strategy/policy_ppo.py): **chỉ là STUB** — đều trả `first_safe_action`. Chưa có model, chưa có script train, chưa được `agent.py` nạp.

## 1.5 Test & benchmark

- [smoke_tests/](../agent/team_agent/smoke_tests/): **65 test pass**. Đáng chú ý: [test_engine_safety.py](../agent/team_agent/smoke_tests/test_engine_safety.py) (drive BomberEnv thật, **self-death=0, bad-action=0** qua 60 seed/500 step), [test_action_mapping.py](../agent/team_agent/smoke_tests/test_action_mapping.py) (khoá ACTION_DELTAS vs engine), test_danger (double-burn/box-removal), test_strategy_rule_v1 (STOP không được thưởng farm).
- [bench/strategy_metrics.py](../agent/team_agent/bench/strategy_metrics.py): win/draw/death/rank/kills/boxes/items/bombs vs Tactical/Smarter/Genius.
- Timing: `scripts/participant/estimate_agent_time.py`.

## 1.6 Kết quả benchmark hiện tại

| Bản | win | draw | death | rank | boxes | items | bombs | survive | time |
|---|---|---|---|---|---|---|---|---|---|
| rule_v1 (seed1/20) | 0.00 | 0.00 | 1.00 | 2.20 | 0 | 0 | 0 | 81 | ~20ms |
| **ver3 (seed1/20)** | 0.05 | 0.90 | 0.05 | **0.05** | 7.55 | 8.35 | 49.3 | 464 | ~8ms |
| **ver3 (seed50/16)** | 0.19 | 0.69 | 0.12 | **0.31** | 8.25 | 7.75 | 49.8 | 427 | |

## 1.7 Điểm mạnh / điểm yếu (đánh giá thẳng)

**Mạnh:** self-death ≈ 0 (engine-verified), nhanh, sống gần hết trận, farm box/item tốt, đặt bom có ích, `avg_rank ≈ 0.05–0.31` (gần như luôn nhóm sống sót), packaging chắc.

**Yếu / rủi ro:**
1. **Draw cao, kill thấp (0.2–0.4)** trên benchmark. **NHƯNG lưu ý quan trọng:** `strategy_metrics` tính rank thuần theo thứ tự chết, **không áp tie-break step-500** (kills>boxes>items>bombs) — mọi người sống sót bị tính rank 0 (hòa). Engine cục bộ (`step()` chỉ trả `obs, terminated, truncated`) cũng không xếp hạng; tie-break do **server** áp. Vì ver3 farm box/item/bomb rất cao, nhiều "draw" này nhiều khả năng **thắng tie-break trên leaderboard thật** ⇒ **benchmark đang đo THẤP sức mạnh thật của ver3.**
2. **Radius over-estimate** → đôi khi quá bảo thủ.
3. **Benchmark chỉ test player 0**, chưa xoay 4 góc.
4. **Hướng ML chưa hiện thực hoá** (mục 1.4).
5. **Version hygiene**: `agent/team_agent/` đang có thay đổi chưa commit, `submit_ver3/` chưa track — dễ lệch giữa source và bản đóng gói.

---

# PHẦN 2 — ROADMAP (trục chính: ML BC→PPO, kèm lan can)

## Nguyên tắc dẫn đường

- **`submit_ver3` là lưới an toàn**: nộp NGAY và đều để gom đủ **≥50 trận** sớm (điều kiện finals). Không đặt cược tất tay vào ML kịp về đích.
- **Mọi policy ML BẮT BUỘC đi qua `final_shield`** (đúng khuyến nghị docs: *Safe RL/action shielding* là RL-add ưu tiên #1). Không thương lượng.
- **Quyết định bằng DATA trên benchmark trung thực với leaderboard**, không theo cảm tính "ML nghe xịn hơn". Docs ghi rõ: PPO không vượt rule rõ ràng thì **bỏ**.
- Mọi thay đổi đụng safety/engine phải **đối chiếu `engine/game.py`** trước (bài học cũ: tài liệu fix từng sai về action mapping).

## Phase 0 — Làm benchmark đáng tin TRƯỚC (tiên quyết, ~1–2 ngày)

Không thể biết BC/PPO có hơn ver3 không nếu thước đo sai luật.

- Sửa [bench/strategy_metrics.py](../agent/team_agent/bench/strategy_metrics.py): khi nhiều agent sống tới cuối, **áp tie-break kills>boxes>items>bombs** (dùng `env.players[i].stats`) thay vì xếp tất cả = rank 0.
- Thêm eval **đa vị trí** (xoay agent qua cả 4 góc) + nhiều dải seed.
- → Đo lại sức mạnh THẬT của ver3 (nhiều khả năng cao hơn số hiện tại) và lấy đó làm chuẩn so cho ML.
- **Nhớ**: chạy mỗi bản trong **process riêng** (module-cache lẫn nhau làm sai số).

## Phase 1 — Behavior Cloning warm-start (cú ăn ML thực tế nhất, ~4–6 ngày)

Pipeline đã có nửa phần: `features.py` + `gen_dataset.py`.

- **Build**: script train CNN nhỏ trên `10×13×13`, **mask logit phi-pháp bằng safe_mask**, cross-entropy tới teacher action; lưu `.pth`/`.onnx`.
- **Nối** [policy_bc.py](../agent/team_agent/person_b_strategy/policy_bc.py): nạp model + inference (ưu tiên numpy/onnxruntime cho nhẹ; torch được nhưng nặng hơn). **Vẫn qua `final_shield`.**
- Sinh dataset **lớn & đa dạng hơn** (nhiều seed, cả 4 vị trí, có thể trộn nhiều loại đối thủ); DAgger-lite nếu còn giờ.
- **Cổng go/no-go**: BC+shield phải **≥ ver3** trên benchmark Phase 0. Trần của BC = chính rule agent nó học theo; giá trị thật của BC là **tốc độ inference** + policy mượt + **nền để PPO khởi động**. BC ≈ ver3 đã là thành công (có nền train được); BC tệ hơn → giữ ver3.
- **Thành thật về rủi ro**: BC hiếm khi vượt thầy. Coi BC chủ yếu là **warm-start cho PPO**, không nhất thiết là bản nộp tốt hơn ngay.

## Phase 2 — PPO / self-play (trần cao, rủi ro cao — chỉ làm nếu còn giờ & Phase 1 vững)

- Init policy từ **trọng số BC**. Masked logits qua safe_mask. Reward: **terminal rank** + shaping nhẹ (boxes/items/kills/survival), canh reward-hacking.
- **Self-play pool**: rule agent + baseline (Tactical/Smarter/Genius) + checkpoint cũ, tránh overfit 1 đối thủ. **Trận thật 4 người — không tối ưu kiểu 1v1.**
- Train **off-machine** (Colab/Kaggle theo docs `train_test/`). Cần **gymnasium wrapper** quanh BomberEnv kèm safe-mask.
- Benchmark checkpoint định kỳ trên thước đo Phase 0.
- **Stop rule cứng**: PPO không vượt rule/BC rõ ràng ⇒ bỏ, nộp ver3 hoặc BC. Không để PPO ăn hết deadline.

## Phase 3 — Hardening & chọn bản cuối (~2–3 ngày cuối, để dành)

- Benchmark lớn (500–1000 trận) cho 2 ứng viên top, đủ 4 vị trí, nhiều dải seed.
- **Latency p99** (đặc biệt nạp + chạy model torch dưới 100ms; cân nhắc ONNX). Startup ≤ 20s.
- Đóng gói theo luật (≤20 file, đuôi cho phép; one-file hoặc model+agent.py).
- Giữ version: `rule baseline (ver3)`, `bc_v1_best`, `ppo_best` (chỉ khi thắng). Nộp bản **được data chứng minh tốt nhất**, giữ ver3 làm fallback.

## Quick wins làm song song (rủi ro thấp)

- **Giảm draw bằng aggression theo tie-break**: vì leaderboard thưởng kills>boxes>items, ver3 vốn farm rất khoẻ — tinh chỉnh trọng số late-game (`phase_profile`) để biến "draw" thành "thắng tie-break"; validate trên benchmark Phase 0.
- **Snapshot radius lúc đặt bom** (ghi lại radius owner khi bom lần đầu xuất hiện qua các step) để giảm bias quá bảo thủ — **engine-verify** và giữ fallback bảo thủ.
- **Version hygiene**: commit `team_agent`, đảm bảo `submit_ver3` == source, tag baseline.

## Timeline gợi ý (~19 ngày)

| Khi | Việc |
|---|---|
| **Ngay** | Nộp ver3 để bắt đầu gom trận (cần ≥50). Re-submit tinh chỉnh rule an toàn vài ngày/lần (3/ngày) để vừa gom trận vừa nhích μ. |
| Ngày 1–2 | Phase 0 (benchmark trung thực). |
| Ngày 3–8 | Phase 1 (BC) + quick-win tuning. |
| Ngày 9–15 | Phase 2 (PPO/self-play) NẾU BC vững; không thì tiếp tục tune rule. |
| Ngày 16–19 | Phase 3 hardening + chọn bản cuối + **nộp chốt trước 21/6**. |

---

# Cách kiểm chứng / tái lập (để mọi số liệu đều check được)

```powershell
# Test (65 pass) + engine safety harness (self-death=0)
python -m pytest agent/team_agent/smoke_tests -q
$env:TEAM_SAFETY_SEEDS='60'; $env:TEAM_SAFETY_MAX_STEPS='500'; python -m pytest agent/team_agent/smoke_tests/test_engine_safety.py -q -s

# Benchmark (MỖI bản 1 process riêng để tránh module-cache lẫn nhau)
python -m agent.team_agent.bench.strategy_metrics --agent-path submit_ver3 --opponents TacticalRuleAgent SmarterRuleAgent GeniusRuleAgent --num-episodes 20 --seed 1

# Timing < 100ms
python -m scripts.participant.estimate_agent_time submit_ver3 --opponents TacticalRuleAgent SmarterRuleAgent GeniusRuleAgent --num_matches 10 --seed 1
```

# Rủi ro & lan can (tóm tắt)

- **Đừng để ML ăn hết deadline** — ver3 là sàn; gom ≥50 trận sớm.
- **Safety shield bắt buộc** cho mọi policy ML.
- **Verify mọi thay đổi safety/engine** với `engine/game.py`.
- **Model torch**: canh 100ms inference + 20s startup; ưu tiên ONNX/net nhỏ.
- **Benchmark phải áp tie-break**, nếu không sẽ xếp sai ứng viên.
