# PPO Actor-Critic

PPO là hướng mạnh nếu có pipeline rollout tốt, nhưng chi phí train cao hơn DQN. Với đội mới, PPO nên là hướng sau khi đã có rule/hybrid baseline.

## Mục tiêu

Train actor-critic:

- Actor output xác suất 6 action.
- Critic output value của state.

Inference:

- Có thể chọn action xác suất cao nhất.
- Hoặc sampling nhẹ nhưng vẫn qua safety mask.

## Cần chuẩn bị

- Gymnasium wrapper cho `BomberEnv`.
- Observation encoder.
- Reward function.
- Opponent sampler.
- Vectorized env nếu dùng stable-baselines3.
- Callback evaluation.
- Save/load policy CPU.

## Observation

PPO có thể dùng:

- Feature vector MLP nếu muốn nhanh.
- CNN nếu dùng spatial channel.

Với map 13x13, CNN nhỏ là hợp lý. Nhưng nếu triển khai vội, vector feature giàu chiến thuật có thể dễ train hơn.

## Action masking

Stable-baselines3 PPO mặc định không có action masking chuẩn trong core PPO. Vì vậy có hai cách:

1. Dùng safety wrapper sau khi policy chọn action.
2. Dùng thư viện hỗ trợ mask nếu có thời gian kiểm soát dependency.

Trong submission, vẫn nên giữ safety layer độc lập với model.

## Reward

PPO nhạy với scale reward. Reward quá lớn hoặc quá nhiễu làm update bất ổn.

Gợi ý:

- Normalize reward hoặc giữ trong khoảng nhỏ.
- Reward cuối trận rõ.
- Reward phụ ít và có mục đích.
- Theo dõi entropy để tránh policy collapse.

## Hyperparameter gợi ý

| Tham số | Gợi ý |
|---|---|
| `gamma` | `0.95..0.99` |
| `gae_lambda` | `0.9..0.95` |
| `clip_range` | `0.1..0.2` |
| `learning_rate` | `1e-4..3e-4` |
| `n_steps` | tùy số env, đủ rollout |
| `batch_size` | `64..512` |
| `ent_coef` | nhỏ, để giữ exploration |

## Ưu điểm

- Policy stochastic.
- Kết hợp self-play tốt.
- Có critic đánh giá state.
- Dễ dùng với stable-baselines3 nếu wrapper chuẩn.

## Nhược điểm

- Cần nhiều rollout.
- Dễ tốn thời gian debug wrapper.
- Cần CPU inference nhẹ.
- Nếu không mask action, agent có thể chọn hành động tự sát.

## Khuyến nghị thi đấu

Không nộp PPO thuần nếu chưa vượt hybrid rule trong test. Nên dùng:

```text
PPO policy -> safety filter -> fallback rule
```

Nếu PPO không vượt rule, vẫn có thể dùng PPO để chọn mục tiêu hoặc làm prior trong action scoring.

