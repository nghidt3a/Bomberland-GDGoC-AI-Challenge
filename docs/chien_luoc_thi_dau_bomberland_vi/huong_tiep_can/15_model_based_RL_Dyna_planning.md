# Model-based RL và Dyna-style planning

Model-based RL dùng mô hình dự đoán state tiếp theo để học hoặc lập kế hoạch. Với Bomberland, luật map và bom khá có cấu trúc, nên hướng này có thể hữu ích nếu triển khai giới hạn và kiểm soát sai số.

## Hai kiểu model

1. Forward model theo luật:
   - Mô phỏng di chuyển, bom, nổ, box, item.
   - Chính xác hơn nếu hiểu engine.

2. Learned model:
   - Neural network dự đoán `next_obs`, reward hoặc event.
   - Học được pattern đối thủ nhưng dễ sai ở edge case.

Thực dụng nhất là forward model luật đơn giản cộng opponent model nhẹ.

## Dyna cho DQN

Dyna-style training xen kẽ dữ liệu thật và dữ liệu mô phỏng:

```text
rollout thật -> lưu replay
sample state từ replay -> model rollout ngắn -> thêm transition tưởng tượng
update Q-network
```

Rollout tưởng tượng chỉ nên sâu `1..5` step để giảm lỗi tích lũy.

## Dùng model để đánh giá action

Trong `act()`, có thể dùng simulator nhanh cho vài action ứng viên:

```text
for action in safe_actions:
    simulate 3..6 step với opponent rule
    score leaf state
return action score cao nhất
```

Cách này gần heuristic search/MCTS nhưng dùng trong phạm vi rất nhỏ để không timeout.

## Learned opponent model

Đối thủ là phần khó mô phỏng. Có thể train model dự đoán action đối thủ:

```text
enemy_obs_features -> enemy_action_distribution
```

Khi planning, dùng distribution này thay vì giả định enemy đứng yên hoặc random.

Không cần model quá lớn. MLP nhỏ từ feature chiến thuật là đủ.

## Reward/event model

Nếu không muốn dự đoán full next state, có thể học event:

- Xác suất mình chết trong vài step.
- Xác suất enemy chết.
- Xác suất nhặt item.
- Số safe tiles sau action.

Event model thường dễ ổn hơn full world model.

## Rủi ro

- Simulator sai một luật nhỏ có thể làm policy học sai.
- Learned model sai ở state hiếm như chain explosion.
- Planning online dễ vượt 100ms.
- Model-based phức tạp hơn lợi ích nếu rule search đã đủ tốt.

## Khuyến nghị

Nên dùng model-based theo hướng phụ trợ:

- Sinh thêm rollout ngắn cho DQN.
- Đánh giá một số action candidate.
- Học opponent model nhẹ.

Không nên thay toàn bộ pipeline bằng world model sâu nếu thời gian thi hạn chế.

