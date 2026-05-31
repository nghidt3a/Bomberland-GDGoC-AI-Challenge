# Submit mẫu Bomberland

Thư mục này là mẫu ZIP nộp bài tối giản. File chính là `agent.py`, đã chứa một rule-based agent độc lập:

- Né vùng nổ bằng BFS.
- Chỉ đặt bom khi có thể phá box hoặc đe dọa enemy.
- Kiểm tra có đường thoát sau khi đặt bom.
- Ưu tiên nhặt item an toàn.
- Không cần checkpoint.
- Không train, không network, không ghi file.

## Cách test local

Từ root repo:

```bash
python -m scripts.participant.run_local_match --agent_paths submit_mau TacticalRuleAgent SmarterRuleAgent GeniusRuleAgent --num_episodes 10 --visualize false
python -m scripts.participant.estimate_agent_time submit_mau --opponents TacticalRuleAgent SmarterRuleAgent GeniusRuleAgent --num_matches 10
```

## Cách zip đúng

Khi nộp, `agent.py` phải nằm ở root của ZIP. Nghĩa là zip **nội dung bên trong** thư mục này, không zip cả folder `submit_mau`.

Cấu trúc đúng:

```text
submission.zip
└── agent.py
```

Không cần đưa `README.md` vào ZIP nếu muốn submission gọn nhất.

