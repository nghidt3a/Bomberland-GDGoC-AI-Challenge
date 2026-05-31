# Giới thiệu cuộc thi và luật game

Bomberland là game đối kháng 4 agent trên lưới 13x13. Agent phải di chuyển, đặt bom, phá hộp, nhặt item và loại đối thủ. Mỗi trận tối đa 500 step.

## Bản đồ

| Giá trị map | Ý nghĩa |
|---:|---|
| `0` | Grass, đi được |
| `1` | Wall, không đi qua, chặn nổ |
| `2` | Box, không đi qua, phá được bằng bom |
| `3` | Item tăng bán kính bom |
| `4` | Item tăng số bom mang theo |

Bản đồ có viền tường ngoài, vùng chơi chính 11x11. Spawn ở bốn góc trong:

- Player 0: gần `(1, 1)`.
- Player 1: gần `(11, 11)`.
- Player 2: gần `(1, 11)`.
- Player 3: gần `(11, 1)`.

## Observation

Mỗi step, agent nhận full state:

```python
obs = {
    "map": np.ndarray,      # shape (13, 13)
    "players": np.ndarray,  # shape (4, 5)
    "bombs": np.ndarray,    # shape (N, 4)
}
```

`players[i] = [x, y, alive, bombs_left, bomb_radius_bonus]`.

`bombs[j] = [x, y, timer, owner_id]`.

Tọa độ trong engine là `(x, y)` tương ứng hàng và cột của mảng `map`.

## Action

Mỗi `act()` phải trả về một số nguyên:

| Action | Ý nghĩa |
|---:|---|
| `0` | STOP |
| `1` | LEFT |
| `2` | RIGHT |
| `3` | UP |
| `4` | DOWN |
| `5` | PLACE_BOMB |

Nếu action invalid, timeout hoặc lỗi runtime, evaluator fallback về `0`.

## Thứ tự xử lý mỗi step

Thứ tự quan trọng vì nó quyết định nhiều chiến thuật:

1. Thu action của tất cả agent.
2. Xử lý di chuyển.
3. Nhặt hoặc hủy item ở ô có nhiều agent cùng vào.
4. Đặt bom.
5. Giảm timer bom.
6. Kích nổ bom timer <= 0 và chain reaction.
7. Loại agent nằm trong vùng nổ.
8. Spawn item ngẫu nhiên.
9. Kiểm tra kết thúc trận.

Điểm cần nhớ: agent có thể đứng cùng ô, nhưng không thể đi vào wall, box hoặc ô đang có bom.

## Bom

Thông số chính:

- Timer mặc định: 7 step.
- Bán kính ban đầu: 1.
- Bán kính tối đa: 5.
- Số bom ban đầu: 1.
- Số bom tối đa: 5.

Bom nổ theo hình chữ thập. Wall chặn nổ. Box bị phá và cũng chặn tia nổ sau nó. Vụ nổ đi xuyên qua player. Bom có thể kích hoạt chain reaction nếu nằm trong vùng nổ của bom khác.

Khi đặt bom, agent cần chắc chắn có đường thoát khỏi vùng nổ trước khi timer về 0. Đây là yêu cầu sống còn của mọi hướng tiếp cận.

## Item

Box bị phá có xác suất rơi:

- 30% item tăng radius.
- 30% item tăng capacity.
- 40% không rơi gì.

Ngoài ra, item có xác suất nhỏ tự spawn trên ô grass trống theo thời gian. Nếu nhiều agent cùng bước vào một item trong cùng step, item bị hủy và không ai nhận.

## Kết thúc và rank

Trận kết thúc khi:

- Chỉ còn tối đa 1 agent sống.
- Hoặc tới step 500.

Rank tốt nhất là `0`. Agent sống sót lâu hơn có rank tốt hơn. Nếu nhiều agent chết cùng step, họ cùng rank. Nếu còn nhiều agent sống ở step 500, evaluator dùng thống kê để tie-break giữa các agent còn sống: kills, boxes, items, bombs.

## Điều luật kỹ thuật quan trọng

- `act()` phải hoàn tất trong 100ms.
- Agent startup tối đa 20 giây.
- Chấm CPU-only.
- Không dùng LLM trong `Agent`.
- Không network.
- Không ghi file trong match.
- Được load checkpoint đi kèm ZIP.

