# Huong dan thanh vien A - Tuan 2-3

File nay la checklist lam viec tiep theo cho thanh vien A sau khi da co:

- `rule_v1` chay duoc trong `agent/team_agent/`;
- safety core da co test smoke va engine harness;
- `submit_rule_v1/` da duoc tao de nop thu.

Quy uoc bat buoc:

- Source chinh de phat trien la `agent/team_agent/`.
- Khong sua truc tiep `submit_rule_v1/`; folder do chi la artifact nop thu.
- Moi thay doi safety/API phai co test hoac benchmark kem theo.
- Safety thang scoring. Neu agent tu chet vi bomb cua minh, dung tune strategy va sua safety truoc.

## 1. Vai tro cua A

A la safety/engine/benchmark lead, chiu trach nhiem:

- parse observation dung engine;
- danger map va chain reaction dung;
- BFS thoat bomb dung theo truc thoi gian engine;
- `legal_actions`, `safe_actions`, `can_place_bomb_safely`, `final_shield`;
- harness an toan engine va phan loai death reason;
- feature encoder cho BC/PPO;
- hardening truoc submit va validate folder submit.

Cau hoi A phai tra loi moi ngay:

```text
Agent co chet ngu khong?
Neu chet, chet vi danger map, mask, shield, timeout, hay scorer?
```

## 2. Uu tien ngay

Lam theo thu tu nay:

1. Regression replay cho 6 seed loi tu `data_logs`.
2. Audit `safe_actions` va `final_shield` o cac state truoc khi `safe=[]`.
3. Lam `first_escape_action(...)` hoac helper tuong duong de shield uu tien thoat som khoi blast line.
4. Harden `can_place_bomb_safely` voi cac case dat bom roi bi ep STOP.
5. Chay lai analyzer sau moi fix safety.
6. Harden safety harness len 300 seed.
7. Test agent o du 4 slot `agent_id = 0, 1, 2, 3`.
8. Phan loai death reason trong benchmark/replay.
9. Chuan hoa `person_a_safety/features.py` cho BC.
10. Lam ro semantic cua `safe_distances`.
11. Ho tro B sinh dataset BC nhung khong dua train code vao `act()`.

## 2.1 Tình trạng mới từ data_logs submit_rule_v1

Nguon bao cao:

- `agent/team_agent/reports/data_logs/BAO_CAO_TONG_HOP_948d41ec.md`
- `agent/team_agent/reports/data_logs/VAN_DE_PERSON_A_SAFETY.md`
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
current_code_safety_replay_flag = 6 tran
```

Case safety can xu ly truoc:

- `109659`: own-bomb escape failure, step `86-92`, dat bom `[11,9]`, dung/kẹt quanh `[11,8]`, den luc replay co `safe=[]`, `shielded=STOP`.
- `290518`: own-bomb escape failure, step `321-327`, dat bom `[7,5]`, sau do STOP lien tiep tai `[7,4]`.
- `225587`: own-bomb escape failure, step `218-223`, dat bom `[3,3]`, kẹt `[3,4]`, co bom doi thu chen line.
- `585440`: own-bomb escape failure, step `411-417`, chet trong blast line bom minh radius lon.
- `648293`: own-bomb escape failure, step `126-132`, dat bom `[7,7]`, quay lai blast line.
- `836037`: enemy-bomb trap, step `58-63`, ping-pong trong vung bom doi thu.

Ket luan tam thoi:

- Nhieu replay example co `safe=[]`, `shielded=STOP`; nghia la luc do shield da het move hop le de cuu.
- A khong nen chi sua fallback khi `safe=[]`; can bat dau canh bao/ep escape som hon tu cac step truoc do.
- Death classification trong report van la heuristic, phai xac minh bang replay/harness truoc khi ket luan bug safety tuyet doi.

## 3. API A can chot

Giu on dinh API hien co:

```python
parse_obs(obs, agent_id)
compute_danger_map(state)
legal_actions(state)
safe_actions(state, danger_time)
can_place_bomb_safely(state)
final_shield(action, state, danger_time)
safe_distances(state, danger_time)
```

Them hoac chuan hoa API cho BC:

```python
FEATURE_CHANNELS: tuple[str, ...]
encode_features(state, danger_time=None) -> np.ndarray
```

Feature encoder can tra ve:

```text
shape: (C, 13, 13)
dtype: np.float32
khong doc file
khong goi network
khong tinh qua nang trong act()
```

Channels toi thieu:

```text
wall
box
item_radius
item_capacity
self
opponents
bombs
bomb_timer_norm
danger_time_norm
safe_reachable_cells
```

Neu can, them helper moi thay vi doi semantic helper cu:

```python
safe_relative_distances(state, danger_time, start=None, start_time=0)
first_escape_action(state, danger_time)
```

Ly do: `safe_distances` hien dang gan voi truc thoi gian BFS. Neu caller dung nhu khoang cach tuong doi, can API/doc ro de tranh B score sai.

## 4. Checklist tuan 2

### A1. Safety hardening 300 seed

Can lam:

- Chay engine harness voi 300 seed.
- Luu seed nao fail, step chet, action truoc khi chet.
- Phan loai death:
  - `own_bomb`;
  - `enemy_bomb`;
  - `chain_reaction`;
  - `walked_into_danger`;
  - `self_trap_after_bomb`;
  - `safe_mask_empty`;
  - `timeout_or_invalid_action`;
  - `unknown`.

Definition of done:

```text
own_bomb_deaths = 0
bad_actions = 0
co danh sach seed neu co enemy/unknown death dang chu y
```

### A2. Test du 4 agent_id

Can lam:

- Chay match local voi agent nam o tung slot:

```bash
python -m scripts.participant.run_local_match --agent_paths agent/team_agent None None None --num_episodes 10 --visualize false --seed 1
python -m scripts.participant.run_local_match --agent_paths None agent/team_agent None None --num_episodes 10 --visualize false --seed 1
python -m scripts.participant.run_local_match --agent_paths None None agent/team_agent None --num_episodes 10 --visualize false --seed 1
python -m scripts.participant.run_local_match --agent_paths None None None agent/team_agent --num_episodes 10 --visualize false --seed 1
```

Definition of done:

```text
khong crash
action luon trong [0, 5]
khong co loi import khi agent khong o slot 0
```

### A3. Feature encoder cho BC

Can lam:

- Sua `person_a_safety/features.py`.
- Them `FEATURE_CHANNELS`.
- Them test:
  - shape `(C, 13, 13)`;
  - dtype `np.float32`;
  - agent_id 0-3;
  - bombs rong, mot bomb, nhieu bomb;
  - agent da chet;
  - map co wall, box, item.

Definition of done:

```text
encode_features chay duoc cho moi obs hop le cua engine
feature khong phu thuoc file/log/global mutable state
```

### A4. Ho tro dataset BC

Can cung cap cho B:

```python
features = encode_features(state, danger_time)
safe_mask = safe_actions(state, danger_time)
```

Khong can train model. A chi dam bao feature va mask on dinh, nhanh, test du.

### A8. Regression từ data_logs

Muc tieu:

- Bien cac seed loi trong `data_logs` thanh regression replay co the chay lai sau moi fix.
- Phan biet ro 3 loai:
  - safety sai vi cho action nguy hiem;
  - scorer di vao trap som nhung safety luc do van hop le;
  - state da trapped-before-action, khong con duong cuu that.

Case bat buoc:

- Seed `109659`, steps `86-92`: dat bom o `[11,9]`, dung tai `[11,8]`, chet do own bomb.
- Seed `225587`, steps `218-223`: dat bom `[3,3]`, ket `[3,4]`, co enemy bomb trong cung blast line.
- Seed `648293`, steps `126-132`: dat bom `[7,7]`, quay lai blast line truoc khi bom no.
- Seed `836037`, steps `58-63`: ping-pong trong vung bom doi thu.

Can lam:

- Reconstruct obs tu log tai tung step can xem.
- Chay `parse_obs`, `compute_danger_map`, `safe_actions`, `final_shield`.
- Luu bang:
  - `step`;
  - `pos`;
  - `logged_action`;
  - `safe_actions`;
  - `shielded_action`;
  - `danger_time[self_pos]`;
  - `death_class`.
- Neu `safe=[]`, truy nguoc 3-8 step truoc do de tim action dau tien lam mat duong thoat.

Definition of done:

```text
replay khong con den trang thai safe=[] muon ma khong co canh bao truoc
neu khong co duong thoat that, report phai phan loai trapped-before-action
own_bomb_escape_failure trong log regression giam ve 0 hoac co giai thich khong the cuu
```

## 5. Checklist tuan 3

### A5. Benchmark hardening lon

Can lam:

- Chay 500-1000 tran cho version ung vien.
- Do rieng:
  - average rank;
  - win/top2;
  - death before 50/100/200;
  - self-death;
  - survive to 500;
  - p95/p99/max latency.

Definition of done:

```text
co bang metric de chon version
khong ket luan bang replay don le
```

### A6. Step 500 analysis

Can lam:

- Loc tran ket thuc o step 500.
- Dem agent song.
- So tie-break: kills, boxes, items, bombs.
- Bao cho B neu agent song lau nhung thua tie-break.

Output mong doi:

```text
step500_tiebreak_rank
step500_tiebreak_win_rate
ly do thua tie-break neu co
```

### A7. Submit hardening

Khi B chot version:

- Tao folder `submit_rule_v2/` hoac `submit_bc_v1/` tu source chinh.
- Root folder submit phai co `agent.py`.
- Tong file <= 20.
- Khong copy:
  - tests;
  - bench;
  - train;
  - README;
  - `requirements.txt`;
  - `__pycache__`.

Validate zip sau khi dong goi:

```bash
python -c "from pathlib import Path; from competition.ingestion.collector import validate_zip_bytes; ok, reason, manifest = validate_zip_bytes(Path('submission.zip').read_bytes()); print(ok, reason, manifest)"
```

## 6. Lenh bat buoc

Chay nhanh:

```bash
python -m pytest agent/team_agent/smoke_tests
python -m compileall agent/team_agent
```

Safety harness:

```bash
TEAM_SAFETY_SEEDS=300 python -m pytest agent/team_agent/smoke_tests/test_engine_safety.py -q -s
```

Timing:

```bash
python -m scripts.participant.estimate_agent_time agent/team_agent --opponents None None None --num_matches 5
```

Match sanity:

```bash
python -m scripts.participant.run_local_match --agent_paths agent/team_agent None None None --num_episodes 20 --visualize false --seed 1
```

Data log analyzer:

```bash
python agent/team_agent/bench/analyze_data_logs.py --log-dir agent/data_logs --team-id 948d41ec-3dbd-4840-9ee5-f0d01cc1b6c0 --out-dir agent/team_agent/reports/data_logs
```

## 7. Khong duoc submit neu

- `act()` crash.
- Action ngoai `[0, 5]`.
- `own_bomb_deaths > 0` trong harness.
- p99 gan hoac vuot 100ms.
- `final_shield` bi bypass.
- Feature/model load file trong moi `act()`.
- Chua benchmark toi thieu 50 tran cho version moi.

## 8. Version can giu

Khong ghi de version cu neu chua benchmark version moi.

Can giu:

```text
rule_v1_safe
rule_v2_candidate
rule_v2_best
bc_v1_best neu co
submit_final
```

## 9. Definition of done cua A den cuoi tuan 3

```text
pytest pass
compileall pass
engine safety harness 300 seed pass own_bomb_deaths = 0
data_logs regression khong con own_bomb_escape_failure chua giai thich
current-code replay unsafe actions da duoc phan loai: safety qua chat, scorer vao trap som, hay log tu code submit cu
feature encoder san sang cho BC
benchmark/report co p95/p99 latency
submit folder cua version chot validate pass
```
