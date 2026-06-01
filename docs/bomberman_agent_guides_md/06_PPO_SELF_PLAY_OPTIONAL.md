# 06 — PPO và self-play: phần optional

PPO/self-play chỉ nên làm khi rule safety + benchmark + BC đã ổn. Nếu còn ít thời gian, ưu tiên hardening rule/hybrid hơn.

## 1. PPO là gì?

PPO = Proximal Policy Optimization. PPO học trực tiếp policy:

```text
state → xác suất chọn từng action
```

PPO thường dùng Actor-Critic:

- Actor chọn action;
- Critic đánh giá state tốt/xấu.

## 2. Vì sao PPO rủi ro trong Bomberman?

Bomberman có:

- reward trễ;
- random exploration dễ tự sát;
- multi-agent không ổn định;
- tie-break phức tạp;
- sparse reward.

Nếu train PPO không mask, agent dễ học:

- đặt bom ngu;
- đứng yên để sống;
- spam hành động;
- train reward tăng nhưng rank giảm.

## 3. Điều kiện bắt đầu PPO

Chỉ bắt đầu khi có:

```text
rule agent tốt
BC init hoặc policy init ổn
benchmark harness
opponent pool cơ bản
log replay
safety shield chắc
```

Nếu thiếu, PPO rất dễ tốn thời gian nhưng không ra kết quả.

## 4. Masked PPO

Trước khi sample action:

```python
logits = policy(obs)
logits[~safe_mask] = -1e9
dist = Categorical(logits=logits)
action = dist.sample()
```

Khi submit thường dùng deterministic:

```python
action = argmax(masked_logits)
action = final_shield(action, state)
```

## 5. Reward shaping sau tie-break mới

Gợi ý reward khởi điểm:

```python
reward = 0
reward += 1.0 * boxes_destroyed_this_step
reward += 1.5 * items_collected_this_step
reward += 8.0 * kills_this_step

if died:
    reward -= 20.0
if self_death:
    reward -= 40.0
if died and step < 100:
    reward -= 10.0

reward += 0.001 * alive_this_step
reward -= 0.001  # chống stall rất nhẹ
```

Cuối trận thêm terminal rank reward:

```python
if final_rank == 1:
    reward += 20
elif final_rank == 2:
    reward += 8
elif final_rank == 3:
    reward -= 5
else:
    reward -= 15
```

Không thưởng trực tiếp mọi lần đặt bom. Nếu muốn, chỉ thưởng nhẹ `useful bomb`:

```text
+0.2 đến +0.5 nếu bom phá box hoặc tạo threat và agent có escape path
```

## 6. Tránh reward hacking

| Reward sai | Hành vi xấu |
|---|---|
| thưởng sống quá cao | camping |
| thưởng bomb placed | spam bom |
| thưởng item quá cao | chase item qua danger |
| phạt death quá nhẹ | đánh liều |
| không terminal rank | farm tốt nhưng rank thấp |

Cách chống:

- benchmark bằng rank, không chỉ reward;
- reward sống rất nhỏ;
- không thưởng bomb placed bừa;
- phạt self-death rất nặng;
- shield luôn bật.

## 7. Opponent pool

Pool nên gồm:

```text
random_agent
camper_agent
farmer_agent
aggressive_agent
rule_defensive
rule_aggressive
baseline BTC
bc_v1
ppo snapshots cũ
```

Mỗi trận:

```text
current_agent + 3 opponents sample từ pool
```

Phải có camper để đảm bảo agent học farm/tie-break, không chỉ học né.

## 8. Chọn checkpoint PPO

Không chọn theo training reward. Chọn theo:

```text
average rank tốt hơn rule/BC
self-death không tăng
step500 tie-break tốt hơn
box/item/kills ổn
p99 latency ổn
```

Nếu PPO không vượt rule rõ ràng, submit rule/hybrid.

## 9. Model size

Khi submit chỉ cần actor nhỏ:

```text
CNN nhỏ hoặc MLP nhỏ
output 6 logits
không ensemble nặng
không critic nếu không cần
```

Critic chỉ dùng lúc train.

## 10. Dấu hiệu nên dừng PPO

Dừng hoặc rollback nếu:

- self-death tăng;
- rank giảm dù reward tăng;
- agent spam bom;
- agent camping;
- latency tăng;
- PPO làm mất hành vi farm của rule/BC.

## 11. MAPPO/CTDE có nên làm không?

Không khuyến khích cho team ít kinh nghiệm. Setup phức tạp, debug khó, dễ không kịp. Với cuộc thi mỗi đội submit một agent, self-play/IPPO đơn giản hơn nhiều.

## 12. MCTS/lookahead có nên làm không?

Chỉ optional, rất nông:

```text
top 2–3 action
depth 1–2
heuristic eval
```

Chỉ bật nếu A/B benchmark cải thiện và p99 latency vẫn < 100ms.
