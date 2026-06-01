# 07 — Test, hardening và checklist submit

Bản submit cần ổn định hơn là “trông thông minh”. Một agent crash, timeout hoặc tự sát nhiều sẽ mất điểm rất nhanh.

## 1. Nguyên tắc submit

Bản nộp phải:

- chạy được ngay;
- không network;
- không train trong lúc chấm;
- không import thư viện ngoài môi trường;
- `act()` dưới 100ms;
- không crash khi obs lạ;
- có fallback action.

## 2. Test interface

`agent.py` cần đúng interface:

```python
class Agent:
    def __init__(self, agent_id: int):
        self.agent_id = agent_id
        # load model nếu có, chỉ load một lần

    def act(self, obs: dict) -> int:
        return action  # int trong [0, 5]
```

Test:

```python
for agent_id in [0, 1, 2, 3]:
    agent = Agent(agent_id)
    action = agent.act(sample_obs)
    assert isinstance(action, int)
    assert 0 <= action <= 5
```

## 3. Test import/startup

Kiểm tra:

- không load file online;
- không dùng path tuyệt đối từ máy local;
- model file nằm trong zip;
- startup dưới timeout;
- không dùng GPU;
- không import thư viện lạ.

Nếu dùng PyTorch:

```python
model.load_state_dict(torch.load(path, map_location="cpu"))
model.eval()
```

Không load model trong mỗi `act()`.

## 4. Test latency

Viết `profile_act.py`:

```python
times = []
for obs in many_obs:
    t0 = time.perf_counter()
    action = agent.act(obs)
    t1 = time.perf_counter()
    times.append((t1 - t0) * 1000)
```

In:

```text
mean
p50
p95
p99
max
```

Mục tiêu:

```text
mean < 10ms
p95 < 50ms
p99 < 100ms
```

Nếu p99 vượt 100ms, agent có thể bị ép STOP.

## 5. Test safety cases

Tạo hoặc tìm replay cho:

1. Không có bom.
2. Một bom gần agent.
3. Nhiều bom chain reaction.
4. Bom của đối thủ radius lớn.
5. Agent đang đứng trên bom và cần rời đi.
6. Đặt bom trong corridor.
7. Đặt bom trong góc.
8. Box chặn blast.
9. Wall chặn blast.
10. Agent bị vây bởi nhiều bomb.

Pass khi:

```text
không chọn action tự sát nếu còn đường sống
không đặt bom nếu không có escape path
danger map dự đoán đúng vùng nổ
```

## 6. Test observation lạ

`act()` không được crash nếu:

- `bombs` rỗng;
- nhiều bombs;
- agent đã chết;
- opponents chết;
- item nằm cạnh agent;
- map nhiều box;
- map gần như trống;
- dtype khác dự kiến nhưng shape đúng.

Trong submit có thể bọc fallback:

```python
try:
    return choose_action(obs)
except Exception:
    return STOP
```

Tốt hơn là fallback an toàn hơn STOP nếu có state hợp lệ, nhưng tuyệt đối không crash.

## 7. Benchmark cuối

Trước khi nộp, chạy nếu có thời gian:

```text
500+ trận
nhiều seed
nhiều opponent pool
đủ 4 agent_id
```

Bảng cuối cần có:

```text
average rank
win rate
top2
self-death
death before 100
kills
boxes
items
bombs
step500 tiebreak rank
p99 latency
```

## 8. Checklist package

- [ ] Đúng cấu trúc file BTC yêu cầu.
- [ ] Có `agent.py` đúng interface.
- [ ] Nếu có model, model nằm trong zip.
- [ ] Không có dataset/log/training file nặng.
- [ ] Không vượt size limit.
- [ ] Không dùng absolute path.
- [ ] Không dùng network.
- [ ] Không cần GPU.
- [ ] Không train trong submit.
- [ ] Không ghi file lớn khi chấm.
- [ ] Không print quá nhiều.

## 9. Checklist logic cuối

- [ ] Danger map tính chain reaction.
- [ ] Bomb radius lấy từ `owner_id`.
- [ ] Fire duration đúng engine.
- [ ] Legal mask phân biệt đi vào bom và rời khỏi bom.
- [ ] `PLACE_BOMB` chỉ khi `bombs_left > 0`.
- [ ] `PLACE_BOMB` chỉ khi ô hiện tại chưa có bom.
- [ ] `can_place_bomb_safely` mô phỏng thêm bom mới.
- [ ] Final shield luôn bật.
- [ ] Fallback không crash.
- [ ] Anti-loop không làm agent chạy vào danger.
- [ ] Attack không override safety.
- [ ] Item collector không chase item qua danger.

## 10. Version không nên submit

Không submit nếu:

- `act()` đôi khi crash;
- p99 vượt 100ms;
- self-death tăng rõ;
- agent đặt bom không escape;
- chỉ benchmark dưới 50 trận;
- model load quá lâu;
- dùng dependency không chắc có;
- PPO reward cao nhưng average rank thấp.
