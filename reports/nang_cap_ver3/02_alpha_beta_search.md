# 02 — Alpha-Beta / Expectimax Search (lookahead trên scoring)

## 1. TL;DR / Kết luận nhanh

- **Verdict**: Hướng nâng cấp **ROI cao nhất mà KHÔNG cần train**. Nên làm sớm, song song với [01](01_quick_wins_va_benchmark_trung_thuc.md).
- ver3 hiện là **greedy depth-1** (chỉ chấm action ngay lập tức). Thêm lookahead 2–3 bước = đánh trúng điểm yếu **kill thấp / draw cao** (thấy trước bẫy & cơ hội kill).
- **Tận dụng gần như toàn bộ ver3**: forward model + hàm lá `E(s)` = scoring sẵn có. Chỉ thêm 1 file policy.
- **Rủi ro chính**: 100ms budget + minimax worst-case làm agent **nhút nhát hơn** → dùng **expectimax với mô hình địch rẻ** + deadline nội bộ + fallback depth-1.
- **Go/no-go**: giữ nếu **≥ ver3** trên benchmark đúng luật (01) và **max latency < 100ms** ổn định; không thì fallback depth-1 (= ver3).

## 2. Ý tưởng & vì sao hợp ver3

[scoring.py](../../agent/team_agent/person_b_strategy/scoring.py) đã làm sẵn vài "lookahead thủ công" rời rạc (`trap_score` mô phỏng đặt bom rồi đếm ô thoát địch; `bomb_escape_quality`). Alpha-Beta **tổng quát hóa** việc đó: thay vì hard-code từng heuristic 1 bước, ta **duyệt cây trò chơi tới độ sâu `d`** và để `E(s)=scoring` chấm các nút lá. Lợi ích: bắt được tương tác nhiều bước mà heuristic 1 bước bỏ sót (vd "đi đây thì 2 bước nữa địch dồn mình vào hẻm cụt", hoặc "đặt bom + ép hướng → kill"). Đây chính là *hybrid heuristic search* mà [docs so sánh](../../docs/chien_luoc_thi_dau_bomberland_vi/09_so_sanh_cac_huong_tiep_can.md) gọi là "hướng thực dụng nhất".

> **Liên quan [06 — chain-bomb](06_chain_bomb_offensive.md)**: kill bằng cách chain off bom địch (kích nổ bom mình sớm) là một *payoff* mà search depth-d sẽ tự phát hiện — **miễn là mô hình địch KHÔNG giả định né-hoàn-hảo-chain**. Doc 06 là bản heuristic rẻ, độc lập với search, làm được ngay mà không cần dựng cây.

## 3. ver3 đã có sẵn gì để tái dùng

| Thành phần search | Hàm có sẵn |
|---|---|
| **Forward model** (state→state') | [search.py::move](../../agent/team_agent/person_a_safety/search.py) (di chuyển) · [bomb.py::copy_state_with_new_bomb_at_self](../../agent/team_agent/person_a_safety/bomb.py) (đặt bom) · [danger.py::compute_hazard_map](../../agent/team_agent/person_a_safety/danger.py) (tái tính lửa) |
| **Sinh nước hợp lệ/an toàn** | [masks.py::safe_actions](../../agent/team_agent/person_a_safety/masks.py) (branching nhỏ: thường 2–4 nước) |
| **Hàm lá `E(s)`** | [scoring.py::score_action / score_actions](../../agent/team_agent/person_b_strategy/scoring.py) (đã có sẵn, tinh chỉnh tốt) |
| **Cổng an toàn cuối** | [shield.py::final_shield](../../agent/team_agent/person_a_safety/shield.py) |
| **Fallback depth-1** | [policy_rule.py::RulePolicy](../../agent/team_agent/person_b_strategy/policy_rule.py) |
| **Cập nhật trạng thái địch** | obs cho biết vị trí địch mỗi step → mô hình địch rẻ |

→ Phần "khó nhất" (mô phỏng lửa chính xác + chấm điểm) **đã có**. Chỉ cần lớp duyệt cây.

## 4. Thiết kế tích hợp (build-ready)

Thêm file mới `person_b_strategy/policy_search.py`. [agent.py](../../agent/team_agent/agent.py) chọn policy này (vẫn qua `final_shield` cuối cùng).

### 4.1 Khung 1-vs-All + expectimax (KHÔNG dùng worst-case thuần)

```python
# policy_search.py
import time
from person_a_safety.masks import safe_actions
from person_a_safety.danger import compute_hazard_map
from person_b_strategy.scoring import score_actions  # E(s) cho nút lá

INTERNAL_DEADLINE_MS = 65   # chừa biên dưới 100ms

def choose_action(state, hazard, deadline_ms=INTERNAL_DEADLINE_MS):
    t0 = time.perf_counter()
    best = rule_fallback(state, hazard)        # luôn có sẵn 1 đáp án (= depth-1)
    for depth in range(2, MAX_DEPTH + 1):      # iterative deepening
        try:
            val, action = _search(state, hazard, depth, -INF, +INF, t0, deadline_ms)
            best = action                      # chỉ nhận khi search depth này XONG
        except _Timeout:
            break
    return best

def _search(state, hazard, depth, alpha, beta, t0, deadline_ms):
    if (time.perf_counter() - t0) * 1000 > deadline_ms:
        raise _Timeout
    if depth == 0 or _terminal(state):
        return leaf_value(state, hazard), None      # E(s)

    actions = ordered_safe_actions(state, hazard)   # move ordering (mục 4.3)
    best_val, best_act = -INF, actions[0]
    for a in actions:                               # nút MAX = agent ta
        ns = apply_self_action(state, a)            # forward model
        # nút "Min/Chance" = phản ứng địch (mục 4.2)
        val = expected_opponent_value(ns, depth - 1, alpha, beta, t0, deadline_ms)
        if val > best_val:
            best_val, best_act = val, a
        alpha = max(alpha, best_val)
        if alpha >= beta:                           # cắt tỉa Alpha-Beta
            break
    return best_val, best_act
```

### 4.2 Mô hình địch rẻ (tránh nhút nhát)

Minimax thuần giả định 3 địch hợp sức giết ta → quá bi quan trong FFA → agent co cụm (làm draw tệ thêm). Hai lựa chọn cho `expected_opponent_value`:

- **(Khuyến nghị) Expectimax với mô hình hành vi**: dự đoán mỗi địch đi 1 nước "hợp lý rẻ" (về box/item gần nhất hoặc né lửa — tái dùng BFS [search.py](../../agent/team_agent/person_a_safety/search.py)), rồi đệ quy. Không nhân branching theo địch.
- **(Tùy chọn) Minimax 1-vs-All giới hạn**: chỉ xét địch **gần nhất** chọn nước xấu nhất cho ta; 2 địch còn lại đứng yên. Rẻ, nhưng bi quan hơn.

### 4.3 Ép vào 100ms (rất quan trọng)

- **Chỉ mở rộng `safe_actions`** (branching 2–4, không phải 6).
- **Iterative deepening + deadline nội bộ ~65ms**: hết giờ trả kết quả depth hoàn chỉnh gần nhất.
- **Move ordering**: xét trước nước có `score_actions` cao (tận dụng cắt tỉa α-β tốt hơn).
- **Tái dùng cache**: hazard chỉ tái tính khi có đặt bom/box đổi; tránh copy `GameState` thừa.
- **Fallback cứng**: bất kỳ exception/timeout → `RulePolicy` depth-1 (= hành vi ver3 hiện tại).

### 4.4 Điểm cắm pipeline

```
act(): parse_obs → compute_hazard_map → safe_actions(mask)
     → policy_search.choose_action(...)        # THAY cho RulePolicy.choose_action
     → final_shield(raw, state, hazard, mask)   # GIỮ NGUYÊN cổng cứng
```

## 5. Ngân sách 100ms / tài nguyên

- Không train, không model file, chỉ numpy. Startup không đổi.
- Latency là rủi ro chính → deadline nội bộ + đo `p99`. Depth khả thi cần **đo thực nghiệm** (xem mục 6); kỳ vọng depth 2–3 với branching ≤4 và mô hình địch rẻ là khả thi dưới 100ms với engine này (avg ver3 chỉ ~8ms → còn nhiều biên).

## 6. Kế hoạch test & đo

- **Latency**: `scripts/participant/estimate_agent_time.py` cho bản search; phải max-spike < 100ms. Tăng `MAX_DEPTH` dần tới khi chạm trần → chốt depth an toàn.
- **An toàn**: `test_engine_safety.py` (60 seed) phải self-death=0 (shield vẫn cuối cùng).
- **Sức mạnh**: benchmark đúng luật (01) — search phải **≥ ver3**, kỳ vọng **kills↑ / draw↓**.
- Thêm test: timeout → fallback trả về đúng action depth-1.

## 7. Rủi ro & lan can

- **Latency vượt 100ms** → deadline nội bộ + iterative deepening + fallback depth-1.
- **Nhút nhát do worst-case** → expectimax mô hình hành vi thay vì minimax thuần; kiểm tra draw-rate không tăng.
- **Mô hình địch sai** → search "ảo tưởng"; giữ depth nhỏ, coi search như *tinh chỉnh* trên scoring, không thay scoring.
- Luôn fallback an toàn về ver3 ⇒ downside ~0.

## 8. Công sức & timeline · Tham chiếu

- **Công sức**: ~2–4 ngày (khung + mô hình địch + tune depth/deadline + đo). Làm ở giai đoạn đầu, song song 01.
- **Tham chiếu**: [../../docs/chien_luoc_thi_dau_bomberland_vi/huong_tiep_can/03_hybrid_rule_based_heuristic_search.md](../../docs/chien_luoc_thi_dau_bomberland_vi/huong_tiep_can/03_hybrid_rule_based_heuristic_search.md) · [.../04_minimax_alpha_beta_iterative_deepening.md](../../docs/chien_luoc_thi_dau_bomberland_vi/huong_tiep_can/04_minimax_alpha_beta_iterative_deepening.md) · `AI_Challenge_..._sieu_chi_tiet.md` mục 12–13 (Minimax/Alpha-Beta, heuristic E(s), iterative deepening, move ordering).
