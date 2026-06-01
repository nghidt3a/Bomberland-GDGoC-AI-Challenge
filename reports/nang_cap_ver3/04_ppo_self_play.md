# 04 — PPO + Self-Play

## 1. TL;DR / Kết luận nhanh

- **Verdict**: Trần cao nhất (cửa *thực sự* vượt ver3) nhưng **rủi ro cao, tốn nhất**. Chỉ làm khi [03 BC](03_behavior_cloning.md) đã vững **và** còn ≥ ~1 tuần.
- Là **một trong hai nhánh learning** (cùng [05 DQN](05_dqn_dueling.md)) — **chọn 1**, không làm cả hai.
- **Cổng go/no-go cứng** (theo docs): PPO không vượt rule/BC rõ ràng ⇒ **bỏ**, nộp ver3/BC. Không để PPO ăn hết deadline.
- Bắt buộc: **warm-start từ BC**, **masked logits bằng safe_mask**, **final_shield** vẫn bọc, train **off-machine**.

## 2. Ý tưởng & vì sao hợp/không hợp ver3

PPO tối ưu trực tiếp policy `π(a|s)` qua tương tác + self-play để *khám phá* chiến thuật người không code tay (dồn/zoning/chain nhiều bước) → cửa duy nhất tăng **kills** thật. Nhưng (xem [roadmap](../ke_hoach_hien_trang_va_roadmap_ml.md)): ver3 là baseline mạnh & shield ghim PPO vào khe "nước-an-toàn"; reward thưa + FFA non-stationary + PPO kém hiệu quả mẫu → **chạm trần đó trong 19 ngày là khó**. Vì vậy PPO = canh bạc upside, không phải đường chắc ăn.

## 3. ver3 đã có sẵn gì để tái dùng

- [features.py::encode_features](../../agent/team_agent/person_a_safety/features.py): observation encoder (10×13×13) cho mạng.
- [masks.py::safe_actions](../../agent/team_agent/person_a_safety/masks.py): **action mask** để mask logits (Safe-RL shielding).
- [policy_bc.py](../../agent/team_agent/person_b_strategy/policy_bc.py) (sau [03]): **trọng số warm-start**.
- [engine/game.py::BomberEnv](../../engine/game.py): `reset(seed)`, `step(actions)` → `(obs, terminated, truncated)`; `players[i].stats` cho reward terminal.
- [policy_ppo.py](../../agent/team_agent/person_b_strategy/policy_ppo.py): **stub** chờ nối inference.
- Đối thủ pool sẵn: `TacticalRuleAgent`, `SmarterRuleAgent`, `GeniusRuleAgent` + chính ver3.

→ Thiếu: **gym wrapper** + **vòng train PPO/self-play** + **nối inference**.

## 4. Thiết kế tích hợp (build-ready)

| File | Vai trò |
|---|---|
| `train/env_wrapper.py` (mới) | Bọc `BomberEnv` thành `gymnasium.Env` 1-agent (3 đối thủ là môi trường); expose `action_masks()` từ `safe_actions`; tính reward. |
| `train/train_ppo.py` (mới) | `sb3_contrib.MaskablePPO`, warm-start từ BC, self-play pool, lưu checkpoint, **export ONNX**. |
| sửa [policy_ppo.py](../../agent/team_agent/person_b_strategy/policy_ppo.py) | Nạp ONNX → logits → mask `safe_mask` → argmax (hoặc sample). |

### 4.1 Gym wrapper (điểm mấu chốt)

```python
class BomberlandSingleAgentEnv(gymnasium.Env):
    def __init__(self, agent_seat, opponents, seed):
        self.env = BomberEnv(max_steps=500, seed=seed)
    def reset(...):
        obs = self.env.reset(seed); return encode_features(parse_obs(obs, seat)), info
    def step(self, action):
        actions = [opp.act(obs) for opp ...]; actions[seat] = action   # ghép action 4 người
        obs, term, trunc = self.env.step(actions)
        return encode_features(...), self._reward(...), term, trunc, info
    def action_masks(self):                       # MaskablePPO đọc cái này
        return safe_actions(parse_obs(self.cur_obs, seat), hazard)
```

### 4.2 Reward (terminal rank + shaping nhẹ — cẩn thận reward-hacking)

Lấy từ doc generic, giữ **thưa-nhưng-đúng-mục-tiêu**: `+` thắng/sống lâu, `+` enemy death, `+` item, `+` đặt bom phá box có escape, `−` chết, `−` mỗi step (chống camp). **Trọng số shaping phải nhỏ** so với terminal để không dạy agent farm-vô-tận thay vì thắng (xem [reward hacking](../../docs/chien_luoc_thi_dau_bomberland_vi/06_reward_design_va_reward_hacking.md)).

### 4.3 Self-play pool

Pool = `{rule ver3, Tactical, Smarter, Genius, + snapshot PPO cũ}`; mỗi epoch random đối thủ; định kỳ thêm snapshot; **randomize seat** (4 góc) để không overfit vị trí. Train off-machine (Colab/Kaggle).

### 4.4 Inference (giữ shield)

Như [03 §4.3] nhưng model PPO; `final_shield` vẫn là cổng cuối trong [agent.py](../../agent/team_agent/agent.py).

## 5. Ngân sách 100ms / tài nguyên

- **Inference**: net nhỏ + ONNX → vài ms (OK). **Train**: nặng — cần nhiều env steps; engine Python chậm ⇒ chạy nhiều env song song / off-machine, kiên nhẫn.
- Startup nạp ONNX ≪ 20s.

## 6. Kế hoạch test & đo

- Benchmark checkpoint định kỳ trên thước đo đúng luật (01); chỉ so với ver3 & BC.
- `test_engine_safety.py` self-death=0; latency < 100ms.
- Theo dõi **kills/draw** (mục tiêu thật) + cảnh giác reward-hacking (camp/farm vô tận).

## 7. Rủi ro & lan can

- **Không vượt ver3/BC** (khả năng cao trong 19 ngày) → **stop-rule cứng**, nộp ver3/BC.
- **Self-play bất ổn / overfit pool / quên đối thủ cũ** → pool đa dạng + giữ baseline rule trong pool.
- **Reward-hacking** → shaping nhỏ, ưu tiên terminal rank.
- **Ăn hết deadline** → đặt mốc cứng: nếu tới ngày X chưa ≥ BC thì dừng.

## 8. Công sức & timeline · Tham chiếu

- **Công sức**: cao (~1 tuần+ gồm wrapper + train + tune). Phase 2 của roadmap, chỉ khi BC vững.
- **Tham chiếu**: [../../docs/chien_luoc_thi_dau_bomberland_vi/huong_tiep_can/06_PPO_actor_critic.md](../../docs/chien_luoc_thi_dau_bomberland_vi/huong_tiep_can/06_PPO_actor_critic.md) · [.../08_self_play_curriculum.md](../../docs/chien_luoc_thi_dau_bomberland_vi/huong_tiep_can/08_self_play_curriculum.md) · [../../docs/chien_luoc_thi_dau_bomberland_vi/train_test/05_train_PPO_SB3_goi_y_kien_truc.md](../../docs/chien_luoc_thi_dau_bomberland_vi/train_test/05_train_PPO_SB3_goi_y_kien_truc.md) · [.../06_self_play_training_loop.md](../../docs/chien_luoc_thi_dau_bomberland_vi/train_test/06_self_play_training_loop.md) · `AI_Challenge_..._sieu_chi_tiet.md` mục 22–24 (PPO, GAE, self-play).
