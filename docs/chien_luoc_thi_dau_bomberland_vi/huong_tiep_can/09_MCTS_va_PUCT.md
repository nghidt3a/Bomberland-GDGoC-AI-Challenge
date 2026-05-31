# MCTS và PUCT

MCTS/PUCT là hướng nâng cao. Trong cuộc thi này, ràng buộc 100ms khiến triển khai đầy đủ khó, nhưng bản giới hạn vẫn có thể hữu ích cho tình huống chiến thuật.

## Mục tiêu thực tế

Không cần MCTS toàn trận. Chỉ dùng để:

- Chọn đường thoát khi nhiều bom.
- Kiểm tra đặt bom có giết/ép enemy không.
- Endgame enemy gần.
- So sánh vài action ứng viên.

## Forward model

MCTS cần mô phỏng state tiếp theo. Có hai lựa chọn:

1. Dùng engine thật với copy state.
2. Viết simulator tối giản cho vài step.

Engine thật chính xác hơn nhưng copy state có thể chậm. Simulator tối giản nhanh hơn nhưng dễ sai.

## Budget

Trong `act()` chỉ có 100ms. Nếu dùng MCTS:

- Chỉ cho MCTS 50-70ms.
- Luôn có fallback action trước khi search.
- Dừng theo deadline, không theo số simulation cố định.
- Giới hạn action candidate.

## Rollout policy

Rollout random thuần thường tệ. Nên dùng rollout rule:

- Né danger.
- Đi tới item/box.
- Đặt bom nếu có escape.

MCTS mạnh hơn khi rollout policy không quá ngu.

## Leaf evaluation

Thay vì rollout sâu đến terminal, đánh giá leaf:

```text
value =
  alive_score
  + safe_space
  + item_score
  + box_score
  + enemy_threat
  - danger
  - dead_end
```

Điều này nhanh hơn và hợp budget.

## PUCT với policy prior

Nếu có model BC/PPO, dùng output probability làm prior:

```text
prior(action) = model_prob(action)
```

PUCT sẽ thử action model nghĩ tốt nhiều hơn, nhưng vẫn khám phá.

## Rủi ro

- Timeout.
- Mô phỏng sai.
- Rollout nhiễu.
- Không cải thiện so với heuristic scoring.
- Khó debug.

## Khuyến nghị

Chỉ thử MCTS sau khi:

- Hybrid rule đã ổn.
- Benchmark time dư nhiều.
- Có tình huống cụ thể cần search.

Nếu không, dùng heuristic search depth nhỏ sẽ đơn giản và đáng tin hơn.

