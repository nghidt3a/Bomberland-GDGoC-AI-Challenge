# Q-learning và DQN

Q-learning học giá trị của từng hành động trong từng trạng thái. DQN dùng neural network để xấp xỉ Q-value khi state quá lớn để lưu bảng.

## Q-learning tabular

Công thức:

```text
Q(s,a) <- Q(s,a) + alpha * (r + gamma * max_a' Q(s',a') - Q(s,a))
```

Ý nghĩa:

- `Q(s,a)`: niềm tin hiện tại về action `a`.
- `r`: reward vừa nhận.
- `max Q(s',a')`: hành động tốt nhất ở state tiếp theo.
- `alpha`: learning rate.
- `gamma`: discount.

Tabular Q-learning không phù hợp trực tiếp với Bomberland vì state gồm map 13x13, bombs, players, item, timer. Số trạng thái quá lớn.

## DQN

DQN thay bảng Q bằng neural network:

```text
input: encoded obs
output: 6 Q-values cho action 0..5
```

Agent chọn:

```text
argmax_a Q(s,a)
```

Trong train, dùng epsilon-greedy:

- Xác suất `epsilon`: chọn random để khám phá.
- Còn lại: chọn action có Q cao nhất.

## Hai cơ chế ổn định

### Experience replay

Lưu transition:

```text
(state, action, reward, next_state, done)
```

Sau đó sample random minibatch để train. Replay giúp giảm tương quan giữa các state liên tiếp.

### Target network

DQN dùng hai mạng:

- Online network: đang train.
- Target network: tạo TD target ổn định hơn.

Định kỳ copy online sang target.

## Double DQN

DQN thường overestimate Q-value. Double DQN sửa bằng cách:

- Online network chọn action tốt nhất ở `s'`.
- Target network đánh giá Q-value của action đó.

Target:

```text
y = r + gamma * Q_target(s', argmax_a Q_online(s',a))
```

Double DQN thường đáng thử vì cải thiện ổn định với chi phí thấp.

## Dueling DQN

Dueling DQN tách:

- `V(s)`: state này tốt không.
- `A(s,a)`: action này tốt hơn trung bình bao nhiêu.

Rồi ghép lại thành Q. Hữu ích khi nhiều action có giá trị gần nhau, ví dụ nhiều hướng di chuyển đều an toàn.

## DQN cho Bomberland

Input nên gồm:

- One-hot map.
- Vị trí mình.
- Vị trí enemy.
- Bomb timer.
- Bomb owner.
- Danger map.
- Scalar: bombs left, radius, enemy alive count.

Output là 6 action.

Nên dùng action mask:

- Mask action invalid.
- Mask action đi vào nổ ngay.
- Mask đặt bom tự sát.

## Điểm mạnh

- Dễ triển khai hơn PPO nếu đã có transition.
- Sample efficient hơn PPO.
- Phù hợp action rời rạc `0..5`.
- Có thể train đối đầu baseline cụ thể.

## Điểm yếu

- Reward design khó.
- Dễ bất ổn.
- Dễ học spam bom hoặc đứng yên nếu reward sai.
- Một policy greedy có thể bị bắt bài.
- Cần nhiều trận mô phỏng.

## Hyperparameter gợi ý

| Tham số | Gợi ý |
|---|---|
| `gamma` | `0.95..0.99` |
| learning rate | `1e-4..1e-3` |
| replay buffer | `10k..200k` |
| batch size | `64..256` |
| epsilon start | `1.0` |
| epsilon min | `0.05..0.1` |
| target update | mỗi `500..5000` step hoặc mỗi vài episode |

## Cách dùng thực dụng

Không để DQN quyết toàn bộ ngay. Dùng:

```text
raw_action = dqn(obs)
if raw_action unsafe:
    action = rule_fallback(obs)
else:
    action = raw_action
```

Hoặc dùng DQN để chấm điểm các action safe đã qua rule filter.

