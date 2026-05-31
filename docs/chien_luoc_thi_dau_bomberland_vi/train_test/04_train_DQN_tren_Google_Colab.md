# Train DQN trên Google Colab

Colab phù hợp để thử nhanh và lưu checkpoint vào Google Drive. Tài liệu này chỉ hướng dẫn workflow.

## Setup runtime

Trong Colab:

1. Runtime -> Change runtime type.
2. Chọn GPU nếu train neural network.
3. Nếu chỉ test rule-based, CPU cũng đủ.

## Mount Google Drive

```python
from google.colab import drive
drive.mount('/content/drive')
```

Tạo folder lưu checkpoint:

```python
!mkdir -p /content/drive/MyDrive/bomberland_ckpts
```

## Clone repo

```python
%cd /content
!git clone https://github.com/VLTisME/Bomberland-GDGoC-AI-Challenge.git
%cd /content/Bomberland-GDGoC-AI-Challenge
```

Nếu dùng fork của đội, thay URL.

## Cài dependency

```python
!pip install -r requirements.txt
```

## Train DQN

```python
!python agent/dqn_agent/agent.py --enemy_type tactical --num_episodes 10000 --save_model
```

Sau khi train, copy checkpoint sang Drive:

```python
!cp -r ckpts /content/drive/MyDrive/bomberland_ckpts/
```

## Resume train

Nếu có checkpoint:

```python
!python agent/dqn_agent/agent.py --enemy_type genius --num_episodes 5000 --save_model --load_model /content/drive/MyDrive/bomberland_ckpts/path/to/model.pth
```

## Test trên Colab

```python
!python -m scripts.participant.estimate_rankings --agent_path agent/dqn_agent --num_matches 100
```

Benchmark time trên Colab không giống máy chấm, nhưng vẫn giúp phát hiện spike lớn:

```python
!python -m scripts.participant.estimate_agent_time agent/dqn_agent --opponents TacticalRuleAgent SmarterRuleAgent GeniusRuleAgent --num_matches 10
```

Vẫn cần benchmark lại local nếu có thể.

## Làm việc với branch

Nếu đội dùng Git:

```python
!git status
!git checkout <branch>
!git pull
```

Sau khi train, không commit checkpoint lớn nếu repo không muốn lưu binary. Có thể dùng Drive/Kaggle output để lưu riêng.

## Lưu ý submission

Colab path như `/content/drive/...` không tồn tại khi chấm. Trong `agent.py` nộp bài phải load:

```python
Path(__file__).parent / "model.pth"
```

Không để path Colab trong code submit.

