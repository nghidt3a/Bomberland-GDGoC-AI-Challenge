# Safe RL và action shielding

Safe RL đặt ràng buộc an toàn vào quá trình học và inference. Với Bomberland, đây là hướng rất thực dụng vì lỗi lớn nhất của RL thường là tự sát khi đặt bom hoặc đi vào vùng nổ.

## Ý tưởng

Policy RL chỉ được chọn trong tập action an toàn:

```text
safe_actions = shield(obs)
action = policy(obs, safe_actions)
```

Shield là lớp kiểm tra luật, không phải neural network chính.

## Ràng buộc an toàn

Shield nên loại:

- Action đi vào wall, box hoặc bomb.
- Action đi vào ô nổ ngay nếu còn lựa chọn khác.
- `PLACE_BOMB` khi không có đường thoát.
- Action đi vào dead-end khi enemy/bomb đe dọa.
- Action làm giảm safe reachable tiles xuống quá thấp.

Nếu không có action an toàn tuyệt đối, chọn action kéo dài thời gian sống lâu nhất.

## Train với shield

Có hai cách:

1. Shield chỉ dùng ở inference.
2. Shield dùng cả trong train và inference.

Nên dùng cách 2 để distribution train giống lúc nộp. Nếu train không shield nhưng inference có shield, policy có thể liên tục đề xuất action bị chặn.

## Constrained reward

Có thể thêm cost riêng:

```text
cost_deadly_action = 1 nếu policy đề xuất action bị shield chặn
cost_no_escape_bomb = 1 nếu muốn đặt bom không có escape
```

Tối ưu:

```text
maximize reward
subject to expected_cost <= threshold
```

Nếu không triển khai constrained RL đầy đủ, vẫn có thể log cost và phạt nhẹ trong reward.

## Risk-aware value

Một cách khác là học thêm risk head:

```text
model(obs) -> action_logits, value, death_risk
```

Inference:

```text
chọn action có reward tốt nhưng death_risk dưới ngưỡng
```

Risk label có thể lấy từ rollout: agent chết trong `n` step tới hay không.

## Metric quan trọng

- Shield rate: bao nhiêu phần trăm action bị chặn.
- No-escape bomb attempts.
- Death within 3 steps after chosen action.
- Self-kill rate.
- Win/rank sau khi giảm self-kill.

Shield rate quá cao nghĩa là policy chưa học luật sống còn.

## Ưu điểm

- Giảm mạnh lỗi tự sát.
- Giúp RL tập trung học chiến thuật.
- Dễ ghép với DQN, PPO, MAPPO, BC.
- Hợp ràng buộc 100ms nếu shield BFS được tối ưu.

## Rủi ro

- Shield quá chặt làm agent bỏ lỡ cơ hội tấn công.
- Nếu shield sai, policy bị giới hạn sai.
- BFS/escape check chậm có thể timeout.

## Khuyến nghị

Đây là hướng nên áp dụng cho mọi neural policy. Đừng coi safety layer là chi tiết phụ; trong Bomberland nó gần như là phần bắt buộc của RL agent thi đấu.

