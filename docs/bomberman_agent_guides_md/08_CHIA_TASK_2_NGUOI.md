# 08 — Chia task cho team 2 người

File này chia việc cho team 2 người theo hướng ít xung đột, dễ review, có output rõ mỗi ngày.

## 1. Vai trò đề xuất

### Người A — Safety/Engine/Benchmark Lead

Phụ trách:

```text
parse obs
danger map
chain reaction
BFS escape
legal/safe mask
bomb checker
final shield
benchmark
debug replay
submit hardening
```

Người A chịu trách nhiệm chính cho câu hỏi: **agent có chết ngu không?**

### Người B — Strategy/Scoring/ML Lead

Phụ trách:

```text
farm scorer
item collector
attack/pressure scorer
anti-loop
rule policy
Behavior Cloning
PPO optional
opponent pool
metric analysis
```

Người B chịu trách nhiệm chính cho câu hỏi: **agent có chủ động và rank cao không?**

## 2. Nguyên tắc phối hợp

Không ai được bypass safety core.

Mọi policy của Người B phải đi qua:

```text
safe_mask
final_shield
```

Người A cần cung cấp API ổn định:

```python
parse_obs(obs, agent_id)
compute_danger_map(state)
legal_actions(state)
safe_actions(state)
can_place_bomb_safely(state)
final_shield(action, state)
```

## 3. Tuần 1 — Rule safety + farm

### Ngày 1

Người A:

- setup repo;
- viết `constants.py`;
- viết `parse_obs`;
- dump obs vài step;
- test agent_id 0–3.

Người B:

- đọc luật game;
- viết skeleton `scoring.py`;
- ghi ý tưởng farm/item/attack;
- viết dummy random/safe policy nếu cần.

Output: chạy được 1 trận local, parse obs không lỗi.

### Ngày 2

Người A:

- viết `blast_cells`;
- lấy radius từ owner_id;
- viết danger map cơ bản;
- test wall/box/radius.

Người B:

- viết `box_gain(cell)`;
- tìm candidate cell phá box;
- tạo camper/farmer dummy opponent nếu có thể.

Output: danger map đúng case 1 bom, box_gain chạy được.

### Ngày 3

Người A:

- thêm chain reaction;
- test 2–3 bom chain;
- xác minh fire duration.

Người B:

- viết item target logic;
- viết distance helper;
- bắt đầu scoring v1.

Output: danger map có chain, item/box scoring prototype.

### Ngày 4

Người A:

- viết time-expanded BFS;
- viết `safe_at`;
- trả path escape;
- test corridor/góc.

Người B:

- tích hợp scoring với safe path;
- viết anti-loop đơn giản;
- chuẩn bị metric list.

Output: agent chạy thoát bom đơn giản.

### Ngày 5

Người A:

- legal mask;
- safe mask;
- bomb placement checker;
- final shield.

Người B:

- rule policy v1;
- tích hợp farm/item/anti-loop;
- đảm bảo không chọn action ngoài safe mask.

Output: rule_v0 chạy nhiều trận không crash.

### Ngày 6

Người A:

- debug self-death;
- log reason override;
- profile latency sơ bộ.

Người B:

- thêm pressure/attack scorer;
- tune trọng số;
- thêm logic late game chủ động hơn.

Output: rule_v1 biết farm, nhặt item, ít loop.

### Ngày 7

Người A:

- viết `benchmark.py`;
- metric safety/latency;
- chạy 200+ trận.

Người B:

- phân tích replay lỗi;
- tune scoring;
- viết bảng so sánh version.

Output cuối Tuần 1: `rule_v1` submit được.

Nếu chưa đạt, không sang BC/PPO. Cả hai cùng sửa safety/scoring.

## 4. Tuần 2 — Rule_v2 hoặc BC

Đầu Tuần 2 quyết định:

```text
Nếu rule_v1 còn yếu → rule_v2
Nếu rule_v1 ổn → BC
```

### Nhánh Rule_v2

Người A:

- tăng test danger/bomb checker;
- cải thiện benchmark;
- debug death case;
- tối ưu latency.

Người B:

- tune farm/item/attack;
- thêm pressure score;
- thêm tie-break tracker;
- thêm behavior early/mid/late.

Output: rule_v2 mạnh hơn rule_v1.

### Nhánh BC

Người A:

- viết `encode(obs)`;
- đảm bảo feature có danger/safe info;
- hỗ trợ sinh dataset.

Người B:

- viết `gen_dataset.py`;
- train model nhỏ;
- benchmark BC+shield.

Output: bc_v1 chạy được, không tệ hơn rule quá nhiều.

## 5. Tuần 3 — Hardening hoặc PPO optional

Nếu chưa có bản submit rất ổn: hardening.

Nếu rule/BC tốt và còn thời gian: thử PPO.

### Hardening

Người A:

- benchmark 500–1000 trận;
- analyze_step500;
- submit checklist;
- package zip.

Người B:

- tune final scorer;
- chọn version;
- sửa anti-camping/tie-break;
- viết notes chiến thuật.

### PPO optional

Người A:

- rollout/benchmark/eval cố định;
- đảm bảo mask/shield trong train và inference;
- profile latency.

Người B:

- train PPO init từ BC;
- thiết kế reward;
- self-play opponent pool;
- chọn checkpoint.

Nếu PPO không vượt rule rõ ràng, submit rule/BC ổn nhất.

## 6. Quy tắc khi conflict

- Safety thắng attack.
- Benchmark rank thắng train reward.
- Version đơn giản thắng version phức tạp nếu metric gần nhau.
- Nếu một module chưa có test, chưa xem là xong.
