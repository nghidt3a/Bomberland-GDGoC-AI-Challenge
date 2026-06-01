# 03 — Scoring farm, item, attack theo tie-break mới

Safety core trả lời “action nào sống được?”. Scoring trả lời “trong các action sống được, action nào tốt nhất?”.

Tie-break mới là:

```text
Kills > Boxes Destroyed > Items Collected > Bombs Placed
```

Nhưng không được vì tie-break mà phá safety.

## 1. Công thức scoring tổng quát

Gợi ý:

```text
score(action)
= W_survival * survival_score
+ W_kill * kill_score
+ W_pressure * pressure_score
+ W_box * box_score
+ W_item * item_score
+ W_mobility * mobility_score
+ W_useful_bomb * useful_bomb_score
- W_danger * danger_penalty
- W_self_trap * self_trap_penalty
- W_loop * loop_penalty
- W_useless_bomb * useless_bomb_penalty
```

Quan hệ trọng số:

```text
safety penalty cực lớn
> kill cơ hội chắc
> box farming
> item collection
> mobility
> activity nhỏ
```

Ví dụ khởi điểm:

```python
W_SURVIVAL = 1000
W_SELF_TRAP = 1000
W_DANGER = 800
W_KILL = 120
W_PRESSURE = 20
W_BOX = 50
W_ITEM = 40
W_MOBILITY = 10
W_USEFUL_BOMB = 5
W_LOOP = 15
W_USELESS_BOMB = 40
```

Không cần giữ đúng số này. Phải tune bằng benchmark.

## 2. Survival score

Ngay cả trong safe actions, vẫn có action an toàn hơn action khác. Nên thưởng action:

- tới ô có nhiều safe cells reachable;
- giữ nhiều đường thoát;
- không đi sâu vào corridor hẹp khi có bom gần;
- tăng khoảng cách khỏi vùng danger tương lai.

Gợi ý:

```python
survival_score = number_of_reachable_safe_cells_after_action
```

## 3. Box farming

Boxes Destroyed là tie-break thứ 2 và là nguồn item. Early game nên ưu tiên phá box.

### 3.1. Đặt bom phá box

Với action `PLACE_BOMB`:

```text
box_gain = số box bom sẽ phá
escape_ok = can_place_bomb_safely(state)
```

Chỉ thưởng khi:

```text
escape_ok == True
box_gain >= 1
```

Pseudo-code:

```python
if action == PLACE_BOMB and can_place_bomb_safely(state):
    box_score = box_gain(self_pos)
else:
    box_score = 0
```

### 3.2. Di chuyển tới vị trí phá box

Nếu chưa đứng ở vị trí tốt, tìm các cell grass mà đặt bom tại đó phá được box:

```python
candidate_cells = []
for cell in grass_cells:
    gain = box_gain(cell)
    if gain > 0 and has_escape_if_bomb_at(cell):
        candidate_cells.append((cell, gain))
```

Điểm di chuyển:

```text
box_move_score = gain / (safe_distance + 1)
```

## 4. Item collection

Items Collected là tie-break thứ 3 và còn tăng sức mạnh.

- Radius giúp phá nhiều box/kill dễ hơn.
- Capacity giúp đặt nhiều bom hơn, kiểm soát map tốt hơn.

Chỉ chase item nếu đường đi an toàn:

```text
item_score = item_value / (safe_distance + 1)
```

Gợi ý:

```python
radius_value = 1.0
capacity_value = 1.1
```

Sau khi phá box, agent nên quay lại nhặt item nếu an toàn. Nếu không, đối thủ có thể nhặt mất.

## 5. Bombs Placed

Bombs Placed là tie-break cuối, không nên tối ưu trực tiếp bằng spam bom.

Không làm:

```text
+1 cho mọi lần PLACE_BOMB
```

Chỉ thưởng `useful_bomb_score` nếu bom:

- phá ít nhất 1 box;
- hoặc tạo pressure lên opponent;
- hoặc mở đường tới item/vùng mới;
- và có escape path.

Phạt `useless_bomb_penalty` nếu bom không phá gì, không pressure ai, hoặc làm giảm mobility.

## 6. Attack: pressure và kill

Nên chia attack thành 2 mức.

### 6.1. Pressure score

Pressure là gây áp lực, chưa chắc kill ngay. Ví dụ:

- đặt bom làm đối thủ phải rời vị trí tốt;
- đặt bom ở corridor;
- đặt bom gần đường đi của đối thủ;
- ép đối thủ rời cụm item/box.

Điều kiện:

```text
mình có escape path chắc chắn
bom không tự trap
đối thủ nằm gần blast zone tương lai
```

Pressure score nên nhỏ để tránh đánh liều.

### 6.2. Kill score

Kill score chỉ bật khi cơ hội rõ:

```text
opponent_distance <= self_radius + 2
opponent_escape_cells thấp
mình có escape path riêng
opponent ở corridor/góc/kẹt bởi wall/box/bomb
```

Pseudo-code:

```python
if action == PLACE_BOMB and can_place_bomb_safely(state):
    enemy_risk = estimate_enemy_trap_score(state)
    kill_score = enemy_risk
```

Không để `kill_score` override safety.

## 7. Anti-loop và anti-camping

Agent rule dễ bị đi qua đi lại hoặc đứng yên. Lưu lịch sử:

```python
recent_positions = deque(maxlen=12)
recent_actions = deque(maxlen=12)
last_progress_step = step có phá box/nhặt item/đặt bom hữu ích gần nhất
```

Phạt:

- quay lại ô vừa đứng;
- lặp A-B-A-B;
- STOP nhiều step;
- không có progress trong N step.

Nếu quá lâu không progress:

```text
tăng tạm W_BOX/W_ITEM
giảm điểm STOP
đẩy agent tới cụm box/item an toàn gần nhất
```

## 8. Chiến thuật theo giai đoạn

### Early game: step 0–150

Mục tiêu: phá box, nhặt item, mở không gian, tránh combat rủi ro.

Ưu tiên:

```text
box_score cao
item_score cao
attack chỉ khi gần như miễn phí
```

### Mid game: step 150–350

Mục tiêu: farm tiếp, kiểm soát vị trí, bắt đầu pressure đối thủ.

Ưu tiên:

```text
farm box còn lại
nhặt item
pressure corridor
không chase quá sâu
```

### Late game: step 350–500

Nếu đang dẫn tie-break: chơi an toàn, chỉ attack khi chắc.

Nếu đang thua tie-break: tăng farm/pressure/attack có kiểm soát.

Có thể ước lượng mình đang thua bằng proxy:

```text
kills/boxes/items của mình thấp
agent ít đặt bom hữu ích quá lâu
```

## 9. Track tie-break nội bộ

Agent có thể tự track tương đối:

```python
estimated_boxes_destroyed
estimated_items_collected
estimated_bombs_placed
estimated_kills
```

Cách ước lượng:

| Chỉ số | Cách track |
|---|---|
| Boxes destroyed | box biến mất sau explosion liên quan tới bom của mình |
| Items collected | mình bước vào ô item và item biến mất |
| Bombs placed | action PLACE_BOMB hợp lệ |
| Kills | opponent alive 1→0 sau explosion do bom owner là mình |

Không cần hoàn hảo, chỉ cần đủ để agent bớt thụ động.
