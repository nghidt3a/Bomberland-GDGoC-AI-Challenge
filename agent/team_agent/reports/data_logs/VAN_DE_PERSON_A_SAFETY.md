# Vấn Đề Person A Safety

Báo cáo này tách 2 loại bằng chứng:

- Death classification là heuristic từ log: xem bomb timer/blast line quanh death step.
- Current-code replay check chạy lại `parse_obs`, `compute_danger_map`, `safe_actions`, `final_shield` trên code hiện tại; nó không đảm bảo giống 100% bản đã submit.

## Tổng Hợp Safety

| seed | death class | death step | last alive pos | checked | unsafe replay | shield changes |
| --- | --- | --- | --- | --- | --- | --- |
| 109659 | own_bomb_escape_failure | 92 | [11, 8] | 92 | 5 | 0 |
| 548846 | survived | - | [3, 2] | 500 | 0 | 0 |
| 156663 | survived | - | [11, 5] | 500 | 0 | 0 |
| 83824 | survived | - | [5, 7] | 500 | 0 | 0 |
| 290518 | own_bomb_escape_failure | 327 | [7, 4] | 327 | 5 | 0 |
| 548409 | survived | - | [10, 10] | 500 | 0 | 0 |
| 225587 | own_bomb_escape_failure | 223 | [3, 4] | 223 | 4 | 0 |
| 836037 | enemy_bomb_trap | 63 | [4, 1] | 63 | 6 | 0 |
| 585440 | own_bomb_escape_failure | 417 | [3, 9] | 417 | 1 | 0 |
| 648293 | own_bomb_escape_failure | 132 | [7, 6] | 132 | 1 | 0 |
| 126779 | survived | - | [11, 10] | 500 | 0 | 0 |
| 609286 | survived | - | [9, 3] | 500 | 0 | 0 |

## Case Cần Ưu Tiên

### Seed 109659 - own_bomb_escape_failure

- File: `match_20260601_094346_109659.json`
- Player index: 3
- Death step: 92
- Reason: Chết trong blast line của bom mình gần thời điểm nổ.
- Exploding bombs: `[{"pos": [11, 9], "timer": 1, "owner": 3, "radius": 2}, {"pos": [11, 7], "timer": 2, "owner": 1, "radius": 2}]`
- Current replay unsafe actions: 5/92
- Current replay shield changes: 0

Replay examples:
- step 88, pos [11, 8], action STOP, safe=[], shielded=STOP
- step 89, pos [11, 8], action STOP, safe=[], shielded=STOP
- step 90, pos [11, 8], action STOP, safe=[], shielded=STOP
- step 91, pos [11, 8], action STOP, safe=[], shielded=STOP
- step 92, pos [11, 8], action STOP, safe=[], shielded=STOP

### Seed 290518 - own_bomb_escape_failure

- File: `match_20260601_094357_290518.json`
- Player index: 3
- Death step: 327
- Reason: Chết trong blast line của bom mình gần thời điểm nổ.
- Exploding bombs: `[{"pos": [7, 5], "timer": 1, "owner": 3, "radius": 3}, {"pos": [7, 3], "timer": 2, "owner": 0, "radius": 2}]`
- Current replay unsafe actions: 5/327
- Current replay shield changes: 0

Replay examples:
- step 323, pos [7, 4], action STOP, safe=[], shielded=STOP
- step 324, pos [7, 4], action STOP, safe=[], shielded=STOP
- step 325, pos [7, 4], action STOP, safe=[], shielded=STOP
- step 326, pos [7, 4], action STOP, safe=[], shielded=STOP
- step 327, pos [7, 4], action STOP, safe=[], shielded=STOP

### Seed 225587 - own_bomb_escape_failure

- File: `match_20260601_094452_225587.json`
- Player index: 3
- Death step: 223
- Reason: Chết trong blast line của bom mình gần thời điểm nổ.
- Exploding bombs: `[{"pos": [3, 6], "timer": 1, "owner": 0, "radius": 3}, {"pos": [3, 3], "timer": 2, "owner": 3, "radius": 3}, {"pos": [3, 5], "timer": 3, "owner": 0, "radius": 3}]`
- Current replay unsafe actions: 4/223
- Current replay shield changes: 0

Replay examples:
- step 220, pos [3, 4], action STOP, safe=[], shielded=STOP
- step 221, pos [3, 4], action STOP, safe=[], shielded=STOP
- step 222, pos [3, 4], action STOP, safe=[], shielded=STOP
- step 223, pos [3, 4], action STOP, safe=[], shielded=STOP

### Seed 836037 - enemy_bomb_trap

- File: `match_20260601_094453_836037.json`
- Player index: 0
- Death step: 63
- Reason: Chết trong blast line của bom đối thủ gần thời điểm nổ.
- Exploding bombs: `[{"pos": [3, 1], "timer": 1, "owner": 1, "radius": 2}]`
- Current replay unsafe actions: 6/63
- Current replay shield changes: 0

Replay examples:
- step 58, pos [5, 1], action LEFT, safe=[], shielded=LEFT
- step 59, pos [4, 1], action RIGHT, safe=[], shielded=RIGHT
- step 60, pos [5, 1], action LEFT, safe=[], shielded=LEFT
- step 61, pos [4, 1], action RIGHT, safe=[], shielded=RIGHT
- step 62, pos [5, 1], action LEFT, safe=[], shielded=LEFT

### Seed 585440 - own_bomb_escape_failure

- File: `match_20260601_094457_585440.json`
- Player index: 1
- Death step: 417
- Reason: Chết trong blast line của bom mình gần thời điểm nổ.
- Exploding bombs: `[{"pos": [1, 10], "timer": 1, "owner": 1, "radius": 4}]`
- Current replay unsafe actions: 1/417
- Current replay shield changes: 0

Replay examples:
- step 417, pos [3, 9], action DOWN, safe=[], shielded=DOWN

### Seed 648293 - own_bomb_escape_failure

- File: `match_20260601_094501_648293.json`
- Player index: 3
- Death step: 132
- Reason: Chết trong blast line của bom mình gần thời điểm nổ.
- Exploding bombs: `[{"pos": [7, 7], "timer": 1, "owner": 3, "radius": 3}]`
- Current replay unsafe actions: 1/132
- Current replay shield changes: 0

Replay examples:
- step 132, pos [7, 6], action UP, safe=[], shielded=UP

## Đề Xuất Cho A

- Thêm regression test từ các seed có `own_bomb_escape_failure` và `enemy_bomb_trap`.
- Khi current replay flag nhiều unsafe action, cần replay bằng obs step trước action để xem `safe_actions` có quá chặt hay submit policy cũ đã khác code hiện tại.
- Audit các case STOP liên tiếp trong blast line timer <= 2: final shield nên ưu tiên first escape action thay vì cho STOP nếu còn move hợp lệ.
