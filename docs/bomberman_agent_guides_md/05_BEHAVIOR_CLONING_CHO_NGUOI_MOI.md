# 05 — Behavior Cloning cho team chưa nhiều ML/RL

Behavior Cloning (BC) là hướng ML dễ hiểu và ít rủi ro hơn RL thuần. BC học bắt chước rule agent tốt.

## 1. BC là gì?

Ta có rule agent đóng vai trò “thầy”. Cho thầy chơi nhiều trận và lưu:

```text
observation → action thầy chọn
```

Sau đó train model như bài toán phân loại:

```text
input: observation đã encode
output: 1 trong 6 action
```

BC không cần reward. Nó chỉ học “ở state này, thầy sẽ làm gì”.

## 2. Vì sao BC hữu ích?

BC giúp model có nền trước khi thử PPO:

- biết né bom tương đối;
- biết farm box;
- biết nhặt item;
- ít chọn action ngu hơn random;
- làm khởi tạo tốt cho PPO.

Nhưng BC có hạn chế:

- không dễ vượt thầy;
- copy cả lỗi của thầy;
- gặp state lạ có thể xử lý kém;
- vẫn cần safety shield.

Cách chạy inference đúng:

```text
BC model đề xuất action
→ mask unsafe action
→ final shield kiểm tra lần cuối
→ return action
```

Không submit BC trần không shield.

## 3. Khi nào nên làm BC?

Chỉ làm khi rule agent đã tương đối ổn:

```text
self-death thấp
có farm box
biết nhặt item
không loop quá nhiều
benchmark ổn
```

Nếu rule agent còn tự sát, BC sẽ học lại lỗi đó.

## 4. Dataset BC cần lưu gì?

Mỗi sample nên có:

```python
{
  "obs_tensor": encoded_obs,
  "teacher_action": final_action_from_rule,
  "legal_mask": legal_mask,
  "safe_mask": safe_mask,
  "agent_id": agent_id,
  "step": step,
}
```

Nên lấy `teacher_action` sau khi rule đã qua shield, vì đó là action an toàn thật.

## 5. Sinh dataset thế nào?

Chạy rule agent với nhiều đối thủ:

- random;
- camper;
- farmer;
- aggressive;
- baseline BTC;
- rule variants.

Nếu chỉ train từ rule vs random, model có thể yếu trước aggressive/camper.

## 6. Cân bằng action

Dữ liệu thường lệch: di chuyển rất nhiều, `PLACE_BOMB` ít. Nếu không xử lý, model có thể ít đặt bom và farm kém.

Cách xử lý:

- xem phân bố action;
- oversample state có `PLACE_BOMB`;
- tăng class weight cho `PLACE_BOMB`;
- lưu nhiều replay state farm/attack;
- đo accuracy riêng cho `PLACE_BOMB`.

Metric cần xem:

```text
overall accuracy
PLACE_BOMB accuracy
danger-state accuracy
escape-state accuracy
```

Accuracy tổng cao nhưng `PLACE_BOMB` thấp thì gameplay vẫn kém.

## 7. Encode feature

Input nên là tensor `C × 13 × 13`.

Plane gợi ý:

```text
wall
box
item_radius
item_capacity
self_position
opponents_all
bomb_position
bomb_timer_normalized
bomb_radius_normalized
danger_time_normalized
reachable_safe_cells
```

Có thể thêm scalar:

```text
bombs_left
self_radius
nearest_item_distance
nearest_safe_distance
nearest_box_target_distance
step_normalized
```

Với team mới, bắt đầu bằng grid planes là đủ.

## 8. Agent_id và spawn bias

Agent có thể là ID 0–3. Nếu data lệch, model có thể mạnh ở góc này nhưng yếu ở góc khác.

Cách đơn giản:

```text
sinh dataset đủ cả 4 agent_id
benchmark đủ cả 4 agent_id
```

Cách nâng cao là xoay/lật board để self luôn ở quy chiếu chuẩn, nhưng team mới có thể bỏ để tránh bug.

## 9. Model nhỏ đề xuất

Map 13×13 rất nhỏ, không cần model lớn.

Ví dụ:

```text
Conv2D(C → 32, kernel 3)
ReLU
Conv2D(32 → 64, kernel 3)
ReLU
Flatten
Linear → 128 hoặc 256
ReLU
Linear → 6 logits
```

Không dùng Transformer/model nặng. Submit CPU-only cần inference nhanh.

## 10. Masked cross-entropy

Model output 6 logits. Trước khi tính loss, mask action bất hợp lệ:

```python
logits[~legal_mask] = -1e9
loss = cross_entropy(logits, teacher_action)
```

Nếu dùng safe mask khi train, cần đảm bảo inference cũng dùng safe mask.

Khuyến nghị:

```text
training: mask legal, có thể mask safe nếu pipeline ổn
inference: luôn safe mask + final shield
```

## 11. Đánh giá BC

Không chỉ nhìn loss/accuracy. Cần benchmark BC+shield với cùng opponent pool như rule.

So với rule:

| Metric | BC nên thế nào |
|---|---|
| self-death | không tăng đáng kể |
| average rank | xấp xỉ rule hoặc tốt hơn |
| boxes/items | không giảm mạnh |
| p99 latency | dưới 100ms |

Nếu BC tệ hơn rule, vẫn có thể dùng làm init PPO, nhưng không submit BC.

## 12. DAgger nhẹ

BC có lỗi distribution shift: model tự đi vào state mà teacher ít gặp.

DAgger nhẹ:

1. Train BC lần 1.
2. Cho BC+shield chơi.
3. Lưu state mà BC chọn khác rule hoặc bị shield override.
4. Cho rule gán nhãn action.
5. Thêm vào dataset.
6. Train lại.

Tập trung vào state gần bom, sau khi đặt bom, có item gần, có cơ hội attack, hoặc bị loop.

## 13. Inference BC trong submit

```python
state = parse_obs(obs, self.agent_id)
danger = compute_danger_map(state)
safe_mask = compute_safe_mask(state, danger)
x = encode(state)
logits = model(x)
logits[~safe_mask] = -1e9
raw_action = argmax(logits)
action = final_shield(raw_action, state)
return int(action)
```

Không load model trong mỗi `act()`.
