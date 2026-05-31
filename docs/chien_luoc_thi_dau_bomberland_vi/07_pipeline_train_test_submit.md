# Pipeline train, test và submit

Pipeline tốt giúp đội không bị cuốn vào train mù. Mỗi thay đổi cần có experiment, metric và quyết định rõ ràng.

## Vòng lặp chuẩn

```text
Ý tưởng -> Implement agent -> Test nhỏ -> Benchmark time -> Test nhiều trận
-> So sánh checkpoint -> Đóng gói -> Nộp -> Đọc leaderboard/log -> Lặp lại
```

Không nộp agent chưa qua benchmark 100ms và chưa chạy thử với baseline.

## Bước 1: baseline rule

Trước RL, cần có baseline:

- Né bom.
- Tìm ô safe bằng BFS.
- Đặt bom phá box nếu có escape.
- Nhặt item.
- Tấn công enemy nếu cùng hàng/cột và có escape.

Baseline này dùng để:

- Nộp bản đầu.
- Làm opponent để train.
- Làm expert để behavior cloning.
- Làm fallback cho model RL.

## Bước 2: local test nhanh

Chạy headless nhiều trận với baseline:

```bash
python -m scripts.participant.run_local_match --agent_paths path/to/agent None None None --num_episodes 20 --visualize false
```

Chạy visualize khi cần xem lỗi hành vi:

```bash
python -m scripts.participant.run_local_match --agent_paths path/to/agent TacticalRuleAgent SmarterRuleAgent GeniusRuleAgent --num_episodes 3 --visualize true
```

## Bước 3: estimate ranking

```bash
python -m scripts.participant.estimate_rankings --agent_path path/to/agent --num_matches 100
```

Con số local không phải leaderboard thật, nhưng dùng để so sánh giữa các version.

## Bước 4: benchmark 100ms

```bash
python -m scripts.participant.estimate_agent_time path/to/agent --opponents TacticalRuleAgent SmarterRuleAgent GeniusRuleAgent --num_matches 10
```

Mục tiêu:

- Average < 20ms nếu có thể.
- Max spike < 100ms.
- Không import/load model trong `act()`.

## Bước 5: train cloud

Nếu dùng RL, train trên Kaggle/Colab:

- Lưu checkpoint định kỳ.
- Lưu config hyperparameter.
- Lưu win rate và reward curve.
- Download checkpoint tốt về repo local hoặc lưu Drive/Kaggle output.

Không train trực tiếp trên máy yếu nếu quá chậm.

## Bước 6: chọn checkpoint

Mỗi checkpoint cần được test cùng một bộ seed:

```text
seeds = [0, 1, 2, 3, 4, 10, 20, 42, 86, 123]
opponents = random + simple + smarter + tactical + genius
```

Chọn checkpoint theo metric tổng hợp:

```text
score_local = 3 * win_rate
            + 1 * draw_rate
            - 0.5 * average_rank
            - timeout_penalty
            - self_kill_penalty
```

Không cần dùng đúng công thức này, nhưng phải có tiêu chí nhất quán.

## Bước 7: đóng gói

ZIP nên tối giản:

```text
submission.zip
├── agent.py
├── model.pth        # nếu cần
└── config.json      # nếu cần
```

Tránh đưa notebook, log, ảnh plot, checkpoint cũ vào ZIP.

## Bước 8: sau khi nộp

Theo dõi:

- Submission valid hay invalid.
- 12 trận đầu tốt hay xấu.
- Runtime stats nếu có log.
- Leaderboard `mu`, `sigma`, `score`.
- Replay các trận thua để tìm lỗi.

Nếu score thấp do sigma cao nhưng hành vi tốt, cần thêm thời gian để agent chơi thêm trận. Nếu score thấp do chết sớm hoặc timeout, sửa ngay.

