# Tuyệt chiêu Bomberland cho ver3 — Tổng quan (gap-driven, build-ready)

Bộ này là **các tuyệt chiêu/tricks chơi game** mà ver3 hiện **chưa làm hoặc làm yếu**, mỗi chiêu may đo build-ready (theo đúng kiểu [../06_chain_bomb_offensive.md](../06_chain_bomb_offensive.md) — chiêu prototype). Khác với nhóm "hướng tiếp cận thuật toán" [01–05](../00_README_tong_quan.md) (BC/PPO/Alpha-Beta...), đây là **nước cờ trong game** cắm thẳng vào scoring/policy.

> Mọi chiêu vẫn qua [final_shield](../../../agent/team_agent/person_a_safety/shield.py); verify với [engine/game.py](../../../engine/game.py); đo bằng benchmark đúng luật ([doc 01](../01_quick_wins_va_benchmark_trung_thuc.md)). `ver3` là sàn — chiêu nào không đạt **≥ ver3** thì bỏ.

## Ma trận tuyệt chiêu

| # | Tuyệt chiêu | ROI | Công sức | Rủi ro | Cần mô-hình-địch? | Hợp 19 ngày | Liên quan |
|---|---|---|---|---|---|---|---|
| [01](01_lua_don_hem_cut.md) | Lùa/dồn địch vào hẻm cụt | Cao | TB | TB | Có | ⭐⭐ | 02, 06 |
| [02](02_bit_hanh_lang_2_bom.md) | Bịt 2 đầu hành lang (2 bom) | Cao | TB | TB | Một phần | ⭐⭐ | 01, [chain 06](../06_chain_bomb_offensive.md) |
| [03](03_bom_don_dau_du_doan.md) | Bom đón đầu theo dự đoán | Cao | TB | TB–cao | **Có** | ⭐⭐ | 04 |
| [04](04_pha_doat_item_dich.md) | Phá/đoạt item của địch | TB | Thấp | Thấp | Một phần | ⭐⭐⭐ | 03 |
| [05](05_dong_tran_endgame_1v1.md) | Đóng trận endgame + 1v1 | **Cao** | Thấp | Thấp | Không | ⭐⭐⭐ | [doc 01](../01_quick_wins_va_benchmark_trung_thuc.md) |
| [06](06_ky_luat_duong_thoat.md) | Kỷ luật giữ đường thoát (phòng thủ) | Cao | Thấp | Thấp | Không | ⭐⭐⭐ | 01 |

Gợi ý làm trước: **05 + 06 + 04** (rủi ro thấp, không/ít cần mô hình địch, ROI rõ) → rồi **01/02/03** (tấn công nhiều bước, cần mô hình địch).

## Building block dùng chung: mô hình địch rẻ

Chiêu 01/03/04/05 cần **dự đoán địch**. Để tránh mỗi doc tự định nghĩa lại, viết **1 helper chung** (đề xuất `person_b_strategy/opponent_model.py`):

- `predict_enemy_next(state, enemy) -> Cell`: địch bước về **target gần nhất** (box/item theo logic [scoring.farm_targets/item_targets](../../../agent/team_agent/person_b_strategy/scoring.py)) hoặc **né lửa**; mặc định đứng yên nếu mơ hồ.
- `enemy_reachable_area(state, enemy, hazard, horizon) -> set[Cell]`: tái dùng [search.time_expanded_bfs](../../../agent/team_agent/person_a_safety/search.py) từ ô địch để lấy vùng địch với tới (an toàn).

Mô hình **cố ý rẻ & bảo thủ** (đoán sai không sao vì `final_shield` vẫn bảo vệ mình). Đây cũng là mô hình địch mà [Alpha-Beta search (doc 02)](../02_alpha_beta_search.md) dùng — thống nhất 1 nguồn.

## ⚠️ Phối hợp & tránh double-count (quan trọng)

Các chiêu tấn công 01/02/03/04 + [chain-bomb (06)](../06_chain_bomb_offensive.md) + `pressure_score`/`trap_score` sẵn có **đều cộng vào "offense"** khi đặt/đi đặt bom. Nếu cộng dồn vô tội vạ → agent **đặt bom bừa**. Quy ước:

1. **Một trần `offense` chung** (vd cap tổng offense ~3.0) sau khi cộng mọi thành phần tấn công.
2. **Gate ngữ nghĩa rạch ròi** để không tính trùng một tình huống: `chain` = khai thác **bom CÓ SẴN của địch**; `trap` = ép bằng **bom mình tự tạo (1 quả)**; `seal (02)` = phối hợp **≥2 bom của mình**; `predict (03)` = đón đầu vị trí **tương lai**; `herd (01)` = nước **MOVE** lùa địch (không phải bom).
3. Weight vừa phải, thêm dần từng chiêu và **đo lại** trên benchmark đúng luật sau mỗi lần.

## Tham chiếu

- Chiêu prototype: [../06_chain_bomb_offensive.md](../06_chain_bomb_offensive.md)
- Thước đo: [../01_quick_wins_va_benchmark_trung_thuc.md](../01_quick_wins_va_benchmark_trung_thuc.md)
- Cách tổng quát (thay nhiều heuristic bằng lookahead): [../02_alpha_beta_search.md](../02_alpha_beta_search.md)
- Cơ chế game: [../../../docs/COMPETITION_GUIDE.md](../../../docs/COMPETITION_GUIDE.md)
