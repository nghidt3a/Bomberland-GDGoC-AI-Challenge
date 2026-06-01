# 06 — Kỷ luật giữ đường thoát / chống bị lùa (phòng thủ chủ động)

## 1. TL;DR

- **Verdict**: ver3 đã không tự sát (shield) nhưng **chưa có bất biến "giữ ≥2 đường thoát độc lập"** và **chưa nhận biết bị địch lùa**. Thêm `containment_penalty` (mềm, chỉ reorder nước đã an toàn).
- **ROI cao** (giảm bị trap = giảm chết/loss), **rủi ro/công sức THẤP, không train**. Là mặt phòng thủ đối xứng của [01 herding](01_lua_don_hem_cut.md).
- **Go/no-go**: death/loss-rate↓ (đặc biệt do bị địch dồn) mà farm không tụt; ≥ ver3.

## 2. Chiêu là gì & closes gap nào

Tránh đi vào ô mà **một bom địch ở choke có thể bịt kín** (ô khớp/articulation), và **nhận ra khi vùng tự do của mình đang co lại** (bị lùa) để thoát ra vùng mở sớm. Trúng gap: ver3 an toàn *từng-tick* nhưng có thể **tự đi vào túi cụt** rồi bị địch bom bịt — `final_shield` lúc đó hết nước.

## 3. ver3 đã có gì (gap)

- [positional_risk / enemy_risk_penalty](../../../agent/team_agent/person_b_strategy/scoring.py): phạt **mềm** khi ở sát địch trong ô chật (`open_neighbors<=2`) — nhưng chỉ xét **láng giềng tức thời**, không xét **vùng thoát toàn cục** hay **choke**.
- [safe_actions](../../../agent/team_agent/person_a_safety/masks.py) đòi *có* đường thoát, nhưng **1 đường mong manh** vẫn pass (địch bom 1 phát là kẹt).
- Không theo dõi **vùng tự do co lại theo thời gian** (bị lùa).

## 4. Thiết kế tích hợp (build-ready)

Thêm `containment_penalty(state, next_pos, hazard)` cho **action MOVE/STOP**; component `"containment_penalty"`; weight `containment`. Thêm theo dõi lịch sử vùng vào [loop_tracker](../../../agent/team_agent/person_b_strategy/loop_tracker.py).

```python
def containment_penalty(state, next_pos, hazard):
    # vùng an toàn với tới được từ next_pos
    area = safe_relative_distances(state, hazard, start=next_pos, start_time=1)  # reuse search.py
    n_reach = len(area)
    exits = open_neighbors(state, next_pos)                 # số lối ra trực tiếp
    pen = 0.0
    if n_reach <= SMALL_AREA:        pen += (SMALL_AREA - n_reach) * 0.3   # vùng nhỏ = nguy cơ bị nhốt
    if exits <= 1:                   pen += 2.0                            # ngõ cụt/1 lối
    # nặng hơn nếu địch ở vị trí có thể bom cái choke
    if state.opponents:
        choke = sole_exit_cell(state, next_pos)             # opponent_model / BFS
        if choke is not None and any(manhattan(e, choke) <= e_reach for e in state.opponents):
            pen += 2.5
    return pen   # trả về dương; component = -weights.containment * min(pen, 6.0)
```

- Counter-herding: trong `loop_tracker` lưu `recent_area_sizes`; nếu **vùng tự do co liên tục vài bước** và có địch gần → tăng nhẹ `containment` (bias thoát ra vùng mở). Reuse cấu trúc `deque` sẵn có.
- **Chỉ reorder nước đã an toàn** (safe mask vẫn là cổng cứng) → không bao giờ làm agent kẹt cứng vì điểm phạt; chỉ *ưu tiên* nước thoáng hơn khi ngang ngửa.
- Reuse [search.safe_relative_distances](../../../agent/team_agent/person_a_safety/search.py), `open_neighbors`. Giữ `final_shield`.

## 5. Ngân sách 100ms

1 BFS vùng (đã dùng kiểu này ở scoring) cho ô đích của vài nước MOVE — reuse hạ tầng có sẵn. Rẻ. Không model/train.

## 6. Test & đo

- Smoke: 2 ô an toàn ngang điểm, một dẫn vào túi cụt 1 lối có địch gần choke, một ra vùng mở → agent chọn vùng mở (`containment_penalty` lớn hơn ở túi cụt).
- `test_engine_safety` self-death=0; benchmark đúng luật: **death/loss do bị dồn↓**, farm không tụt; ≥ ver3.

## 7. Rủi ro & lan can

- **Quá thận trọng → thụ động/né cả ô farm tốt** → weight vừa phải; vẫn cho vào túi cụt **ngắn** nếu lối ra rõ và không có địch ở choke. Chỉ là điểm mềm.
- **Đối nghịch nhẹ với farm**: đôi khi box ngon nằm trong ngách → để `box_*` thắng khi địch không đe doạ choke (gate theo `manhattan(e, choke)`).
- Là mặt phòng thủ của [01 herding](01_lua_don_hem_cut.md): dùng chung khái niệm vùng/choke trong `opponent_model`.

## 8. Công sức & timeline · Tham chiếu

- **Công sức**: ~1 ngày. Cụm **rủi ro thấp làm sớm** (cùng 05/04).
- **Tham chiếu**: [01_lua_don_hem_cut.md](01_lua_don_hem_cut.md) (đối xứng tấn công), [../../../agent/team_agent/person_a_safety/search.py](../../../agent/team_agent/person_a_safety/search.py), [../02_alpha_beta_search.md](../02_alpha_beta_search.md) (search thấy được bẫy nhiều bước).
