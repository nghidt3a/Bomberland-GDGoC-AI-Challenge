# Nâng cấp `submit_ver3` — Tổng quan các hướng (build-ready, may đo cho agent hiện tại)

Bộ tài liệu này phân tích **từng hướng nâng cấp cụ thể cho ver3**: ver3 đã có sẵn gì → sửa/thêm file & hàm nào → pseudocode → test → ngân sách 100ms → ROI/rủi ro/go-no-go. Đọc xong là bắt tay code được.

> Khác với [docs/.../huong_tiep_can/](../../docs/chien_luoc_thi_dau_bomberland_vi/huong_tiep_can/) (giải thích kỹ thuật chung chung). Bộ này **gắn vào code thật** trong [agent/team_agent/](../../agent/team_agent/). Bối cảnh tổng & roadmap: [../ke_hoach_hien_trang_va_roadmap_ml.md](../ke_hoach_hien_trang_va_roadmap_ml.md).

## Ma trận so sánh nhanh

| # | Hướng | ROI | Công sức | Rủi ro | Cần train? | Hợp 19 ngày | Phụ thuộc |
|---|---|---|---|---|---|---|---|
| [01](01_quick_wins_va_benchmark_trung_thuc.md) | Quick-wins + benchmark trung thực | Cao | Thấp | Thấp | Không | ⭐⭐⭐ | — |
| [02](02_alpha_beta_search.md) | Alpha-Beta / expectimax search | Cao | Trung bình | Trung bình | **Không** | ⭐⭐⭐ | 01 (để đo) |
| [03](03_behavior_cloning.md) | Behavior Cloning | Trung bình | Trung bình | Thấp–TB | Có (nhẹ) | ⭐⭐ | 01 |
| [04](04_ppo_self_play.md) | PPO + self-play | Cao (trần) | Cao | Cao | Có (nặng) | ⭐ | 01, 03 |
| [05](05_dqn_dueling.md) | Double/Dueling DQN | Trung bình–cao | Cao | Cao | Có | ⭐ | 01 |
| [06](06_chain_bomb_offensive.md) | Chain-bomb tấn công (khai thác bom địch) | Cao | Thấp | Thấp | **Không** | ⭐⭐⭐ | 01 (để đo) |

ROI = lợi ích kỳ vọng trên leaderboard. "Hợp 19 ngày" càng nhiều sao càng nên ưu tiên khi quỹ thời gian hẹp.

> ⚠️ **Trước khi KẾT HỢP nhiều hướng/chiêu**, đọc [07 — Tương tác · Xung đột · Tương thích](07_tuong_tac_xung_dot_tuong_thich.md): ma trận cộng hưởng/xung đột, ràng buộc toàn cục (latency · trần offense · nhất quán mô hình địch · cân bằng trọng số), giao thức ablation thêm-từng-cái, và **bundle khuyến nghị** cho bản nộp. Gộp bừa có thể làm agent *tệ đi* dù từng cái tốt.

## Thứ tự khuyến nghị

```
01 benchmark trung thực  ──►  (tiên quyết: phải đo đúng luật trước khi đánh giá mọi nâng cấp)
        │
        ├─► 02 Alpha-Beta search   (upside KHÔNG train, xây trên ver3 — làm sớm)
        │
        ├─► 06 Chain-bomb tấn công (heuristic rẻ KHÔNG train — tăng kill, cùng cụm scoring)
        │
        └─► 03 Behavior Cloning    (deliverable ML thực tế, nền cho RL)
                    │
                    └─► chọn 1: 04 PPO+self-play  HOẶC  05 DQN   (canh bạc upside, có cổng go/no-go)
                                          │
                                          └─► hardening + chọn bản nộp cuối
```

- **01 là bắt buộc làm đầu tiên**: benchmark hiện tại không áp tie-break step-500 → đo thấp sức mạnh thật của ver3, và không thể biết nâng cấp nào "thắng" nếu thước đo sai luật.
- **02 (Alpha-Beta) là upside không-train đáng giá nhất** — nên làm song song với 01.
- **06 (chain-bomb) là tinh chỉnh tấn công không-train, rẻ** — làm cùng cụm scoring với 01, trúng điểm yếu kill thấp; cũng là payoff tường minh của 02.
- **04 và 05 là hai nhánh thay thế nhau** (chọn 1), chỉ làm khi 03 vững và còn thời gian.

## Quy ước dùng chung (áp cho mọi hướng)

1. **`final_shield` là cổng cứng**: mọi policy mới (search/BC/PPO/DQN) chỉ *đề xuất* action; action cuối luôn đi qua [shield.py::final_shield](../../agent/team_agent/person_a_safety/shield.py). Không bao giờ bỏ qua.
2. **Verify thay đổi safety/engine** với [engine/game.py](../../engine/game.py) trước khi tin tài liệu (bài học cũ: tài liệu fix từng sai về action mapping).
3. **Benchmark phải đúng luật**: áp tie-break `kills > boxes > items > bombs`, và chạy **mỗi bản trong process riêng** (module-cache `person_a_safety`/`person_b_strategy` lẫn nhau làm sai số) — xem [01](01_quick_wins_va_benchmark_trung_thuc.md).
4. **`ver3` là sàn/fallback**: luôn giữ ≥1 bản nộp tốt; mọi nâng cấp phải đạt **≥ ver3** trên benchmark đúng luật mới thay thế, nếu không thì giữ ver3.
5. **Ràng buộc cứng của cuộc thi**: `act()` < 100ms/step, startup ≤ 20s, zip ≤ 20 file, đuôi cho phép (`.py/.onnx/.pth/.pkl/...`). Model ML ưu tiên **ONNX + net nhỏ**.

## Tham chiếu

- Roadmap & hiện trạng tổng: [../ke_hoach_hien_trang_va_roadmap_ml.md](../ke_hoach_hien_trang_va_roadmap_ml.md)
- Lý thuyết các hướng (generic): [../../docs/chien_luoc_thi_dau_bomberland_vi/huong_tiep_can/](../../docs/chien_luoc_thi_dau_bomberland_vi/huong_tiep_can/)
- Giải thích siêu chi tiết: [../../docs/AI_Challenge_GDGoC_HCMUS_Huong_dan_sieu_chi_tiet.md](../../docs/AI_Challenge_GDGoC_HCMUS_Huong_dan_sieu_chi_tiet.md)
- Luật & xếp hạng: [../../docs/COMPETITION_GUIDE.md](../../docs/COMPETITION_GUIDE.md)
