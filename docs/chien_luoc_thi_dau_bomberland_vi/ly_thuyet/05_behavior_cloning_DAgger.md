# Behavior Cloning và DAgger

Behavior Cloning học bắt chước hành động của expert bằng supervised learning. Đây là cách nhanh để có policy neural tương đối hợp lý trước khi RL.

## Behavior Cloning là gì

Dataset gồm cặp:

```text
(state, expert_action)
```

Model học:

```text
state -> action
```

Loss thường dùng là cross entropy giữa action model dự đoán và action expert.

## Expert có thể là gì

Trong Bomberland, expert có thể là:

- Rule-based agent mạnh của đội.
- Baseline mạnh như tactical/genius nếu thu được action.
- Người chơi thủ công nếu có tool ghi action.
- Agent hybrid đã tune tốt.

Thực dụng nhất là dùng chính rule-based tốt của đội làm expert.

## Vì sao BC hữu ích

- Không cần reward phức tạp.
- Train nhanh hơn RL.
- Có policy neural để warm-start DQN/PPO.
- Có thể nén logic rule-based phức tạp thành model nhỏ.

## Nhược điểm

BC chỉ học phân phối state expert đã gặp. Nếu model đi lệch, nó gặp state lạ và dễ sai tiếp. Đây là distribution shift.

Ví dụ:

- Expert luôn né bom đúng.
- Model sai một bước, đứng gần dead-end.
- State này không có trong dataset.
- Model không biết thoát, lỗi tích lũy.

## DAgger

DAgger sửa bằng cách lặp:

1. Train BC từ dataset ban đầu.
2. Cho model chơi.
3. Ghi lại state model gặp.
4. Hỏi expert nên chọn action gì ở các state đó.
5. Thêm vào dataset.
6. Train lại.

Với Bomberland, expert có thể là rule-based safety. Ta không cần người label thủ công từng state.

## Pipeline BC thực dụng

1. Chạy rule-based agent qua nhiều seed.
2. Lưu `obs` và `action`.
3. Encode `obs` thành tensor/feature.
4. Train classifier 6 action.
5. Test model trong match thật.
6. Thêm safety mask khi submit.

## Metric cho BC

Không chỉ đo validation accuracy. Cần đo:

- Win rate khi model tự chơi.
- Average rank.
- Tỉ lệ action bị safety fallback.
- Tỉ lệ tự chết.
- Inference time CPU.

Accuracy cao nhưng agent chết nhiều nghĩa là dataset hoặc safety chưa đủ.

## Kết hợp BC và RL

BC có thể dùng để:

- Khởi tạo policy PPO.
- Khởi tạo DQN behavior policy.
- Làm model gợi ý action trong hybrid.
- Distill rule-based để inference nhanh hơn nếu rule quá phức tạp.

Khuyến nghị: BC + safety layer là hướng vừa dễ train vừa ít rủi ro hơn RL thuần.

