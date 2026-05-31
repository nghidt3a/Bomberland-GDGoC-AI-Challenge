# Intrinsic motivation và exploration reward

Intrinsic motivation thêm reward khám phá để agent học nhanh hơn khi reward chính thưa. Hướng này hữu ích trong giai đoạn đầu train RL, nhưng cần kiểm soát để agent không chỉ đi khám phá mà quên thắng trận.

## Vì sao cần

Trong Bomberland, nhiều reward quan trọng xảy ra muộn:

- Enemy chết sau khi đặt bom vài step.
- Thắng trận ở cuối episode.
- Item chỉ xuất hiện sau khi phá box.

Nếu chỉ dùng reward cuối trận, agent có thể học rất chậm.

## Count-based novelty

Cách đơn giản nhất:

```text
bonus = 1 / sqrt(visit_count(feature_state))
```

Feature state có thể là:

- Vùng map agent đang đứng.
- Số box còn lại gần agent.
- Danger level.
- Item gần nhất.
- Enemy distance bucket.

Không nên dùng full observation làm key vì quá thưa.

## RND

Random Network Distillation dùng hai network:

- Target network random, cố định.
- Predictor network học dự đoán output target.

State càng lạ thì prediction error càng cao, dùng làm exploration bonus.

```text
reward_total = extrinsic_reward + beta * rnd_bonus
```

Giảm `beta` dần theo thời gian để policy quay về mục tiêu thắng.

## ICM

Intrinsic Curiosity Module thưởng cho state mà agent khó dự đoán sau action. ICM có thể hữu ích khi action tạo thay đổi như đặt bom, phá box, mở đường.

Nhưng trong game đối kháng, state đối thủ thay đổi cũng tạo novelty. Nếu không cẩn thận, agent học chạy theo nhiễu của đối thủ.

## Exploration có kiểm soát

Intrinsic reward phải đi cùng safety:

- Không thưởng khám phá nếu action bị shield chặn.
- Không thưởng đi vào danger timer thấp.
- Bonus khám phá nhỏ hơn reward sống/chết.
- Tắt hoặc giảm mạnh bonus khi self-play/eval.

## Curriculum

Giai đoạn phù hợp:

1. Train với map/opponent dễ, bonus khám phá cao.
2. Khi biết sống sót và farm, giảm bonus.
3. Chuyển sang reward rank/enemy death.
4. Fine-tune không intrinsic reward hoặc chỉ rất nhỏ.

## Metric nên log

- Extrinsic reward riêng.
- Intrinsic reward riêng.
- Tỷ lệ action khám phá bị shield chặn.
- Số vùng map đã đi qua.
- Số item/box thật sự đạt được.
- Win/rank khi tắt intrinsic reward.

Nếu intrinsic reward tăng nhưng extrinsic reward giảm, agent đang học mục tiêu phụ.

## Khi nên dùng

Dùng khi DQN/PPO học quá chậm do reward thưa. Không dùng để sửa policy tự sát; lỗi đó cần safety layer và reward chết rõ hơn trước.

