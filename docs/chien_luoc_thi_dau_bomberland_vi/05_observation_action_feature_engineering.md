# Observation, action và feature engineering

Feature tốt thường quyết định agent mạnh hơn việc chọn thuật toán phức tạp. Với Bomberland, điều quan trọng nhất là biến full state thành các feature chiến thuật: an toàn, đường thoát, mục tiêu farm, mục tiêu tấn công.

## Feature tối thiểu

Từ `obs`, tạo các feature:

- Vị trí bản thân.
- Vị trí enemy còn sống.
- Ô đi được.
- Ô bị chặn bởi wall, box, bomb.
- Danger map theo bom hiện tại.
- Timer nguy hiểm nhỏ nhất tại mỗi ô.
- Ô safe có thể đến được trước khi bom nổ.
- Ô item.
- Ô đặt bom có thể phá box.
- Ô đặt bom có thể đe dọa enemy.

## Valid actions

Valid movement:

- Không ra ngoài map.
- Không vào wall `1`.
- Không vào box `2`.
- Không vào ô có bomb.

Agent có thể đứng cùng ô với agent khác theo engine, nhưng về chiến thuật vẫn nên coi enemy là vật cản mềm nếu đang cần né bom hoặc tranh item.

Action `5` chỉ hợp lệ nếu:

- `bombs_left > 0`.
- Ô hiện tại chưa có bomb cũ.

## Danger map

Danger map là tập ô sẽ bị ảnh hưởng bởi bom. Với mỗi bomb:

1. Lấy `(x, y, timer, owner_id)`.
2. Tính radius tại lúc đặt bom. Trong docs/code hiện tại, radius tương ứng `1 + bomb_radius_bonus` của owner.
3. Quét bốn hướng đến radius.
4. Dừng khi gặp wall.
5. Thêm box vào vùng nổ rồi dừng sau box.

Nên lưu:

- `danger_any`: ô sẽ bị nổ bởi ít nhất một bomb.
- `danger_soon`: ô có bomb timer thấp, ví dụ `timer <= 2`.
- `min_timer[x][y]`: timer nhỏ nhất của bomb đe dọa ô đó.

## Escape feature

Khi cân nhắc đặt bom, cần kiểm tra:

```text
Nếu đặt bom ở ô hiện tại, có đường đi đến ít nhất một ô ngoài vùng nổ trước khi timer hết không?
```

Thực dụng nhất:

- Giả lập thêm bomb của mình ở ô hiện tại.
- Tạo blast tiles của bomb đó.
- BFS từ vị trí hiện tại.
- Tìm ô safe không nằm trong blast và không nằm trong danger soon.
- Giới hạn depth khoảng 7-10 step.

Nếu không có đường thoát, không đặt bom.

## Feature cho rule/hybrid

Một action score có thể gồm:

```text
score =
  + safe_bonus
  + escape_space_bonus
  + item_bonus
  + box_farm_bonus
  + enemy_pressure_bonus
  - danger_penalty
  - dead_end_penalty
  - idle_penalty
```

Nên tách hard rule và soft score:

- Hard rule: không đi vào ô nổ ngay, không đặt bom tự sát.
- Soft score: chọn giữa các action còn lại.

## Feature cho neural network

Dạng CNN nhỏ:

- 5 channel one-hot map: grass, wall, box, item radius, item capacity.
- 1 channel vị trí mình.
- 1 channel enemy sống.
- 1 channel bomb timer chuẩn hóa.
- 1 channel bomb owner hoặc own bomb.
- 1 channel danger map.
- 1 channel safe reachable.

Scalar feature:

- `bombs_left / 5`.
- `bomb_radius / 5`.
- Số enemy sống.
- Khoảng cách đến item gần nhất.
- Khoảng cách đến enemy gần nhất.
- Có đang trong danger không.

## Action masking

Với DQN/PPO, nên mask action nguy hiểm trước khi chọn:

- Nếu model chọn action invalid, thay bằng action safe tốt nhất.
- Nếu model chọn đặt bom tự sát, thay bằng action né bom hoặc farm.
- Nếu không có action safe, chọn action có timer chết muộn nhất.

Action masking giúp RL không cần tự học lại những luật sống còn và giảm reward hacking.

## Những feature có giá trị cao

| Feature | Vì sao quan trọng |
|---|---|
| `min_bomb_timer_at_tile` | Biết còn bao lâu để thoát |
| `reachable_safe_tiles` | Tránh tự nhốt |
| `box_count_in_blast` | Đặt bom farm hiệu quả |
| `enemy_in_line_of_blast` | Cơ hội tấn công |
| `escape_after_bomb` | Điều kiện đặt bom |
| `nearest_item_distance` | Tăng power lâu dài |
| `open_neighbors` | Tránh dead-end |

