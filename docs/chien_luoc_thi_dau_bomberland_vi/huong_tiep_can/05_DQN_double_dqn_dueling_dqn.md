# DQN, Double DQN và Dueling DQN

DQN phù hợp với action rời rạc `0..5`. Hướng này nên làm sau khi đã có rule-based baseline và reward/feature rõ ràng.

## Mục tiêu

Train model dự đoán Q-value cho 6 action:

```text
Q(obs) -> [Q_STOP, Q_LEFT, Q_RIGHT, Q_UP, Q_DOWN, Q_BOMB]
```

Khi inference, chọn action Q cao nhất trong các action an toàn.

## Pipeline

1. Encode observation.
2. Chọn action bằng epsilon-greedy.
3. Step environment.
4. Tính reward.
5. Lưu transition vào replay buffer.
6. Sample minibatch.
7. Update Q-network.
8. Định kỳ update target network.
9. Test checkpoint trước baseline.

## Double DQN

Nên thêm Double DQN vì chi phí thấp:

```text
best_next_action = argmax Q_online(next_state)
target = reward + gamma * Q_target(next_state, best_next_action)
```

Giúp giảm overestimate Q-value.

## Dueling DQN

Dueling DQN đáng thử nếu model thường khó phân biệt action:

```text
Q(s,a) = V(s) + A(s,a) - mean(A(s,*))
```

Nó giúp model học state value riêng với action advantage.

## Feature khuyến nghị

Spatial channels:

- Map one-hot.
- My position.
- Enemy positions.
- Bomb timer.
- Own bomb.
- Danger map.
- Safe reachable map.

Scalar:

- `bombs_left / 5`.
- `radius / 5`.
- Số enemy sống.
- Khoảng cách item gần nhất.
- Khoảng cách enemy gần nhất.
- Đang trong danger hay không.

## Reward khuyến nghị

Bắt đầu đơn giản:

- `+2` win.
- `+1` enemy death.
- `-2` agent death.
- `+0.1` item.
- `+0.05` đặt bom phá box có escape.
- `+0.1` rời danger.
- `-0.05` đi vào danger.
- `-0.005` mỗi step.

Sau đó tune theo replay.

## Safety layer

Bắt buộc nên có:

```text
q_values = model(obs)
mask unsafe actions
if no safe model action:
    return rule_fallback(obs)
return argmax safe q_values
```

Safety layer giúp DQN không tự sát trong những state hiếm.

## Opponent curriculum

Train theo thứ tự:

1. Simple.
2. Box farmer.
3. Smarter.
4. Tactical.
5. Genius.
6. Mixed pool.
7. Self-play snapshots.

Nếu train ngay với opponent mạnh, agent mới có thể chết nhanh và học chậm.

## Khi nào checkpoint tốt

Checkpoint tốt nếu:

- Vượt rule baseline hoặc bổ trợ tốt cho rule baseline.
- Average rank tốt qua nhiều seed.
- Không có reward hacking.
- Inference CPU ổn.

Nếu DQN kém hơn hybrid rule, dùng DQN như prior phụ hoặc bỏ khỏi bản nộp.

