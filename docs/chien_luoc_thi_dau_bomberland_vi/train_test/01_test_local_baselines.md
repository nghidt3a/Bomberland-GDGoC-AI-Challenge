# Test local với baseline

Local test giúp phát hiện lỗi interface, lỗi hành vi và timeout trước khi nộp. Không dùng kết quả local như leaderboard thật, nhưng dùng để so sánh các version.

Nếu cần hướng dẫn chi tiết cách chọn đúng 4 agent và mở viewer PyGame để xem trận đấu, đọc thêm [09_huong_dan_test_4_agents_va_visualize.md](09_huong_dan_test_4_agents_va_visualize.md).

## Chạy match headless

```bash
python -m scripts.participant.run_local_match --agent_paths path/to/agent None None None --num_episodes 20 --visualize false
```

`None` sẽ random baseline trong repo.

## Chạy với baseline cụ thể

```bash
python -m scripts.participant.run_local_match --agent_paths path/to/agent TacticalRuleAgent SmarterRuleAgent GeniusRuleAgent --num_episodes 20 --visualize false
```

Baseline có thể dùng:

- `RandomAgent`
- `SimpleRuleAgent`
- `BoxFarmerAgent`
- `SmarterRuleAgent`
- `TacticalRuleAgent`
- `GeniusRuleAgent`

## Visualize để debug

```bash
python -m scripts.participant.run_local_match --agent_paths path/to/agent TacticalRuleAgent SmarterRuleAgent GeniusRuleAgent --num_episodes 3 --visualize true
```

Chỉ dùng visualize cho vài trận vì chậm. Dùng để xem:

- Agent chết vì bom nào.
- Có bỏ item không.
- Có đặt bom tự kẹt không.
- Có đứng yên vô lý không.

## Estimate ranking

```bash
python -m scripts.participant.estimate_rankings --agent_path path/to/agent --num_matches 100
```

Script này chơi với các baseline mạnh và tính estimated TrueSkill local. Dùng để so sánh giữa checkpoint/version.

## Benchmark thời gian

```bash
python -m scripts.participant.estimate_agent_time path/to/agent --opponents TacticalRuleAgent SmarterRuleAgent GeniusRuleAgent --num_matches 10
```

Mục tiêu:

- Average thấp hơn 100ms rõ rệt.
- Max spike không vượt 100ms.
- Không lỗi trong nhiều trận.

## Ma trận test gợi ý

| Test | Mục tiêu |
|---|---|
| vs Random/Simple | Agent không chết ngu |
| vs BoxFarmer | Cạnh tranh item/farm |
| vs Tactical/Smarter | Né/tấn công ổn |
| vs Genius | Kiểm tra pressure |
| vs bản cũ | Không regression |
| random baseline mix | Gần match thật hơn |

## Số trận tối thiểu

Trước khi nộp:

- 20 trận smoke test.
- 100 trận estimate ranking.
- 10 trận benchmark time.
- 3-5 trận visualize nếu có hành vi lạ.

Trước bản cuối:

- 300-1000 trận nếu có thời gian/cloud.
- Nhiều seed cố định và random.
