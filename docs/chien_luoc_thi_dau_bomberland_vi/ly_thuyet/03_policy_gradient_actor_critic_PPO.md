# Policy Gradient, Actor-Critic và PPO

Policy gradient học trực tiếp policy thay vì học Q-value. Với Bomberland, PPO có thể hữu ích vì policy stochastic giúp agent ít bị bắt bài hơn, nhưng cần nhiều rollout và pipeline tốt.

## Policy trực tiếp

Policy là phân phối:

```text
pi(a | s)
```

Network nhận state và output xác suất cho 6 action. Khi train, agent lấy mẫu action từ phân phối. Khi submit, có thể chọn action xác suất cao nhất hoặc vẫn giữ sampling có kiểm soát.

## Policy gradient

Ý tưởng:

- Nếu action dẫn đến kết quả tốt, tăng xác suất action đó trong state tương tự.
- Nếu action dẫn đến kết quả xấu, giảm xác suất action đó.

Công thức trực giác:

```text
gradient ~ log_prob(action) * advantage
```

`advantage` đo action vừa làm tốt hơn hay tệ hơn kỳ vọng.

## Actor-Critic

Actor-Critic có hai phần:

- Actor: policy `pi(a|s)`.
- Critic: value `V(s)`.

Advantage:

```text
A(s,a) = return - V(s)
```

Critic giúp giảm nhiễu so với REINFORCE thuần.

## PPO

PPO giới hạn mức policy được thay đổi trong mỗi update bằng clipping:

```text
min(r_t * A_t, clip(r_t, 1-eps, 1+eps) * A_t)
```

Trong đó:

- `r_t` là tỉ lệ xác suất action giữa policy mới và policy cũ.
- `eps` thường là `0.1..0.2`.

Clipping giúp tránh một update làm policy hỏng hoàn toàn.

## Chu trình PPO

1. Collect rollout bằng policy hiện tại.
2. Tính reward, return, advantage.
3. Update actor bằng PPO loss.
4. Update critic bằng value loss.
5. Lặp lại với rollout mới.

PPO là on-policy hoặc gần on-policy, nên dữ liệu cũ nhanh hết giá trị.

## PPO trong Bomberland

Cần chuẩn bị:

- Gymnasium wrapper cho `BomberEnv`.
- Observation encoder ổn định.
- Action mask hoặc safety layer.
- Vectorized env nếu muốn train nhanh.
- Reward không bị hack.
- Opponent sampling đa dạng.

## Điểm mạnh

- Học policy stochastic.
- Ổn định hơn policy gradient cổ điển.
- Có thể kết hợp self-play tốt.
- Hợp với multi-agent nếu có rollout pipeline đúng.

## Điểm yếu

- Sample inefficient, cần nhiều trận.
- Dễ tốn thời gian nếu wrapper chưa chuẩn.
- Nếu reward sai, PPO vẫn học sai.
- Model policy sampling cần kiểm soát để không chọn action ngu khi submit.

## Khi nào nên dùng PPO

Nên dùng nếu:

- Đội đã có rule-based baseline.
- Đã có observation encoder và reward tương đối tốt.
- Có thời gian train trên cloud.
- Có thể test hàng trăm trận để chọn checkpoint.

Không nên dùng nếu:

- Chưa có safety layer.
- Chưa hiểu vì sao agent chết.
- Chưa có local evaluation đáng tin.

## Cách kết hợp thực dụng

PPO không cần quyết định một mình:

```text
safe_actions = rule_filter(obs)
policy_probs = ppo(obs)
action = highest_prob_action_in_safe_actions
```

Safety layer làm giảm khả năng policy chọn hành động tự sát, đồng thời giữ inference đơn giản.

