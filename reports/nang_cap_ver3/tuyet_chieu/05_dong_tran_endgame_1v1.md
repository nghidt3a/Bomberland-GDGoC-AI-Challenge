# 05 — Đóng trận: endgame theo tie-break + chế độ 1v1

## 1. TL;DR

- **Verdict**: `phase_profile` của ver3 chỉ đổi theo `turn_index`, **không theo số người còn sống** cũng **không theo chênh lệch tie-break**. Thêm **endgame mode** chọn *thủ-để-giữ-hạng* hay *ép-kill-để-lật*.
- **ROI cao, rủi ro/công sức THẤP, không train, không cần mô hình địch** → nên làm sớm.
- **Mấu chốt luật**: sống tới step 500 thì xếp hạng theo **kills > boxes > items > bombs**. ⇒ cuối trận phải biết mình đang **thắng hay thua** metric nào để hành xử đúng.
- **Go/no-go**: win-rate/avg_rank↑ ở các trận kéo dài tới ~500; ≥ ver3.

## 2. Chiêu là gì & closes gap nào

Hai tình huống cuối trận ver3 chơi chưa tối ưu:
1. **Dẫn tie-break + gần step 500** → đáng lẽ **thủ chặt, không mạo hiểm** (chết = mất hạng). ver3 vẫn farm/đặt bom như giữa trận.
2. **Thua tie-break** (vd kém kills) → phải **ép kill** (metric ưu tiên cao nhất) thay vì farm thêm boxes vô ích.
3. **1v1 (chỉ còn 1 địch)** → không còn bên thứ 3, **an toàn để áp sát/ép kill hơn**; ver3 vẫn dùng `enemy_risk` như đánh 4 người.

## 3. ver3 đã có gì (gap)

- [phase_profile(turn_index, tracker)](../../../agent/team_agent/person_b_strategy/scoring.py): early/mid/late + `late_leading`/`late_chasing` — nhưng `late_*` chọn theo `tracker.proxy_score` tổng quát, **không theo #người sống** và **không so từng metric tie-break**.
- [loop_tracker](../../../agent/team_agent/person_b_strategy/loop_tracker.py): đã có `proxy_boxes/proxy_items/proxy_bombs/proxy_kills` + `proxy_kills = sĩ số địch ban đầu − còn sống` → **đủ liệu để biết mình mạnh metric nào** (dù không thấy stat chính xác của địch).
- `state.alive_players` / `state.opponents`: biết còn mấy người.

## 4. Thiết kế tích hợp (build-ready)

Thêm nhánh endgame trong [phase_profile](../../../agent/team_agent/person_b_strategy/scoring.py) (hoặc lớp mỏng trong [RulePolicy](../../../agent/team_agent/person_b_strategy/policy_rule.py) trước khi chấm điểm).

```python
def endgame_profile(state, tracker, turn_index, base):
    n_alive = len(state.alive_players)
    near_500 = turn_index >= 430
    duel = len(state.opponents) <= 1
    if not (near_500 or n_alive <= 2):
        return base                      # chưa endgame -> giữ phase_profile thường

    # ước lượng mình đang DẪN hay THUA (proxy; bảo thủ)
    leading = tracker.proxy_kills >= 1 or tracker.proxy_score >= LEAD_THRESH

    w = base
    if near_500 and leading:
        # GIỮ HẠNG: tăng survival/mobility, giảm mạo hiểm tấn công
        w = replace(w, survival=w.survival*1.6, danger=w.danger*1.4,
                    enemy_risk=w.enemy_risk*1.5, pressure=w.pressure*0.3, trap=w.trap*0.4)
    else:
        # THUA hoặc cần kết liễu: ưu tiên KILL (metric tie-break cao nhất)
        w = replace(w, pressure=w.pressure*1.6, trap=w.trap*1.8,
                    chain=getattr(w,'chain',0)*1.5)          # phối với chiêu tấn công
        if duel:
            w = replace(w, enemy_risk=w.enemy_risk*0.5)      # 1v1: dám áp sát hơn
    return w
```

- `LEAD_THRESH`: ngưỡng proxy_score coi như đang dẫn (tune).
- Vì **không thấy stat chính xác của địch** → quy tắc **bảo thủ**: khi nghi ngờ mà gần 500, **ưu tiên không chết** (chết chắc chắn mất hạng; thủ hòa vẫn có tie-break từ boxes/items/bombs mình đã farm — vốn ver3 rất cao).
- Pipeline không đổi; chỉ đổi bộ weight đưa vào `score_actions`. Vẫn `final_shield`.

## 5. Ngân sách 100ms

Chỉ vài phép so sánh + thay weight. **0 chi phí thêm**. Không model/train.

## 6. Test & đo

- Smoke: dựng tracker proxy "đang dẫn" + turn 480 → profile trả weight survival cao; "đang thua kills" → weight pressure/trap cao; 1v1 → enemy_risk giảm.
- Benchmark đúng luật ([01](../01_quick_wins_va_benchmark_trung_thuc.md)) với `--max-steps 500`: kỳ vọng **win-rate↑** ở các trận đi tới 500 (lật được tie-break / giữ được hạng); ≥ ver3. `test_engine_safety` self-death=0.

## 7. Rủi ro & lan can

- **Proxy sai** (không thấy stat địch) → mặc định **bảo thủ khi dẫn** (không chết); chỉ "ép kill" khi rõ ràng thua hoặc 1v1.
- **Ép kill quá liều → tự chết** → safe mask + `final_shield` vẫn chặn; chỉ nới `enemy_risk`, không nới safety.
- Phụ thuộc [01](../01_quick_wins_va_benchmark_trung_thuc.md) để **đo đúng** (benchmark phải áp tie-break, nếu không sẽ không thấy lợi ích).

## 8. Công sức & timeline · Tham chiếu

- **Công sức**: ~0.5–1 ngày. **Làm sớm** (rủi ro thấp, ROI cao, hợp deadline).
- **Tham chiếu**: [../01_quick_wins_va_benchmark_trung_thuc.md](../01_quick_wins_va_benchmark_trung_thuc.md) (tie-break + thước đo), [loop_tracker.py](../../../agent/team_agent/person_b_strategy/loop_tracker.py), [../../../docs/COMPETITION_GUIDE.md](../../../docs/COMPETITION_GUIDE.md) (mục 5: tie-break & win/draw/loss).
