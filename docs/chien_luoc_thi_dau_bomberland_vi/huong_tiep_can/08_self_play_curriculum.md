# Self-play curriculum

Self-play giúp agent không chỉ học thắng một baseline cố định. Curriculum giúp quá trình này không quá hỗn loạn.

## Mục tiêu

Train agent qua các mức đối thủ:

1. Dễ để học luật sống còn.
2. Trung bình để học farm.
3. Mạnh để học né/tấn công.
4. Snapshot của chính mình để chống bị bắt bài.

## Pool ban đầu

Pool gợi ý:

```text
[
  RandomAgent,
  SimpleRuleAgent,
  BoxFarmerAgent,
  SmarterRuleAgent,
  TacticalRuleAgent,
  GeniusRuleAgent,
  best_rule_agent_v1,
]
```

Sau mỗi mốc, thêm snapshot:

```text
policy_ep_1000
policy_ep_3000
policy_ep_5000
best_current
```

## Sampling đối thủ

Gợi ý:

| Loại đối thủ | Xác suất |
|---|---:|
| Baseline yếu/trung bình | 20% |
| Baseline mạnh | 30% |
| Snapshot cũ | 30% |
| Best current/self-play mới | 20% |

Điều chỉnh nếu agent học quá chậm hoặc overfit.

## Trận 4 agent

Lineup gợi ý:

- `[main, baseline, baseline, snapshot]`
- `[main, snapshot_old, tactical, smarter]`
- `[main, main_snapshot, random, genius]`
- `[main, policy_copy_1, policy_copy_2, baseline]`

Randomize vị trí để giảm bias góc spawn.

## Chọn snapshot thêm vào pool

Không thêm mọi checkpoint. Thêm khi:

- Win rate vượt mốc.
- Average rank tốt.
- Lối chơi khác đáng kể.
- Không timeout.

Pool quá lớn làm train chậm và khó kiểm soát. Giữ khoảng 5-20 snapshot là đủ.

## Tránh overfit self-play

Test định kỳ với:

- Baseline không có trong train gần đây.
- Seed cố định.
- Bản rule agent cũ.
- Bản submission tốt nhất.

Nếu self-play win rate tăng nhưng thua baseline, policy đang lệch.

## Kết hợp với rule safety

Self-play vẫn cần safety layer. Nếu không, agent có thể học chiến thuật đánh đổi mạng làm reward ngắn hạn tốt nhưng rank thật xấu.

## Khi nên dùng

Dùng self-play khi đã có:

- Agent không tự sát thường xuyên.
- Reward ổn.
- Pipeline train/test tự động.
- Tài nguyên cloud.

Không dùng self-play để "cứu" agent chưa biết né bom.

