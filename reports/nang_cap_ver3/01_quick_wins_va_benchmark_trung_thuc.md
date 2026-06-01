# 01 — Quick-wins + Benchmark trung thực

## 1. TL;DR / Kết luận nhanh

- **Verdict**: Làm **đầu tiên**, trước mọi nâng cấp khác.
- **ROI cao, công sức thấp, rủi ro thấp, không train.**
- Gồm 4 việc: (a) **benchmark áp tie-break + 4 góc** (tiên quyết), (b) tune `phase_profile` late-game để biến draw→thắng tie-break, (c) *(tùy chọn)* radius snapshot giảm bias bảo thủ, (d) version hygiene.
- **Go/no-go**: (a) và (d) làm ngay vô điều kiện; (b) giữ nếu **≥ ver3** trên benchmark mới; (c) chỉ giữ nếu engine-verify self-death vẫn = 0.

## 2. Ý tưởng & vì sao hợp ver3

Benchmark hiện tại ([bench/strategy_metrics.py](../../agent/team_agent/bench/strategy_metrics.py)) tính rank thuần theo thứ tự chết: **mọi agent sống tới step 500 đều = rank 0 (hòa)**. Nhưng luật thi áp **tie-break `kills > boxes > items > bombs`** cho nhóm sống sót (server làm, engine cục bộ không làm — `step()` chỉ trả `obs, terminated, truncated`). Vì ver3 farm box/item/bomb rất cao (boxes ~8, items ~8, bombs ~49), **rất nhiều "draw 90%" trong benchmark thực ra là thắng tie-break trên leaderboard** ⇒ ta đang đo thấp ver3 và **không có thước đo đúng luật để chấm các nâng cấp**. Đây là lý do nó là tiên quyết.

## 3. ver3 đã có sẵn gì để tái dùng

- [bench/strategy_metrics.py](../../agent/team_agent/bench/strategy_metrics.py): vòng benchmark; đã đọc `env.players[0].stats` (keys `kills/boxes/items/bombs`) và có `ranks_from_deaths(survivors, death_order)`.
- [engine/game.py](../../engine/game.py): `env.players[i].stats` có đủ 4 metric cho **mọi** player; `env.players[i].alive`.
- `scripts.participant.run_local_match.make_agents([agent_path, *opponents], seed)`: tạo agent theo thứ tự seat (agent_path → seat 0).
- [scoring.py::phase_profile](../../agent/team_agent/person_b_strategy/scoring.py): các profile `late_leading`/`late_chasing` (turn ≥ 350) đã tách sẵn — chỗ để tune aggression cuối trận.
- [danger.py::bomb_radius](../../agent/team_agent/person_a_safety/danger.py): hiện suy radius từ radius **hiện tại** của owner (over-estimate).

## 4. Thiết kế tích hợp (build-ready)

### 4a. Áp tie-break vào ranking (sửa `ranks_from_deaths` → `ranks_with_tiebreak`)

```python
# bench/strategy_metrics.py
TIEBREAK_KEYS = ("kills", "boxes", "items", "bombs")

def ranks_with_tiebreak(survivors, death_order, env):
    ranks = [0, 0, 0, 0]
    # 1) Người chết: rank theo thứ tự chết ngược (chết sau = rank tốt hơn)
    current_rank = len(survivors) if survivors else 1   # survivors chiếm các rank đầu
    # gán rank cho survivors trước (xem bước 2), rồi tới người chết:
    # 2) Survivors: KHÔNG còn đồng hạng — xếp theo tie-break giảm dần
    def key(pid):
        s = env.players[pid].stats
        return tuple(s.get(k, 0) for k in TIEBREAK_KEYS)
    ordered = sorted(survivors, key=key, reverse=True)
    rank = 0
    prev = None
    for i, pid in enumerate(ordered):
        if prev is not None and key(pid) != prev:   # khác stats → tụt hạng
            rank = i
        ranks[pid] = rank          # stats hệt nhau ⇒ chia sẻ rank (draw thật)
        prev = key(pid)
    # 3) Người chết nhận rank sau survivors
    base = len(survivors)
    for j, pid in enumerate(reversed(death_order)):
        ranks[pid] = base + j
    return ranks
```

Và sửa phần kết toán win/draw cho seat của agent (`agent_seat`, mục 4b): **win** nếu `ranks[agent_seat] == 0` và là duy nhất ở rank 0; **draw** nếu rank 0 nhưng chia sẻ; **loss** nếu rank > 0.

### 4b. Xoay 4 góc (giảm bias chỉ test seat 0)

```python
for seat in range(4):                      # đặt agent vào lần lượt 4 vị trí
    order = opponents[:]                    # 3 đối thủ
    order.insert(seat, agent_path)          # agent ở 'seat'
    agents, _ = make_agents(order, seed=episode_seed)
    # ... chạy trận, đọc env.players[seat].stats và alive[seat]
    # cộng dồn metric theo seat -> trung bình hóa trên cả 4 seat
```

Thêm cờ CLI `--rotate-seats` (mặc định bật) để giữ tương thích lệnh cũ.

### 4c. *(Tùy chọn)* Radius snapshot — giảm over-estimate

`bomb_radius` hiện over-estimate vì dùng radius hiện tại của owner. Snapshot = nhớ radius **lúc bom xuất hiện lần đầu**:

- Trong [agent.py](../../agent/team_agent/agent.py): giữ `self._bomb_radius_seen: dict[Cell, int]`. Mỗi step, với mỗi bom trong obs: nếu pos chưa thấy → ghi `1 + players[owner].radius_bonus` *tại thời điểm đó*; dọn entry khi bom biến mất.
- Truyền dict này vào `compute_hazard_map`/`bomb_radius` (thêm tham số optional). **Fallback**: pos không có trong dict → giữ công thức over-estimate hiện tại (an toàn).
- ⚠️ **Đây là thay đổi safety** → bắt buộc engine-verify (mục 6) self-death vẫn = 0 trước khi giữ. Đây là việc invasive nhất trong nhóm quick-win; hoãn nếu thiếu thời gian.

### 4d. Version hygiene

Commit `agent/team_agent/`; xác nhận `submit_ver3/` == source (diff); tag baseline (vd `git tag ver3-baseline`). Tránh lệch giữa source và bản đóng gói khi bắt đầu thử nâng cấp.

## 5. Ngân sách 100ms / tài nguyên

Không ảnh hưởng `act()` (chỉ sửa benchmark + tune trọng số). Radius snapshot: thêm 1 dict nhỏ + vài phép gán/step → không đáng kể.

## 6. Kế hoạch test & đo

- Unit: thêm test cho `ranks_with_tiebreak` (survivors cùng stats → đồng hạng; khác stats → đúng thứ tự kills>boxes>items>bombs).
- Re-baseline ver3 trên benchmark mới (tie-break + 4 góc, **process riêng**); kỳ vọng win-rate **tăng rõ** so với số cũ.
- Radius snapshot: `TEAM_SAFETY_SEEDS=60 TEAM_SAFETY_MAX_STEPS=500 pytest .../test_engine_safety.py` phải vẫn **self-death=0, bad-action=0**.
- 4c/4b: đối chiếu lại với [engine/game.py](../../engine/game.py) cơ chế tie-break & elimination.

## 7. Rủi ro & lan can

- Tie-break sai logic đồng hạng → xếp sai; đã xử "stats hệt nhau ⇒ chia sẻ rank".
- Radius snapshot là điểm dễ gây tự sát nếu sai → giữ fallback over-estimate + engine-verify; nếu nghi ngờ, **bỏ 4c**, vẫn còn 4a/4b/4d giá trị cao.

## 8. Công sức & timeline · Tham chiếu

- **Công sức**: 4a+4b ~0.5–1 ngày; 4d ~15 phút; 4c ~0.5–1 ngày (tùy chọn). Nằm ở **Phase 0** của roadmap.
- **Tham chiếu**: [../ke_hoach_hien_trang_va_roadmap_ml.md](../ke_hoach_hien_trang_va_roadmap_ml.md) (Phase 0 + Quick wins); [../../docs/COMPETITION_GUIDE.md](../../docs/COMPETITION_GUIDE.md) (mục 5 tie-break); [../../docs/bomberman_agent_guides_md/04_BENCHMARK_DEBUG_VA_CHON_VERSION.md](../../docs/bomberman_agent_guides_md/04_BENCHMARK_DEBUG_VA_CHON_VERSION.md).
