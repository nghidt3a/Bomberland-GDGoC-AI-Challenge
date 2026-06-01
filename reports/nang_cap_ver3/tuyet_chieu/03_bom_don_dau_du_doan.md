# 03 — Bom đón đầu theo dự đoán di chuyển địch

## 1. TL;DR

- **Verdict**: ver3 doạ/trap theo **vị trí địch HIỆN TẠI** — nhưng địch di chuyển trước khi bom nổ, nên bom thường trượt. Thêm `predict_bomb_score`: đặt bom phủ ô địch **sắp tới**.
- **ROI cao** nhưng **rủi ro TB–cao** (dự đoán sai → bom phí). **Cần mô hình địch.**
- **Hiệu quả nhất khi**: (a) bom nổ SỚM do chain ([06](../06_chain_bomb_offensive.md)) — horizon dự đoán ngắn, đáng tin; hoặc (b) địch bị **ép đi 1 đường** (cornered / chạy về item duy nhất). → gate theo độ tin cậy.
- **Go/no-go**: kills↑ mà không tăng bomb-phí (theo dõi tỉ lệ bomb có ích); ≥ ver3.

## 2. Chiêu là gì & closes gap nào

Bom nổ sau `t_det` tick; địch sẽ ở **ô khác** lúc đó. Đón đầu = đặt bom sao cho **vùng nổ tại `t_det` phủ ô địch ĐƯỢC DỰ ĐOÁN**. Trúng gap **kill thấp**: `pressure_score` chỉ tính địch trong blast *bây giờ*.

## 3. ver3 đã có gì (gap)

- [pressure_score](../../../agent/team_agent/person_b_strategy/scoring.py): dùng `blast_cells(self_pos, self_radius)` + vị trí địch hiện tại.
- [trap_score](../../../agent/team_agent/person_b_strategy/scoring.py): mô phỏng hazard nhưng địch vẫn lấy ở pos hiện tại; `enemy_escape_count` cho địch *né*, không *dự đoán địch tới đâu*.
- Không có mô hình "địch sẽ đi đâu".

## 4. Thiết kế tích hợp (build-ready)

Dùng `predict_enemy_path(state, enemy, k)` từ `opponent_model` (xem [00_README](00_README.md)): trả list ô địch dự kiến ở các tick 1..k (bước về target gần nhất / né lửa). Thêm `predict_bomb_score` gọi trong nhánh `PLACE_BOMB` (reuse `sim_hazard`).

```python
def predict_bomb_score(state, simulated, sim_hazard):
    if not state.opponents:
        return 0.0
    t_det = earliest_at(sim_hazard, state.self_pos)   # tick bom mình nổ (7 hoặc sớm hơn do chain)
    if t_det >= sim_hazard.shape[0]:
        return 0.0
    blast_at_det = sim_hazard[t_det]                  # vùng nổ kết hợp tại tick nổ
    best = 0.0
    for enemy in state.opponents:
        path = predict_enemy_path(state, enemy, k=t_det)   # ô địch dự kiến tới tick t_det
        conf = prediction_confidence(state, enemy)         # 1 nếu địch có 1 hướng ép buộc, ~0.2 nếu nhiều lựa chọn
        if t_det < len(path) and bool(blast_at_det[path[t_det]]):
            best = max(best, 1.5 * conf)
    return min(best, 2.0)
```

- `prediction_confidence`: cao khi địch bị cornered (ít lối — reuse `open_neighbors`/vùng reachable nhỏ) hoặc chỉ có 1 target rõ; thấp khi địch ở vùng mở nhiều lựa chọn → **tự hạ điểm khi đoán không chắc**.
- Cộng vào `offense` + component `"predict_bonus"`; weight `predict` (cao ở late_chasing). Reuse `earliest_at`, `sim_hazard`. Giữ `final_shield`.
- **Cộng hưởng với [chain 06](../06_chain_bomb_offensive.md)**: khi `t_det` nhỏ (chain sớm), dự đoán ngắn → đáng tin hơn nhiều.

## 5. Ngân sách 100ms

`predict_enemy_path` = vài bước BFS/greedy cho mỗi địch (rẻ); reuse `sim_hazard`. Không model/train.

## 6. Test & đo

- Smoke: địch 1 lối duy nhất hướng về item → ô dự đoán tại `t_det` nằm trong blast → `predict_bomb_score>0` với conf cao; địch ở ngã tư mở → conf thấp → điểm ~0.
- `test_engine_safety` self-death=0; benchmark đúng luật: theo dõi **kills↑** và **tỉ lệ bomb có ích không giảm** (chống đặt bom phí); ≥ ver3.

## 7. Rủi ro & lan can

- **Dự đoán sai → bom phí / lộ ý đồ** → gate bằng `prediction_confidence`, weight thấp, ưu tiên kết hợp chain (horizon ngắn).
- **Double-count** với pressure/trap → predict tính theo **ô tương lai**; nếu địch đã ở trong blast hiện tại thì pressure lo rồi (đặt trần `offense` chung, [00_README](00_README.md)).

## 8. Công sức & timeline · Tham chiếu

- **Công sức**: ~1.5–2 ngày (gồm `opponent_model.predict_enemy_path`). Làm sau cụm 05/06/04.
- **Tham chiếu**: [04_pha_doat_item_dich.md](04_pha_doat_item_dich.md) (chung mô hình "địch đi về item"), [../06_chain_bomb_offensive.md](../06_chain_bomb_offensive.md), [../02_alpha_beta_search.md](../02_alpha_beta_search.md) (search nội suy dự đoán này qua nhiều ply).
