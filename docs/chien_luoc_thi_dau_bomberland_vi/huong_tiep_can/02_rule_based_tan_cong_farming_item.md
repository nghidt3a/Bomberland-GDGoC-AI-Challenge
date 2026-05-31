# Rule-based tấn công, farming và item

Sau khi có safety BFS, cần làm agent biết tạo lợi thế: phá hộp, lấy item và tấn công enemy đúng lúc.

## Mục tiêu chiến thuật

Trong Bomberland, power-up rất quan trọng:

- Capacity cao giúp đặt nhiều bom.
- Radius cao giúp kiểm soát nhiều ô.
- Phá box mở đường và tạo item.

Vì vậy agent nên farm đầu game, chuyển sang pressure khi có đủ sức mạnh hoặc khi enemy ở vị trí dễ kẹt.

## Farming box

Một ô đặt bom tốt nếu:

- Blast hit ít nhất 1 box.
- Hit càng nhiều box càng tốt.
- Sau khi đặt bom có đường thoát.
- Đường thoát không tranh chấp với enemy gần.

Score gợi ý:

```text
box_bomb_score = 2.0 * boxes_hit
               + 0.5 * escape_space
               - 1.0 * danger_penalty
```

## Nhặt item

Ưu tiên item theo tình trạng:

- Nếu `bombs_left` hoặc max capacity thấp, ưu tiên capacity.
- Nếu radius thấp, ưu tiên radius.
- Nếu item nằm trong danger sắp nổ, bỏ qua.

Không nên tranh item nếu nhiều agent có thể vào cùng step, vì item sẽ bị hủy.

## Tấn công enemy

Chỉ đặt bom tấn công nếu:

- Enemy cùng hàng/cột trong radius.
- Wall/box không chặn line.
- Mình có escape.
- Enemy có ít đường thoát hoặc đang gần dead-end.

Một cơ hội tấn công mạnh:

- Enemy đứng trong corridor hẹp.
- Enemy đang bị bomb khác giới hạn đường.
- Enemy gần box/wall làm chặn lối.
- Mình có nhiều bomb/radius hơn.

## Pressure thay vì all-in

Không cần luôn cố giết ngay. Pressure tốt là:

- Đặt bom mở đường và ép enemy rời vị trí.
- Chiếm item.
- Khóa corridor.
- Buộc enemy vào vùng blast của bom khác.

Agent top cần sống lâu; all-in tự sát thường làm rank xấu.

## Ưu tiên theo giai đoạn

### Early game

- Né bom.
- Phá box an toàn.
- Lấy item gần.
- Tránh giao tranh nếu yếu.

### Mid game

- Tăng pressure.
- Đuổi enemy yếu.
- Kiểm soát item.
- Dùng nhiều bom để khóa đường.

### Late game

- Ưu tiên sống và rank.
- Tấn công nếu enemy bị kẹt.
- Tránh đặt bom nếu khiến mình mất escape.

## Lỗi thường gặp

- Tham phá box rồi chết.
- Nhặt item trong vùng nổ.
- Đặt bom khi enemy dễ thoát còn mình bị kẹt.
- Đuổi enemy quá gần trong corridor có bom.
- Không cân bằng farm và attack.

## Tiêu chí hoàn thành

- Agent lấy item nhiều hơn baseline yếu.
- Agent phá box đều nhưng ít tự chết.
- Agent có kill khi enemy cùng line và bị giới hạn đường.
- Win/rank cải thiện so với safety-only.

