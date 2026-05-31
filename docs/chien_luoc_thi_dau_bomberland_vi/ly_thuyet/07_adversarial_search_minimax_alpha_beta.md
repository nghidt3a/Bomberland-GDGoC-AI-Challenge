# Adversarial Search: Minimax và Alpha-Beta

Adversarial search chọn action bằng cách dự đoán đối thủ cũng cố gắng làm mình thua. Bomberland có 4 agent nên minimax chuẩn 2 người chơi không áp dụng trực tiếp, nhưng ý tưởng search ngắn vẫn hữu ích.

## Minimax

Minimax cho game 2 người:

```text
Max chọn action làm điểm cao nhất
Min chọn action làm điểm của Max thấp nhất
```

Với state `s`:

```text
V(s) = max_a min_b V(Result(s, a, b))
```

Trong Bomberland, có thể đơn giản hóa:

- Mình là Max.
- Enemy gần nhất là Min.
- Hai agent còn lại coi như môi trường hoặc dùng rule cố định.

## Max-N

Với nhiều người chơi, Max-N mở rộng minimax bằng vector utility cho từng agent. Mỗi agent chọn action tăng utility của chính nó.

Nhược điểm:

- Branching cực lớn.
- Cần mô hình utility cho từng agent.
- Khó chạy dưới 100ms nếu search sâu.

## Alpha-Beta

Alpha-beta cắt nhánh không cần xét trong minimax 2 người:

- `alpha`: giá trị tốt nhất Max đã đảm bảo.
- `beta`: giá trị tốt nhất Min đã đảm bảo.

Nếu nhánh không thể cải thiện kết quả, bỏ qua.

Alpha-beta hiệu quả nhất khi action được sắp xếp tốt: action hứa hẹn xét trước.

## Dùng trong Bomberland

Không nên search toàn bộ 4 agent x 6 action sâu nhiều step. Thay vào đó:

1. Lọc action của mình còn 2-4 action safe.
2. Chỉ xét enemy gần nhất hoặc enemy có thể giết mình.
3. Enemy action cũng lọc còn 2-3 action hợp lý.
4. Depth 2-4.
5. Dùng heuristic evaluation ở leaf.

## Heuristic evaluation

Một state tốt nếu:

- Mình alive.
- Mình không trong danger sắp nổ.
- Có nhiều ô safe reachable.
- Có item gần.
- Có thể phá box.
- Enemy bị kẹt hoặc nằm trong threat.
- Mình có nhiều bomb/radius hơn.

Một state xấu nếu:

- Mình chết.
- Mình trong dead-end với bomb timer thấp.
- Không có escape sau khi đặt bom.
- Enemy có đường đặt bom ép mình.

## Iterative deepening

Do timeout 100ms, nên search theo depth tăng dần:

```text
depth = 1 -> lưu best
depth = 2 -> nếu còn thời gian, cập nhật best
depth = 3 -> nếu còn thời gian, cập nhật best
```

Khi gần hết budget, trả best action ở depth cuối hoàn tất.

## Khuyến nghị

Adversarial search nên là module phụ trong hybrid:

- Dùng cho endgame hoặc khi enemy gần.
- Dùng để kiểm tra đặt bom/tấn công.
- Không dùng thay thế toàn bộ rule safety.

Nếu đội còn ít thời gian, làm heuristic action scoring sẽ hiệu quả hơn minimax phức tạp.

