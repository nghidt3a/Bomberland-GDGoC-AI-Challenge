# Mục tiêu đạt top cao

Mục tiêu không chỉ là thắng vài trận local. Mục tiêu thực tế là có điểm TrueSkill cao, sigma thấp, ổn định qua nhiều đối thủ và không bị lỗi khi chấm.

## Hiểu TrueSkill

Leaderboard dùng:

```text
score = mu - 3 * sigma
```

Trong đó:

- `mu`: ước lượng sức mạnh trung bình.
- `sigma`: độ bất định.
- `score`: điểm xếp hạng bảo thủ.

Một agent có `mu` cao nhưng `sigma` lớn vẫn có thể xếp thấp. Vì vậy cần vừa thắng, vừa chơi đủ nhiều trận để giảm bất định.

## Chiến lược nộp bài

1. Nộp sớm khi agent đã pass interface và timeout.
2. Không chờ agent "hoàn hảo" mới nộp, vì submission cần số trận để giảm `sigma`.
3. Mỗi bản nộp phải là bản có khả năng sống ổn, không phải thử nghiệm ngẫu nhiên.
4. Sau khi có bản tốt, tiếp tục cải thiện local rồi nộp bản tốt hơn.
5. Tránh dùng hết lượt nộp trong ngày cho checkpoint chưa benchmark.

Submission hợp lệ sẽ chạy ngay 12 trận ban đầu. Background evaluator tiếp tục đưa agent vào pool nếu đủ điều kiện active; CLI background trong repo hiện mặc định chạy 5 trận mỗi batch, rồi lặp tiếp theo cấu hình vận hành.

## Điều kiện agent cạnh tranh

Một agent top cao cần thỏa các tiêu chí sau:

| Tiêu chí | Mục tiêu |
|---|---|
| Sống sót | Ít chết do bom của chính mình |
| Né bom | Tính vùng nổ theo timer và radius thật |
| Farm | Phá hộp, lấy item, tăng radius/capacity |
| Tấn công | Chỉ đặt bom khi có lợi và có đường thoát |
| Ổn định | Ít lỗi, ít timeout, ít action invalid |
| Tổng quát | Chơi được nhiều seed và nhiều đối thủ |
| Tốc độ | Trung bình thấp hơn 100ms nhiều lần, nên nhắm < 20ms |

## Hướng đi khuyến nghị

Thứ tự thực dụng:

1. Rule-based an toàn bằng BFS.
2. Rule-based farming và item collection.
3. Hybrid heuristic có scoring từng action.
4. Behavior cloning từ rule agent tốt để tạo policy nhanh.
5. DQN/PPO train trên cloud, dùng rule-based làm fallback.
6. Self-play để giảm khả năng bị bắt bài.

Không nên bắt đầu bằng PPO hoặc MCTS phức tạp khi đội chưa có baseline rule-based. Nếu RL chưa đủ mạnh, vẫn cần fallback rule-based để tránh chết ngu và timeout.

## Đối thủ cần test

Test tối thiểu với:

- `RandomAgent`.
- `SimpleRuleAgent`.
- `BoxFarmerAgent`.
- `SmarterRuleAgent`.
- `TacticalRuleAgent`.
- `GeniusRuleAgent`.
- Bản cũ của chính mình.

Không chỉ test 1v1. Vì trận thật có 4 agent, cần test tổ hợp 4 người và random vị trí.

## Metric cần theo dõi

Các metric nên ghi cho mỗi experiment:

- Win rate.
- Draw rate.
- Average rank.
- Survival steps.
- Kills.
- Boxes destroyed.
- Items collected.
- Bombs placed.
- Timeout count.
- Average và max inference time.
- Estimated TrueSkill local.

Một checkpoint chỉ nên được xem là tốt hơn nếu thắng trên nhiều seed, không chỉ một vài trận đẹp.

## Những lỗi làm tụt hạng nhanh

- Đặt bom nhưng không có đường thoát.
- Đuổi enemy vào vùng nổ đang đến gần.
- Đứng yên quá nhiều vì pathfinding không tìm được target.
- Farm hộp nhưng bỏ qua item.
- Tấn công bằng bom khi enemy có quá nhiều đường thoát.
- Dùng model quá lớn khiến startup hoặc `act()` chậm.
- Import thư viện nặng trong `act()`.
- Đường dẫn checkpoint sai khi zip.
