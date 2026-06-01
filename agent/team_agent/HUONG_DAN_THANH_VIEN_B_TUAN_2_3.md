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

1. Dung analyzer report lam baseline rule_v1 khi so rule_v2.
2. Sua anti-loop/anti-camping truoc khi tune farm sau.
3. Giam diem STOP theo streak cuc bo, tru khi STOP la action safe duy nhat.
4. Phat `PLACE_BOMB` neu sau bomb escape-space thap hoac de bi ep STOP.
5. Tang progress target khi step > 350 de cai thien tie-break.
6. Phan tich ket qua submit thu `submit_rule_v1`.
7. Benchmark `rule_v1` bang fixed seeds de lam baseline.
8. Tune `rule_v2` trong source chinh `agent/team_agent/`.
9. Giam bomb spam, tang useful bomb ratio.
10. Cai thien step500 tie-break.
11. Chi bat dau BC khi `rule_v2` da co metric tot hoac it nhat on dinh hon `rule_v1`.

## 2.1 Tình trạng mới từ data_logs submit_rule_v1

Nguon bao cao:

- `agent/team_agent/reports/data_logs/BAO_CAO_TONG_HOP_948d41ec.md`
- `agent/team_agent/reports/data_logs/VAN_DE_PERSON_B_STRATEGY.md`
- `agent/team_agent/reports/data_logs/TIMELINE_CAC_TRAN_QUAN_TRONG.md`

Metric hien tai cua 12 tran log:

```text
average_rank = 2.00
survived_to_step500 = 6/12
died_before_step500 = 6/12
early_death_before_step150 = 3/12
stop_streak_ge_20 = 6/12
own_bomb_escape_failure = 5 case
enemy_bomb_trap = 1 case
safety_replay_flag = 6 tran
```

Van de strategy noi bat:

- STOP/camping qua dai:
  - seed `548846`: max STOP `74`;
  - seed `225587`: max STOP `115`;
  - seed `609286`: max STOP `255`.
- Lap A-B-A-B bi flag o `11/12` tran.
- Song toi step 500 nhung tie-break yeu:
  - seed `548846`;
  - seed `126779`.
- Dat bom qua it:
  - seed `156663`;
  - seed `225587`;
  - seed `609286`.
- Mot so death xay ra sau khi dat bom roi khong thoat du xa; B can giam score bomb neu sau do agent de bi ep STOP.

Ket luan tam thoi:

- Neu A dang sua safety, B van phai giam xac suat dua agent vao trap som.
- Rule_v2 can uu tien anti-loop va progress truoc; neu chi tang farm/pressure se lam own-bomb death nang hon.
- `data_logs` la baseline hanh vi that cua rule_v1, nhung khong thay the benchmark 50-100 tran.

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

### B8. Rule_v2 theo data_logs

Muc tieu:

- Sua nhung hanh vi da thay trong 12 log truoc khi mo rong sang BC/PPO.
- Giu survival khong kem rule_v1, nhung giam camping va cai thien tie-break.

Tasks:

- Chong STOP streak:
  - phat STOP theo streak cuc bo khi `recent_stop_count >= 3`;
  - muc tieu max STOP streak < `20` tren 12 log hien tai;
  - STOP chi duoc giu diem cao neu no la action safe duy nhat hoac dang doi fire het.
- Chong ping-pong:
  - phat quay lai cell cach 2 step neu khong co danger;
  - neu A-B-A-B lap nhieu lan, day agent toi farm/item target gan nhat co safe path.
- Bomb escape quality:
  - truoc khi cong `box_bomb`, kiem tra sau dat bom co it nhat mot escape route co buffer;
  - phat `PLACE_BOMB` neu target value thap va sau do de bi ep STOP;
  - rieng cac seed own-bomb death, replay scoring quanh step dat bom de xem component nao thang.
- Late tie-break:
  - neu step > `350`, nhieu opponent con song va proxy rank kem, tang farm/pressure thay vi STOP;
  - neu khong con farm target tot, uu tien mobility va pressure an toan.
- Useful bomb ratio:
  - giam no-value bomb o seed `126779`;
  - giu hoac tang useful bombs o cac seed song lau;
  - khong tang avg_bombs neu avg_boxes/items/kills khong tang.

Acceptance rule_v2 theo log:

```text
survived_to_step500 >= 6/12
death_before_step150 < 3/12
own_bomb_death khong tang
max STOP streak giam ro o seed 225587 va 609286
seed 548846 va 126779 cai thien rank hoac tang proxy box/item/bomb value
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

Analyze data_logs baseline:

```bash
python agent/team_agent/bench/analyze_data_logs.py --log-dir agent/data_logs --team-id 948d41ec-3dbd-4840-9ee5-f0d01cc1b6c0 --out-dir agent/team_agent/reports/data_logs
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
- analyzer van bao `own_bomb_escape_failure` tang;
- STOP streak >= `100` con xuat hien o nhieu seed;
- song toi 500 nhung rank/proxy tie-break khong cai thien so voi rule_v1;
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
data_logs analyzer cho thay STOP streak va own-bomb trap khong te hon rule_v1
p99 latency < 100ms
BC duoc benchmark neu da train
co bang version selection de chot submit_final
```
