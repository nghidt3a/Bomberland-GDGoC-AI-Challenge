# Rainbow DQN: prioritized replay, n-step và distributional value

Rainbow DQN là hướng nâng cấp từ DQN cơ bản. Không nên bắt đầu bằng Rainbow nếu đội chưa có DQN chạy đúng, nhưng đây là hướng đáng thử khi DQN đã học được sống sót và cần tăng độ ổn định.

## Mục tiêu

Giữ action rời rạc `0..5`, nhưng cải thiện quá trình học Q-value bằng nhiều kỹ thuật:

- Double DQN để giảm overestimate.
- Dueling network để tách state value và action advantage.
- Prioritized replay để học nhiều hơn từ transition quan trọng.
- N-step return để lan truyền reward nhanh hơn.
- Distributional value để học phân phối return thay vì một giá trị trung bình.
- Noisy network để exploration tốt hơn epsilon-greedy.

## Phiên bản tối giản nên làm

Không cần triển khai đủ Rainbow ngay. Bản thực dụng:

```text
Double DQN + Dueling DQN + prioritized replay + n-step return
```

Distributional DQN và noisy network chỉ thêm sau khi pipeline ổn.

## Prioritized replay

Replay buffer chọn sample theo TD-error:

```text
priority = abs(td_error) + epsilon
```

Transition agent chết, đặt bom hiệu quả, né bom thành công hoặc enemy chết thường có TD-error cao và nên được học lại nhiều hơn.

Rủi ro là model overfit vào vài tình huống hiếm. Cần dùng importance sampling weight và cập nhật priority sau mỗi batch.

## N-step return

Thay vì target 1 step:

```text
r_t + gamma * Q(s_{t+1})
```

dùng target nhiều step:

```text
r_t + gamma r_{t+1} + ... + gamma^n Q(s_{t+n})
```

Bomberland có reward thưa như enemy chết hoặc thắng trận, nên n-step giúp tín hiệu quay về các action chuẩn bị trước đó, ví dụ đặt bom rồi chạy.

## Distributional value

Distributional DQN học phân phối return. Điều này hữu ích vì cùng một action có thể:

- Rất tốt nếu enemy mắc kẹt.
- Rất tệ nếu mình không có đường thoát.
- Trung bình nếu chỉ farm box.

Nếu đội dùng PyTorch tự viết, QR-DQN thường dễ hơn C51 vì không cần cố định support atom quá chặt.

## Action masking vẫn bắt buộc

Rainbow không thay thế safety layer:

```text
q_values = rainbow_model(obs)
mask invalid action
mask action đặt bom không có escape
mask action đi vào danger timer 1 nếu còn lựa chọn
return argmax q_values trong action an toàn
```

Nếu không mask, replay sẽ chứa nhiều state chết vô ích và quá trình học chậm.

## Metric nên theo dõi

- Average rank qua nhiều seed.
- Self-kill rate.
- TD-error trung bình và max.
- Tỷ lệ sample priority cao là state nào.
- Fallback/safety mask rate.
- CPU inference time.

Nếu TD-error cao nhất luôn là các state chết do lỗi rule/simulator, cần sửa feature hoặc reward trước khi tune thuật toán.

## Khi nên dùng

Dùng Rainbow-lite khi:

- DQN cơ bản đã train được.
- Có replay buffer tốt.
- Có evaluation tự động.
- Muốn cải thiện sample efficiency mà không đổi sang PPO.

Không nên dùng nếu DQN cơ bản vẫn chưa vượt rule baseline hoặc reward còn nhiễu.

