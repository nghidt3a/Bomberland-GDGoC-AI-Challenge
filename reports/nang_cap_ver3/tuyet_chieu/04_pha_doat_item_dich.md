# 04 — Phá / đoạt item của địch (denial & contest)

## 1. TL;DR

- **Verdict**: ver3 chỉ **né tranh item** (`enemy_contest_risk`), chưa **chủ động phá** item địch sắp lấy (không cho địch mạnh lên). Thêm `item_denial_score`.
- **ROI trung bình, rủi ro/công sức THẤP** — dễ làm, không train. Một phần cần mô hình địch (ai tới item trước).
- Hai biến thể: (a) **bom phá item** địch sắp lấy; (b) **đạp item cùng tick** để huỷ (engine: ≥2 agent vào ô item → item bị huỷ).
- **Go/no-go**: hạn chế địch farm power-up mà không giảm farm của mình; ≥ ver3.

## 2. Chiêu là gì & closes gap nào

Power-up (radius/capacity) quyết định sức mạnh cuối trận. Nếu mình **không kịp lấy** một item giá trị mà địch sắp lấy → **phá nó** (bom phủ ô item, hoặc đạp cùng tick) để **từ chối** địch tăng sức mạnh. Trúng gap **kiểm soát kinh tế đối thủ** (ver3 chỉ tối ưu kinh tế của mình).

## 3. ver3 đã có gì (gap)

- [enemy_contest_risk](../../../agent/team_agent/person_b_strategy/scoring.py): chỉ khiến **mình bỏ qua** item mà địch tới kịp/nhanh hơn — thuần phòng thủ kinh tế.
- [item_value / item_targets](../../../agent/team_agent/person_b_strategy/scoring.py): đánh giá item cho **mình lấy**, không có khái niệm "phá của địch".
- Cơ chế engine khai thác (xem [engine/game.py](../../../engine/game.py) + [COMPETITION_GUIDE](../../../docs/COMPETITION_GUIDE.md)): **nổ huỷ item**; **≥2 agent cùng vào ô item → item bị huỷ, không ai nhận**.

## 4. Thiết kế tích hợp (build-ready)

Thêm `item_denial_score(state, action, next_pos, simulated, sim_hazard)` trong [scoring.py](../../../agent/team_agent/person_b_strategy/scoring.py); component `"deny_bonus"`; weight `deny`.

```python
def item_denial_score(state, action, next_pos, simulated, sim_hazard):
    score = 0.0
    for cell in high_value_item_cells(state):              # ITEM_RADIUS/ITEM_CAPACITY giá trị cao (reuse item_value)
        my_d  = my_safe_dist_to(cell)                      # reuse safe_distances
        en_d  = min(manhattan(e, cell) for e in state.opponents) if state.opponents else INF
        if my_d <= en_d:                                   # mình tới trước -> đi lấy (đã có item_move_score lo)
            continue
        val = item_value(state, cell)
        # (a) bom phá item: action PLACE_BOMB và vùng nổ phủ ô item (reuse sim_hazard bất kỳ tick)
        if action == PLACE_BOMB and sim_hazard[:, cell[0], cell[1]].any():
            score = max(score, 0.8 * val)
        # (b) đạp cùng tick: action MOVE tới ô item mà địch cũng tới ngay -> huỷ item
        if action != PLACE_BOMB and next_pos == cell and en_d <= 1:
            score = max(score, 0.6 * val)
    return min(score, 2.0)
```

- `high_value_item_cells` = các ô item mà `item_value` cao (vd radius khi địch radius thấp). `my_safe_dist_to` reuse [search.safe_distances](../../../agent/team_agent/person_a_safety/search.py).
- (a) cộng vào `offense` (để không bị `useless_bomb_penalty` loại quả bom phá-item); (b) là điểm cho MOVE.
- Giữ `final_shield`; bom phá item vẫn phải có escape (safe_mask).

## 5. Ngân sách 100ms

Lặp vài ô item + vài phép khoảng cách + reuse `sim_hazard`/`safe_distances` (đã tính). Rẻ. Không model/train.

## 6. Test & đo

- Smoke: item radius giá trị cao, địch cách 1 ô còn mình cách 3 → `PLACE_BOMB` phủ ô item cho `deny_bonus>0`; mình tới trước → 0.
- `test_engine_safety` self-death=0; benchmark đúng luật: theo dõi **địch ít power-up hơn** (gián tiếp qua avg_rank↑) mà boxes/items của mình không tụt; ≥ ver3.

## 7. Rủi ro & lan can

- **Phá item = phí lượt/bom của mình** → chỉ kích hoạt với **item giá trị cao** và **mình chắc chắn thua cuộc đua**; weight vừa phải.
- **(b) đạp cùng tick** rủi ro vị trí (lại gần địch) → gate `en_d<=1` + `positional_risk` vẫn áp.
- **Double-count**: tách rõ với `item_move_score` (mình lấy) bằng điều kiện `my_d > en_d`.

## 8. Công sức & timeline · Tham chiếu

- **Công sức**: ~1 ngày. Thuộc cụm **rủi ro thấp làm sớm** (cùng 05/06).
- **Tham chiếu**: [03_bom_don_dau_du_doan.md](03_bom_don_dau_du_doan.md) (chung mô hình địch→item), cơ chế huỷ item trong [../../../docs/COMPETITION_GUIDE.md](../../../docs/COMPETITION_GUIDE.md) (mục 2 & 5), [../01_quick_wins_va_benchmark_trung_thuc.md](../01_quick_wins_va_benchmark_trung_thuc.md).
