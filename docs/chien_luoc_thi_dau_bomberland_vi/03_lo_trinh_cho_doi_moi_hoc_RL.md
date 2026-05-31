# Lộ trình cho đội mới học RL

Đội chưa có nền RL không nên nhảy thẳng vào PPO hoặc self-play. Cách đi an toàn là xây agent có năng lực bằng luật trước, sau đó dùng RL để cải thiện.

## Lộ trình 7 ngày

Mục tiêu: có agent rule-based ổn để nộp sớm.

| Ngày | Việc chính |
|---|---|
| 1 | Đọc luật game, observation, action, timeout, submission |
| 2 | Viết module phân tích danger map và valid actions |
| 3 | BFS tìm ô an toàn, né bom, tránh tự sát |
| 4 | Logic đặt bom phá hộp khi có đường thoát |
| 5 | Logic nhặt item và ưu tiên capacity/radius |
| 6 | Test nhiều baseline, fix timeout và lỗi edge case |
| 7 | Đóng gói ZIP, nộp bản đầu tiên, lưu log |

Kết quả mong muốn: agent sống lâu, farm được, thắng baseline yếu và không vi phạm kỹ thuật.

## Lộ trình 14 ngày

Mục tiêu: nâng rule-based thành hybrid, chuẩn bị RL.

Tuần 1 làm như lộ trình 7 ngày.

Tuần 2:

| Ngày | Việc chính |
|---|---|
| 8 | Thêm scoring action: an toàn, item, box, enemy, escape |
| 9 | Thêm simulation ngắn 2-4 step để tránh bẫy bom |
| 10 | Thu dữ liệu từ rule agent tốt làm dataset behavior cloning |
| 11 | Train BC nhỏ trên Colab/Kaggle |
| 12 | Dùng BC làm policy gợi ý, rule-based làm safety layer |
| 13 | Benchmark local, estimate rank, benchmark 100ms |
| 14 | Chọn giữa hybrid rule và hybrid BC để nộp |

## Lộ trình 21 ngày

Mục tiêu: có pipeline RL/self-play và agent cuối ổn định.

Tuần 1: rule-based ổn.

Tuần 2: hybrid và behavior cloning.

Tuần 3:

| Ngày | Việc chính |
|---|---|
| 15 | Train DQN với reward shaping và opponent curriculum |
| 16 | So sánh DQN với hybrid rule trên 100-300 trận local |
| 17 | Thử PPO nếu đã có Gym wrapper đáng tin |
| 18 | Self-play với pool gồm bản cũ và baseline mạnh |
| 19 | Distill hoặc ensemble policy tốt với rule safety |
| 20 | Benchmark CPU, giảm model, đóng gói checkpoint |
| 21 | Nộp bản cuối, chuẩn bị giải thích thuật toán cho pitching |

## Kiến thức RL cần học trước

Không cần học toàn bộ RL ngay. Học theo thứ tự:

1. MDP: state, action, reward, transition, policy.
2. Q-learning: học giá trị hành động.
3. DQN: Q-learning với neural network.
4. Policy gradient và PPO: học trực tiếp policy.
5. Self-play: train chống lại chính mình và các bản cũ.
6. Reward hacking: agent tối ưu reward sai mục tiêu.

## Vai trò trong đội

Nếu có 3-4 người:

- 1 người phụ trách luật game, feature, danger map, BFS.
- 1 người phụ trách rule/hybrid agent.
- 1 người phụ trách train cloud, log, checkpoint.
- 1 người phụ trách test, benchmark, submission, tài liệu pitching.

Nếu chỉ có 1-2 người, bỏ bớt PPO/MCTS phức tạp, tập trung hybrid rule-based và DQN/BC nhỏ.

## Tiêu chí dừng một hướng

Nên dừng hoặc hạ ưu tiên nếu:

- Train 1-2 ngày không vượt rule-based.
- Model không chạy dưới 100ms CPU.
- Reward tăng nhưng win rate giảm.
- Agent chỉ thắng một loại baseline nhưng thua các loại khác.
- Cần sửa engine quá nhiều mới train được.

