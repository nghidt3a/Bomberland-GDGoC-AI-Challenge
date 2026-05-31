# Benchmark 100ms và tối ưu inference

Timeout là lỗi rất nặng: evaluator fallback action về `0`, làm agent đứng yên và dễ chết. Agent tốt phải chạy nhanh, ổn định và ít spike.

## Benchmark chính

```bash
python -m scripts.participant.estimate_agent_time path/to/agent --opponents TacticalRuleAgent SmarterRuleAgent GeniusRuleAgent --num_matches 10
```

Nên chạy với nhiều opponent vì state phức tạp khác nhau có thể làm `act()` chậm khác nhau.

## Mục tiêu thời gian

| Metric | Mục tiêu |
|---|---:|
| Average | < 20ms |
| Max spike | < 100ms |
| Startup | < 20s |
| Import | Không quá nặng |

Nếu average 80-90ms, agent rất rủi ro vì máy chấm có thể chậm hơn local.

## Tối ưu rule-based

- Tính danger map một lần mỗi `act()`.
- Dùng set cho bomb positions.
- BFS giới hạn depth khi cần.
- Không lặp toàn map nhiều lần nếu có thể cache trong cùng step.
- Tránh deepcopy lớn.
- Không print trong `act()`.

## Tối ưu neural model

- Load model trong `__init__`, không load trong `act()`.
- Dùng `model.eval()`.
- Dùng `torch.no_grad()`.
- Chạy CPU rõ ràng.
- Model nhỏ.
- Tránh batch dimension xử lý phức tạp.
- Có thể cân nhắc ONNX nếu model PyTorch chậm và đội kiểm soát được dependency.

## Tối ưu search

- Có deadline nội bộ.
- Iterative deepening.
- Candidate action filtering.
- Leaf heuristic thay rollout dài.
- Nếu hết giờ, trả best safe action.

## Chống spike

Spike thường do:

- Lần đầu model warm-up.
- Import lazy trong `act()`.
- Pathfinding search quá rộng.
- Python object allocation nhiều.
- Print/log quá nhiều.

Giải pháp:

- Warm up model trong `__init__` nếu cần.
- Precompute constants.
- Giới hạn BFS/search.
- Tắt debug print.

## Checklist trước submit

- [ ] Benchmark 10 trận.
- [ ] Benchmark với baseline mạnh.
- [ ] Không có max spike >= 100ms.
- [ ] Không có error/invalid action.
- [ ] Startup không load file thừa.
- [ ] Không dùng GPU.
- [ ] Không ghi file.

