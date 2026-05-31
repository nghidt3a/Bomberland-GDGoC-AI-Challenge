# Thiết kế experiment và log

Không có log thì không biết agent thật sự tốt hơn hay chỉ may mắn. Mỗi lần thay đổi chiến thuật, reward hoặc checkpoint cần ghi lại.

## Tên experiment

Đặt tên có cấu trúc:

```text
YYYYMMDD_algo_opponent_seed_note
```

Ví dụ:

```text
20260601_dqn_tactical_seed86_reward_v2
20260601_hybrid_rule_escape_v5
20260602_bc_dagger_round2
```

## Thông tin cần lưu

- Code version hoặc commit.
- Agent type.
- Reward version.
- Feature version.
- Opponent pool.
- Seed list.
- Số episode train.
- Checkpoint path.
- Win rate.
- Draw rate.
- Average rank.
- Survival steps.
- Timeout/max inference time.
- Ghi chú hành vi.

## Bảng log mẫu

| Version | Opponent | Matches | Win | Draw | Avg rank | Avg step | Time avg/max | Ghi chú |
|---|---|---:|---:|---:|---:|---:|---|---|
| hybrid_v1 | mixed | 100 | 25% | 18% | 1.4 | 310 | 3/12ms | tự sát ít |
| dqn_v3 | tactical | 100 | 18% | 20% | 1.7 | 280 | 8/35ms | bỏ item |

## Seed

Dùng cả seed cố định và random:

```text
fixed_seeds = [0, 1, 2, 3, 4, 10, 20, 42, 86, 123]
```

Seed cố định giúp so regression. Seed random giúp tránh overfit.

## Opponent pool

Không chỉ test một đối thủ. Gợi ý pool:

```text
[
  RandomAgent,
  SimpleRuleAgent,
  BoxFarmerAgent,
  SmarterRuleAgent,
  TacticalRuleAgent,
  GeniusRuleAgent,
  old_best_agent
]
```

## Quy tắc chọn version tốt hơn

Một version được coi là tốt hơn nếu:

- Win/rank tốt hơn trên cùng seed.
- Không tăng timeout.
- Không tăng self-kill.
- Không chỉ thắng một baseline nhưng thua nhiều baseline khác.

Nếu chỉ tốt hơn 1-2 trận, chưa đủ kết luận.

## Log replay hành vi

Khi agent thua kỳ lạ, ghi:

- Step chết.
- Lý do chết: bomb của ai, timer bao nhiêu.
- Action trước khi chết.
- Có escape không.
- Vì sao policy chọn sai.

Các ghi chú này giúp sửa rule/reward nhanh hơn chỉ nhìn score.

