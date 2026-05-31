# Train PPO bằng Stable-Baselines3: gợi ý kiến trúc

Repo đã liệt kê `stable-baselines3` và `gymnasium` trong requirements. Để train PPO, cần wrapper Bomberland thành Gym environment. Đây là hướng nâng cao, không nên làm trước rule-based.

## Thành phần cần viết

Một wrapper tối thiểu cần:

- `reset() -> (obs_encoded, info)`.
- `step(action) -> (obs_encoded, reward, terminated, truncated, info)`.
- `observation_space`.
- `action_space = Discrete(6)`.
- Opponent agents cho 3 slot còn lại.

## Observation space

Hai hướng:

### MLP feature vector

Feature vector gồm:

- Vị trí mình normalized.
- Bombs left, radius.
- Enemy relative positions.
- Danger flags.
- Distance item/box/enemy.
- Safe action mask.

Dễ train, inference nhanh, nhưng mất thông tin spatial chi tiết.

### CNN channel map

Tensor shape ví dụ `(C, 13, 13)`:

- Map one-hot.
- My position.
- Enemy positions.
- Bomb timer.
- Danger map.
- Safe reachable map.

Giữ spatial tốt hơn, model lớn hơn một chút.

## Reward

PPO cần reward scale ổn định:

- Reward cuối trận rõ.
- Reward phụ nhỏ.
- Có penalty chết.
- Có penalty timeout/action invalid nếu wrapper ghi được.

Không để reward item/box lớn hơn win.

## Opponent wrapper

Khi PPO action cho player chính, 3 player còn lại dùng:

- Baseline random/simple/tactical.
- Snapshot cũ.
- Mixed pool theo xác suất.

Randomize `agent_id` nếu muốn giảm position bias, nhưng cần wrapper phức tạp hơn.

## Action safety

SB3 PPO core không tự biết action invalid. Có thể:

- Dùng wrapper sửa action unsafe thành fallback.
- Đưa action mask vào observation và phạt action unsafe.
- Dùng thư viện maskable PPO nếu đội chấp nhận thêm phụ thuộc và kiểm soát được submission.

Hướng an toàn: vẫn có rule safety trong agent submit.

## Evaluation callback

Định kỳ test:

- 50-100 trận vs mixed baseline.
- Ghi win/draw/rank.
- Save best theo average rank, không chỉ reward.

## Deploy PPO

Khi submit:

- Không đưa toàn bộ training wrapper nếu không cần.
- Agent chỉ load policy và encode obs.
- Chạy CPU.
- Có fallback rule.

## Khi không nên dùng PPO

Không dùng nếu:

- Chưa có wrapper chắc.
- Reward chưa debug.
- Train quá chậm.
- Model không vượt hybrid rule.
- Không đảm bảo 100ms.

