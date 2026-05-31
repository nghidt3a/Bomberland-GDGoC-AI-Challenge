# Hướng dẫn test 4 agents và hiển thị trận đấu

Tài liệu này hướng dẫn chọn đúng 4 agent, chạy một trận mô phỏng, xem kết quả trên terminal và mở viewer PyGame để quan sát trận đấu trên màn hình.

## Nguyên tắc chọn 4 agent

`run_local_match` luôn cần đúng 4 agent trong `--agent_paths`. Mỗi vị trí tương ứng player id:

| Thứ tự trong lệnh | Player id | Spawn |
|---:|---:|---|
| Agent 1 | `0` | góc trên trái |
| Agent 2 | `1` | góc dưới phải |
| Agent 3 | `2` | góc trên phải |
| Agent 4 | `3` | góc dưới trái |

Ví dụ:

```bash
python -m scripts.participant.run_local_match --agent_paths submit_mau TacticalRuleAgent SmarterRuleAgent GeniusRuleAgent --num_episodes 1 --visualize false
```

Trong ví dụ trên:

- `submit_mau` là player 0.
- `TacticalRuleAgent` là player 1.
- `SmarterRuleAgent` là player 2.
- `GeniusRuleAgent` là player 3.

## Các kiểu agent có thể truyền vào

| Kiểu | Ví dụ | Khi dùng |
|---|---|---|
| Folder custom agent | `submit_mau` hoặc `agent/dqn_agent` | Folder có `agent.py` bên trong |
| File custom agent | `agent/tactical_rule_agent.py` | File `.py` có class agent |
| Baseline name | `TacticalRuleAgent` | Dùng baseline có sẵn |
| Random baseline | `None` hoặc `Random` | Để script random một baseline |

Baseline name có sẵn:

```text
RandomAgent
SimpleRuleAgent
BoxFarmerAgent
SmarterRuleAgent
TacticalRuleAgent
GeniusRuleAgent
```

## Test nhanh không hiển thị màn hình

Dùng headless trước để biết agent có load và chạy được không:

```bash
python -m scripts.participant.run_local_match --agent_paths submit_mau RandomAgent SimpleRuleAgent TacticalRuleAgent --num_episodes 1 --visualize false
```

Chạy nhiều episode hơn:

```bash
python -m scripts.participant.run_local_match --agent_paths submit_mau TacticalRuleAgent SmarterRuleAgent GeniusRuleAgent --num_episodes 10 --visualize false
```

Kết quả terminal sẽ có dạng:

```text
Episode 1: Draw | Died: [...]

=== Summary ===
submit_mau: 0 wins
TacticalRuleAgent: ...
```

## Test với seed cố định

Dùng seed để replay lại cùng một map và chuỗi random:

```bash
python -m scripts.participant.run_local_match --agent_paths submit_mau TacticalRuleAgent SmarterRuleAgent GeniusRuleAgent --num_episodes 1 --seed 42 --visualize false
```

Khi debug, luôn ghi lại seed gây lỗi để tái hiện.

## Hiển thị trận đấu bằng PyGame

Mở viewer:

```bash
python -m scripts.participant.run_local_match --agent_paths submit_mau TacticalRuleAgent SmarterRuleAgent GeniusRuleAgent --num_episodes 1 --seed 42 --visualize true
```

Viewer sẽ mô phỏng episode rồi mở cửa sổ PyGame để xem. Nên để `--num_episodes` nhỏ, ví dụ `1..3`, vì visualize chủ yếu dùng để debug hành vi.

## Xem từng bước thủ công

Tắt autoplay:

```bash
python -m scripts.participant.run_local_match --agent_paths submit_mau TacticalRuleAgent SmarterRuleAgent GeniusRuleAgent --num_episodes 1 --seed 42 --visualize true --autoplay false
```

Phím điều khiển trong viewer:

| Phím | Tác dụng |
|---|---|
| `D` | Sang step tiếp theo |
| `A` | Lùi step trước |
| `S` | Sang episode tiếp theo |
| `W` | Lùi episode trước |
| `SPACE` | Pause/Play |
| `ESC` | Thoát viewer |

## Các kịch bản test nên chạy

### 1. Smoke test agent mới

Mục tiêu: agent load được, không crash.

```bash
python -m scripts.participant.run_local_match --agent_paths submit_mau RandomAgent SimpleRuleAgent TacticalRuleAgent --num_episodes 1 --visualize false
```

### 2. Test với baseline mạnh

Mục tiêu: xem agent có sống nổi trước đối thủ tốt hơn không.

```bash
python -m scripts.participant.run_local_match --agent_paths submit_mau TacticalRuleAgent SmarterRuleAgent GeniusRuleAgent --num_episodes 20 --visualize false
```

### 3. Test vị trí spawn khác

Đổi thứ tự agent để agent của mình không chỉ chơi player 0:

```bash
python -m scripts.participant.run_local_match --agent_paths TacticalRuleAgent submit_mau SmarterRuleAgent GeniusRuleAgent --num_episodes 10 --visualize false
python -m scripts.participant.run_local_match --agent_paths TacticalRuleAgent SmarterRuleAgent submit_mau GeniusRuleAgent --num_episodes 10 --visualize false
python -m scripts.participant.run_local_match --agent_paths TacticalRuleAgent SmarterRuleAgent GeniusRuleAgent submit_mau --num_episodes 10 --visualize false
```

### 4. Test random mixed pool

Mục tiêu: gần với trận thật hơn vì đối thủ đa dạng.

```bash
python -m scripts.participant.run_local_match --agent_paths submit_mau None None None --num_episodes 50 --visualize false
```

### 5. Visualize một seed bị lỗi

Nếu headless thấy agent chết lạ ở seed `42`, mở viewer:

```bash
python -m scripts.participant.run_local_match --agent_paths submit_mau TacticalRuleAgent SmarterRuleAgent GeniusRuleAgent --num_episodes 1 --seed 42 --visualize true --autoplay false
```

Sau đó dùng `D` để xem từng step trước khi chết.

## Test thuật toán DQN/PPO/BC đã đóng gói

Nếu agent thuật toán nằm trong folder có `agent.py`, truyền folder đó:

```bash
python -m scripts.participant.run_local_match --agent_paths agent/dqn_agent TacticalRuleAgent SmarterRuleAgent GeniusRuleAgent --num_episodes 5 --visualize false
```

Nếu đó là thư mục submit riêng:

```bash
python -m scripts.participant.run_local_match --agent_paths path/to/my_submission_folder TacticalRuleAgent SmarterRuleAgent GeniusRuleAgent --num_episodes 5 --visualize false
```

Điều kiện folder custom:

- Có file `agent.py`.
- Có class `Agent`.
- Checkpoint nếu có phải load bằng path tương đối từ `agent.py`.
- Không chạy train khi import.

## Benchmark thời gian sau khi test hành vi

Sau khi agent chơi được, đo thời gian:

```bash
python -m scripts.participant.estimate_agent_time submit_mau --opponents TacticalRuleAgent SmarterRuleAgent GeniusRuleAgent --num_matches 10
```

Nếu dùng DQN/PPO:

```bash
python -m scripts.participant.estimate_agent_time agent/dqn_agent --opponents TacticalRuleAgent SmarterRuleAgent GeniusRuleAgent --num_matches 10
```

Không nộp agent nếu có spike vượt 100ms.

## Cách đọc trận visualize

Khi xem viewer, chú ý:

- Player id và màu ở sidebar.
- `B`: số bom còn lại.
- `R`: bonus radius.
- Số trên bomb: timer còn lại.
- Ô cam/vàng: vùng nổ vừa xảy ra.
- Item `R`: tăng radius.
- Item `C`: tăng capacity.

Các câu hỏi cần trả lời khi agent chết:

- Agent chết bởi bom của ai?
- Trước khi chết có đường thoát không?
- Agent có đặt bom tự kẹt không?
- Agent có đi vào vùng nổ timer thấp không?
- Agent có đứng yên vì không tìm được path không?
- Agent có tranh item làm item bị hủy không?

## Lưu ý môi trường

- Viewer PyGame cần chạy trên máy có giao diện màn hình.
- Trên Kaggle/Colab thường không mở cửa sổ PyGame trực tiếp được; dùng headless để train/test trên cloud, visualize trên máy local.
- Nếu viewer lỗi do thiếu `pygame`, cài dependency từ `requirements.txt`.

