# 11 — Roadmap 3 tuần đã chỉnh theo feedback thực chiến

Roadmap này giữ tinh thần kế hoạch 3 tuần ban đầu, nhưng giảm rủi ro: PPO không còn là bắt buộc; rule safety + benchmark là trọng tâm.

## Tuần 1: Safety core + rule hybrid submit được

Mục tiêu cuối tuần:

```text
rule_v1 chạy ổn
self-death thấp
farm box/item cơ bản
thắng hoặc không thua camper ở step500 tie-break
benchmark có số
```

### Ngày 1: Setup + parse obs

- Setup simulator.
- Viết constants/action ids.
- Viết `parse_obs`.
- Xác nhận `bombs = [row, col, timer, owner_id]`.
- Xác nhận `radius = 1 + players[owner_id][4]`.
- Test agent_id 0–3.

### Ngày 2: Blast + danger map cơ bản

- Viết `blast_cells`.
- Wall chặn.
- Box chặn và bị phá.
- Tính danger_time.
- Test 1 bom với radius khác nhau.

### Ngày 3: Chain reaction + fire duration

- Viết chain reaction fixpoint.
- Test 2–3 bom.
- Xác minh fire duration = 1 step hoặc theo engine thực tế.
- Log/visualize danger map.

### Ngày 4: Time-expanded BFS

- Viết BFS theo `(cell, t)`.
- Cho phép STOP.
- Không đi qua wall/box.
- Kiểm tra safe_at theo danger_time.
- Test corridor/góc.

### Ngày 5: Masks + bomb checker + shield

- Legal action mask.
- Safe action mask.
- `can_place_bomb_safely`.
- `final_shield`.
- `least_bad_action`.

### Ngày 6: Farm/item/anti-loop

- Box gain.
- Tìm cụm box.
- Item collector.
- Anti-loop/anti-camping.
- Scoring v1.

### Ngày 7: Benchmark + fix bug

- Chạy 200–300 trận.
- Đo metric.
- Phân tích self-death.
- Tạo `rule_v1`.
- Nếu chưa đạt self-death thấp, kéo dài Tuần 1, chưa sang BC.

## Tuần 2: Rule_v2 hoặc Behavior Cloning

Đầu tuần 2 quyết định:

```text
Nếu rule_v1 còn nhiều lỗi → rule_v2
Nếu rule_v1 ổn → BC
```

### Nhánh rule_v2

- Sửa bug từ replay.
- Tăng farm/item drive.
- Thêm pressure score.
- Thêm step500 tie-break tracker.
- Benchmark 300+ trận.
- Chốt `rule_v2`.

### Nhánh BC

- Chốt `encode(obs)`.
- Sinh dataset từ rule_v1/rule_v2.
- Train CNN nhỏ.
- Đánh giá BC+shield.
- DAgger nhẹ nếu có thời gian.
- Chốt `bc_v1` nếu không tệ hơn rule nhiều.

## Tuần 3: Hardening hoặc PPO optional

Đầu tuần 3 quyết định:

```text
Nếu chưa có bản submit rất ổn → hardening
Nếu có bản submit ổn và còn thời gian → thử PPO
```

### Nhánh hardening khuyến nghị

- Benchmark lớn 500–1000 trận.
- Tune scoring cuối.
- Phân tích riêng step500.
- Test agent_id 0–3.
- Profile latency p99.
- Đóng gói submit.
- Chọn version cuối.

### Nhánh PPO optional

- PPO init từ BC.
- Masked logits bằng safe_mask.
- Reward có terminal rank.
- Self-play opponent pool.
- Benchmark checkpoint định kỳ.
- Nếu PPO không vượt rule rõ ràng, bỏ PPO.

## Quy tắc dừng

Dừng làm PPO/MCTS nếu:

```text
rule chưa ổn
benchmark chưa có
self-death còn cao
latency chưa đo
chỉ còn ít ngày
```

Dừng train và sửa safety nếu:

```text
agent tự chết
danger map sai
bomb checker sai
```

## Version nên giữ

Luôn giữ:

```text
rule_v1_safe
rule_v2_best
bc_v1_best nếu có
ppo_best nếu thật sự vượt benchmark
submit_final
```

Không ghi đè version cũ khi chưa benchmark version mới.
