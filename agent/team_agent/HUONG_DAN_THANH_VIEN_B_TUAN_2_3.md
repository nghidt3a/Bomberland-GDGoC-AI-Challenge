# Huong dan thanh vien B - Tuan 2-3

File nay la checklist lam viec tiep theo cho thanh vien B sau khi da co:

- `rule_v1` trong `agent/team_agent/person_b_strategy/`;
- safety core cua A da co engine harness;
- `submit_rule_v1/` da duoc tao de nop thu.

Quy uoc bat buoc:

- Source chinh de phat trien la `agent/team_agent/`.
- Khong sua truc tiep `submit_rule_v1/`; folder do chi la artifact nop thu.
- B chi de xuat action trong `safe_mask`.
- Action cuoi cung van phai qua `final_shield`.
- Moi thay doi scoring/BC/PPO phai co benchmark, khong chi xem mot replay.

## 1. Vai tro cua B

B la strategy/scoring/ML lead, chiu trach nhiem:

- rule scorer va `rule_v2`;
- tie-break strategy;
- anti-loop/anti-camping;
- behavior theo phase early/mid/late;
- dataset/train/inference cho BC;
- PPO optional neu rule/BC da on;
- bang benchmark va chon version.

Cau hoi B phai tra loi moi ngay:

```text
Agent co chu dong hon khong?
Average rank co tot hon khong?
Farm/item/kill co tang ma self-death khong tang khong?
```

## 2. Uu tien ngay

Lam theo thu tu nay:

1. Phan tich ket qua submit thu `submit_rule_v1`.
2. Benchmark `rule_v1` bang fixed seeds de lam baseline.
3. Tune `rule_v2` trong source chinh `agent/team_agent/`.
4. Giam bomb spam, tang useful bomb ratio.
5. Cai thien step500 tie-break.
6. Chi bat dau BC khi `rule_v2` da co metric tot hoac it nhat on dinh hon `rule_v1`.

## 3. Bat bien safety

Khong duoc lam cac viec nay:

- tu tinh danger map rieng trong B;
- cho phep action ngoai `safe_mask`;
- dat bomb chi vi score cao ma khong qua safety cua A;
- print lien tuc trong `act()`;
- train/load model trong moi `act()`;
- sua `submit_rule_v1/` roi tuong do la source chinh.

Flow bat buoc:

```text
obs
-> A parse/danger/safe_mask
-> B RulePolicy/BC/PPO de xuat raw_action
-> A final_shield
-> return action
```

## 4. Rule_v2 tasks

### B1. Lap baseline metric cho rule_v1

Can chay:

```bash
python agent/team_agent/bench/strategy_metrics.py --num-episodes 100 --seed 1
python agent/team_agent/bench/strategy_metrics.py --num-episodes 100 --seed 101 --opponents None None None
python agent/team_agent/bench/benchmark.py --num-matches 50
```

Can ghi bang:

```text
Version | AvgRank | Win | Top2 | SelfDeath | Box | Item | Kill | Bomb | p99ms
rule_v1
```

Definition of done:

```text
co so lieu baseline truoc khi tune
khong tune theo cam giac
```

### B2. Tune farm/item theo tie-break

Muc tieu:

- Boxes la tie-break quan trong sau kills.
- Items giup manh len nhung khong chase qua danger.
- Bombs placed la tie-break cuoi, khong duoc spam.

Can lam trong `person_b_strategy/scoring.py`:

- Tang diem `box_bomb` khi bomb pha duoc box va co escape.
- Tang diem di toi farm target neu target gan va gain cao.
- Giam item chase khi:
  - item qua xa;
  - dang co farm target tot hon;
  - dang trong/gan danger.
- Phat bomb vo ich manh hon neu bomb khong pha box, khong pressure, khong mo duong.

Metric mong doi:

```text
avg_boxes tang
avg_items khong giam manh
self_death khong tang
avg_bombs khong tang vo ly
```

### B3. Improve proxy tracker

Can lam trong `loop_tracker.py` va `policy_rule.py`:

- Track proxy:
  - `estimated_boxes_destroyed`;
  - `estimated_items_collected`;
  - `estimated_bombs_placed`;
  - `estimated_kills`;
  - `steps_without_progress`;
  - `recent_target_cell`.
- Progress duoc tinh khi:
  - box count giam sau bomb cua minh;
  - self radius/capacity tang;
  - dat bomb huu ich;
  - tien gan farm/item target;
  - opponent chet gan thoi diem bomb cua minh no.

Dung proxy de:

- neu dang dan tie-break late game: tang survival/mobility;
- neu dang thua late game: tang farm/pressure co kiem soat;
- neu loop lau: day toi farm/item target gan nhat.

### B4. Pressure/attack co kiem soat

Chi cong pressure khi:

- action la `PLACE_BOMB`;
- `safe_mask[PLACE_BOMB] == True`;
- opponent trong blast line clear, corridor, hoac it escape cells;
- khong hy sinh farm target tot o early game.

Phase:

```text
early 0-150: attack chi khi gan nhu free
mid 150-350: pressure co kiem soat
late 350-500: neu thua proxy thi pressure cao hon
```

Metric mong doi:

```text
avg_kills tang nhe
self_death khong tang
avg_rank tot hon hoac khong giam
```

### B5. Step500 tie-break

Can lam:

- Dung proxy tracker de biet minh co dang camping khong.
- Neu step > 350 va nhieu opponent con song:
  - uu tien box/item neu con an toan;
  - dat bomb huu ich de mo box/pressure;
  - khong STOP/lap loop neu khong danger.

Acceptance:

```text
survive_to_500_rate cao nhung step500_tiebreak_rank khong thap
neu song toi 500 thi boxes/items/bombs phai co tien do
```

## 5. Behavior Cloning tasks

Chi bat dau khi:

```text
rule_v2 chay 100+ tran khong crash
self-death thap
p99 < 100ms
farm/item tot hon rule_v1 hoac average rank tot hon
```

### B6. Dataset

Nang `train/gen_dataset.py` de luu moi sample:

```python
{
    "features": encode_features(state, danger_time),
    "teacher_action": final_action,
    "safe_mask": safe_mask,
    "agent_id": agent_id,
    "step": step,
}
```

Dataset can co:

- du 4 `agent_id`;
- opponents mixed pool;
- danger states;
- post-bomb escape states;
- item/farm opportunities;
- oversample `PLACE_BOMB`.

Khong dua dataset vao submit.

### B7. Train BC nho

Model de xuat:

```text
Conv2D(C -> 32, kernel 3)
ReLU
Conv2D(32 -> 64, kernel 3)
ReLU
Flatten
Linear -> 128
ReLU
Linear -> 6 logits
```

Metric train:

```text
overall accuracy
PLACE_BOMB accuracy
danger-state accuracy
escape-state accuracy
```

Inference:

```text
logits
-> mask unsafe action bang safe_mask
-> argmax
-> final_shield
```

BC chi duoc submit neu benchmark khong thua rule ro rang.

## 6. PPO optional

Chi lam PPO khi:

```text
rule_v2 tot
BC chay duoc
benchmark harness on
con du thoi gian
```

Yeu cau PPO:

- init tu BC neu co;
- masked logits bang `safe_mask`;
- reward theo terminal rank;
- phat self-death rat nang;
- khong thuong bomb placed bua bai;
- benchmark checkpoint dinh ky.

Bo PPO neu:

- average rank thua rule;
- self-death tang;
- spam bomb;
- camping;
- p99 latency tang.

## 7. Lenh bat buoc

Smoke:

```bash
python -m pytest agent/team_agent/smoke_tests
python -m compileall agent/team_agent
```

Benchmark rule:

```bash
python agent/team_agent/bench/strategy_metrics.py --num-episodes 100 --seed 1
python agent/team_agent/bench/benchmark.py --num-matches 50
```

Match voi baseline manh:

```bash
python -m scripts.participant.run_local_match --agent_paths agent/team_agent TacticalRuleAgent SmarterRuleAgent GeniusRuleAgent --num_episodes 20 --visualize false
```

Timing:

```bash
python -m scripts.participant.estimate_agent_time agent/team_agent --opponents None None None --num_matches 5
```

## 8. Khong duoc submit version moi neu

- crash hoac import fail;
- action ngoai `[0, 5]`;
- p99 gan/vuot 100ms;
- self-death tang ro;
- benchmark duoi 50 tran;
- chi thang random nhung thua baseline manh qua ro;
- BC/PPO rank kem rule nhung van muon submit vi loss/reward dep.

## 9. Version can giu

Khong ghi de version cu neu chua benchmark version moi.

Can giu:

```text
rule_v1_safe
rule_v2_candidate
rule_v2_best
bc_v1_best neu co
ppo_best neu that su vuot benchmark
submit_final
```

Bang chon version cuoi:

```text
Version | AvgRank | Win | Top2 | SelfDeath | Box | Item | Kill | Bomb | Step500Rank | p99ms | Pick
rule_v1
rule_v2
bc_v1
ppo_best
```

## 10. Definition of done cua B den cuoi tuan 3

```text
rule_v2 co benchmark tot hon hoac on dinh hon rule_v1
self-death khong tang
boxes/items/kills hoac step500 rank cai thien
p99 latency < 100ms
BC duoc benchmark neu da train
co bang version selection de chot submit_final
```
