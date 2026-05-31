# Hierarchical RL với options và macro-actions

Hierarchical RL chia quyết định thành hai tầng: tầng cao chọn mục tiêu chiến thuật, tầng thấp thực hiện action cụ thể. Hướng này rất hợp Bomberland vì nhiều hành vi có cấu trúc rõ như né bom, farm box, nhặt item và ép enemy.

## Ý tưởng

Thay vì để policy chọn trực tiếp `0..5` ở mọi step, tạo các option:

- `SAFETY`: thoát khỏi danger.
- `FARM_BOX`: tìm ô đặt bom phá box.
- `COLLECT_ITEM`: đi lấy item an toàn.
- `CHASE_ENEMY`: áp sát enemy khi không nguy hiểm.
- `ATTACK_TRAP`: đặt bom ép enemy nếu có escape.
- `POSITION_CONTROL`: chiếm vùng an toàn nhiều lối thoát.

High-level policy chọn option. Low-level controller chuyển option thành action.

## Kiến trúc thực dụng

Ban đầu nên dùng:

```text
RL high-level policy -> chọn option
rule low-level controller -> chọn action 0..5
```

Cách này giảm không gian học cho RL. Model không cần học lại BFS, danger map hay escape check từ đầu.

## Tần suất chọn option

Không nhất thiết chọn option mỗi step. Có thể giữ option trong `k` step:

```text
k = 3..8
```

Option kết thúc sớm khi:

- Đã đạt mục tiêu.
- Tình huống nguy hiểm xuất hiện.
- Target không còn hợp lệ.
- Low-level không tìm được action an toàn.

## Train high-level policy

State cho high-level nên là feature chiến thuật:

- Đang trong danger không.
- Item gần nhất có an toàn không.
- Có ô đặt bom phá box không.
- Enemy gần nhất và khả năng trap.
- Safe reachable tiles.
- Số enemy sống.
- Step hiện tại.

Action của high-level là option, không phải action game.

Thuật toán có thể dùng:

- DQN nếu option rời rạc và train đơn giản.
- PPO nếu muốn policy stochastic và self-play.

## Reward

Reward high-level nên gắn với kết quả option:

- `SAFETY`: thưởng khi ra khỏi danger.
- `FARM_BOX`: thưởng khi phá box hoặc tạo đường đến item.
- `COLLECT_ITEM`: thưởng khi nhặt item.
- `ATTACK_TRAP`: thưởng enemy chết hoặc enemy bị giảm vùng an toàn.
- Reward cuối trận vẫn quan trọng nhất.

Tránh thưởng quá lớn cho việc bắt đầu option, vì agent có thể đổi option liên tục.

## Ưu điểm

- Dễ giải thích hơn neural policy thuần.
- RL học quyết định chiến thuật, rule xử lý an toàn.
- Ít sample hơn policy action trực tiếp.
- Dễ kết hợp với ensemble.

## Rủi ro

- Option thiết kế kém sẽ giới hạn trần sức mạnh.
- Low-level rule sai thì high-level cũng khó cứu.
- Cần log option để debug.
- Nếu option switching quá thường xuyên, agent sẽ thiếu nhất quán.

## Khi nên dùng

Rất nên thử nếu đội đã có nhiều rule module nhỏ. Đây là hướng tốt để dùng RL cải thiện một hybrid agent thay vì thay toàn bộ bằng neural policy.

