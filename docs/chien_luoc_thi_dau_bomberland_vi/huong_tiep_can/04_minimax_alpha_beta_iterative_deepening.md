# Minimax, Alpha-Beta và Iterative Deepening

Hướng này dùng search đối kháng ngắn để xử lý các tình huống enemy gần. Không nên dùng full minimax cho cả 4 agent vì quá tốn thời gian.

## Mục tiêu

Dự đoán vài step tới:

- Mình có chết nếu đi action này không?
- Enemy có thể né bomb không?
- Đặt bom có ép enemy vào dead-end không?
- Có action nào tránh bẫy tốt hơn BFS tham lam không?

## Giản lược bài toán

Thay vì xét cả 4 agent:

- Mình là Max.
- Enemy nguy hiểm nhất là Min.
- Hai agent còn lại giả định dùng action hiện tại, random, hoặc bỏ qua.

Enemy nguy hiểm nhất có thể là:

- Enemy gần nhất.
- Enemy có thể đặt bom hit mình.
- Enemy có radius/capacity cao nhất.

## Candidate action

Không xét đủ 6 action nếu không cần. Lọc:

- Action safe.
- PLACE_BOMB nếu có escape và hit target.
- Action tiến tới item/box/enemy.

Enemy cũng lọc tương tự.

## Iterative deepening

```text
best = safe_fallback
for depth in [1, 2, 3, 4]:
    nếu còn thời gian:
        best = search(depth)
return best
```

Mỗi `act()` nên có budget nội bộ nhỏ hơn 100ms, ví dụ 60-80ms.

## Evaluation function

Leaf score:

```text
score =
  + 10000 nếu mình sống và enemy chết
  - 10000 nếu mình chết
  + 100 * survival_margin
  + 20 * item_advantage
  + 10 * box_potential
  + 5 * enemy_trapped_score
  - 20 * danger_score
  - 10 * dead_end_score
```

Không cần quá chính xác, nhưng phải phản ánh survival là ưu tiên số một.

## Alpha-Beta

Alpha-beta giúp cắt nhánh trong minimax 2 người. Hiệu quả phụ thuộc action ordering:

1. Action thoát danger.
2. Action giết/ép enemy.
3. Action lấy item.
4. Action farm.
5. Action đứng yên.

Action tốt xét trước giúp cắt nhiều hơn.

## Rủi ro

- Mô phỏng engine sai dẫn tới quyết định sai.
- Search sâu quá timeout.
- Giả định enemy quá đơn giản.
- 4-agent dynamics không giống minimax 2 người.

## Cách dùng an toàn

Dùng như module phụ:

- Nếu enemy trong radius hoặc gần corridor, gọi tactical search.
- Nếu không, dùng hybrid scoring.
- Nếu search timeout, dùng BFS safe fallback.

## Khi nên bỏ hướng này

Bỏ hoặc giảm ưu tiên nếu:

- Search không cải thiện average rank.
- Tốn quá 20-30ms thường xuyên.
- Bug mô phỏng nhiều.
- Đội còn thiếu safety/farming cơ bản.

