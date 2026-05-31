# Train DQN trên Kaggle

Kaggle phù hợp để train DQN vì có GPU miễn phí và lưu output theo notebook. Tài liệu này mô tả quy trình; không cần chạy ngay trên máy local.

## Chuẩn bị

1. Tạo notebook mới trên Kaggle.
2. Bật internet nếu cần clone public repo.
3. Nếu repo private, tạo GitHub token và lưu trong Kaggle Secrets.
4. Chọn accelerator GPU nếu muốn train nhanh hơn.

## Clone repo public

```python
!git clone https://github.com/VLTisME/Bomberland-GDGoC-AI-Challenge.git
%cd /kaggle/working/Bomberland-GDGoC-AI-Challenge
```

Nếu dùng fork/private, thay URL bằng repo của đội.

## Clone repo private bằng secret

```python
from kaggle_secrets import UserSecretsClient
user_secrets = UserSecretsClient()
token = user_secrets.get_secret("github_token")
```

```python
!git clone https://<github_username>:{token}@github.com/<owner>/<repo>.git
%cd /kaggle/working/<repo>
```

Không hard-code token vào notebook public.

## Cài dependency

```python
!pip install -r requirements.txt
```

Nếu chỉ train DQN, vẫn nên dùng requirements của repo để tránh thiếu package.

## Train DQN hiện có

```python
!python agent/dqn_agent/agent.py --enemy_type tactical --num_episodes 10000 --save_model
```

Các đối thủ:

```text
simple, smarter, tactical, genius, box_farmer
```

Nên train theo curriculum:

```python
!python agent/dqn_agent/agent.py --enemy_type simple --num_episodes 3000 --save_model
!python agent/dqn_agent/agent.py --enemy_type tactical --num_episodes 10000 --save_model --load_model path/to/checkpoint.pth
```

## Lưu output

Kaggle lưu file trong `/kaggle/working`. Sau khi train, checkpoint thường nằm trong folder `ckpts/...`.

Nên tải về:

- Checkpoint `.pth`.
- Plot reward/loss nếu có.
- File config nếu tự tạo.

## Test checkpoint trên Kaggle

Sau khi chỉnh `agent.py` load checkpoint đúng, chạy:

```python
!python -m scripts.participant.estimate_rankings --agent_path agent/dqn_agent --num_matches 100
!python -m scripts.participant.estimate_agent_time agent/dqn_agent --opponents TacticalRuleAgent SmarterRuleAgent GeniusRuleAgent --num_matches 10
```

Không nộp checkpoint chưa benchmark CPU.

## Lưu ý khi đưa checkpoint vào submission

- Copy checkpoint tốt nhất vào cùng folder với `agent.py`.
- Trong `agent.py`, load bằng `Path(__file__).parent / "model.pth"`.
- Không giữ nhiều checkpoint trong ZIP.
- Đảm bảo model load CPU khi chấm.

## Lỗi thường gặp trên Kaggle

| Lỗi | Cách xử lý |
|---|---|
| Không clone được repo private | Kiểm tra secret token và quyền repo |
| Pygame lỗi display | Dùng headless, không visualize |
| Checkpoint quá lớn | Giảm model hoặc chỉ lưu state_dict |
| Train reward tăng nhưng rank thấp | Sửa reward, action mask, opponent pool |
| Notebook mất session | Lưu checkpoint định kỳ vào output |

