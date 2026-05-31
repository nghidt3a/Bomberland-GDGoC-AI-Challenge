# Offline RL từ log trận và replay

Offline RL học từ dữ liệu đã thu thập sẵn, không cần tương tác liên tục với môi trường trong lúc update. Hướng này hữu ích nếu đội có nhiều log từ rule agent, baseline hoặc self-play cũ.

## Mục tiêu

Tạo dataset transition:

```text
(obs_encoded, action, reward, next_obs_encoded, done, info)
```

Sau đó train policy/Q-network từ dataset này trước khi fine-tune online.

## Nguồn dữ liệu

Có thể lấy từ:

- Rule-based safety/farming agent.
- Hybrid heuristic agent.
- BC/DAgger rollout.
- Các checkpoint self-play cũ.
- Baseline public trong repo.

Dataset tốt cần đa dạng seed, vị trí spawn và đối thủ. Nếu chỉ log một rule agent chơi một kiểu, offline policy sẽ hẹp.

## Bắt đầu bằng BC trước

Trước khi làm offline RL phức tạp, nên train behavior cloning:

```text
obs -> action_logged
```

BC cho biết encoder và dataset có đủ thông tin để dự đoán hành vi không. Nếu BC accuracy thấp ở state quan trọng, offline RL cũng khó ổn.

## Thuật toán phù hợp

Với action rời rạc, có thể thử:

- Conservative Q-Learning dạng discrete.
- Implicit Q-Learning bản discrete nếu tự triển khai được.
- DQN với regularization giữ gần behavior policy.
- BC warm-start rồi fine-tune bằng DQN/PPO.

Không nên dùng DQN offline thuần mà không kiểm soát out-of-distribution action, vì Q-value có thể ảo cho action chưa từng thấy.

## Chống out-of-distribution

Offline RL dễ chọn action dataset chưa đủ phủ. Cần:

- Action mask an toàn.
- Penalty cho action có xác suất behavior quá thấp.
- Conservative loss để hạ Q của action lạ.
- Fine-tune online ngắn với opponent pool trước khi nộp.

## Dataset schema nên log

Ngoài transition chính, nên log thêm:

- `agent_id`.
- `seed`.
- `step`.
- `rank/death_status`.
- `source_policy`.
- `safety_mask`.
- `fallback_used`.
- Feature tóm tắt như danger, safe_tiles, nearest_item_distance.

Những field này giúp lọc dataset và debug reward hacking.

## Evaluation

Không chọn model theo offline loss. Chọn theo:

- Win/rank khi chạy thật.
- Fallback rate.
- Self-kill rate.
- Mức vượt rule expert.
- Robust qua seed chưa log.

Offline loss đẹp nhưng policy chết sớm là chuyện thường gặp.

## Khi nên dùng

Dùng offline RL khi:

- Đội đã có agent rule đủ mạnh để sinh dữ liệu.
- Muốn tận dụng nhiều trận mô phỏng đã chạy.
- Online training tốn thời gian hoặc không ổn định.

Không nên dùng nếu dataset ít, lệch hoặc chứa nhiều action tự sát.

