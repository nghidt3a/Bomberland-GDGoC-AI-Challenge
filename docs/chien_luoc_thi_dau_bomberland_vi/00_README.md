# Bộ tài liệu chiến lược Bomberland

Thư mục này gom các tài liệu tiếng Việt phục vụ mục tiêu thi đấu thực tế: hiểu luật, chọn hướng tiếp cận, train/test tiết kiệm trên Kaggle hoặc Google Colab, benchmark agent và chuẩn bị nộp bài. Nội dung ưu tiên tính thực dụng cho đội mới học reinforcement learning, nhưng vẫn đủ nền tảng để phân tích thuật toán.

## Thứ tự đọc khuyến nghị

1. Đọc luật và mục tiêu thi:
   - [01_gioi_thieu_cuoc_thi_va_luat_game.md](01_gioi_thieu_cuoc_thi_va_luat_game.md)
   - [02_muc_tieu_dat_top_cao.md](02_muc_tieu_dat_top_cao.md)
   - [04_agent_interface_va_quy_chuan_nop_bai.md](04_agent_interface_va_quy_chuan_nop_bai.md)
2. Nếu đội chưa biết RL:
   - [03_lo_trinh_cho_doi_moi_hoc_RL.md](03_lo_trinh_cho_doi_moi_hoc_RL.md)
   - [ly_thuyet/01_RL_can_ban_MDP_MC_TD.md](ly_thuyet/01_RL_can_ban_MDP_MC_TD.md)
   - [ly_thuyet/02_Q_learning_va_DQN.md](ly_thuyet/02_Q_learning_va_DQN.md)
3. Chọn hướng làm:
   - [09_so_sanh_cac_huong_tiep_can.md](09_so_sanh_cac_huong_tiep_can.md)
   - [huong_tiep_can/01_rule_based_an_toan_BFS.md](huong_tiep_can/01_rule_based_an_toan_BFS.md)
   - [huong_tiep_can/03_hybrid_rule_based_heuristic_search.md](huong_tiep_can/03_hybrid_rule_based_heuristic_search.md)
   - Nếu muốn thử thêm RL nâng cao:
     - [huong_tiep_can/11_rainbow_DQN_distributional_prioritized_replay.md](huong_tiep_can/11_rainbow_DQN_distributional_prioritized_replay.md)
     - [huong_tiep_can/12_MAPPO_CTDE_multi_agent_RL.md](huong_tiep_can/12_MAPPO_CTDE_multi_agent_RL.md)
     - [huong_tiep_can/13_hierarchical_RL_options_macro_actions.md](huong_tiep_can/13_hierarchical_RL_options_macro_actions.md)
     - [huong_tiep_can/14_offline_RL_tu_log_va_replay.md](huong_tiep_can/14_offline_RL_tu_log_va_replay.md)
     - [huong_tiep_can/15_model_based_RL_Dyna_planning.md](huong_tiep_can/15_model_based_RL_Dyna_planning.md)
     - [huong_tiep_can/16_population_based_training_va_league_self_play.md](huong_tiep_can/16_population_based_training_va_league_self_play.md)
     - [huong_tiep_can/17_safe_RL_action_shielding.md](huong_tiep_can/17_safe_RL_action_shielding.md)
     - [huong_tiep_can/18_intrinsic_motivation_exploration.md](huong_tiep_can/18_intrinsic_motivation_exploration.md)
4. Khi bắt đầu train/test:
   - [05_observation_action_feature_engineering.md](05_observation_action_feature_engineering.md)
   - [06_reward_design_va_reward_hacking.md](06_reward_design_va_reward_hacking.md)
   - [07_pipeline_train_test_submit.md](07_pipeline_train_test_submit.md)
   - [train_test/01_test_local_baselines.md](train_test/01_test_local_baselines.md)
   - [train_test/09_huong_dan_test_4_agents_va_visualize.md](train_test/09_huong_dan_test_4_agents_va_visualize.md)
5. Khi dùng cloud:
   - [08_colab_kaggle_huong_dan_chay_mo_phong.md](08_colab_kaggle_huong_dan_chay_mo_phong.md)
   - [train_test/03_train_DQN_tren_Kaggle.md](train_test/03_train_DQN_tren_Kaggle.md)
   - [train_test/04_train_DQN_tren_Google_Colab.md](train_test/04_train_DQN_tren_Google_Colab.md)

## Khuyến nghị chiến lược ngắn gọn

Với thời gian và tài nguyên hạn chế, hướng an toàn nhất là xây một rule-based hoặc hybrid mạnh trước, sau đó dùng RL để cải thiện chứ không đặt toàn bộ kỳ vọng vào RL ngay từ đầu.

Ưu tiên theo thứ tự:

1. Agent không chết vô nghĩa: né bom, biết đường thoát sau khi đặt bom.
2. Agent farm ổn: phá hộp, lấy item, tăng số bom và bán kính.
3. Agent biết tấn công khi có cơ hội chắc chắn.
4. Agent chạy ổn dưới 100ms mỗi `act()`.
5. Agent được test nhiều seed, nhiều vị trí, nhiều tổ hợp baseline.

Nếu đội muốn thiên về RL, cách ít rủi ro nhất là dùng rule/hybrid làm safety layer và để RL học phần chọn chiến thuật, chọn mục tiêu hoặc ưu tiên action trong tập action an toàn.

## Các ràng buộc cần nhớ

| Nhóm | Quy định |
|---|---|
| Interface | File nộp phải có `agent.py`, class `Agent`, hàm `act(obs) -> int` |
| Action | Số nguyên `0..5`: STOP, LEFT, RIGHT, UP, DOWN, PLACE_BOMB |
| Timeout | Startup tối đa 20 giây, mỗi `act()` tối đa 100ms |
| Môi trường chấm | CPU-only, không network, không ghi file trong match |
| Nộp bài | ZIP <= 100MB, tối đa 20 file, `agent.py` ở root ZIP |
| Scoring | TrueSkill, `score = mu - 3 * sigma` |
| Sau khi nộp | Submission hợp lệ chạy ngay 12 trận ban đầu |
| Background CLI | Lệnh background evaluator trong repo mặc định chạy 5 trận mỗi batch |

## Cách dùng bộ tài liệu này

Mỗi file độc lập đủ để đọc riêng. Khi triển khai code, dùng các checklist trong `checklists/` để kiểm tra trước khi train, trước khi submit và trước khi chọn checkpoint cuối.
