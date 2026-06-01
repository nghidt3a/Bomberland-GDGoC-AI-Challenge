# 03 — Behavior Cloning (BC từ rule agent đã shield)

## 1. TL;DR / Kết luận nhanh

- **Verdict**: Deliverable ML **thực tế nhất** và là **warm-start cho PPO/DQN**. Pipeline đã có sẵn nửa phần.
- **Trần của BC = chính rule agent (ver3) nó bắt chước** → khó *vượt* ver3; giá trị thật là **tốc độ inference**, policy mượt, và **nền để train RL**.
- **Rủi ro thấp–TB**: train nhẹ, có safety shield phủ; rủi ro chính là distribution shift.
- **Go/no-go**: BC+shield **≥ ver3** trên benchmark đúng luật (01) thì giữ làm ứng viên/nền; nếu kém hơn rõ → vẫn dùng làm warm-start cho RL, bản nộp giữ ver3.

## 2. Ý tưởng & vì sao hợp ver3

Học có giám sát: thu `(features, action_của_ver3)` rồi train mạng dự đoán action. Hợp vì: (a) ver3 là "thầy" tốt sẵn có; (b) **không cần thiết kế reward** (tránh reward-hacking); (c) train nhanh, hội tụ nhanh; (d) cho ra **policy 1 lần forward** → nhanh hơn search, và là điểm khởi đầu khả vi cho PPO. Nó **không** trực tiếp sửa điểm yếu kill/draw của ver3 (vì chỉ sao chép ver3), nên coi BC là *bước đệm năng lực ML*, không phải cú nhảy chất lượng.

## 3. ver3 đã có sẵn gì để tái dùng

- [features.py::encode_features](../../agent/team_agent/person_a_safety/features.py): tensor **10 kênh × 13×13** (`FEATURE_CHANNELS`: walls, boxes, item_radius, item_capacity, self, opponents, bombs, bomb_timer_norm, danger_time_norm, safe_reachable). **Input mạng đã định nghĩa xong.**
- [train/gen_dataset.py::collect_rule_samples](../../agent/team_agent/train/gen_dataset.py): đã thu `features`, `teacher_action` (action của `Agent` đã shield), `safe_mask`, `agent_id`, `step`, `episode_seed` → lưu `.npz`. **Bộ sinh dataset đã xong.**
- [policy_bc.py::BehaviorCloningPolicy](../../agent/team_agent/person_b_strategy/policy_bc.py): **stub** (`choose_action` trả `first_safe_action`) — chỗ để nối model.
- [agent.py](../../agent/team_agent/agent.py): pipeline + `final_shield` để bọc.

→ Thiếu đúng 2 mảnh: **script train** + **nối inference vào `policy_bc`**.

## 4. Thiết kế tích hợp (build-ready)

### 4.1 Thành phần thêm

| File | Vai trò |
|---|---|
| `train/train_bc.py` (mới) | Train CNN từ `.npz`, mask logit bằng `safe_mask`, CE tới `teacher_action`, early stopping, **export ONNX**. |
| `train/model_bc.py` (mới, hoặc trong train_bc) | Định nghĩa CNN nhỏ (vài conv 3×3 + head 6 logits). |
| sửa [policy_bc.py](../../agent/team_agent/person_b_strategy/policy_bc.py) | Nạp ONNX (onnxruntime), `encode_features` → logits → mask → argmax. |
| `submit_.../bc_model.onnx` | Model nộp kèm (zip ≤20 file, `.onnx` hợp lệ). |

### 4.2 Train loop (theo BC pseudocode trong doc)

```python
# train/train_bc.py
data = np.load(path)                       # features (N,10,13,13), teacher_action (N,), safe_mask (N,6)
Xtr, Xval = split(data, 0.2)
model = SmallCNN(in_ch=10, n_actions=6)
for epoch in range(max_epochs):
    for xb, ab, mb in batches(Xtr):
        logits = model(xb)
        logits = logits.masked_fill(~mb, -1e9)   # KHÔNG học action phi-an-toàn
        loss = cross_entropy(logits, ab)
        loss.backward(); opt.step()
    if val_loss not improved for `patience`: break    # early stopping
save_best(); export_onnx(model, "bc_model.onnx")
```

### 4.3 Inference (nối `policy_bc.py`, giữ shield)

```python
class BehaviorCloningPolicy:
    def __init__(self, model_path="bc_model.onnx"):
        self.sess = onnxruntime.InferenceSession(model_path)   # nạp 1 lần (startup <20s)
    def choose_action(self, state, safe_mask, hazard):
        x = encode_features(state, hazard)[None]               # (1,10,13,13)
        logits = self.sess.run(None, {"obs": x})[0][0]
        logits = np.where(safe_mask, logits, -1e9)             # mask an toàn
        return int(np.argmax(logits))                          # shield vẫn bọc ở agent.py
```

### 4.4 Dataset lớn & đa dạng hơn

`collect_rule_samples` hiện chạy seed cố định, agent ở cả 4 seat (đã có `for i in range(4): Agent(i)`). Mở rộng: **nhiều seed band**, **trộn đối thủ** (không chỉ 4 bản ver3) để phủ state đa dạng → giảm distribution shift. **DAgger-lite** (nếu còn giờ): chạy BC, ghi state nó gặp, gán nhãn lại bằng ver3, train lại.

## 5. Ngân sách 100ms / tài nguyên

- CNN nhỏ + ONNX trên CPU: 1 forward ~vài ms (thừa biên 100ms). `encode_features` đã chạy sẵn trong ver3 (~ms).
- Startup: nạp `.onnx` 1 lần ≪ 20s. Train: trên CPU/Colab vài chục nghìn frame là đủ (doc khuyến nghị "vài chục nghìn frame").

## 6. Kế hoạch test & đo

- **Sanity**: val accuracy khớp action ver3 cao (vd >85–90%).
- **An toàn**: `test_engine_safety.py` self-death=0 (shield bọc).
- **Sức mạnh**: benchmark đúng luật (01) BC+shield vs ver3; ngưỡng giữ = **≥ ver3**.
- **Latency**: `estimate_agent_time.py` < 100ms (gồm cả ONNX load + infer).

## 7. Rủi ro & lan can

- **Distribution shift / lỗi tích lũy** → DAgger-lite, dataset đa dạng; shield chặn hậu quả chết.
- **BC ≤ ver3** (bình thường) → đừng kỳ vọng vượt; dùng làm warm-start RL.
- **Lệ thuộc chất lượng thầy** → thầy = ver3 (đã tốt), nhưng BC kế thừa luôn điểm yếu kill/draw của ver3.

## 8. Công sức & timeline · Tham chiếu

- **Công sức**: ~4–6 ngày (script train + nối inference + dataset + đo). Phase 1 của roadmap.
- **Tham chiếu**: [../../docs/chien_luoc_thi_dau_bomberland_vi/huong_tiep_can/07_behavior_cloning_tu_rule_agent.md](../../docs/chien_luoc_thi_dau_bomberland_vi/huong_tiep_can/07_behavior_cloning_tu_rule_agent.md) · [../../docs/bomberman_agent_guides_md/05_BEHAVIOR_CLONING_CHO_NGUOI_MOI.md](../../docs/bomberman_agent_guides_md/05_BEHAVIOR_CLONING_CHO_NGUOI_MOI.md) · `AI_Challenge_..._sieu_chi_tiet.md` mục 25–28 (BC + DAgger).
