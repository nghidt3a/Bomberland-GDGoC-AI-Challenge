# Agent interface và quy chuẩn nộp bài

File nộp phải là ZIP có `agent.py` ở root. Trong `agent.py` phải có class `Agent`.

## Interface bắt buộc

```python
class Agent:
    def __init__(self, agent_id: int):
        self.agent_id = agent_id

    def act(self, obs: dict) -> int:
        return 0
```

`agent_id` là id player mà agent điều khiển, từ `0` đến `3`. Dùng:

```python
my_data = obs["players"][self.agent_id]
```

để lấy vị trí, trạng thái sống, số bom còn lại và bonus radius.

## Quy định nộp

| Mục | Quy định |
|---|---|
| File bắt buộc | `agent.py` |
| Vị trí `agent.py` | Root của ZIP |
| Số file tối đa | 20 |
| Kích thước ZIP | <= 100MB |
| Kích thước file đơn | <= 150MB |
| Startup | <= 20 giây |
| `act()` | <= 100ms mỗi step |
| Môi trường | CPU-only, không network, không ghi file |

Được kèm checkpoint như `.pth`, `.pt`, `.onnx`, `.pkl`, `.json`, miễn là nằm trong ZIP và được load bằng path tương đối từ `agent.py`.

## Cách load checkpoint an toàn

```python
from pathlib import Path

class Agent:
    def __init__(self, agent_id: int):
        self.agent_id = agent_id
        self.base_dir = Path(__file__).resolve().parent
        self.model_path = self.base_dir / "model.pth"
```

Không dùng path tuyệt đối như `D:\...` hoặc `/kaggle/...` trong agent nộp bài.

## Không làm trong `act()`

Không nên:

- Import `torch`, `numpy`, model lớn trong mỗi lần `act()`.
- Load checkpoint trong mỗi lần `act()`.
- Ghi log ra file.
- Gọi network hoặc API.
- Dùng LLM.
- Chạy search quá sâu không kiểm soát thời gian.

Nên khởi tạo model và cache cấu trúc tĩnh trong `__init__`, còn `act()` chỉ xử lý observation hiện tại và trả action.

## Fallback bắt buộc

Agent nên luôn có fallback:

```python
def act(self, obs):
    try:
        action = self._decide(obs)
        return int(action) if 0 <= int(action) <= 5 else 0
    except Exception:
        return 0
```

Fallback tốt hơn có thể là một safety rule đơn giản thay vì `STOP`, nhưng không được làm phức tạp đến mức gây timeout.

## Checklist ZIP

Trước khi nộp:

- [ ] ZIP mở ra thấy `agent.py` ngay ở root.
- [ ] Chỉ có một `agent.py`.
- [ ] Class tên đúng là `Agent`.
- [ ] `Agent(agent_id)` khởi tạo được.
- [ ] `act(obs)` trả int trong `0..5`.
- [ ] Checkpoint load bằng `Path(__file__).parent`.
- [ ] Không phụ thuộc file ngoài ZIP.
- [ ] Không có code train chạy khi import.
- [ ] Code train nằm trong `if __name__ == "__main__":`.
- [ ] Benchmark dưới 100ms trên CPU.

## Lỗi hay gặp

| Lỗi | Cách tránh |
|---|---|
| `agent.py` nằm trong folder con | Zip trực tiếp file, không zip folder |
| Checkpoint path sai | Dùng `Path(__file__).parent` |
| Import module local lỗi | Đặt helper file cùng root ZIP hoặc gộp vào `agent.py` |
| Timeout startup | Giảm model, tránh import quá nặng |
| Timeout `act()` | Cache, giảm search depth, precompute |
| Action invalid | Luôn sanitize output |
| Train tự chạy khi chấm | Bọc train trong `if __name__ == "__main__":` |

