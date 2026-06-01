# 10 — Prompt đưa AI khác review/debug code agent

Có thể copy các prompt này đưa cho AI khác khi cần review kế hoạch, code hoặc replay lỗi.

## 1. Prompt review tổng thể

```text
Bạn là senior ML/RL engineer và game AI engineer có kinh nghiệm với Bomberman/Pommerman-like multi-agent grid game.

Mình đang xây agent cho cuộc thi Bomberland/Bomberman-like. Bối cảnh:
- Grid 13×13.
- 4 agent FFA.
- Action: 0 STOP, 1 LEFT, 2 RIGHT, 3 UP, 4 DOWN, 5 PLACE_BOMB.
- act() phải chạy khoảng dưới 100ms CPU-only.
- Không network, không train khi chấm.
- Tie-break step 500: Kills > Boxes Destroyed > Items Collected > Bombs Placed.

Mình dùng hướng: rule-based safety core + hybrid scoring farm/item/attack + final safety shield. ML/RL nếu có chỉ là optional.

Hãy review code/thiết kế/log theo các tiêu chí:
1. parse observation có sai không?
2. Bomb radius có lấy đúng từ owner_id không?
3. Danger map có tính wall, box, chain reaction đúng không?
4. Fire duration có thể bị lệch step không?
5. Time-expanded BFS có xét thời gian đúng không?
6. Legal action mask có xử lý đúng việc đi ra khỏi bom không?
7. can_place_bomb_safely có mô phỏng thêm bom mới đúng không?
8. Final shield có thể bị bypass không?
9. Scoring farm/item/attack có làm agent quá tham hoặc quá nhát không?
10. Có rủi ro self-trap/self-kill không?
11. Có rủi ro camping/stalling sau tie-break mới không?
12. Có vấn đề latency không?
13. Metric/benchmark nào còn thiếu?

Trả lời theo format:
- Lỗi nghiêm trọng cần sửa ngay.
- Lỗi logic có thể gây self-death.
- Điểm làm agent yếu về tie-break.
- Điểm có thể gây timeout.
- Gợi ý sửa cụ thể.
- Unit test nên thêm.
- Pseudo-code sửa nếu cần.
```

## 2. Prompt debug self-death

```text
Mình có replay agent tự chết trong Bomberland. Hãy phân tích nguyên nhân.

Thông tin game:
- Grid 13×13.
- Bomb nổ theo 4 hướng, wall chặn, box chặn và bị phá, có chain reaction.
- bombs trong obs: [row, col, timer, owner_id].
- radius bomb = 1 + players[owner_id][bomb_radius_bonus].
- action space: STOP, LEFT, RIGHT, UP, DOWN, PLACE_BOMB.

Mình sẽ đưa log các step trước khi chết, gồm:
- position
- bombs
- map
- action model chọn
- action sau shield
- legal/safe mask
- danger map nếu có
- can_place_bomb_safely nếu có

Hãy xác định:
1. Agent chết do own bomb, enemy bomb, chain reaction, self-trap, walked into danger hay timeout?
2. Danger map có dự đoán đúng ô chết không?
3. Nếu danger map đúng, vì sao safe mask/shield vẫn cho action đó?
4. Nếu danger map sai, lỗi có thể nằm ở wall/box/radius/chain/fire duration/timer lệch step nào?
5. Sửa code nên bắt đầu từ đâu?
6. Unit test cụ thể để tái hiện bug.
```

## 3. Prompt review reward PPO

```text
Mình đang train PPO masked cho agent Bomberland. Hãy review reward shaping sau.

Bối cảnh:
- 4 agent FFA.
- Tie-break step 500: Kills > Boxes Destroyed > Items Collected > Bombs Placed.
- Mục tiêu: rank cao, tự sát thấp, farm tốt, kill cơ hội.
- Policy vẫn qua action mask và final shield.

Reward hiện tại:
[PASTE REWARD]

Metric benchmark:
[PASTE METRICS]

Hãy chỉ ra:
1. Reward có khuyến khích camping không?
2. Reward có khuyến khích spam bom không?
3. Reward có làm agent quá hung hăng không?
4. Reward có phản ánh đúng tie-break không?
5. Có cần terminal rank reward không?
6. Nên chỉnh hệ số thế nào?
7. Metric nào chứng minh reward đang bị hacking?
8. Nếu train reward tăng nhưng average rank giảm thì xử lý gì?
```

## 4. Prompt chọn version submit

```text
Mình có bảng benchmark các version agent Bomberland. Hãy giúp chọn version nên submit.

Luật:
- act() CPU-only dưới 100ms.
- Tie-break step 500: Kills > Boxes Destroyed > Items Collected > Bombs Placed.

Bảng metric:
[PASTE TABLE]

Hãy chọn version theo tiêu chí:
1. Không crash.
2. p99 latency an toàn.
3. self-death thấp.
4. average rank tốt.
5. top-2 rate cao.
6. step500 tie-break tốt.
7. farm/item/kills ổn.
8. code đơn giản ít rủi ro nếu metric gần nhau.

Giải thích vì sao chọn và vì sao loại các version còn lại.
```

## 5. Prompt nhờ viết unit test

```text
Hãy viết unit test cho safety core của agent Bomberland.

Module cần test:
- blast_cells
- compute_danger_map
- chain reaction
- time_expanded_bfs
- legal_actions
- safe_actions
- can_place_bomb_safely
- final_shield

Luật:
- Grid 13×13.
- map: 0 grass, 1 wall, 2 box, 3 item radius, 4 item capacity.
- bombs: [row, col, timer, owner_id].
- players: [row, col, alive, bombs_left, bomb_radius_bonus].
- radius bomb = 1 + players[owner_id][4].
- wall chặn blast.
- box bị phá và chặn blast.
- chain reaction làm bomb khác nổ cùng step.

Hãy tạo test case cụ thể với expected output rõ ràng, ưu tiên lỗi self-kill thường gặp.
```
