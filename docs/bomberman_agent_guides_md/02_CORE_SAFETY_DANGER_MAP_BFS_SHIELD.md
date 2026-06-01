# 02 — Safety Core: danger map, BFS, masks và shield

Đây là file quan trọng nhất. Nếu safety core sai, mọi phần ML/RL phía sau đều không cứu được agent.

## 1. Safety core là gì?

Safety core giúp agent trả lời:

1. Ô nào đang hoặc sắp nổ?
2. Action nào hợp lệ?
3. Action nào còn đường thoát?
4. Đặt bom xong có tự nhốt mình không?
5. Nếu policy chọn action nguy hiểm, fallback là gì?

Các module bắt buộc:

```text
danger map
time-expanded BFS
legal action mask
safe action mask
bomb placement checker
final safety shield
least bad fallback
```

## 2. Danger map

`danger_time[r, c]` là step sớm nhất ô `(r,c)` sẽ có lửa. Nếu không nguy hiểm trong horizon thì bằng `INF`.

Ví dụ:

```text
danger_time[5, 7] = 3
```

nghĩa là ô `(5,7)` sẽ nguy hiểm sau 3 step.

## 3. Blast cells

Bom nổ theo 4 hướng. Quy tắc:

- wall chặn hoàn toàn;
- box bị phá và chặn blast tại box;
- agent không chặn blast;
- item/grass không chặn blast.

Pseudo-code:

```python
def blast_cells(pos, radius, walls, boxes):
    cells = {pos}
    for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
        r, c = pos
        for _ in range(radius):
            r += dr
            c += dc
            if walls[r, c]:
                break
            cells.add((r, c))
            if boxes[r, c]:
                break
    return cells
```

## 4. Radius của bom

Observation `bombs` có dạng:

```text
[row, col, timer, owner_id]
```

Do đó radius phải lấy từ `players`:

```python
owner_id = int(bomb[3])
radius = 1 + int(players[owner_id][4])
```

Đây là lỗi rất dễ mắc. Nếu lấy radius sai, agent sẽ đánh giá thấp vùng nổ của đối thủ đã ăn item Radius.

## 5. Chain reaction

Nếu blast của bom A chạm bom B, B nổ ngay cùng step với A. Cách tính đơn giản:

```python
def compute_explosion_times(bombs, players, walls, boxes):
    t = [bomb.timer for bomb in bombs]
    changed = True
    while changed:
        changed = False
        for i, bomb_i in enumerate(bombs):
            cells_i = blast_cells(bomb_i.pos, get_radius(bomb_i, players), walls, boxes)
            for j, bomb_j in enumerate(bombs):
                if i == j:
                    continue
                if bomb_j.pos in cells_i and t[i] < t[j]:
                    t[j] = t[i]
                    changed = True
    return t
```

Vì số bomb thường không quá nhiều, lặp fixpoint như vậy đủ nhanh.

## 6. Fire duration

Tài liệu nói vụ nổ kéo dài 1 step. Nên cấu hình:

```python
FIRE_DURATION = 1
```

Nhưng cần xác nhận bằng simulator. Nếu lệch 1 step, agent có thể đi vào ô vừa nổ hoặc né quá lâu.

## 7. Time-expanded BFS

BFS thường chỉ xét `(r,c)`. Trong Bomberman cần xét cả thời gian:

```text
state = (row, col, t)
```

Vì một ô có thể an toàn bây giờ nhưng nổ sau 2 step.

Pseudo-code:

```python
def safe_at(cell, t, danger_time):
    d = danger_time[cell]
    if d == INF:
        return True
    return not (d <= t < d + FIRE_DURATION)

def time_expanded_bfs(start, walls, boxes, danger_time, horizon):
    q = deque([(start, 0)])
    visited = {(start, 0)}
    parent = {}
    safe_targets = []

    while q:
        cell, t = q.popleft()
        if is_eventually_safe(cell, t, danger_time):
            safe_targets.append((cell, t))

        if t >= horizon:
            continue

        for action in [STOP, LEFT, RIGHT, UP, DOWN]:
            nb = move(cell, action)
            if action != STOP and (walls[nb] or boxes[nb]):
                continue
            if not safe_at(nb, t + 1, danger_time):
                continue
            if (nb, t + 1) not in visited:
                visited.add((nb, t + 1))
                parent[(nb, t + 1)] = (cell, t)
                q.append((nb, t + 1))

    return safe_targets, parent
```

## 8. Legal action mask

Legal mask xét luật cơ bản:

- không đi vào wall;
- không đi vào box;
- không đi vào bom đã tồn tại từ step trước;
- không đặt bom khi `bombs_left <= 0`;
- không đặt bom nếu ô hiện tại đã có bom từ step trước.

Cần xử lý ngoại lệ: nếu agent đang đứng trên ô có bom, agent vẫn có thể rời đi. Không được cấm movement chỉ vì ô hiện tại có bom.

## 9. Safe action mask

Safe mask lọc tiếp từ legal mask:

- action đưa tới ô không nổ ngay;
- từ vị trí sau action còn escape path;
- nếu là `PLACE_BOMB`, phải pass `can_place_bomb_safely`.

```python
for action in ACTIONS:
    if not legal_mask[action]:
        safe_mask[action] = False
    elif action == PLACE_BOMB and not can_place_bomb_safely(state):
        safe_mask[action] = False
    elif not has_escape_after_action(state, action):
        safe_mask[action] = False
```

## 10. Bomb placement checker

Khi xét đặt bom, phải mô phỏng thêm bom của mình tại vị trí hiện tại, tính lại danger map, rồi chạy BFS.

```python
def can_place_bomb_safely(state):
    simulated = copy_state_with_new_bomb_at_self(state)
    danger2 = compute_danger_map(simulated)
    safe_targets, _ = time_expanded_bfs(state.self_pos, simulated.walls, simulated.boxes, danger2, HORIZON)
    return len(safe_targets) > 0
```

Cần unit test hành lang/góc/chain reaction vì đây là nơi self-trap xảy ra nhiều.

## 11. Final safety shield

Action cuối luôn phải qua shield:

```python
def final_shield(action, state):
    if action_is_safe(action, state):
        return action
    safe_actions = get_safe_actions(state)
    if safe_actions:
        return best_escape_action(safe_actions, state)
    return least_bad_action(state)
```

`least_bad_action` chọn action chết muộn nhất hoặc còn nhiều mobility nhất nếu không còn đường sống chắc.

## 12. Unit test bắt buộc

- một bom ở giữa map;
- bom bị wall chặn;
- bom gặp box và dừng;
- hai bom chain reaction;
- đặt bom trong góc không thoát;
- đặt bom cạnh box nhưng có đường thoát;
- agent đang đứng trên bom cần rời đi;
- bombs rỗng;
- nhiều bombs cùng lúc;
- agent_id khác nhau, radius khác nhau.

Nếu safety core chưa pass test, chưa nên làm BC/PPO.
