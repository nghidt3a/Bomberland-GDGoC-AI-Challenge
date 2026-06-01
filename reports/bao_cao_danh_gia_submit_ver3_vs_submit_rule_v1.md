# Bao cao danh gia `submit_ver3` vs `submit_rule_v1`

## Ket luan nhanh

Nen chon **`submit_ver3`** lam ban nop tiep theo.

Ly do chinh: `submit_ver3` vuot `submit_rule_v1` rat ro o hanh vi thi dau, do an toan, packaging va toc do inference. `submit_rule_v1` khong co loi syntax/timing nghiem trong, nhung benchmark cho thay agent gan nhu khong tao tien trien: ti le chet 100% trong hai dai seed da chay, `boxes/items/bombs` deu bang 0.

`submit_ver3` khong phai ban da toi uu hoan toan: ti le draw con cao va kill rate con thap. Tuy vay, day la ban on dinh va co kha nang canh tranh hon nhieu: song gan het tran, farm box/item tot, dat bomb chu dong, va van nam duoi nguong timeout 100ms.

## Pham vi danh gia

- Hai thu muc duoc danh gia:
  - `submit_ver3/`
  - `submit_rule_v1/`
- Doi thu benchmark:
  - `TacticalRuleAgent`
  - `SmarterRuleAgent`
  - `GeniusRuleAgent`
- Vi tri agent trong benchmark: player 0.
- Gioi han moi tran: 500 steps.
- Luu y ve metric: `self_death_rate` trong `agent.team_agent.bench.strategy_metrics` duoc tinh la ti le agent player 0 chet truoc/khi ket thuc tran. Ten metric co chu "self", nhung khong tach rieng nguyen nhan tu sat bang bomb.

## Kiem tra packaging va interface

### `submit_ver3`

`submit_ver3/submission.zip` chi chua:

```text
agent.py
```

Diem manh:

- `agent.py` da bundle thanh one-file, giam rui ro evaluator chi load root `agent.py` nhung khong thay package helper.
- Van giu source module `person_a_safety/` va `person_b_strategy/` trong thu muc de audit, nhung file zip nop that gon hon.
- Interface dung yeu cau: co class `Agent`, `Agent(agent_id)`, va `act(obs) -> int`.

### `submit_rule_v1`

`submit_rule_v1/submission.zip` chua:

```text
agent.py
person_a_safety/
person_b_strategy/
```

Diem chap nhan duoc:

- Co dung `agent.py` o root zip.
- Chi co mot file `agent.py`.
- Cac helper module di kem trong zip nen ve mat local import co the chay duoc.

Rui ro:

- Phu thuoc viec evaluator giu dung cau truc folder helper va cho import tu thu muc submission.
- So voi one-file bundle cua `submit_ver3`, packaging nay de bi loi hon neu moi truong cham chi uu tien load `agent.py` root hoac copy file theo cach toi gian.

## So sanh ky thuat

### Loi an toan va danger map

`submit_rule_v1` dung `compute_danger_map(state) -> danger_time[r, c]`, tuc moi o chi luu thoi diem chay som nhat. Cach nay don gian nhung co loi mo hinh: mot o co the bi nhieu bomb quet qua o nhieu tick khac nhau. Khi chi luu "lan chay som nhat", BFS co the tin rang o do da an toan sau lan chay dau, trong khi thuc te o do co the chay lai ve sau.

`submit_ver3` chuyen sang `compute_hazard_map(state) -> hazard[t, r, c]`. Cach nay luu nguy hiem theo tung tick, nen safety/search nhin duoc moi lan chay cua tung o. Ban nay cung mo phong:

- chain reaction theo fix-point trong cung tick;
- box bi pha sau tick hien tai, cho phep bomb no muon lan xa hon qua box da bien mat;
- cache blast theo tick de giu timing tot.

Tac dong: `submit_ver3` an toan hon trong cac tinh huong nhieu bomb, chain reaction, va duong thoat phu thuoc vao timing.

### Dat bomb va thoat sau bomb

`submit_rule_v1` chi can co duong thoat sau khi dat bomb theo danger map earliest-time. Do danger map mat thong tin "chay lai", agent co the danh gia qua lac quan trong mot so trang thai.

`submit_ver3` yeu cau duong thoat sau bomb phai den duoc o an toan ben vung trong horizon: `has_permanent_escape_after_bomb` kiem tra target khong bi chay lai trong hazard tensor. Dieu nay bao thu hon, nhung phu hop muc tieu submit: song sot truoc, ghi diem sau.

### Scoring va chien luoc

`submit_rule_v1` co scoring farm/item/pressure, nhung thuc te benchmark cho thay policy bi ket o trang thai thu dong:

- khong pha box;
- khong nhat item;
- khong dat bomb;
- chet truoc khi tao gia tri.

Mot nguyen nhan quan trong trong source: `box_move_score` cua `submit_rule_v1` khong loai `STOP`, nen dung yen canh box van co the duoc tinh nhu dang co gia tri farming. Viec nay khuyen khich camp/STOP thay vi di chuyen hoac dat bomb co ich.

`submit_ver3` sua diem nay va them nhieu thanh phan scoring chu dong hon:

- `STOP` khong con duoc tinh diem farm box;
- co trap score dua tren so o thoat cua doi thu bi mat sau khi dat bomb;
- co enemy risk/corridor risk de tranh bi ap sat trong vi tri chat;
- co item contest risk de tranh tranh item khi doi thu den nhanh hon;
- co phase late-game theo proxy score de chon phong thu/ruot duoi.

### Timing va do phuc tap

Mac du `submit_ver3` co logic hazard map phong phu hon, benchmark timing ngan cho thay ban nay nhanh hon `submit_rule_v1`. Nguyen nhan co kha nang den tu viec toi uu lai shield/safe mask, tranh recompute thua, va cache blast khi mo phong hazard.

## Benchmark hanh vi

Lenh benchmark:

```powershell
python -m agent.team_agent.bench.strategy_metrics --agent-path submit_ver3 --opponents TacticalRuleAgent SmarterRuleAgent GeniusRuleAgent --num-episodes 20 --max-steps 500 --seed 1
python -m agent.team_agent.bench.strategy_metrics --agent-path submit_rule_v1 --opponents TacticalRuleAgent SmarterRuleAgent GeniusRuleAgent --num-episodes 20 --max-steps 500 --seed 1
python -m agent.team_agent.bench.strategy_metrics --agent-path submit_ver3 --opponents TacticalRuleAgent SmarterRuleAgent GeniusRuleAgent --num-episodes 16 --max-steps 500 --seed 50
python -m agent.team_agent.bench.strategy_metrics --agent-path submit_rule_v1 --opponents TacticalRuleAgent SmarterRuleAgent GeniusRuleAgent --num-episodes 16 --max-steps 500 --seed 50
```

### Seed 1, 20 tran

| Ban | Win rate | Draw rate | Death rate | Avg survival | Avg rank | Avg kills | Avg boxes | Avg items | Avg bombs |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `submit_rule_v1` | 0.000 | 0.000 | 1.000 | 81.200 | 2.200 | 0.000 | 0.000 | 0.000 | 0.000 |
| `submit_ver3` | 0.050 | 0.900 | 0.050 | 464.050 | 0.050 | 0.200 | 7.550 | 8.350 | 49.300 |

Nhan xet:

- `submit_rule_v1` chet ca 20/20 tran va khong co bat ky chi so tien trien nao.
- `submit_ver3` song trung binh 464/500 steps, draw 90%, va da co kha nang farm/item/bomb ro rang.
- Avg rank cua `submit_ver3` gan 0, tuc thuong nam trong nhom song den cuoi hoac chien thang.

### Seed 50, 16 tran

| Ban | Win rate | Draw rate | Death rate | Avg survival | Avg rank | Avg kills | Avg boxes | Avg items | Avg bombs |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `submit_rule_v1` | 0.000 | 0.000 | 1.000 | 113.062 | 1.875 | 0.000 | 0.000 | 0.000 | 0.000 |
| `submit_ver3` | 0.188 | 0.688 | 0.125 | 427.375 | 0.312 | 0.375 | 8.250 | 7.750 | 49.750 |

Nhan xet:

- Ket qua seed 50 xac nhan xu huong cua seed 1, khong phai do may man mot dai seed.
- `submit_ver3` co win rate cao hon, nhung draw van la ket qua pho bien. Day la diem can toi uu tiep neu muon tang TrueSkill nhanh hon.
- `submit_rule_v1` van khong farm, khong item, khong bomb.

## Benchmark timing

Lenh benchmark:

```powershell
python -m scripts.participant.estimate_agent_time submit_ver3 --opponents TacticalRuleAgent SmarterRuleAgent GeniusRuleAgent --num_matches 5 --seed 1
python -m scripts.participant.estimate_agent_time submit_rule_v1 --opponents TacticalRuleAgent SmarterRuleAgent GeniusRuleAgent --num_matches 5 --seed 1
```

| Ban | So tran | Active steps | Avg time/step | Max spike | Ket luan timeout |
|---|---:|---:|---:|---:|---|
| `submit_rule_v1` | 5 | 2094 | 20.09 ms | 76.30 ms | Pass 100ms |
| `submit_ver3` | 5 | 2205 | 8.10 ms | 28.32 ms | Pass 100ms |

Nhan xet:

- Ca hai ban deu duoi nguong 100ms/step trong phep do nay.
- `submit_ver3` nhanh hon ro ret, du logic an toan day du hon.
- `submit_rule_v1` pass timing nhung that bai ve quality hanh vi, nen khong nen dung lam ban nop chinh.

## Kiem tra syntax va smoke tests

Lenh da chay:

```powershell
python -m compileall submit_ver3 submit_rule_v1
python -m pytest agent\team_agent\smoke_tests -q
```

Ket qua:

```text
65 passed in 54.21s
```

Y nghia:

- Hai thu muc submission parse/compile duoc.
- Bo smoke tests cua `agent/team_agent` pass, bao gom cac kiem tra safety, masks, search, danger, strategy va action mapping hien co.
- Luu y: smoke tests chu yeu bao phu source team agent/hien trang ver3; ket qua benchmark rieng van la bang chung quan trong nhat khi so sanh voi `submit_rule_v1`.

## Rui ro con lai cua `submit_ver3`

- Draw rate con cao: seed 1 draw 90%, seed 50 draw 68.8%. Agent song tot nhung chua ket lieu tran du manh.
- Avg kills con thap: 0.200 va 0.375 theo hai dai seed. Nen tang kha nang trap/pressure co chon loc neu muon leo leaderboard nhanh hon.
- Chien luoc van thien ve safety/farming. Day la huong dung cho ban nop on dinh, nhung co the bi cac agent tan cong manh ep draw hoac gianh diem kill.
- Hazard map uoc luong radius cua bomb theo radius hien tai cua owner vi observation khong expose radius tai thoi diem dat bomb. Day la bias an toan, co the lam agent qua bao thu trong mot so tinh huong.

## Khuyen nghi nop bai

1. Nop **`submit_ver3/submission.zip`** thay vi `submit_rule_v1/submission.zip`.
2. Giu `submit_rule_v1` lam baseline lich su, khong dung lam candidate chinh.
3. Truoc khi nop that, nen chay them mot lan timing 10 tran va local match 20-50 tran neu con thoi gian.
4. Huong cai tien tiep theo cho `submit_ver3`:
   - giam draw bang trap/kill decision tot hon o late game;
   - them benchmark theo nhieu vi tri player, khong chi player 0;
   - ghi lai action distribution de theo doi STOP/bomb/move ratio sau moi lan chinh weight;
   - chay seed band lon hon de uoc luong on dinh TrueSkill.

## Acceptance checklist

- [x] Co ket luan ro rang.
- [x] Co so sanh packaging.
- [x] Co so sanh source/ky thuat.
- [x] Co bang benchmark hanh vi cho seed 1 va seed 50.
- [x] Co timing benchmark va doi chieu nguong 100ms.
- [x] Co ghi lai lenh kiem tra da chay.
- [x] Co neu rui ro con lai va khuyen nghi nop bai.

