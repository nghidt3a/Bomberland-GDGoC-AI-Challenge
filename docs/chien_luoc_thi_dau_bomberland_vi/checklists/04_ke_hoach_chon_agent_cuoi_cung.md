# Kế hoạch chọn agent cuối cùng

## Ứng viên

Liệt kê tất cả ứng viên:

| Agent | Loại | Checkpoint | Điểm mạnh | Điểm yếu |
|---|---|---|---|---|
| hybrid_vX | rule/hybrid | none | ổn định | có thể bị bắt bài |
| dqn_vY | DQN | model.pth | học pattern | cần safety |
| bc_vZ | BC | model.pth | nhanh | không vượt expert |

## Bộ test cuối

Mỗi ứng viên chạy cùng bộ:

- 100 trận mixed baseline.
- 100 trận vs strong baseline.
- 10 trận benchmark time.
- Một số trận visualize.
- Nếu có thời gian, 300-1000 trận cloud.

## Metric so sánh

| Metric | Trọng số quyết định |
|---|---|
| Pass kỹ thuật | Bắt buộc |
| Không timeout | Bắt buộc |
| Average rank | Rất cao |
| Win rate | Cao |
| Survival steps | Cao |
| Self-kill rate | Rất cao |
| Items/boxes | Trung bình |
| Kills | Trung bình |
| Dễ debug | Trung bình |

## Quy tắc chọn

Chọn agent:

1. Không vi phạm kỹ thuật.
2. Ít self-kill nhất trong nhóm mạnh.
3. Average rank tốt nhất trên mixed baseline.
4. Inference nhanh nhất nếu hiệu năng tương đương.
5. Có hành vi dễ giải thích.

Nếu RL agent mạnh hơn một chút nhưng hay timeout hoặc tự sát, chọn hybrid ổn định hơn.

## Trước giờ nộp cuối

- [ ] Rebuild ZIP sạch.
- [ ] Test load ZIP hoặc folder tương đương.
- [ ] Benchmark lại.
- [ ] Ghi version nộp.
- [ ] Giữ bản backup của ZIP.
- [ ] Chuẩn bị giải thích thuật toán, reward, feature, test result.

## Sau khi nộp

- [ ] Theo dõi valid/invalid.
- [ ] Theo dõi 12 trận đầu.
- [ ] Ghi `mu`, `sigma`, `score`.
- [ ] Xem replay/log nếu có.
- [ ] Nếu lỗi kỹ thuật, sửa và nộp lại khi còn lượt.

