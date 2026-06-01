# Hướng dẫn tiếp theo cho bạn A và bạn B

File này là checklist làm việc sau khi đã có scaffold `agent/team_agent/`. Mục tiêu ngắn hạn là có `rule_v1` chạy ổn định, ít tự chết, biết phá box/nhặt item, và có benchmark rõ ràng trước khi tính đến BC/PPO.

## 0. Nguyên tắc chung

Luồng action bắt buộc:

```text
obs
-> A: parse_obs
-> A: compute_danger_map
-> A: legal_actions / safe_actions
-> B: RulePolicy.choose_action chỉ chọn trong safe_mask
-> A: final_shield
-> return action
```

Không ai được bypass `safe_actions` và `final_shield`.

Quy tắc sửa code:

- A ưu tiên đúng safety trước khi tối ưu.
- B ưu tiên scorer để agent có tiến độ farm/item, nhưng không sửa logic safety nếu chưa thống nhất với A.
- Mỗi task xong phải có ít nhất 1 test hoặc 1 lệnh benchmark nhỏ để chứng minh.
- Không train, không ghi file nặng, không print liên tục trong `act()`.

## 1. Lệnh cần chạy thường xuyên

Chạy smoke test:

```bash
python -m pytest agent/team_agent/smoke_tests
```

Kiểm tra cú pháp:

```bash
python -m compileall agent/team_agent
```

Chạy match nhanh:

```bash
python -m scripts.participant.run_local_match --agent_paths agent/team_agent None None None --num_episodes 5 --visualize false --seed 1
```

Đo latency:

```bash
python -m scripts.participant.estimate_agent_time agent/team_agent --opponents None None None --num_matches 5
```

Benchmark ranking nhỏ:

```bash
python agent/team_agent/bench/benchmark.py --num-matches 20
```

## 2. Bạn A cần làm tiếp theo

Bạn A sở hữu thư mục:

```text
agent/team_agent/person_a_safety/
```

### A1. Làm chắc `parse_obs`

File: `person_a_safety/obs.py`

Cần làm:

- Test `agent_id` 0, 1, 2, 3.
- Test agent đã chết vẫn return `STOP` an toàn.
- Test `bombs` rỗng, 1 bomb, nhiều bomb.
- Test map có wall, box, item radius, item capacity.
- Đảm bảo tọa độ trong code khớp engine: action LEFT/RIGHT thay đổi hàng, UP/DOWN thay đổi cột theo `engine/player.py`.

Output mong đợi:

- Thêm test vào `agent/team_agent/smoke_tests/test_obs.py`.
- `parse_obs` không crash với observation hợp lệ của engine.

Definition of done:

```text
pytest pass
agent_id 0-3 chạy được local match ngắn
```

### A2. Làm đúng danger map

File: `person_a_safety/danger.py`

Cần làm:

- Viết test `blast_cells` cho 4 case:
  - wall chặn blast;
  - box được tính vào blast rồi chặn;
  - item/grass không chặn;
  - radius lấy từ `players[owner_id][4]`, không lấy từ `bombs`.
- Viết test chain reaction:
  - bomb A timer 2 chạm bomb B timer 6 thì B nổ lúc 2;
  - chain 3 bomb liên tiếp;
  - chain bị wall chặn thì không kích nổ.
- Xác nhận `FIRE_DURATION = 1` có khớp engine. Nếu engine thay đổi, sửa ở `constants.py`.

Output mong đợi:

- Thêm `test_danger.py`.
- `compute_danger_map(state)[cell]` trả về thời điểm nổ sớm nhất.

Definition of done:

```text
danger map đúng case 1 bomb, wall, box, radius, chain
không có magic number radius trong code B
```

### A3. Cải thiện BFS thoát bom

File: `person_a_safety/search.py`

Cần làm:

- Test `safe_at(cell, t, danger_time)` cho trước/sau explosion.
- Test corridor:
  - đang đứng trong vùng sắp nổ, có đường thoát;
  - đang đứng trong góc, đặt bom là tự nhốt;
  - cần chờ 1 step rồi mới đi được.
- Kiểm tra `time_expanded_bfs` không coi một ô là safe nếu nó sẽ nổ trước khi agent kịp rời đi.
- Nếu cần, thêm helper `first_escape_action(state, danger_time)`.

Output mong đợi:

- `has_escape_path` đúng cho cả movement và đặt bom.
- B có thể dùng `safe_distances` để tính item/box mà không tự viết BFS riêng.

Definition of done:

```text
agent không đặt bom trong góc không lối thoát
agent biết rời khỏi bomb đang đứng trên đó
```

### A4. Hoàn thiện mask và bomb checker

Files:

```text
person_a_safety/masks.py
person_a_safety/bomb.py
```

Cần làm:

- `legal_actions` đúng luật cơ bản:
  - không đi vào wall/box;
  - không đi vào bomb có sẵn;
  - được rời khỏi ô đang có bomb mình vừa đặt ở step trước;
  - không đặt bomb nếu `bombs_left <= 0`;
  - không đặt bomb nếu ô hiện tại đã có bomb.
- `safe_actions` phải lọc tiếp:
  - không đi vào ô nổ ngay;
  - sau action còn escape path;
  - `PLACE_BOMB` phải qua `can_place_bomb_safely`.
- `can_place_bomb_safely` phải mô phỏng bomb mới, tính lại chain reaction, rồi BFS.

Output mong đợi:

- Thêm `test_masks.py` và `test_bomb_checker.py`.
- `safe_mask[PLACE_BOMB]` chỉ true khi đặt bomb có đường thoát.

Definition of done:

```text
local match 20 trận không crash
self-death vì đặt bomb ngu giảm rõ
```

### A5. Final shield và debug log

File: `person_a_safety/shield.py`

Cần làm:

- `final_shield` override mọi action unsafe.
- `least_bad_action` chọn action chết muộn nhất nếu không còn đường sống chắc.
- Thêm cơ chế debug nhẹ, ví dụ `DebugDecision` hoặc dict optional, nhưng không print mặc định trong `act()`.

Output mong đợi:

- Khi B trả về action sai, shield vẫn giữ agent không crash/không chọn action illegal.

Definition of done:

```text
test: policy cố tình trả về PLACE_BOMB unsafe thì shield override
```

### A6. Feature encoder cho BC/PPO

File: `person_a_safety/features.py`

Cần làm sau khi rule_v1 ổn:

- Chuẩn hóa feature shape cố định `(channels, 13, 13)`.
- Thêm channel danger, safe cells, self, opponents, bombs, boxes, items.
- Không đưa feature cần đọc file hoặc tính quá chậm vào `act()`.

Definition of done:

```text
encode_features chạy được cho mọi agent_id và bombs rỗng/nhiều bombs
```

## 3. Bạn B cần làm tiếp theo

Bạn B sở hữu thư mục:

```text
agent/team_agent/person_b_strategy/
```

### B1. Tạo rule_v0 có mục tiêu rõ

Files:

```text
person_b_strategy/scoring.py
person_b_strategy/policy_rule.py
```

Cần làm:

- Giữ nguyên nguyên tắc: chỉ score action có `safe_mask[action] == True`.
- Tách score thành các thành phần để debug được:
  - survival;
  - box;
  - item;
  - pressure;
  - mobility;
  - loop penalty;
  - useful/useless bomb.
- Nếu cần debug, tạo helper `explain_action_scores(...)` nhưng không gọi/print trong match mặc định.

Output mong đợi:

- Agent không chỉ đứng yên.
- Agent ưu tiên phá box khi an toàn.

Definition of done:

```text
run_local_match 20 trận không crash
có ít nhất vài trận agent đặt bomb phá box
```

### B2. Cải thiện farm scorer

File: `person_b_strategy/scoring.py`

Cần làm:

- Nâng cấp `box_gain(state, cell)`:
  - đếm số box bomb tại `cell` phá được;
  - không tính box sau wall/box đầu tiên;
  - ưu tiên cell có escape nếu đặt bomb tại đó.
- Thêm candidate cell:
  - mọi ô grass/item có `box_gain > 0`;
  - có đường đi an toàn tới đó;
  - đặt bomb tại đó không tự nhốt.
- Score di chuyển tới cell farm:

```text
box_move_score = box_gain / (safe_distance + 1)
```

Cần hỏi A nếu thiếu API:

```python
has_escape_if_bomb_at(state, cell)
safe_distances(state, danger_time)
```

Output mong đợi:

- Early game agent đi tới vị trí phá box thay vì chase enemy.

Definition of done:

```text
boxes destroyed trung bình tăng so với scaffold ban đầu
```

### B3. Cải thiện item collector

File: `person_b_strategy/scoring.py`

Cần làm:

- Ưu tiên item theo tình trạng hiện tại:
  - nếu radius thấp, radius item có giá trị cao;
  - nếu bombs_left/max capacity thấp, capacity item có giá trị cao;
  - không chase item nếu đường đi qua danger gần.
- Nếu có nhiều item, chọn theo:

```text
item_value / (safe_distance + 1)
```

Output mong đợi:

- Agent quay lại nhặt item sau khi phá box nếu an toàn.

Definition of done:

```text
items collected trung bình tăng mà self-death không tăng
```

### B4. Anti-loop và anti-camping

Files:

```text
person_b_strategy/loop_tracker.py
person_b_strategy/policy_rule.py
```

Cần làm:

- Track gần đây:
  - `recent_positions`;
  - `recent_actions`;
  - số step không có tiến độ.
- Phạt:
  - A-B-A-B loop;
  - STOP nhiều;
  - quay lại ô vừa đứng nếu không có lý do safety;
  - đi lòng vòng gần 1 cụm box/item.
- Nếu quá lâu không tiến độ:
  - tăng tạm thời điểm box/item;
  - giảm điểm STOP;
  - đẩy agent tới target farm/item gần nhất.

Output mong đợi:

- Agent bớt đứng yên khi không có bomb nguy hiểm.

Definition of done:

```text
quan sát replay/match thấy agent có tiến độ trong 50 step đầu
```

### B5. Pressure/attack đơn giản

File: `person_b_strategy/scoring.py`

Cần làm sau khi farm/item ổn:

- Chỉ tính pressure khi:
  - action là `PLACE_BOMB`;
  - mình có escape path;
  - opponent nằm trong blast hoặc gần corridor;
  - không hy sinh farm/item quá nhiều.
- Kill/pressure score không được lớn hơn safety penalty.
- Ưu tiên attack late game hơn early game.

Output mong đợi:

- Agent đặt bomb gần enemy khi có lối thoát, nhưng không chase sâu.

Definition of done:

```text
kill/pressure tăng nhẹ, self-death không tăng rõ
```

### B6. Phase behavior và tie-break tracker

Files:

```text
person_b_strategy/policy_rule.py
person_b_strategy/scoring.py
```

Cần làm:

- Early game step 0-150:
  - ưu tiên box/item;
  - attack chỉ khi miễn phí.
- Mid game step 150-350:
  - farm còn lại;
  - pressure có kiểm soát.
- Late game step 350-500:
  - nếu đang có lợi thế proxy thì an toàn hơn;
  - nếu thua proxy thì tăng farm/pressure.
- Track proxy:
  - bomb đã đặt;
  - box biến mất gần explosion của mình;
  - item đã nhặt;
  - opponent chết sau bomb của mình.

Cần hỏi A nếu cần thêm state/log để track chính xác.

Definition of done:

```text
rank step 500 tốt hơn camper/random baseline
```

### B7. BC/PPO chỉ làm sau rule_v1

Files:

```text
train/gen_dataset.py
person_b_strategy/policy_bc.py
person_b_strategy/policy_ppo.py
```

Chỉ bắt đầu khi:

```text
rule_v1 chạy 100+ trận không crash
self-death thấp
latency p99 < 100ms
farm/item tốt hơn baseline scaffold
```

Việc cần làm:

- Dùng `encode_features` của A.
- Sinh dataset từ rule policy.
- Train model nhỏ.
- Inference model chỉ đề xuất action, vẫn qua `safe_mask` và `final_shield`.
- Nếu BC/PPO kém rule trên benchmark, submit rule.

## 4. Thứ tự làm trong 3 ngày tới

### Ngày 1: safety đúng trước

A:

- Hoàn thiện test parse_obs, blast, radius, wall/box.
- Sửa danger map nếu test fail.

B:

- Tách score component để debug.
- Tăng farm scorer cơ bản.

Output cuối ngày:

```text
pytest pass
run_local_match 5-10 trận không crash
```

### Ngày 2: đặt bomb không tự chết

A:

- Test BFS corridor/góc.
- Hoàn thiện `can_place_bomb_safely`.
- Test shield override unsafe action.

B:

- Thêm candidate cell phá box.
- Thêm item collector tốt hơn.
- Giảm loop/STOP.

Output cuối ngày:

```text
agent biết đặt bomb phá box và rời khỏi blast
```

### Ngày 3: benchmark và tune

A:

- Chạy latency.
- Ghi lại seed bị chết ngu để viết test mới.

B:

- Tune weights.
- Thêm pressure score nhẹ.
- So sánh scaffold cũ vs rule_v1.

Output cuối ngày:

```text
benchmark 20-50 trận có bảng số liệu
có danh sách 3 lỗi cần sửa tiếp
```

## 5. Bảng bàn giao API giữa A và B

B được gọi các API này:

```python
state = parse_obs(obs, agent_id)
danger_time = compute_danger_map(state)
legal_mask = legal_actions(state)
safe_mask = safe_actions(state, danger_time)
distances = safe_distances(state, danger_time)
can_bomb = can_place_bomb_safely(state)
action = final_shield(raw_action, state, danger_time)
```

B không nên:

- tự tính danger map riêng;
- tự cho phép action ngoài `safe_mask`;
- đặt bomb chỉ vì score cao mà không qua `can_place_bomb_safely`;
- sửa `constants.py` nếu chưa báo A.

A khi đổi API cần:

- giữ tên hàm cũ nếu có thể;
- nếu đổi return type, cập nhật `agent.py`, code của B, smoke tests;
- thêm test cho case gây đổi API.

## 6. Khi nào được xem là rule_v1

Rule_v1 đạt tiêu chuẩn tối thiểu khi:

```text
python -m pytest agent/team_agent/smoke_tests
python -m scripts.participant.run_local_match --agent_paths agent/team_agent None None None --num_episodes 20 --visualize false
python -m scripts.participant.estimate_agent_time agent/team_agent --opponents None None None --num_matches 5
```

Và kết quả:

- không crash;
- action luôn nằm trong `[0, 5]`;
- self-death vì đặt bomb trong góc hiếm;
- agent phá box/nhặt item thay vì chỉ né;
- p99 latency dưới 100ms;
- code có test cho safety core chính.

## 7. Cách debug khi agent chết ngu

Làm theo thứ tự:

1. Ghi lại command, seed, step agent chết.
2. Xác định chết vì:
   - danger map sai;
   - BFS/safe mask sai;
   - B scorer quá tham;
   - shield không override;
   - engine behavior khác giả định.
3. Viết test nhỏ tại `smoke_tests/` tái hiện case.
4. Sửa module sở hữu lỗi.
5. Chạy lại pytest và match với seed đó.

Nếu chưa rõ lỗi ở A hay B:

```text
Nếu action nằm ngoài safe_mask mà vẫn return -> lỗi shield/A.
Nếu safe_mask cho action nguy hiểm -> lỗi safety/A.
Nếu safe_mask đúng nhưng B liên tục chọn action kém trong safe set -> lỗi scoring/B.
```

## 8. Checklist trước khi submit

- `agent/team_agent/agent.py` load được bằng folder path.
- Không có training code chạy trong `act()`.
- Không có network, file write, print spam trong `act()`.
- Không import package lạ nếu môi trường submit chưa chắc có.
- Match local nhiều seed không crash.
- Timing pass.
- Zip submit chỉ cần file cần thiết nếu dùng submission riêng.
