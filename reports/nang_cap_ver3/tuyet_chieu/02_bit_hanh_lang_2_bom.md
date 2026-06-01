# 02 — Bịt 2 đầu hành lang bằng 2 bom (pincer / sealing)

## 1. TL;DR

- **Verdict**: ver3 chấm **mỗi quả bom độc lập**; chưa **phối hợp bom MÌNH đã đặt** với bom sắp đặt để bịt cả 2 lối thoát của địch. Thêm `seal_score`.
- **ROI cao** (kill chắc khi địch trong hành lang), công sức/rủi ro TB. Cần `capacity ≥ 2`.
- **Go/no-go**: kills↑, không tăng self-death (đặt quả 2 vẫn phải còn escape cho mình); ≥ ver3.

## 2. Chiêu là gì & closes gap nào

Địch đang ở trong hành lang/ngách 1 chiều: đặt **bom thứ 2** ở đầu còn lại sao cho **vùng nổ kết hợp (bom cũ của mình + bom mới)** phủ kín mọi lối → địch hết đường thoát. Trúng gap **kill thấp** trong các thế mà 1 bom không đủ bịt.

## 3. ver3 đã có gì (gap)

- [compute_hazard_map(simulated)](../../../agent/team_agent/person_a_safety/danger.py) **đã gộp mọi bom** (kể cả bom cũ của mình) → vùng nổ kết hợp *có* trong hazard.
- NHƯNG [trap_score](../../../agent/team_agent/person_b_strategy/scoring.py) chỉ xét **địch gần nhất** và **chỉ khi địch trong `self_radius+2` của MÌNH**, đo hiệu ứng *biên* của riêng quả mới. ⇒ Khi quả seal ĐẦU TIÊN của mình ở xa mình còn địch kẹt quanh nó, trap_score **bỏ lỡ**.
- Không có khái niệm "mình đang có sẵn bom trên sân → phối hợp".

## 4. Thiết kế tích hợp (build-ready)

Thêm `seal_score(state, simulated, sim_hazard)` trong [scoring.py](../../../agent/team_agent/person_b_strategy/scoring.py), gọi trong nhánh `PLACE_BOMB` (reuse `simulated`/`sim_hazard` đã tính như [chain 06](../06_chain_bomb_offensive.md) ⇒ 0 chi phí thêm). Cộng vào `offense` + component `"seal_bonus"`; weight `seal`.

```python
def seal_score(state, simulated, sim_hazard):
    own_active = [b for b in state.bombs if b.owner_id == state.agent_id]
    if not own_active or not state.opponents:        # cần ≥1 bom mình ĐANG có trên sân
        return 0.0
    best = 0.0
    for enemy in state.opponents:
        # chỉ xét địch ở gần MỘT trong các bom (mình cũ HOẶC mới) -> bound chi phí
        near = min([manhattan(enemy, b.pos) for b in own_active] +
                   [manhattan(enemy, state.self_pos)])
        if near > state.self_radius + 2:
            continue
        before = enemy_escape_count(state, enemy, hazard_now)        # hazard hiện tại
        after  = enemy_escape_count(simulated, enemy, sim_hazard)    # + bom mới (gộp bom cũ)
        if before <= 0:
            continue
        if after == 0:
            best = max(best, 2.5)                  # bịt kín cả 2 đầu -> kill
        else:
            best = max(best, 1.2 * (before - after) / before)
    return min(best, 2.5)
```

- `hazard_now` = tham số `hazard` sẵn có trong [score_action_components](../../../agent/team_agent/person_b_strategy/scoring.py).
- Khác `trap_score`: **lặp mọi địch** + xét **khoảng cách tới bom CŨ của mình** (không chỉ tới mình) → bắt được thế pincer.
- An toàn: PLACE_BOMB chỉ vào safe_mask khi [can_place_bomb_safely](../../../agent/team_agent/person_a_safety/bomb.py) đúng ⇒ đặt quả 2 vẫn đảm bảo mình thoát.

## 5. Ngân sách 100ms

Reuse `simulated`/`sim_hazard` (0 mô phỏng thêm) + vài BFS địch horizon nhỏ, chỉ cho địch ở gần bom. Rẻ. Không model/train.

## 6. Test & đo

- Smoke: map hành lang, 1 bom mình đã ở đầu A + địch giữa → đặt bom đầu B cho `seal_score` cao (after=0); không có bom cũ của mình → 0.
- `test_engine_safety` self-death=0; benchmark đúng luật: kills↑; ≥ ver3.

## 7. Rủi ro & lan can

- **Tốn cả 2 bom** (capacity) → chỉ thưởng khi `after` giảm mạnh/về 0; nếu không, để dành bom.
- **Double-count với trap/chain**: seal yêu cầu **có bom CŨ của mình** (`own_active` không rỗng) — gate phân biệt với trap (1 bom) và chain (bom địch). Đặt dưới trần `offense` chung ([00_README](00_README.md)).
- **Mô hình địch né hoàn hảo** (như enemy_escape_count) → bảo thủ; có thể kết hợp giả định địch-bị-bất-ngờ của [chain 06](../06_chain_bomb_offensive.md) nếu muốn mạnh hơn.

## 8. Công sức & timeline · Tham chiếu

- **Công sức**: ~1–1.5 ngày. Làm cùng cụm tấn công với [01](01_lua_don_hem_cut.md)/[chain 06](../06_chain_bomb_offensive.md).
- **Tham chiếu**: [01_lua_don_hem_cut.md](01_lua_don_hem_cut.md) (lùa địch vào hành lang trước), [../06_chain_bomb_offensive.md](../06_chain_bomb_offensive.md), [../02_alpha_beta_search.md](../02_alpha_beta_search.md).
