# 06 — Chain-bomb tấn công (khai thác bom địch để kích nổ sớm)

## 1. TL;DR / Kết luận nhanh

- **Verdict**: ver3 **chưa có** chiêu này như một chiến thuật *chủ động*. Thêm 1 thành phần điểm `chain_bomb_score` — **rẻ, không train, rủi ro thấp**, đánh trúng điểm yếu **kill thấp**.
- An toàn đã được lo sẵn (engine chain reaction đã mô phỏng) → đây thuần là vá **mặt tấn công**.
- **Reuse 0 chi phí**: cắm vào nhánh `PLACE_BOMB` đã có sẵn `simulated`/`sim_hazard` → không thêm mô phỏng → giữ ngân sách 100ms.
- **Go/no-go**: giữ nếu **kills↑** mà draw/death không xấu đi trên benchmark đúng luật ([01](01_quick_wins_va_benchmark_trung_thuc.md)), và `test_engine_safety` vẫn **self-death=0**.

## 2. Ý tưởng & vì sao hợp ver3

Đặt bom của mình cạnh/thẳng hàng một **bom địch có timer ngắn**: chain reaction kéo bom mình **nổ sớm** (ở tick của bom địch, không phải tick 7). Lợi: vùng nổ kết hợp ập tới **sớm hơn địch dự đoán** → kill địch tưởng còn an toàn, trong khi mình *biết trước* thời điểm nổ-sớm nên vẫn né kịp.

ver3 đã mô phỏng chain reaction **cho phòng thủ** ([danger.py::compute_hazard_map](../../agent/team_agent/person_a_safety/danger.py)) nhưng **không có điểm tấn công** nào tìm nước này:
- `pressure_score` chỉ xét blast hình học tức thời của *riêng* bom mình (bỏ qua timing + vùng nổ kết hợp).
- `trap_score` bắt gián tiếp, **chỉ địch gần nhất trong tầm `self_radius+2`** và **giả định địch né hoàn hảo** (không khai thác bất ngờ).
- Hệ quả: quả chain-kill ngon nhưng không phá box & địch không trong blast tức thời của mình → bị [useless_bomb_penalty](../../agent/team_agent/person_b_strategy/scoring.py) **loại bỏ**.

## 3. ver3 đã có sẵn gì để tái dùng

- Nhánh `PLACE_BOMB` trong [scoring.py::score_action_components](../../agent/team_agent/person_b_strategy/scoring.py) **đã tính** `simulated = copy_state_with_new_bomb_at_self(state)` và `sim_hazard = compute_hazard_map(simulated)` → tái dùng nguyên vẹn.
- `hazard` (tham số sẵn, = `compute_hazard_map(state)` **không có** bom mới của mình) → chính là **"hazard ngây thơ" mà địch tin** (chỉ các bom đang có, theo timer riêng).
- [danger.py::earliest_at](../../agent/team_agent/person_a_safety/danger.py): lấy tick cháy sớm nhất của 1 ô.
- [search.py::time_expanded_bfs](../../agent/team_agent/person_a_safety/search.py) / [scoring.py::enemy_escape_count](../../agent/team_agent/person_b_strategy/scoring.py): mô hình né của địch.
- `state.opponents`, [scoring.py::manhattan](../../agent/team_agent/person_b_strategy/scoring.py), `BOMB_TIMER=7` ([constants.py](../../agent/team_agent/person_a_safety/constants.py)).
- Escape của mình đã được bảo đảm: `PLACE_BOMB` chỉ vào `safe_mask` khi [bomb.py::can_place_bomb_safely](../../agent/team_agent/person_a_safety/bomb.py) đúng (đường thoát ứng với nổ-sớm). Scoring chỉ chấm action trong mask ⇒ chain bonus **chỉ áp cho bom mình chắc chắn né được**.

## 4. Thiết kế tích hợp (build-ready)

Thêm hàm `chain_bomb_score` trong [scoring.py](../../agent/team_agent/person_b_strategy/scoring.py); thêm field `chain` vào `ScoreWeights`; cắm vào nhánh `PLACE_BOMB`. (Cần `from person_a_safety.constants import BOMB_TIMER`.)

### 4.1 Hàm điểm

```python
def chain_bomb_score(state, simulated, sim_hazard, naive_hazard) -> float:
    """Thưởng khi bom mình bị bom CÓ SẴN kích nổ SỚM và bắt được địch bất ngờ.
    naive_hazard = compute_hazard_map(state)  # = tham số 'hazard', KHÔNG có bom mới của mình
    """
    if not state.opponents:
        return 0.0
    t_chain = earliest_at(sim_hazard, state.self_pos)
    if t_chain >= BOMB_TIMER:          # bom mình nổ đúng timer riêng -> KHÔNG có chain sớm
        return 0.0

    score = 0.0
    for enemy in state.opponents:
        # (v1) địch đang đứng trong vùng nổ KẾT HỢP tại tick nổ-sớm?
        if not bool(sim_hazard[t_chain][enemy]):
            # (v1b) hoặc địch né tới ô mà nó TƯỞNG an toàn nhưng thực ra cháy ở t_chain
            if not _enemy_surprised(state, enemy, t_chain, sim_hazard, naive_hazard):
                continue
        # địch "tưởng an toàn": dưới naive_hazard, ô địch KHÔNG cháy tại/đến t_chain
        believes_safe = not bool(naive_hazard[: t_chain + 1, enemy[0], enemy[1]].any())
        score += 1.5 if believes_safe else 0.5     # bất ngờ thật ăn đậm hơn
    # nổ càng sớm càng khó né
    score *= 1.0 + 0.15 * max(0, (BOMB_TIMER - t_chain))
    return min(score, 3.0)
```

`_enemy_surprised` (tùy chọn, v2): so số ô thoát của địch bằng `enemy_escape_count` với **horizon = t_chain** dưới `naive_hazard` vs `sim_hazard`; nếu giảm → bị dồn bất ngờ. v1 (chỉ xét địch trong `sim_hazard[t_chain]`) đã đủ để bắt đầu.

### 4.2 Cắm vào `score_action_components` (nhánh PLACE_BOMB)

```python
# trong khối: if action == PLACE_BOMB and _can_simulate_bomb(state):
    escape_quality = bomb_escape_quality(state, simulated, sim_hazard)
    trap_raw       = trap_score(state, hazard, simulated, sim_hazard)
    chain_raw      = chain_bomb_score(state, simulated, sim_hazard, hazard)   # <-- THÊM (hazard = naive)
...
offense = pressure_raw + trap_raw + chain_raw        # <-- chain vào offense -> hủy useless penalty
components["chain_bonus"] = weights.chain * chain_raw # <-- THÊM component
```

Thêm `chain: float = 9.0` vào `ScoreWeights`; trong `phase_profile` đặt cao hơn ở `mid`/`late_chasing`, thấp ở `early`. Pipeline `act()` **không đổi** (vẫn `RulePolicy` → `final_shield`).

## 5. Ngân sách 100ms / tài nguyên

- **0 mô phỏng thêm**: dùng lại `sim_hazard` (đã tính) và `hazard` (đã tính). Chỉ vài lát cắt mảng + (v2) 1 BFS địch horizon nhỏ.
- Không model, không train, không file kèm. Không ảnh hưởng startup.

## 6. Kế hoạch test & đo

- **Unit (smoke)**: dựng state — bom địch timer ngắn cạnh ô mình, địch đứng trong vùng nổ kết hợp tại `t_chain` ⇒ `chain_bomb_score > 0`; không có bom địch / không có chain sớm ⇒ `= 0`; địch ở ô nó *biết* sẽ cháy (trong naive_hazard) ⇒ điểm thấp hơn (không "bất ngờ").
- **An toàn**: `TEAM_SAFETY_SEEDS=60 pytest .../test_engine_safety.py` vẫn **self-death=0, bad-action=0** (shield + can_place_bomb_safely vẫn là cổng).
- **Sức mạnh**: benchmark đúng luật ([01](01_quick_wins_va_benchmark_trung_thuc.md)) so ver3 — kỳ vọng **avg_kills↑**, draw/death **không xấu đi**. Go/no-go = **≥ ver3**.

## 7. Rủi ro & lan can

- **Đối thủ có lường chain** (vd Genius có thể) → chiêu bị vô hiệu **nhưng không hại**: vẫn có escape (đã gate), chỉ là không ăn kill. Thưởng giữ **bảo thủ**: chỉ cộng khi địch *thực sự* trong vùng nổ kết hợp tại `t_chain`.
- **Double-count với `trap_score`** → tách bạch ngữ nghĩa: `chain_bomb_score` khai thác **bom CÓ SẴN của địch** (điều kiện `t_chain < BOMB_TIMER`); `trap_score` đo dồn ép do **bom mình tự tạo**. Cap riêng + weight vừa phải để không cộng dồn quá đà.
- **Cường điệu "bất ngờ"** → nếu nghi ngờ mô hình địch, hạ hệ số `believes_safe` hoặc chỉ dùng v1.

## 8. Công sức & timeline · Tham chiếu

- **Công sức**: ~1–1.5 ngày (hàm + weight + 1–2 smoke test + đo). Làm cùng cụm scoring của [01](01_quick_wins_va_benchmark_trung_thuc.md); hoặc xem như payoff tường minh, rẻ của [02](02_alpha_beta_search.md).
- **Tham chiếu**: chain reaction trong [../../docs/COMPETITION_GUIDE.md](../../docs/COMPETITION_GUIDE.md) (mục 2) & `AI_Challenge_..._sieu_chi_tiet.md` mục 4.3; [02_alpha_beta_search.md](02_alpha_beta_search.md) (chain-kill là payoff của search); [01](01_quick_wins_va_benchmark_trung_thuc.md) (thước đo).
