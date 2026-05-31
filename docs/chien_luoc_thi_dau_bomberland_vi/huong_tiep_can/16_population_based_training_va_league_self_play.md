# Population Based Training và league self-play

Population Based Training (PBT) kết hợp train nhiều policy với việc tự động chọn hyperparameter tốt. Khi ghép với league self-play, đây là hướng mạnh nhưng tốn tài nguyên.

## Ý tưởng

Chạy nhiều worker:

```text
policy_1, policy_2, ..., policy_n
```

Mỗi policy có hyperparameter riêng:

- Learning rate.
- Entropy coefficient.
- Reward weight.
- Opponent sampling.
- Exploration rate.
- Safety penalty.

Định kỳ đánh giá. Policy yếu copy trọng số của policy mạnh rồi mutate hyperparameter.

## League self-play

League gồm:

- Main learners.
- Historical snapshots.
- Rule baselines.
- Exploiters chuyên đánh một nhóm policy.
- Defensive agents ưu tiên sống sót.

Mục tiêu là tránh policy chỉ thắng một đối thủ cố định.

## Lịch PBT đơn giản

Ví dụ mỗi 50k-200k step:

1. Eval mỗi policy qua seed cố định và seed mới.
2. Tính average rank, self-kill, win rate.
3. Chọn nhóm top.
4. Policy bottom copy checkpoint top.
5. Mutate nhẹ hyperparameter.
6. Thêm snapshot tốt vào league.

Không mutate quá mạnh, nếu không kết quả khó quy nguyên nhân.

## Hyperparameter nên mutate

Với PPO/MAPPO:

- `learning_rate`.
- `ent_coef`.
- `clip_range`.
- Reward weight cho item/box/enemy.
- Opponent pool probability.

Với DQN:

- `epsilon`.
- `learning_rate`.
- Prioritized replay alpha/beta.
- N-step.
- Target update interval.

## Metric chọn policy

Không dùng train reward duy nhất. Nên dùng:

- Average rank trước mixed pool.
- Self-kill rate thấp.
- Timeout bằng 0.
- Thắng baseline chưa train cùng gần đây.
- Không phụ thuộc một spawn position.

Có thể dùng điểm tổng:

```text
score = average_rank_score - self_kill_penalty - timeout_penalty
```

## Ưu điểm

- Tự tìm hyperparameter tốt hơn manual tuning.
- Tạo nhiều phong cách policy cho ensemble.
- Giảm overfit nếu league đa dạng.

## Rủi ro

- Tốn GPU/CPU và thời gian.
- Pipeline phức tạp.
- Dễ chọn nhầm policy exploit yếu seed eval.
- Nếu baseline ban đầu kém, cả population học lệch.

## Khi nên dùng

Chỉ dùng khi đội đã có training pipeline tự động và đủ tài nguyên cloud. Nếu thời gian ít, hãy dùng self-play curriculum thường trước.

