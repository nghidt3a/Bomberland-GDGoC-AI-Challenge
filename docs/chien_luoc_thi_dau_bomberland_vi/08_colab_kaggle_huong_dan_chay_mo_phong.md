# Hướng dẫn chạy mô phỏng trên Colab hoặc Kaggle

Mục tiêu của cloud là train và mô phỏng nhiều trận mà không làm nặng máy local. Tài liệu này chỉ hướng dẫn chuẩn bị và chạy khi cần; không yêu cầu chạy ngay.

## Khi nào dùng Kaggle

Kaggle phù hợp khi:

- Cần GPU miễn phí.
- Muốn lưu output/checkpoint theo notebook version.
- Repo private cần clone bằng secret token.
- Muốn chạy notebook dài và ổn định.

## Khi nào dùng Google Colab

Colab phù hợp khi:

- Dễ dùng với Google Drive.
- Muốn mount Drive để lưu checkpoint.
- Muốn thử nhanh nhiều cell.
- Không cần workflow versioning như Kaggle.

## Setup chung

```bash
git clone <repo_url>
cd Bomberland-GDGoC-AI-Challenge
pip install -r requirements.txt
```

Nếu chỉ train DQN hiện có, lệnh mẫu:

```bash
python agent/dqn_agent/agent.py --enemy_type tactical --num_episodes 10000 --save_model
```

Các `enemy_type` hiện có:

- `simple`
- `smarter`
- `tactical`
- `genius`
- `box_farmer`

## Lưu checkpoint

Luôn lưu:

- Checkpoint model.
- Config train.
- Seed.
- Loại opponent.
- Số episode.
- Commit hash hoặc tên version code.

Đặt tên gợi ý:

```text
dqn_tactical_ep10000_seed86_v03.pth
ppo_selfplay_ep5000_seed42_v01.zip
hybrid_bc_rule_v05.pth
```

## Không đưa artifact thừa vào submission

Submission chỉ cần:

- `agent.py`
- checkpoint tốt nhất nếu dùng model
- config nhỏ nếu thật sự cần

Không đưa:

- notebook `.ipynb`
- log train lớn
- nhiều checkpoint
- ảnh plot
- dataset demo

## Lưu ý CPU-only khi chấm

Cloud có thể có GPU, nhưng evaluator chấm CPU-only. Vì vậy:

- Model inference phải nhanh trên CPU.
- Không gọi `.cuda()` trong agent nộp bài.
- Dùng `torch.device("cpu")` khi load checkpoint.
- Model càng nhỏ càng tốt.
- Benchmark bằng script local trước khi nộp.

## Quy tắc chống mất thời gian

Không train quá lâu nếu agent chưa có safety:

1. Rule-based safety trước.
2. Train model nhỏ.
3. Test 100 trận.
4. Nếu không vượt rule baseline, sửa reward/feature trước khi tăng episode.

Nhiều episode với reward sai chỉ làm agent học sai chắc hơn.

