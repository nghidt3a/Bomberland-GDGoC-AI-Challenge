# 07 — Tương tác · Xung đột · Tương thích giữa các hướng nâng cấp

> **Đọc trước khi kết hợp nhiều hướng/chiêu.** Gộp bừa các nâng cấp dễ làm ver3 **TỆ ĐI** dù từng cái riêng lẻ đều tốt. File này map cộng hưởng/xung đột + giao thức tích hợp an toàn.

Nguyên tắc xuyên suốt: **thêm từng cái một → đo trên benchmark đúng luật ([01](01_quick_wins_va_benchmark_trung_thuc.md)) → giữ nếu ≥ ver3, revert nếu tệ.**

## 1. Danh mục "moving parts"

| Nhóm | Thành phần |
|---|---|
| **Lõi ver3 (đang chạy)** | `survival`, `box_move`/`box_bomb`, `item`, `mobility`, `pressure_score`, `trap_score`, `enemy_risk_penalty`(`positional_risk`), `useless_bomb_penalty`, `apply_escape_bias`, `phase_profile`/`adjusted_weights`, `loop_tracker`, `final_shield` — trong [scoring.py](../../agent/team_agent/person_b_strategy/scoring.py) |
| **Tuyệt chiêu đề xuất** | herding **t01**, seal **t02**, predict **t03**, item-denial **t04**, endgame **t05**, containment **t06** ([tuyet_chieu/](tuyet_chieu/)) + chain-bomb **06** ([06](06_chain_bomb_offensive.md)) |
| **Hướng thuật toán** | quick-wins+benchmark **a01**, Alpha-Beta **a02**, BC **a03**, PPO **a04**, DQN **a05** ([00_README](00_README_tong_quan.md)) |

## 2. Phân loại theo "trục" (để thấy xung đột ngay)

| Thành phần | Loại | Cần opponent_model | Dùng latency mỗi step | Vào "offense" | Là *policy thay thế* |
|---|---|---|---|---|---|
| chain 06 | tấn công (bom) | không | rẻ (reuse sim) | **có** | không |
| trap (lõi) | tấn công (bom) | né-hoàn-hảo | rẻ | **có** | không |
| seal t02 | tấn công (bom) | né-hoàn-hảo | rẻ–TB | **có** | không |
| predict t03 | tấn công (bom) | **greedy** | TB (BFS địch) | **có** | không |
| pressure (lõi) | tấn công (bom) | không | rẻ | **có** | không |
| item-denial t04 | tấn công/kinh tế | một phần | rẻ | **có** (nhánh bom) | không |
| herding t01 | tấn công (MOVE) | có | TB (BFS vùng) | không | không |
| containment t06 | phòng thủ (MOVE) | nhẹ | TB (BFS vùng) | không | không |
| endgame t05 | điều phối weight | không | ~0 | không | không |
| Alpha-Beta a02 | **policy thay thế** | có | **NẶNG** | n/a | **có** |
| BC/PPO/DQN a03–a05 | **policy thay thế** | (train) | rẻ (1 forward) | n/a | **có** |

→ Hai nguồn xung đột chính lộ ra: **cột "Vào offense"** (double-count → đặt bom bừa) và **cột "policy thay thế"** (không stack được với nhau hay với heuristic).

## 3. Ma trận cụm tấn công (nơi double-count tập trung)

| | chain | trap | seal | predict | pressure | denial |
|---|---|---|---|---|---|---|
| **chain** | — | ⚠️ | ✅ | ✅ | ⚠️ | ⚪ |
| **trap** | ⚠️ | — | ⚠️ | ⚠️ | ⚠️ | ⚪ |
| **seal** | ✅ | ⚠️ | — | ⚪ | ⚪ | ⚪ |
| **predict** | ✅ | ⚠️ | ⚪ | — | ⚠️ | ⚪ |
| **pressure** | ⚠️ | ⚠️ | ⚪ | ⚠️ | — | ⚪ |
| **denial** | ⚪ | ⚪ | ⚪ | ⚪ | ⚪ | — |

⚠️ ở đây = **không sai về ý tưởng nhưng CÙNG cộng vào `offense`** → phải qua **trần offense chung** + gate ngữ nghĩa, nếu không sẽ tính trùng một tình huống và đặt bom bừa. ✅ = cộng hưởng thật (chain rút ngắn `t_det` cho predict; seal nối tiếp chain).

## 4. Các cặp đáng chú ý (cross-group)

- ✅ **a01 (benchmark đúng luật) → TẤT CẢ**: tiên quyết để đo; thiếu nó thì mọi "cải thiện" đều mù. **t05 (endgame) bắt buộc cần a01** (không áp tie-break thì không thấy lợi ích).
- ✅ **herding t01 → seal t02 / chain 06 / trap**: lùa địch vào hẻm rồi mới kết liễu (dựng thế → ra đòn).
- ✅ **herding t01 ↔ containment t06**: đối xứng tấn công/phòng thủ, **chung `opponent_model` + phát hiện choke** → viết 1 lần dùng cả hai.
- ✅ **chain 06 + predict t03**: chain làm `t_det` nhỏ → horizon dự đoán ngắn → đáng tin.
- ✅ **a03 (BC) → a04/a05 (PPO/DQN)**: warm-start.
- ⚠️ **aggression (t01/t03/denial) vs containment t06**: một bên đẩy lại gần địch, một bên giữ khoảng cách & vùng mở → **cùng nặng → dao động/thụ động**. Cân bằng: containment chỉ *reorder mềm*, aggression gate theo độ chắc.
- ⚠️ **endgame t05 vs cụm tấn công**: khi "đang dẫn + gần 500", t05 **giảm** pressure/trap để giữ hạng — đúng ý đồ, nhưng nếu mis-tune sẽ dập luôn các kill đang cần khi *đang thua*. Phải thử cả 2 nhánh leading/chasing.
- ⛔ **Alpha-Beta a02 ⟷ heuristic tấn công t01/t02/t03**: a02 **tổng quát hoá** chúng (search tự thấy trap/seal/herd qua nhiều ply). Chạy **cả hai** = vừa **trùng lặp logic** vừa **đội latency**. → Chọn **"đường heuristic"** *hoặc* **"đường search"**, không chồng.
- ⛔ **policy học a03/a04/a05 ⟷ mọi tuyệt chiêu scoring**: BC/PPO/DQN là **policy THAY THẾ** `RulePolicy`. Tuyệt chiêu là điểm cộng *trong* scoring rule → **không áp dụng** cho bản BC/PPO. Chỉ `final_shield` dùng chung. Đừng kỳ vọng "BC + chain-bomb scoring" cùng lúc.

## 5. Ràng buộc TOÀN CỤC — nơi "vô tình" làm agent tệ

1. **Latency 100ms = tài nguyên chung.** a02 (search) + nhiều BFS địch (t01/t02/t03/t06) **cộng dồn mỗi step**. Vượt 100ms → engine trả **STOP** (thảm hoạ: agent đứng im & dễ chết). → Đặt **ngân sách latency**, deadline nội bộ, đo **p99** sau mỗi lần thêm; không bật search + nhiều heuristic-nặng cùng lúc.
2. **Trần `offense` chung.** Trong [score_action_components](../../agent/team_agent/person_b_strategy/scoring.py), `offense = pressure_raw + trap_raw` và `useless_bomb_penalty` tắt khi `offense>0`. Mọi điểm tấn công mới (chain/seal/predict/denial) phải cộng vào `offense` **rồi cap tổng** — nếu không, useless-penalty mất tác dụng và agent **đặt bom bừa**.
3. **Nhất quán mô hình địch.** chain = địch **bị bất ngờ**; trap/seal = địch **né hoàn hảo**; predict = địch **đi greedy**. Trộn → scoring **mâu thuẫn nội tại**. → 1 `opponent_model` dùng chung + ghi rõ giả định từng chiêu; tránh hai chiêu giả định ngược nhau cùng nặng.
4. **Cân bằng trọng số.** Mỗi component mới **làm loãng** survival/farm. Tương tác với `apply_escape_bias` (đang nhân ×0.10 lên pressure/trap khi đang nguy hiểm) và `adjusted_weights` (tăng farm/loop khi kẹt). → **re-tune `phase_profile` + ablation** sau MỖI lần thêm, không thêm 2–3 cái rồi mới đo.
5. **`final_shield` bất biến.** Mọi hướng (kể cả a02/a03/a04/a05) phải đi qua; **không hướng nào được nới safety** để "mạnh hơn".

## 6. Quy tắc "nên tránh nhau" (tổng hợp)

- ⛔ **Search (a02) + cụm heuristic tấn công** cùng bật → trùng + vỡ latency.
- ⛔ **Policy học (a03/a04/a05) + tuyệt chiêu scoring** trên cùng bản nộp → không áp dụng được.
- ⚠️ **>1 điểm offense mà KHÔNG có trần chung** → đặt bom bừa.
- ⚠️ **aggression mạnh + containment mạnh** → dao động/thụ động.
- ⚠️ **radius-snapshot (a01) bớt bảo thủ** đổi `bomb_radius` → đổi toàn bộ hazard → tác động *mọi* chiêu đặt bom; phải engine-verify self-death=0 trước, rồi mới chồng chiêu tấn công.

## 7. Giao thức tích hợp an toàn (ablation)

1. **One-change-at-a-time**: chỉ thêm 1 thành phần mỗi lần.
2. Sau mỗi lần: chạy **benchmark đúng luật** (process riêng · 4 góc · tie-break — [01](01_quick_wins_va_benchmark_trung_thuc.md)) + `test_engine_safety` (**self-death=0**) + **timing p99 < 100ms**.
3. **Giữ** nếu ≥ ver3 trên *nhiều* metric (kills/avg_rank không đánh đổi survival); **revert** nếu tệ hoặc timeout.
4. **Thứ tự khuyến nghị**: `a01` → `t05` → `t06` → `t04` (rủi ro thấp, không cần/ít opponent_model) → `chain 06` + `t01/t02/t03` (có trần offense + opponent_model chung) → **rẽ nhánh**: `a02` (search) **hoặc** `a03→a04/a05` (học) — **không cả hai**.

## 8. Watch-list suy thoái (đo sau mỗi thay đổi)

| Chỉ số | Ngưỡng/kỳ vọng |
|---|---|
| `self_death_rate` | **= 0** (bất biến) |
| latency **p99** | **< 100ms** |
| `avg_kills` / `avg_rank` (đúng luật) | không giảm |
| `draw_rate` | không tăng |
| **tỉ lệ bomb có ích** | không giảm (chống đặt bom bừa) |
| action distribution (STOP/move/bomb) | không lệch bất thường — mở rộng [bench/analyze_data_logs.py](../../agent/team_agent/bench/analyze_data_logs.py) |

## 9. Bundle khuyến nghị cho bản nộp kế tiếp

- **Bundle A — rule pragmatic (khuyến nghị, rủi ro thấp)**: `a01` + `t05` + `t06` + `t04` + `chain 06` (có **trần offense chung**). Không cặp ⛔, không vỡ latency, đánh trúng kill/endgame/phòng thủ. Thêm `t01/t02/t03` *sau* nếu ablation còn dư địa.
- **Bundle B — search**: `a01` + `a02` (Alpha-Beta đơn lẻ, mô hình địch nhất quán) — **không** kèm cụm heuristic tấn công.
- **Bundle C — học**: `a01` + `a03` (BC) rồi `a04`/`a05` — **không** kèm tuyệt chiêu scoring; chỉ giữ `final_shield`.

> Chọn **một** bundle cho mỗi bản nộp; đừng trộn A với B/C. `ver3` luôn là fallback.

## Tham chiếu

[00_README_tong_quan](00_README_tong_quan.md) · [tuyet_chieu/00_README](tuyet_chieu/00_README.md) (cảnh báo double-count gốc) · [01 benchmark đúng luật](01_quick_wins_va_benchmark_trung_thuc.md) · [02 Alpha-Beta](02_alpha_beta_search.md) · [scoring.py](../../agent/team_agent/person_b_strategy/scoring.py).
