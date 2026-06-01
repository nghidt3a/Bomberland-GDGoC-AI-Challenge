# 01 — Setup repo và quy ước code

File này hướng dẫn cách tổ chức repo để team dễ chia việc, dễ test, dễ benchmark và dễ đóng gói submit.

## 1. Cấu trúc repo đề xuất

```text
agent/
  agent.py              # class Agent, entry point khi submit
  constants.py          # action ids, map ids, timer, horizon
  obs.py                # parse_obs, encode feature nếu dùng ML
  danger.py             # blast cells, chain reaction, danger map
  search.py             # BFS, time-expanded BFS, shortest path
  masks.py              # legal mask, safe mask
  bomb.py               # can_place_bomb_safely, useful bomb checks
  scoring.py            # farm/item/attack/mobility/loop scoring
  shield.py             # final shield, fallback action
  policy_rule.py        # rule-based policy
  policy_bc.py          # inference BC nếu có
  policy_ppo.py         # inference PPO nếu có

train/
  gen_dataset.py        # sinh dataset từ rule expert
  train_bc.py           # Behavior Cloning
  train_ppo.py          # PPO optional
  selfplay.py           # opponent pool optional

bench/
  benchmark.py          # chạy nhiều trận, gom metric
  metrics.py            # tính win/rank/box/item/kill/latency
  analyze_replay.py     # soi replay lỗi
  analyze_step500.py    # phân tích riêng tie-break step 500
  profile_act.py        # đo latency act()

tests/
  test_obs.py
  test_danger.py
  test_chain.py
  test_bfs.py
  test_bomb_checker.py
  test_masks.py

models/
  bc_v1.pt
  ppo_best.pt

submit/
  agent.py
  model.pt nếu có
```

## 2. Quy ước action

Luôn dùng hằng số, không dùng số magic rải rác:

```python
STOP = 0
LEFT = 1
RIGHT = 2
UP = 3
DOWN = 4
PLACE_BOMB = 5

ACTIONS = [STOP, LEFT, RIGHT, UP, DOWN, PLACE_BOMB]

DIRS = {
    STOP: (0, 0),
    LEFT: (0, -1),
    RIGHT: (0, 1),
    UP: (-1, 0),
    DOWN: (1, 0),
}
```

Sai action id hoặc sai trục row/col là lỗi rất khó debug, nên cần test ngay từ đầu.

## 3. Quy ước observation

Observation gồm:

```python
obs = {
    "map": np.ndarray,      # shape (13, 13)
    "players": np.ndarray,  # shape (4, 5)
    "bombs": np.ndarray,    # shape (N, 4)
}
```

`map`:

```text
0 = Grass
1 = Wall
2 = Box
3 = Item Radius
4 = Item Capacity
```

`players[i]`:

```text
[row, col, alive, bombs_left, bomb_radius_bonus]
```

`bombs[k]`:

```text
[row, col, timer, owner_id]
```

Điểm quan trọng:

```python
owner_id = int(bomb[3])
bomb_radius = 1 + int(players[owner_id][4])
```

`bombs` không chứa radius trực tiếp.

## 4. `parse_obs(obs, agent_id)` nên trả gì?

Nên chuẩn hóa thành `state` nội bộ:

```python
state = {
    "grid": grid,
    "walls": walls_bool,
    "boxes": boxes_bool,
    "item_radius": item_radius_bool,
    "item_capacity": item_capacity_bool,
    "players": players,
    "self_pos": (r, c),
    "self_alive": bool,
    "self_bombs_left": int,
    "self_radius": int,
    "opponents": opponents,
    "bombs": bombs_list,
    "bomb_grid": bomb_bool_grid,
}
```

`parse_obs` cần pass các case:

- `bombs` rỗng;
- nhiều bombs;
- agent đã chết;
- opponent đã chết;
- agent_id 0, 1, 2, 3;
- map có item/box/wall đầy đủ.

## 5. API giữa các module

Người viết strategy/ML chỉ nên gọi API ổn định:

```python
state = parse_obs(obs, agent_id)
danger = compute_danger_map(state)
legal_mask = legal_actions(state)
safe_mask = safe_actions(state, danger)
can_bomb = can_place_bomb_safely(state)
action = policy_choose(state, safe_mask)
action = final_shield(action, state)
```

Không nên để policy tự tính lại danger riêng theo logic khác, vì dễ lệch giữa rule và ML.

## 6. Quy ước logging

Trong benchmark, mỗi step nên log:

```python
{
  "step": step,
  "agent_id": agent_id,
  "pos": self_pos,
  "raw_action": action_before_shield,
  "final_action": action_after_shield,
  "override_reason": reason_or_none,
  "legal_mask": legal_mask.tolist(),
  "safe_mask": safe_mask.tolist(),
  "danger_at_self": danger_time[self_pos],
  "bombs_left": self_bombs_left,
  "radius": self_radius,
  "latency_ms": latency,
}
```

Log này giúp trả lời:

- tại sao agent đặt bom;
- shield có override không;
- agent chết do danger map sai hay do scorer quá tham;
- act() có step nào chậm bất thường.

## 7. Quy tắc performance

Trong `act()`:

- không train;
- không load model mỗi step;
- không ghi file nặng;
- không gọi network;
- không print quá nhiều;
- không search sâu nếu chưa profile;
- không dùng model quá lớn.

Mục tiêu:

```text
mean latency < 10ms
p95 < 50ms
p99 < 100ms
```

Map chỉ 13×13 nên code Python rõ ràng thường đủ nhanh. Ưu tiên code đúng, dễ test trước; chỉ tối ưu khi profile cho thấy chậm.

## 8. Quy tắc Git/task

Mỗi tính năng nên có branch/commit riêng:

```text
feat/parse-obs
feat/danger-map
feat/bfs-safety
feat/bomb-checker
feat/farming-scorer
feat/benchmark
feat/bc
feat/ppo
```

Một module được xem là xong khi có:

1. code chạy được;
2. unit test tối thiểu;
3. benchmark nhỏ không crash;
4. không làm hỏng `agent.py`.
