# 05 — Double / Dueling DQN (nhánh learning thay thế PPO)

## 1. TL;DR / Kết luận nhanh

- **Verdict**: Nhánh learning **thay thế [04 PPO](04_ppo_self_play.md)** — chọn **1 trong 2**, không làm cả hai.
- **Vì sao cân nhắc DQN thay PPO**: off-policy + replay buffer ⇒ **hiệu quả mẫu hơn PPO** (PPO on-policy phải thu rollout mới mỗi epoch). Với compute hạn chế, DQN dễ "ra được cái gì đó" hơn.
- **Rủi ro cao**: Deadly Triad (bất ổn/phân kỳ), cùng các khó khăn của RL trong FFA. Vẫn cần shield + go/no-go ≥ ver3.
- **Khuyến nghị**: nếu đội thiên về value-based & muốn tận dụng dữ liệu → DQN; nếu muốn policy ngẫu nhiên/self-play chuẩn → PPO. Mặc định roadmap chọn PPO; DQN là phương án B.

## 2. Ý tưởng & vì sao hợp/không hợp ver3

Học `Q(s,a)` cho 6 action, inference chọn argmax **trong các action an toàn**. Double DQN (giảm overestimate) + Dueling head (tách V(s) và advantage) đều rẻ để thêm. Hợp vì action rời rạc `0..5` (đúng dạng DQN mạnh) và **tận dụng được dữ liệu cũ** qua replay. Không hợp ở chỗ giống PPO: phải vượt baseline mạnh, FFA non-stationary, model nhỏ dưới 100ms, và DQN nhạy siêu tham số.

## 3. ver3 đã có sẵn gì để tái dùng

- [features.py::encode_features](../../agent/team_agent/person_a_safety/features.py): state encoder (10×13×13) làm input Q-net.
- [masks.py::safe_actions](../../agent/team_agent/person_a_safety/masks.py): mask để **chỉ argmax trên action an toàn** + lấy "rule fallback".
- [policy_rule.py::RulePolicy](../../agent/team_agent/person_b_strategy/policy_rule.py): **rule fallback** khi không có action model an toàn (đúng "safety layer" mô tả ở doc generic 05).
- [engine/game.py::BomberEnv](../../engine/game.py) + reward từ `players[i].stats`.
- Đối thủ baseline cho **opponent curriculum**: Simple → BoxFarmer → Smarter → Tactical → Genius → mixed → self-play.

## 4. Thiết kế tích hợp (build-ready)

| File | Vai trò |
|---|---|
| `train/env_wrapper.py` | Dùng chung với [04] (gym wrapper + `action_masks`). |
| `train/train_dqn.py` (mới) | Double+Dueling DQN: replay buffer, target net, ε-greedy giảm dần, opponent curriculum, export ONNX. |
| sửa [policy_ppo.py](../../agent/team_agent/person_b_strategy/policy_ppo.py) *(hoặc file `policy_dqn.py` mới)* | Nạp ONNX → Q-values → mask → argmax; fallback rule. |

### 4.1 Target & head

```python
# Double DQN target
best_next = argmax_a Q_online(s', a)
y = r + gamma * Q_target(s', best_next)        # tách chọn (online) / lượng hóa (target)

# Dueling head
Q(s,a) = V(s) + A(s,a) - mean_a A(s,a)
```

### 4.2 Inference + safety layer (bắt buộc)

```python
def choose_action(state, safe_mask, hazard):
    q = sess.run(None, {"obs": encode_features(state, hazard)[None]})[0][0]
    q = np.where(safe_mask, q, -1e9)
    if not safe_mask.any():                 # hiếm: không có action model an toàn
        return RulePolicy_fallback(state, safe_mask, hazard)
    return int(np.argmax(q))                # final_shield vẫn bọc ở agent.py
```

### 4.3 Reward & curriculum

Reward gợi ý (doc generic 05): `+2` win, `+1` enemy death, `−2` death, `+0.1` item, `+0.05` bom phá box có escape, `+0.1` rời danger, `−0.05` vào danger, `−0.005`/step. Train theo **curriculum** đối thủ từ yếu → mạnh → mixed → self-play snapshots (train thẳng với Genius dễ chết nhanh, học chậm).

## 5. Ngân sách 100ms / tài nguyên

- Inference: Q-net nhỏ + ONNX → vài ms. Startup nạp model ≪ 20s.
- Train: replay buffer tốn RAM vừa phải; nhiều env steps; off-machine (Kaggle/Colab). Cảnh giác Deadly Triad → dùng target net + replay (đã chuẩn).

## 6. Kế hoạch test & đo

- Checkpoint tốt ⇔ (doc 05): vượt rule baseline **hoặc** bổ trợ tốt, avg-rank tốt qua nhiều seed, không reward-hacking, inference CPU ổn.
- Benchmark đúng luật (01) so với ver3/BC; `test_engine_safety.py` self-death=0; latency < 100ms.

## 7. Rủi ro & lan can

- **Deadly Triad / bất ổn** → target net, replay, learning-rate nhỏ, Double DQN.
- **Không vượt hybrid rule** → dùng DQN làm **prior phụ** (cộng điểm) hoặc bỏ khỏi bản nộp; giữ ver3.
- **Nhạy siêu tham số** → bám cấu hình tham khảo, đừng tự chế reward phức tạp.

## 8. Công sức & timeline · Tham chiếu

- **Công sức**: cao (~1 tuần+), tương đương [04]. Là **phương án B** của Phase 2 (chọn 1 nhánh learning).
- **Tham chiếu**: [../../docs/chien_luoc_thi_dau_bomberland_vi/huong_tiep_can/05_DQN_double_dqn_dueling_dqn.md](../../docs/chien_luoc_thi_dau_bomberland_vi/huong_tiep_can/05_DQN_double_dqn_dueling_dqn.md) · [.../11_rainbow_DQN_distributional_prioritized_replay.md](../../docs/chien_luoc_thi_dau_bomberland_vi/huong_tiep_can/11_rainbow_DQN_distributional_prioritized_replay.md) · [../../docs/chien_luoc_thi_dau_bomberland_vi/train_test/03_train_DQN_tren_Kaggle.md](../../docs/chien_luoc_thi_dau_bomberland_vi/train_test/03_train_DQN_tren_Kaggle.md) · `AI_Challenge_..._sieu_chi_tiet.md` mục 17–21 (DQN, Deadly Triad, Double DQN, reward hacking).
