# Behavior Cloning từ rule agent

Behavior Cloning từ rule agent là cách nhanh để tạo neural policy biết chơi cơ bản mà không cần reward phức tạp.

## Mục tiêu

Tạo dataset:

```text
obs_encoded -> action_rule
```

Train model dự đoán action rule. Sau đó dùng model trong agent, kèm safety fallback.

## Thu thập dữ liệu

Chạy rule agent qua nhiều trận:

- Nhiều seed.
- Nhiều vị trí `agent_id`.
- Nhiều tổ hợp đối thủ.
- Ghi lại `obs`, `agent_id`, `action`.

Dataset nên cân bằng action. Nếu quá nhiều `STOP` hoặc move một hướng, model sẽ bias.

## Label expert

Expert nên là hybrid rule tốt nhất của đội. Nếu expert còn tự sát, BC sẽ học tự sát.

Có thể tạo nhiều expert:

- Safety expert cho state nguy hiểm.
- Farming expert cho đầu game.
- Attack expert cho enemy gần.

Sau đó gom dataset hoặc train meta-policy.

## Model

Model nhỏ:

- CNN nhỏ nếu dùng channel map.
- MLP nếu dùng handcrafted feature.

Output:

```text
logits shape = [batch, 6]
loss = cross_entropy(logits, action)
```

## DAgger đơn giản

1. Train BC ban đầu.
2. Cho BC agent chơi.
3. Với state BC gặp, hỏi rule expert action gì.
4. Thêm vào dataset.
5. Train lại.

Lặp 2-5 vòng là đã hữu ích.

## Inference

Không dùng model trần:

```text
action = model_argmax(obs)
if unsafe(action):
    action = rule_fallback(obs)
return action
```

Nếu fallback dùng quá nhiều, model chưa học đủ hoặc safety quá chặt.

## Metric

Theo dõi:

- Validation accuracy.
- Accuracy trong state danger.
- Win rate.
- Average rank.
- Fallback rate.
- CPU inference time.

BC accuracy 90% vẫn có thể chơi dở nếu 10% lỗi nằm ở tình huống bom nguy hiểm.

## Khi nào hữu ích

BC hữu ích nếu:

- Rule agent mạnh nhưng logic phức tạp.
- Muốn warm-start PPO.
- Muốn model nhỏ học pattern action.
- Muốn train nhanh trên cloud.

Không nên dùng BC thay rule nếu rule đã nhanh và mạnh hơn model.

