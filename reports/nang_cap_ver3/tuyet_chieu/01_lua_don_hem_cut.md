# 01 — Lùa/dồn địch vào hẻm cụt (herding nhiều bước)

## 1. TL;DR

- **Verdict**: ver3 chỉ trap **phản ứng 1-bước** (`trap_score` khi đặt bom NGAY); chưa **chủ động lùa** địch về hẻm cụt qua nhiều bước. Thêm `herd_score` (điểm cho nước MOVE) để dựng thế trap.
- **ROI cao** (tạo kill), công sức/rủi ro trung bình. Cần mô hình địch rẻ.
- ⚠️ **Cơ chế quan trọng**: trong engine, **agent KHÔNG chặn nhau** (nhiều agent đứng cùng ô, nổ xuyên qua agent — xem [engine/game.py](../../../engine/game.py)). ⇒ Không thể "lùa" bằng cách lấy thân chặn đường; **lùa = hình học đe doạ bom** (đứng ở phía mở để bom của mình bịt lối, ép địch lùi sâu vào hẻm cụt).
- **Go/no-go**: kills↑ trên benchmark đúng luật, draw/death không xấu đi; self-death=0.

## 2. Chiêu là gì & closes gap nào

Lùa địch vào vùng ít lối thoát rồi mới ra đòn (bom/seal/chain). Đánh trúng gap **kill thấp**: ver3 chờ địch *tự* vào thế bí mới `trap_score`; herding **chủ động tạo** thế bí. Nó là bước "dựng thế" feed cho [02 bịt hành lang](02_bit_hanh_lang_2_bom.md), `trap_score`, và [chain 06](../06_chain_bomb_offensive.md).

## 3. ver3 đã có gì (gap)

- [trap_score / enemy_escape_count](../../../agent/team_agent/person_b_strategy/scoring.py): đo ô thoát địch mất **khi đặt bom ngay** — không có khái niệm "đi vài bước để dồn".
- [positional_risk](../../../agent/team_agent/person_b_strategy/scoring.py): chỉ phạt **mình** đứng sát địch trong hẻm — ngược hướng (phòng thủ), không phải tấn công.
- Không có điểm thưởng cho nước MOVE theo mục tiêu kiểm soát không gian địch.

## 4. Thiết kế tích hợp (build-ready)

Thêm `herd_score(state, action, next_pos, hazard, ctx)` trong [scoring.py](../../../agent/team_agent/person_b_strategy/scoring.py), cộng vào component mới `"herd_bonus"` cho **action MOVE** (không phải PLACE_BOMB); weight `herd` trong `ScoreWeights`, cao hơn ở `mid`/`late_chasing`.

```python
def herd_score(state, action, next_pos, hazard):
    if action in (STOP, PLACE_BOMB) or not state.opponents:
        return 0.0
    enemy = min(state.opponents, key=lambda e: manhattan(next_pos, e))
    area = enemy_reachable_area(state, enemy, hazard, horizon=6)   # opponent_model
    if len(area) > CORNER_CAP:          # địch chưa ở thế cornerable -> chưa lùa
        return 0.0
    choke = exit_choke(area, state)      # ô nối vùng địch ra map mở (articulation)
    if choke is None:
        return 0.0
    # thưởng khi nước đi đưa MÌNH tới "phía mở" của choke (để bom sau bịt được)
    # và vẫn trong tầm doạ bom của địch
    closer = manhattan(next_pos, choke) < manhattan(state.self_pos, choke)
    in_threat = manhattan(next_pos, enemy) <= state.self_radius + 2
    score = 0.0
    if closer and in_threat:
        score += 1.0
        score += 0.5 * (CORNER_CAP - len(area)) / CORNER_CAP   # địch càng bí càng thưởng
    return min(score, 2.0)
```

- `enemy_reachable_area` / `exit_choke`: ở `opponent_model` dùng chung (BFS bằng [time_expanded_bfs](../../../agent/team_agent/person_a_safety/search.py); choke = ô mà bỏ nó đi thì vùng địch tách khỏi map mở — articulation point đơn giản hoá: ô có bậc thoát thấp nối vùng nhỏ với vùng lớn).
- **Bàn giao đòn kết**: khi đã ở thế, `trap_score`/[02 seal](02_bit_hanh_lang_2_bom.md)/[chain 06](../06_chain_bomb_offensive.md) lo phần đặt bom. herd chỉ lo *MOVE để dựng thế*.
- Pipeline `act()` không đổi; vẫn qua `final_shield`.

## 5. Ngân sách 100ms

1 BFS vùng địch (horizon nhỏ ~6) cho **địch gần nhất** mỗi step → rẻ. Reuse `time_expanded_bfs`. Không model, không train.

## 6. Test & đo

- Smoke: dựng map có hẻm cụt + địch trong đó → nước đi về phía choke có `herd_score>0`; địch ở vùng mở → 0.
- `test_engine_safety` self-death=0; benchmark đúng luật kỳ vọng **kills↑ / avg_rank↑**; nếu draw không giảm & kills không tăng → hạ weight hoặc bỏ.

## 7. Rủi ro & lan can

- **Đuổi quá đà vào nguy hiểm** → `enemy_risk_penalty` + safe mask vẫn chặn; gate `in_threat` + cap.
- **Mô hình choke sai** → giữ bảo thủ (chỉ kích hoạt khi vùng địch thật sự nhỏ); herding chỉ *reorder* trong nước đã an toàn.
- **Double-count** với trap/seal: herd chỉ cho MOVE, không cho PLACE_BOMB → không trùng (xem [00_README](00_README.md)).

## 8. Công sức & timeline · Tham chiếu

- **Công sức**: ~1.5–2 ngày (gồm `opponent_model`). Làm sau cụm 05/06/04.
- **Tham chiếu**: [02_bit_hanh_lang_2_bom.md](02_bit_hanh_lang_2_bom.md), [../06_chain_bomb_offensive.md](../06_chain_bomb_offensive.md), [../02_alpha_beta_search.md](../02_alpha_beta_search.md) (search tổng quát hoá herding), cơ chế "agent không chặn nổ/không chặn nhau" trong [../../../docs/COMPETITION_GUIDE.md](../../../docs/COMPETITION_GUIDE.md).
