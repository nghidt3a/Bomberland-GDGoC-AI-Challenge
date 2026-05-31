# So sánh các hướng tiếp cận

Không có thuật toán nào luôn tốt nhất. Với Bomberland, lựa chọn phụ thuộc thời gian, kinh nghiệm RL, tài nguyên train và ràng buộc 100ms.

## Bảng so sánh nhanh

| Hướng | Độ khó | Cần train | Mạnh ở | Rủi ro | Khuyến nghị |
|---|---:|---|---|---|---|
| Rule-based safety BFS | Thấp | Không | Sống sót, ổn định | Dễ bị bắt bài | Làm đầu tiên |
| Rule-based farming/attack | Trung bình | Không | Phá box, lấy item, tấn công rõ | Nhiều edge case | Rất nên làm |
| Hybrid heuristic search | Trung bình | Không/ít | Cân bằng nhiều mục tiêu | Tuning nhiều | Hướng thực dụng nhất |
| Minimax/Alpha-beta | Cao | Không | Tình huống đối kháng ngắn | Branching lớn | Dùng cục bộ, depth nhỏ |
| DQN | Cao | Có | Học policy từ experience | Reward khó, bất ổn | Làm sau baseline |
| Rainbow DQN | Cao | Có | Tăng sample efficiency cho DQN | Nhiều chi tiết dễ bug | Làm khi DQN cơ bản ổn |
| PPO | Cao | Có nhiều | Policy stochastic, self-play | Sample inefficient | Chỉ làm nếu có wrapper tốt |
| MAPPO/CTDE | Rất cao | Có nhiều | Train multi-agent với centralized critic | Wrapper phức tạp, dễ leakage info | Dành cho đội có pipeline mạnh |
| Behavior Cloning | Trung bình | Có dataset | Bắt chước rule/expert nhanh | Không vượt expert dễ | Rất hợp để warm-start |
| Offline RL | Cao | Có dataset | Tận dụng log/replay sẵn | Out-of-distribution Q-value | Dùng sau BC và log tốt |
| Hierarchical RL | Cao | Có/ít | RL chọn chiến thuật, rule xử lý action | Option kém giới hạn trần | Hợp để nâng cấp hybrid |
| Safe RL/action shielding | Trung bình | Có/không | Giảm tự sát, ổn định neural policy | Shield quá chặt | Nên dùng với mọi RL |
| Self-play | Cao | Có nhiều | Chống bị bắt bài | Dễ overfit pool | Dùng giai đoạn sau |
| PBT/league training | Rất cao | Có rất nhiều | Tự tune và tạo policy đa dạng | Tốn tài nguyên | Chỉ dùng khi pipeline tự động |
| Model-based RL/Dyna | Rất cao | Có/không | Rollout ngắn, planning, opponent model | Simulator/model sai | Dùng phụ trợ, không làm lõi vội |
| Intrinsic motivation | Cao | Có | Khám phá khi reward thưa | Học reward phụ, quên thắng | Dùng giai đoạn train sớm |
| MCTS/PUCT | Rất cao | Không/có | Planning online | Khó dưới 100ms | Chỉ thử bản giới hạn |
| Ensemble/meta-policy | Trung bình | Tùy | Kết hợp ưu điểm | Logic chọn policy sai | Hữu ích nếu có nhiều agent |

## Hướng khuyến nghị theo thời gian

### Có 3-5 ngày

Làm:

- Rule-based safety BFS.
- Farming item/box.
- Benchmark và nộp sớm.

Không nên:

- PPO.
- MCTS sâu.
- Self-play phức tạp.

### Có 1-2 tuần

Làm:

- Hybrid heuristic.
- Behavior cloning từ rule agent.
- DQN nhỏ với safety mask.
- Rainbow-lite nếu DQN cơ bản đã ổn.
- Hierarchical RL với rule low-level.
- Offline RL/BC từ log rule agent.
- Test nhiều seed.

### Có 3 tuần trở lên

Làm thêm:

- Opponent curriculum.
- Self-play với pool.
- PPO nếu có wrapper ổn.
- MAPPO/CTDE nếu có wrapper multi-agent tốt.
- PBT hoặc league training nếu có tài nguyên.
- Model-based rollout ngắn hoặc opponent model.
- Intrinsic motivation cho giai đoạn khám phá ban đầu.
- Ensemble rule + neural policy.

## Nhóm RL bổ sung nên ưu tiên

Nếu mục tiêu là thêm RL nhưng vẫn thực dụng, thứ tự nên thử là:

1. Safe RL/action shielding cho mọi model.
2. Hierarchical RL trên nền rule/hybrid đã có.
3. Rainbow-lite để nâng DQN.
4. Offline RL hoặc BC warm-start từ log.
5. PPO/self-play rồi mới đến MAPPO hoặc PBT.

Các hướng như model-based RL, MAPPO và PBT có trần cao hơn nhưng chỉ đáng làm khi pipeline train/test đã tự động và dữ liệu đánh giá đáng tin.

## Tiêu chí chọn hướng cuối

Chọn agent cuối theo dữ liệu, không theo thuật toán nghe hay:

1. Pass submission.
2. Không timeout.
3. Win/rank tốt trên baseline mạnh.
4. Ít self-kill.
5. Ổn định qua seed.
6. Dễ giải thích khi pitching.

Một hybrid rule-based mạnh thường đáng tin hơn một RL agent train chưa đủ.

## Hướng nên tránh

- Model quá lớn chỉ vì GPU train được.
- Reward quá phức tạp không đo được tác dụng.
- Search mọi action của 4 agent quá sâu trong `act()`.
- Agent chỉ tối ưu 1v1 trong khi trận thật 4 agent.
- Không có fallback khi model lỗi.
