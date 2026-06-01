# 09 — Thuật ngữ RL/Bomberman giải thích dễ hiểu

File này dành cho thành viên chưa có nhiều kinh nghiệm ML/RL.

## Agent

Agent là bot của đội mình. Mỗi step agent nhận `obs` và trả về action.

## Environment

Environment là môi trường game: map, bom, box, item, agent khác và luật nổ bom.

## Step

Một lượt xử lý nhỏ của game. Mỗi step agent chọn action, engine xử lý rồi chuyển sang step tiếp theo.

## Episode / Match

Một trận hoàn chỉnh từ đầu đến khi kết thúc. Trong cuộc thi, mỗi trận tối đa 500 steps.

## Observation / Obs

Thông tin agent nhận được:

```python
obs = {"map": ..., "players": ..., "bombs": ...}
```

## Action

Hành động agent trả về:

```text
0 STOP
1 LEFT
2 RIGHT
3 UP
4 DOWN
5 PLACE_BOMB
```

## Policy

Chiến lược chọn action. Rule policy là luật if-else; neural policy là model dự đoán action.

## Reward

Điểm thưởng/phạt dùng để train RL. Ví dụ: phá box +1, nhặt item +1.5, kill +8, chết -20.

## Reward shaping

Thêm reward phụ để agent học nhanh hơn. Nếu shaping sai, agent có thể học hành vi xấu.

## Reward hacking

Agent tìm cách ăn reward nhưng chơi không tốt. Ví dụ thưởng sống quá cao khiến agent camping.

## RL

RL = Reinforcement Learning = học tăng cường. Agent tự chơi, nhận reward và học dần.

## Rule-based

Tự viết luật điều khiển agent. Ví dụ: nếu gần bom thì chạy; nếu đặt bom không có đường thoát thì không đặt.

## Hybrid

Kết hợp rule và ML/RL. Hướng khuyến nghị:

```text
rule đảm bảo safety
model chọn trong safe actions
shield kiểm tra cuối
```

## Action mask

Bộ lọc action. Ví dụ `[False, True, False, True, False, False]` nghĩa là chỉ được chọn LEFT hoặc UP.

## Safety shield

Lớp bảo vệ cuối. Nếu policy chọn action nguy hiểm, shield đổi sang action an toàn hơn.

## Danger map

Bản đồ cho biết ô nào sẽ nổ ở step nào. Đây là nền tảng để né bom.

## BFS

Breadth-First Search, thuật toán tìm đường ngắn nhất trên grid. Dùng để tìm ô an toàn, item, vị trí phá box.

## Time-expanded BFS

BFS có thêm thời gian. State là `(row, col, t)`, giúp biết khi tới ô đó thì ô có nổ không.

## Chain reaction

Bom nổ kích hoạt bom khác nổ theo. Nếu không tính, agent rất dễ tự chết.

## Self-kill

Agent tự làm mình chết, thường do bom của chính mình hoặc tự trap.

## Self-trap

Agent tự nhốt mình. Ví dụ đặt bom trong góc rồi không có đường chạy.

## Farming

Phá box và nhặt item để mạnh lên. Tie-break mới làm farming rất quan trọng.

## Pressure

Gây áp lực lên đối thủ, buộc họ di chuyển hoặc mất vị trí, chưa chắc kill ngay.

## Kill score

Điểm tấn công khi có cơ hội giết đối thủ. Không nên bật quá dễ vì dễ đánh liều.

## Behavior Cloning / BC

Học bắt chước rule/expert:

```text
observation → action expert chọn
```

Train như bài toán phân loại 6 action.

## DAgger

Cải tiến BC: cho model tự chơi, state nào model xử lý kém thì hỏi expert và thêm vào dataset.

## PPO

Thuật toán RL học policy trực tiếp. Chỉ nên dùng PPO nếu có BC init, action mask, shield và benchmark.

## DQN

Thuật toán RL học Q-value cho từng action. Ví dụ action nào có Q cao nhất thì chọn.

## Self-play

Cho agent đấu với chính nó hoặc checkpoint cũ để học nhiều kiểu đối thủ.

## Opponent pool

Danh sách đối thủ dùng để train/benchmark: random, camper, farmer, aggressive, rule cũ, BC, PPO snapshots.

## Benchmark

Chạy nhiều trận để đo agent. Không benchmark thì không biết version nào thật sự tốt.

## Checkpoint

File model lưu trong quá trình train. Không chọn checkpoint theo train reward, chọn theo benchmark rank.

## Latency

Thời gian `act()` chạy. Cuộc thi giới hạn khoảng 100ms.

## p95/p99

p99 = 99% lần chạy nhanh hơn mốc này. Mean thấp nhưng p99 cao vẫn nguy hiểm.

## Overfitting

Agent quá khớp vài seed/opponent, gặp tình huống khác thì yếu.

## Terminal rank reward

Reward cuối trận dựa trên rank. Giúp RL tối ưu đúng mục tiêu cuộc thi.

## Useful bomb

Bom hữu ích là bom phá box, tạo threat hoặc kiểm soát map, và người đặt có đường thoát.

## Camping/Stalling

Agent đứng thủ hoặc né giao tranh, không farm. Tie-break mới làm kiểu này yếu hơn.

## Final fallback

Action dùng khi mọi thứ lỗi hoặc không còn safe action. Fallback không được crash.

## Tóm tắt dễ nhớ

```text
Safety core = tránh chết ngu
Scoring = farm/attack chủ động
BC = học bắt chước rule
PPO = optional nâng cấp
Benchmark = chọn version bằng số liệu
Shield = bảo hiểm cuối cùng
```
