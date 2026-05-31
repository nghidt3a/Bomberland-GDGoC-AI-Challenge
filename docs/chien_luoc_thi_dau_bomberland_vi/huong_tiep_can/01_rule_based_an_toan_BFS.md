# Rule-based an toàn bằng BFS

Đây là hướng nên làm đầu tiên. Một agent sống ổn và không tự sát thường tốt hơn một agent RL chưa train đủ.

## Mục tiêu

Agent phải:

- Biết ô nào đang nguy hiểm.
- Biết chạy khỏi vùng nổ.
- Không đặt bom nếu không có đường thoát.
- Không đi vào wall, box, bomb.
- Có fallback hợp lệ khi không tìm được kế hoạch.

## Module cần có

1. `valid_actions(obs)`: trả các action di chuyển hợp lệ.
2. `blast_tiles(obs)`: tính vùng nổ của tất cả bom.
3. `danger_map(obs)`: lưu ô nguy hiểm và timer nhỏ nhất.
4. `bfs_to_safe(obs)`: tìm action đầu tiên để tới ô safe.
5. `can_escape_after_bomb(obs)`: kiểm tra đặt bom có đường thoát.

## Logic chính

```text
Nếu mình chết: STOP
Nếu đang ở ô nguy hiểm:
    chạy tới ô safe gần nhất bằng BFS
Nếu có item gần và đường đi an toàn:
    đi tới item
Nếu có box gần, có bom, đặt bom xong thoát được:
    PLACE_BOMB
Nếu có ô đặt bom phá box tốt:
    đi tới đó
Nếu không:
    chọn action safe có nhiều ô thoát
```

## BFS tìm ô safe

State BFS nên gồm:

- Vị trí `(x, y)`.
- Depth hoặc time step giả lập.
- Action đầu tiên.

Đơn giản ban đầu có thể không mô phỏng timer theo thời gian, chỉ tránh `danger_soon`. Bản tốt hơn cần xét timer giảm theo từng bước.

## Đánh giá ô safe

Một ô safe tốt:

- Không nằm trong vùng nổ hiện tại/sắp tới.
- Có nhiều neighbor đi được.
- Không phải dead-end.
- Gần item hoặc box target.
- Xa enemy đang có bom.

## Đặt bom an toàn

Chỉ đặt bom nếu:

- `bombs_left > 0`.
- Ô hiện tại chưa có bomb.
- Có box/enemy trong blast.
- BFS sau khi thêm bomb giả lập tìm được escape.

Nếu không thỏa, không đặt bom.

## Điểm mạnh

- Dễ debug.
- Chạy nhanh.
- Không cần train.
- Có thể nộp sớm.
- Làm fallback tốt cho RL.

## Điểm yếu

- Dễ bị bắt bài.
- Tấn công chưa sâu.
- Phải xử lý nhiều edge case.
- Không tự học chiến thuật mới.

## Tiêu chí hoàn thành

- Không chết bởi bom của mình trong phần lớn trận.
- Thắng hoặc hòa ổn trước random/simple.
- Sống tốt trước tactical/smarter.
- `act()` chạy rất nhanh, thường dưới vài ms.

