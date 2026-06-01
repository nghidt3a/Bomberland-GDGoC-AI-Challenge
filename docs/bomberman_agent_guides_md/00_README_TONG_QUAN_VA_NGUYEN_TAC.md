# 00 — README: Tổng quan và nguyên tắc triển khai agent Bomberland

Bộ tài liệu này hướng dẫn team triển khai agent cho cuộc thi Bomberland/Bomberman-like theo hướng **thực dụng, an toàn, dễ debug**, phù hợp với bối cảnh: grid 13×13, 4 agent FFA, action rời rạc, CPU-only, khoảng 100ms cho mỗi `act()`, không network và không train trong lúc chấm.

## 1. Hướng làm chính

Hướng nên chọn:

```text
Rule-based safety core
→ Hybrid farm/item/attack heuristic
→ Benchmark nhiều seed
→ Behavior Cloning nếu còn thời gian
→ PPO/self-play chỉ là optional
```

Không nên bắt đầu bằng RL thuần. Trong game kiểu Bomberman, random exploration rất dễ tạo dữ liệu xấu: đặt bom rồi tự chết, không tính chain reaction, đi vào ô sắp nổ, hoặc học camping để sống lâu nhưng thua tie-break.

Nguyên tắc quan trọng nhất:

```text
Safety là xương sống. ML/RL chỉ được đề xuất action, không được phá safety.
```

## 2. Tie-break mới thay đổi chiến thuật ra sao?

Nếu trận kết thúc ở step 500 và còn nhiều agent sống, thứ hạng xét theo:

1. Kills
2. Boxes Destroyed
3. Items Collected
4. Bombs Placed

Vì vậy agent không thể chỉ né tránh và sống lâu. Agent cần:

- phá box đều;
- nhặt item;
- đặt bom có mục tiêu;
- tìm kill khi rủi ro rất thấp;
- vẫn tránh self-kill/self-trap tuyệt đối.

Thứ tự ưu tiên hành vi nên là:

```text
Không chết sớm
→ Không tự sát
→ Farm box/item
→ Tạo pressure/kill cơ hội
→ Đặt bom hữu ích
→ Không spam bomb
```

## 3. Module bắt buộc

Các module sau là bắt buộc và nên được giữ ổn định xuyên suốt mọi phiên bản:

```text
parse_obs
compute_danger_map
compute_chain_reaction
time_expanded_bfs
legal_action_mask
safe_action_mask
can_place_bomb_safely
final_safety_shield
least_bad_fallback
benchmark_harness
```

Dù dùng rule, BC hay PPO, action cuối vẫn phải đi qua:

```text
final_safety_shield(action, state)
```

## 4. Các điểm kỹ thuật dễ sai

### 4.1. Bomb radius không nằm trực tiếp trong `bombs`

Theo observation của cuộc thi:

```text
players[i] = [row, col, alive, bombs_left, bomb_radius_bonus]
bombs[k]   = [row, col, timer, owner_id]
```

Vì vậy:

```python
radius = 1 + players[owner_id][4]
```

Nếu lấy radius sai, danger map sai và agent sẽ tự chết ở các case đối thủ có radius lớn.

### 4.2. Fire duration cần khớp engine

Tài liệu nói vụ nổ kéo dài 1 step. Nên đặt mặc định:

```python
FIRE_DURATION = 1
```

Sau đó test bằng replay/render để xác nhận có bị lệch 1 step không.

### 4.3. PPO không phải mục tiêu bắt buộc

PPO chỉ nên làm khi rule safety + benchmark + BC đã ổn. Nếu PPO không vượt rule rõ ràng trên benchmark, submit rule/hybrid ổn định hơn.

## 5. Roadmap ngắn

### Nếu còn 3–7 ngày

Chỉ làm:

1. Safety core.
2. Farming/item collector.
3. Anti-loop/anti-camping.
4. Attack cơ hội đơn giản.
5. Benchmark + hardening submit.

### Nếu còn 2 tuần

Làm thêm:

1. Behavior Cloning từ rule agent.
2. Rule_v2 tuning từ replay lỗi.
3. Benchmark riêng step 500 tie-break.

### Nếu còn 3+ tuần

Thử thêm:

1. Masked PPO init từ BC.
2. Self-play opponent pool.
3. Shallow lookahead rất nông nếu latency cho phép.

## 6. Tiêu chí đủ tốt để submit

Agent đủ tốt khi:

- self-death rất thấp;
- death-before-step-100 thấp;
- average rank tốt;
- top-2 rate cao;
- thắng hoặc không thua camper ở tie-break step 500;
- boxes/items ổn;
- useful bomb ratio cao;
- `act()` p99 dưới 100ms;
- không crash trên nhiều seed và đủ 4 `agent_id`.

## 7. Dấu hiệu sai hướng

Cần dừng lại sửa nếu thấy:

- agent tự chết sau khi đặt bom;
- danger map sai chain reaction;
- agent sống tới 500 nhưng rank thấp do farm kém;
- bomb placed cao nhưng useful bomb thấp;
- PPO reward tăng nhưng rank giảm;
- latency p99 gần/vượt 100ms;
- model chọn action unsafe và shield phải override quá nhiều.
