# Hybrid rule-based và heuristic search

Hybrid là hướng thực dụng nhất: dùng rule cứng để đảm bảo an toàn, dùng heuristic score hoặc search ngắn để chọn action tốt hơn.

## Kiến trúc

```text
obs
-> feature extraction
-> hard safety filter
-> action scoring
-> optional short simulation/search
-> fallback
-> action
```

Hard filter loại các action chắc chắn xấu. Heuristic score chọn trong phần còn lại.

## Hard safety filter

Loại action nếu:

- Invalid movement.
- Đi vào bomb/wall/box.
- Đi vào ô nổ timer 1 nếu có lựa chọn khác.
- Đặt bom mà không có escape.
- Đặt bom không hit box/enemy và làm giảm escape.

## Action scoring

Ví dụ:

```text
score(action) =
  + 1000 nếu action sống
  + 20 nếu rời danger
  + 10 nếu lấy item
  + 3 * boxes_hit nếu đặt bom phá box
  + 5 * enemy_threat nếu đặt bom đe dọa enemy
  + 0.5 * open_neighbors
  - 10 nếu vào dead-end
  - 5 nếu gần enemy có bom
  - 0.1 * distance_to_target
```

Các trọng số cần tune bằng replay và test nhiều seed.

## Short simulation

Mô phỏng 2-5 step cho từng action candidate:

- Giả định enemy dùng rule đơn giản.
- Giảm bomb timer.
- Tính xem mình có chết không.
- Tính box/item/enemy opportunity.

Không cần mô phỏng hoàn hảo. Chỉ cần phát hiện bẫy gần.

## Khi dùng search

Chỉ bật search khi:

- Có bom gần.
- Enemy gần.
- Đang cân nhắc đặt bom.
- Có nhiều action cùng điểm.

Các tình huống bình thường dùng scoring nhanh.

## Tối ưu tốc độ

- Precompute blast tiles một lần mỗi `act()`.
- Không copy map quá nhiều.
- Giới hạn candidate action.
- Giới hạn depth.
- Có deadline nội bộ, ví dụ 60ms.
- Nếu hết thời gian, trả best action hiện tại.

## Kết hợp model RL

Model có thể đóng vai trò:

- Thêm điểm prior cho action.
- Chọn target chiến thuật.
- Dự đoán value state.

Nhưng rule safety vẫn giữ quyền phủ quyết.

## Vì sao hướng này mạnh

- Không cần train lớn.
- Debug được.
- Chạy nhanh.
- Dễ giải thích.
- Có thể dùng RL/BC để cải thiện từng phần.

## Tiêu chí hoàn thành

Hybrid tốt hơn rule đơn giản nếu:

- Average rank tốt hơn trên cùng seed.
- Ít self-kill hơn.
- Lấy item/phá box nhiều hơn.
- Kill enemy nhiều hơn mà không giảm survival.

