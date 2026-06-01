# Báo cáo nhiệm vụ — Người A (Safety/Engine)

> Trách nhiệm cốt lõi của A: **"Agent có chết ngu không?"**
> A không lo ghi điểm (việc của B); A đảm bảo mọi action cuối cùng đều an toàn ở
> mức cao nhất có thể chứng minh được, và có quyền **phủ quyết** mọi action của B.

Kết quả sau đợt nâng cấp này: **0 ca tự chết vì bom của chính mình trên 120 seed
chạy engine thật**, latency ~8 ms/step (giới hạn 100 ms), toàn bộ test xanh.

---

## 1. Các module A sở hữu (trong `person_a_safety/`)

| File | Vai trò |
|---|---|
| `constants.py` | Hằng số luật chơi (action id, tile id, `BOMB_TIMER`, `FIRE_DURATION`, `HORIZON`) — phải khớp `engine/`. |
| `obs.py` | `parse_obs(obs, agent_id)` — dịch observation thô của engine sang `GameState` nội bộ. |
| `state.py` | Định nghĩa `GameState`, `BombInfo`. |
| `danger.py` | `blast_cells`, chain reaction, `compute_danger_map` → bản đồ "mỗi ô cháy ở bước thứ mấy". |
| `search.py` | BFS không-thời-gian: `safe_at`, `has_escape_path`, `safe_distances`. |
| `masks.py` | `legal_actions` / `safe_actions` — hợp đồng action giao cho B. |
| `bomb.py` | `can_place_bomb_safely` — chặn đặt bom tự nhốt. |
| `shield.py` | `final_shield` — chốt chặn cuối, override mọi action unsafe của B. |
| `features.py` | `encode_features` cho BC/PPO (dùng sau). |

API ổn định cung cấp cho B:
`parse_obs`, `compute_danger_map`, `legal_actions`, `safe_actions`,
`safe_distances`, `can_place_bomb_safely`, `final_shield`.

---

## 2. Mô hình an toàn (bản chất)

### 2.1. Trục thời gian "move-frame" `t`
- `t = 0`: hiện tại; `t = k`: sau khi agent thực hiện `k` action.
- `danger_time[cell] = T` ⇔ ô đó bốc cháy đúng tại `t = T` (cháy 1 bước rồi tắt vì
  `FIRE_DURATION = 1`).
- Vì engine giải quyết theo thứ tự *di chuyển → bom nổ* trong cùng một step nên
  với bom đang tồn tại: `danger_time = bomb.timer` (đối chiếu `engine/game.py`).

### 2.2. Ba lớp phòng thủ chồng nhau
1. `legal_actions` — đúng luật (không đâm tường/box/bom; hết bom không đặt).
2. `safe_actions` — không vào lửa **và** sau action vẫn còn đường thoát; `PLACE_BOMB`
   phải qua `can_place_bomb_safely`.
3. `final_shield` — nếu B trả action unsafe → override; nếu hết đường sống chắc
   chắn → `least_bad_action` (chết muộn nhất). Luôn trả action trong `[0, 5]`.

Bất biến quy nạp: *nếu mỗi bước còn ít nhất một action an toàn và ta luôn chọn
action an toàn, thì bước sau vẫn còn action an toàn → không bao giờ bị nhốt.*
Điều này chỉ đúng khi phép kiểm tra "còn đường thoát" **chính xác** — và đó là nơi
hai lỗi dưới đây từng phá vỡ.

---

## 3. Hai lỗi an toàn đã phát hiện & sửa

Cả hai cùng một bản chất: **off-by-one "lạc quan quá mức"** — agent *tưởng* còn dư
1 bước thoát, dẫn tới tự sát. Phát hiện nhờ harness chạy engine thật.

### 🔴 Lỗi #1 — Escape sau khi di chuyển reset đồng hồ về `t = 0`
- **Chỗ:** `masks.py::has_escape_after_action` → `search.py::has_escape_path`.
- **Bản chất:** đi tới ô mới đã tiêu 1 bước, nhưng BFS thoát lại bắt đầu ở `t = 0`
  → thừa 1 bước budget không có thật.
- **Sửa:** thêm tham số `start_time` cho BFS; escape sau khi đi dùng `start_time=1`.

### 🔴 Lỗi #2 — `can_place_bomb_safely` bỏ qua lượt đứng yên khi đặt bom
- **Chỗ:** `bomb.py::can_place_bomb_safely`.
- **Bản chất:** đặt bom tiêu trọn một lượt mà agent **không di chuyển**; trong lượt
  đó mọi bom hiện có tick xuống 1. Mô phỏng cũ cho BFS chạy từ `t = 0` (tưởng đi
  được ngay) → thừa budget. Với bom radius 5, thừa 1 bước là đủ chết.
- **Bằng chứng (seed 2):** agent đặt bom thứ 3 trên một hàng radius-5; `safe_mask`
  báo "đặt được", nhưng ngay bước sau `safe_mask` rỗng hoàn toàn → chết.
- **Sửa:** BFS thoát khi đặt bom dùng `start_time=1` (song song Lỗi #1).

### 🟡 Hai giả định "thiên an toàn" (cố ý, đã ghi chú trong code)
- **Bán kính bom** lấy theo bonus *hiện tại* của owner (obs không chứa radius bom).
  Owner nhặt item radius sau khi đặt → ta ước lượng vùng nổ *to hơn* thực tế ⇒ an toàn.
- **Chain reaction** tính trên grid hiện tại (không mô hình box bị phá làm lan xa
  ở cùng step) — khớp đúng engine (engine cũng tính tiles trước khi xóa box).

---

## 4. Kiểm chứng

### 4.1. Unit test (40 test) — `smoke_tests/`
`test_obs.py`, `test_danger.py`, `test_search.py`, `test_masks.py`,
`test_bomb_checker.py`, `test_shield.py` (+ `test_scaffold.py` cũ).
Bao gồm 2 regression khóa chặt Lỗi #1 và Lỗi #2.

### 4.2. Engine cross-validation harness — `smoke_tests/test_engine_safety.py`
Chạy **BomberEnv thật** nhiều seed với 3 đối thủ **tất định, không đặt bom** (nên
bom duy nhất trên sân là của ta) và khẳng định:
1. mọi action ∈ `[0, 5]`;
2. **số lần chết trong vụ nổ bom của chính mình = 0**.

> Đối thủ không đặt bom giúp test (a) tái lập được và (b) cô lập đúng trách nhiệm
> của A — chết vì bom đối thủ dồn ép là chuyện chiến thuật, ngoài phạm vi đã thống
> nhất (không dự đoán bom đối thủ để tránh agent thụ động/tụt rank).

### 4.3. Kết quả
| Hạng mục | Trước fix | Sau fix |
|---|---|---|
| Tự chết bằng bom nhà (40 seed) | **21/40** | **0/40** |
| Tự chết bằng bom nhà (120 seed) | — | **0/120** |
| Action ngoài `[0,5]` | 0 | 0 |
| Latency trung bình | — | ~7.9 ms/step (max spike ~22 ms) |

---

## 5. Lệnh chạy nhanh

```bash
# Unit test (nhanh)
python -m pytest agent/team_agent/smoke_tests \
  --ignore=agent/team_agent/smoke_tests/test_engine_safety.py -q

# Harness an toàn engine (mặc định 40 seed)
python -m pytest agent/team_agent/smoke_tests/test_engine_safety.py -q -s

# Harness sâu khi hardening
TEAM_SAFETY_SEEDS=300 python -m pytest \
  agent/team_agent/smoke_tests/test_engine_safety.py -q -s

# Match thật + latency
python -m scripts.participant.run_local_match \
  --agent_paths agent/team_agent None None None --num_episodes 20 --visualize false
python -m scripts.participant.estimate_agent_time \
  agent/team_agent --opponents None None None --num_matches 5
```

---

## 6. Việc còn lại (đề xuất tiếp theo)
- `features.py`: chuẩn hóa shape `(channels, 13, 13)` + test khi bước sang BC/PPO.
- Mở rộng harness lên 300–500 seed trong CI hardening cuối.
- (Tùy chọn, ngoài phạm vi hiện tại) lớp dự đoán bom đối thủ — chỉ làm nếu chấp
  nhận đánh đổi tính chủ động lấy an toàn cao hơn.
