# Self-play training loop

Self-play cần vòng lặp rõ để tránh train hỗn loạn. Tài liệu này mô tả logic triển khai, không yêu cầu chạy ngay.

## Vòng lặp tổng quát

```text
initialize main policy
initialize opponent pool
for iteration:
    sample opponents from pool
    run matches
    collect transitions/rollouts
    update policy
    evaluate policy
    if improved:
        save snapshot
        maybe add snapshot to pool
```

## Opponent pool

Pool nên có:

- Baseline cố định.
- Snapshot cũ.
- Best current.
- Rule agent của đội.

Không loại baseline cố định ra khỏi pool, vì chúng giữ agent không quên kỹ năng cơ bản.

## Sampling lineup

Mỗi trận chọn 4 slot:

- 1 slot là main agent.
- 3 slot là opponent từ pool.
- Shuffle vị trí.

Nếu train một policy dùng chung cho nhiều id, cần encode `agent_id` đúng.

## Dữ liệu train

Với DQN:

- Lưu transition cho main agent.
- Có thể lưu cho nhiều copy nếu cùng policy.

Với PPO:

- Lưu rollout theo policy hiện tại.
- Không reuse rollout quá cũ.

## Evaluation định kỳ

Mỗi `K` iteration:

- Chạy fixed seed vs baseline.
- Chạy mixed random.
- So với best snapshot.
- Benchmark time nếu model đổi.

Chỉ thêm snapshot vào pool nếu evaluation đủ tốt.

## Pool maintenance

Nếu pool quá lớn:

- Giữ best snapshot.
- Giữ snapshot cũ đa dạng.
- Giữ vài snapshot gần nhất.
- Loại snapshot quá yếu hoặc trùng hành vi.

## Chống collapse

Dấu hiệu policy collapse:

- Chỉ spam một action.
- Win self-play tăng nhưng thua baseline.
- Entropy quá thấp quá sớm.
- Fallback safety bị gọi quá nhiều.

Cách xử lý:

- Tăng đa dạng opponent.
- Giảm learning rate.
- Tăng entropy bonus nếu PPO.
- Sửa reward.
- Warm-start từ BC/rule.

## Kết quả cần đạt

Self-play đáng giữ nếu:

- Tăng rank trước mixed baseline.
- Giảm thua trước bản cũ.
- Không làm inference chậm.
- Hành vi đa dạng hơn nhưng vẫn an toàn.

