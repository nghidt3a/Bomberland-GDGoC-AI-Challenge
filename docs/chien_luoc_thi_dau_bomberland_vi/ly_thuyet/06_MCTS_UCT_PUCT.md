# MCTS, UCT và PUCT

Monte Carlo Tree Search là thuật toán planning online. Mỗi step, agent mô phỏng tương lai nhiều lần để chọn action tốt.

## Bốn bước MCTS

1. Selection: đi từ root xuống node con theo công thức chọn.
2. Expansion: mở rộng action chưa thử.
3. Simulation: rollout hoặc đánh giá state.
4. Backpropagation: cập nhật thống kê ngược lên cây.

Sau nhiều vòng, chọn action có thống kê tốt nhất.

## UCT

UCT cân bằng khai thác và khám phá:

```text
UCT = Q_i / N_i + c * sqrt(log(N_parent) / N_i)
```

Trong đó:

- `Q_i / N_i`: giá trị trung bình của node.
- Thành phần còn lại: bonus cho node ít được thử.
- `c`: hệ số exploration.

## PUCT

PUCT dùng prior từ policy network:

```text
PUCT = Q(s,a) + c_puct * P(s,a) * sqrt(N(s)) / (1 + N(s,a))
```

Trong đó `P(s,a)` là xác suất action từ policy network. PUCT phù hợp khi có model gợi ý action tốt.

## MCTS trong Bomberland khó ở đâu

Bomberland có các rào cản:

- 4 agent cùng hành động.
- Branching factor lớn nếu xét action của mọi agent.
- Bom nổ sau 7 step, cần rollout đủ sâu.
- Mỗi `act()` chỉ 100ms.
- Cần forward model nhanh và chính xác.

MCTS thuần chạy nhiều rollout sâu thường không kịp.

## Cách dùng MCTS giới hạn

Nếu muốn thử, chỉ dùng cục bộ:

- Chỉ search action của mình.
- Đối thủ giả lập bằng rule đơn giản hoặc đứng yên.
- Depth 3-6.
- Budget theo thời gian, ví dụ dừng ở 60-80ms.
- Heuristic leaf evaluation thay vì rollout dài.

Leaf heuristic nên gồm:

- Alive/safe.
- Có escape.
- Item gần.
- Box hit.
- Enemy threat.
- Dead-end penalty.

## Khi nào MCTS hữu ích

MCTS hữu ích trong tình huống chiến thuật ngắn:

- Có nhiều bom sắp nổ.
- Cần chọn đường thoát.
- Cần quyết định đặt bom có kẹt enemy không.
- Endgame còn 1-2 enemy gần nhau.

Không nên dùng MCTS cho toàn bộ decision nếu chưa tối ưu rất kỹ.

## Kết hợp neural policy

Policy network có thể:

- Gợi ý action prior cho PUCT.
- Cắt bớt action tệ.
- Đánh giá leaf state thay rollout.

Nhưng với cuộc thi này, độ phức tạp cao. Hướng thực dụng hơn là dùng heuristic search nhỏ thay vì MCTS đầy đủ.

