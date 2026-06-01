# 04 — Benchmark, debug replay và chọn version

Một trận thắng đẹp không đủ chứng minh agent mạnh. Cần benchmark nhiều seed, nhiều đối thủ và đo đúng metric.

## 1. Mục tiêu benchmark

Benchmark cần trả lời:

1. Agent có tự sát không?
2. Agent có chết sớm không?
3. Agent có farm box/item tốt không?
4. Agent có thắng tie-break step 500 không?
5. Agent có mạnh trước camper/farmer/aggressive không?
6. `act()` có vượt 100ms không?
7. Version mới có thật sự tốt hơn version cũ không?

## 2. Metric bắt buộc

### Kết quả trận

| Metric | Ý nghĩa |
|---|---|
| `average_rank` | Thứ hạng trung bình |
| `win_rate` | Tỉ lệ hạng 1 |
| `top2_rate` | Tỉ lệ vào top 2 |
| `survival_to_500_rate` | Sống tới step 500 |
| `death_before_50/100/200` | Chết sớm |
| `self_death_rate` | Chết do bom/self-trap |

### Tie-break/activity

| Metric | Ý nghĩa |
|---|---|
| `kills_per_game` | Kill trung bình |
| `boxes_destroyed_per_game` | Farm box |
| `items_collected_per_game` | Nhặt item |
| `bombs_placed_per_game` | Hoạt động đặt bom |
| `useful_bomb_ratio` | Bom hữu ích/tổng bom |
| `useless_bomb_ratio` | Bom vô ích/tổng bom |
| `step500_tiebreak_rank` | Rank riêng trong trận step 500 |
| `step500_tiebreak_win_rate` | Tỉ lệ thắng tie-break step 500 |

### Latency

| Metric | Mục tiêu |
|---|---|
| `act_mean_ms` | < 10ms |
| `act_p95_ms` | < 50ms |
| `act_p99_ms` | < 100ms |
| `act_max_ms` | càng thấp càng tốt |

## 3. Nhóm đối thủ cần benchmark

Không chỉ đánh với random. Cần có:

- `random_agent`: kiểm tra cơ bản;
- `camper_agent`: test tie-break mới;
- `farmer_agent`: cạnh tranh box/item;
- `aggressive_agent`: test khả năng né/escape;
- baseline BTC nếu có;
- rule_v1/rule_v2 của mình;
- BC/PPO checkpoint cũ;
- mixed pool random 3 đối thủ.

Nếu agent chỉ thắng random nhưng thua camper/aggressive, chưa đủ ổn.

## 4. Số trận khuyến nghị

| Mốc | Số trận |
|---|---:|
| Test nhanh sau thay đổi nhỏ | 20–50 |
| Cuối ngày | 100–200 |
| Chốt rule_v1 | 300+ |
| Chọn version submit | 500–1000 nếu có thời gian |

FFA có phương sai cao. Dưới 100 trận dễ kết luận sai.

## 5. Seed cố định và seed random

Dùng 2 bộ:

```text
fixed_seeds: so sánh công bằng giữa version
random_seeds: kiểm tra khái quát
```

Không tune quá mức theo fixed seeds để tránh overfit.

## 6. Phân tích riêng step 500

Tie-break mới chỉ kích hoạt khi trận kết thúc ở step 500 và nhiều agent sống. Cần script `analyze_step500.py`:

```text
lọc trận kết thúc step 500
đếm agent sống
so kills/boxes/items/bombs
xác định rank tie-break của agent mình
```

Nếu agent sống tới 500 nhiều nhưng step500 rank thấp, nghĩa là agent đang camping hoặc farm kém.

## 7. Log cần lưu để debug

Mỗi step nên lưu:

```python
{
  "step": step,
  "pos": self_pos,
  "raw_action": raw_action,
  "final_action": final_action,
  "override_reason": reason,
  "legal_mask": legal_mask,
  "safe_mask": safe_mask,
  "danger_at_self": danger_at_self,
  "nearest_bomb": nearest_bomb,
  "can_place_bomb": can_place_bomb,
  "latency_ms": latency,
}
```

Death reason nên phân loại:

```text
enemy_bomb
own_bomb
chain_reaction
self_trap_after_bomb
walked_into_danger
no_escape_available
timeout_STOP
unknown
```

`unknown` càng ít càng tốt.

## 8. Chọn version

Tạo bảng:

| Version | Avg Rank | Win | Top2 | Self-death | Box | Item | Kill | Step500 Rank | p99 ms | Chọn? |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|

Quy tắc:

1. Loại version crash/timeout.
2. Loại version self-death cao.
3. Loại version p99 sát/vượt 100ms.
4. Trong các version còn lại, chọn average rank tốt nhất.
5. Nếu rank gần nhau, chọn step500 tie-break tốt hơn.
6. Nếu vẫn gần nhau, chọn version đơn giản hơn.

## 9. Dấu hiệu sai hướng

| Dấu hiệu | Nguyên nhân có thể | Cách xử lý |
|---|---|---|
| Self-death tăng | danger/BFS/bomb checker sai | dừng train, sửa safety |
| Sống lâu rank thấp | camping, farm kém | tăng farm/item, anti-loop |
| Boxes cao item thấp | không quay lại nhặt item | thêm item collector |
| Bombs cao useful thấp | spam bom | phạt useless bomb |
| Kills luôn 0 | attack quá nhát | thêm pressure score |
| Train reward tăng rank giảm | reward hacking | tin benchmark, sửa reward |
| p99 latency cao | model/search/log nặng | profile, giảm/tắt module |

## 10. Câu hỏi cuối mỗi ngày

- Version nào tốt nhất hôm nay?
- Agent chết vì gì nhiều nhất?
- Self-death có tăng không?
- Boxes/items/kills có cải thiện không?
- Agent có thắng camper ở step500 tie-break không?
- Latency có ổn không?
- Ngày mai sửa gì trước?
