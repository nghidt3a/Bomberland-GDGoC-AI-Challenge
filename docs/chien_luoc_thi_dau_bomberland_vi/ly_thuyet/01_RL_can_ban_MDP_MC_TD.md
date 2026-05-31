# RL căn bản: MDP, Monte Carlo, Temporal Difference

Reinforcement Learning là học bằng tương tác. Agent quan sát trạng thái, chọn hành động, nhận reward và dần học chính sách tốt hơn.

## MDP

Một bài toán RL thường được mô hình hóa bằng Markov Decision Process:

| Ký hiệu | Ý nghĩa trong Bomberland |
|---|---|
| `S` | State: map, players, bombs, items |
| `A` | Action: `0..5` |
| `P(s'|s,a)` | Luật chuyển trạng thái của engine |
| `R(s,a)` | Reward do ta thiết kế |
| `gamma` | Hệ số chiết khấu reward tương lai |
| `pi(a|s)` | Policy chọn action |

Tính Markov nghĩa là state hiện tại chứa đủ thông tin cần thiết để quyết định. Trong Bomberland, full `obs` khá gần Markov vì có map, player, bomb timer và owner.

## Return

Mục tiêu của agent là tối đa hóa tổng reward có chiết khấu:

```text
G_t = r_t + gamma*r_{t+1} + gamma^2*r_{t+2} + ...
```

Nếu `gamma` gần 1, agent quan tâm nhiều đến tương lai. Nếu `gamma` thấp, agent chỉ quan tâm ngắn hạn.

Trong Bomberland nên dùng `gamma` cao như `0.95..0.99` vì đặt bom hiện tại có kết quả sau nhiều step.

## Value function

`V(s)` đo trạng thái tốt đến mức nào:

```text
V(s) = expected return khi bắt đầu từ state s
```

Ví dụ:

- Đứng trong vùng bom timer 1 có `V(s)` thấp.
- Có 3 bom, radius lớn, gần item và an toàn có `V(s)` cao.

## Q function

`Q(s,a)` đo hành động tốt đến mức nào tại state:

```text
Q(s,a) = expected return nếu làm action a ở state s
```

DQN học `Q(s,a)` rồi chọn action có Q cao nhất.

## Monte Carlo

Monte Carlo học từ kết quả cuối episode:

1. Chơi hết một trận hoặc một episode.
2. Tính return từ dữ liệu thật.
3. Cập nhật value/policy theo return đó.

Ưu điểm:

- Dễ hiểu.
- Không cần biết engine transition.

Nhược điểm:

- Phải chờ episode kết thúc.
- Reward cuối trận thưa và nhiễu.
- Bomberland có nhiều step nên variance cao.

## Temporal Difference

TD cập nhật trước khi episode kết thúc:

```text
V(s) <- V(s) + alpha * (r + gamma*V(s') - V(s))
```

TD target là:

```text
r + gamma*V(s')
```

Ưu điểm:

- Học liên tục từng step.
- Phù hợp môi trường dài.

Nhược điểm:

- Dựa vào ước lượng hiện tại nên có bias.
- Với neural network có thể bất ổn nếu không dùng replay/target network.

## MC và TD trong Bomberland

| Tiêu chí | Monte Carlo | TD |
|---|---|---|
| Dữ liệu | Cần episode hoàn chỉnh | Từng step |
| Tốc độ feedback | Chậm | Nhanh |
| Nhiễu | Cao | Trung bình |
| Phù hợp DQN | Không trực tiếp | Có |
| Phù hợp policy gradient | Có | Có với critic |

Bomberland nên dùng TD/DQN hoặc actor-critic hơn là MC thuần, vì hành động đặt bom có delayed consequence nhưng vẫn cần học liên tục.

## Tư duy đúng cho đội mới

Không cần hiểu hết lý thuyết mới bắt đầu code. Cần nắm:

- State là gì.
- Action là gì.
- Reward đang khuyến khích gì.
- Metric thật là win/rank, không phải reward train.
- Safety rule vẫn cần ngay cả khi dùng RL.

