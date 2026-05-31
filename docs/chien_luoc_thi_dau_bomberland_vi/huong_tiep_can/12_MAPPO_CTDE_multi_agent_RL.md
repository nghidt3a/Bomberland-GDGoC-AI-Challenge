# MAPPO và CTDE cho multi-agent RL

MAPPO là biến thể PPO dùng centralized training, decentralized execution. Đây là hướng RL nâng cao cho trận 4 agent, phù hợp nếu đội có wrapper mô phỏng ổn và đủ thời gian train.

## Ý tưởng CTDE

Trong lúc train:

- Actor chọn action từ observation của agent đang điều khiển.
- Critic được xem thêm thông tin toàn cục để ước lượng value tốt hơn.

Khi nộp bài:

- Chỉ dùng actor.
- Actor không phụ thuộc critic.
- Actor vẫn chỉ cần `obs` hợp lệ trong `act()`.

Điều này hợp với cuộc thi vì submission chỉ cần một agent độc lập, nhưng trong train ta có thể tận dụng full state.

## Mục tiêu

Train một shared policy dùng cho mọi `agent_id`:

```text
actor(local_obs, agent_id) -> action_logits
critic(global_state, agent_id) -> value
```

Shared policy giúp model học chung cho bốn góc spawn, giảm bias theo vị trí.

## Observation

Actor nên nhận:

- Spatial channels theo góc nhìn chuẩn hóa quanh agent.
- Vị trí mình và enemy.
- Danger map.
- Bomb timer.
- Item/box/wall.
- Scalar như bombs_left, radius, step, số enemy sống.

Critic có thể nhận:

- Full map không crop.
- State của cả 4 agent.
- Bomb owner và timer.
- Rank/death status.

Không đưa critic vào submission.

## Reward

MAPPO nên dùng reward vừa đủ:

- Rank reward cuối trận.
- Penalty chết sớm.
- Reward enemy death.
- Reward phụ nhỏ cho item, box, escape.

Nếu mỗi agent có reward riêng, cần log rõ reward của agent mình và reward của đối thủ để tránh train sai objective.

## Opponent setup

Có hai kiểu:

1. Train self-play toàn bộ agent cùng shared policy.
2. Train main policy trước pool rule/snapshot.

Thực dụng hơn là trộn:

```text
main policy + baseline mạnh + snapshot cũ + random/rule yếu
```

Vị trí spawn phải randomize.

## Ưu điểm

- Giảm non-stationarity so với PPO độc lập.
- Critic học value tốt hơn nhờ full state.
- Hợp với self-play và league training.
- Có thể train một policy dùng cho mọi agent_id.

## Rủi ro

- Wrapper phức tạp hơn PPO thường.
- Dễ train sai nếu actor nhìn thấy thông tin không có ở inference.
- Cần nhiều rollout.
- Debug khó vì lỗi có thể nằm ở reward, critic hoặc opponent sampling.

## Khuyến nghị

Chỉ làm MAPPO khi đã có:

- Rule/hybrid baseline ổn.
- PPO thường hoặc DQN đã chạy được.
- Evaluation tự động qua nhiều seed.
- Tài nguyên train đủ.

Nếu MAPPO chưa vượt hybrid rule, có thể dùng actor như một policy phụ trong ensemble, vẫn qua safety layer.

