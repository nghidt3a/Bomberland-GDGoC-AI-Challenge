# Checklist trước khi submit

## File ZIP

- [ ] ZIP <= 100MB.
- [ ] Tối đa 20 file.
- [ ] `agent.py` nằm ở root ZIP.
- [ ] Chỉ có một `agent.py`.
- [ ] Checkpoint cần thiết nằm cùng ZIP.
- [ ] Không có notebook/log/dataset/checkpoint thừa.

## Agent interface

- [ ] Có class `Agent`.
- [ ] `__init__(self, agent_id: int)` chạy được.
- [ ] `act(self, obs)` chạy được.
- [ ] `act()` trả int.
- [ ] Action luôn trong `0..5`.
- [ ] Có fallback khi lỗi.

## Runtime

- [ ] Startup dưới 20 giây.
- [ ] Average `act()` thấp hơn 100ms rõ rệt.
- [ ] Max spike dưới 100ms trong benchmark.
- [ ] Không import/load model trong `act()`.
- [ ] Không print/log quá nhiều.

## Quy định

- [ ] Không dùng LLM trong `Agent`.
- [ ] Không gọi network.
- [ ] Không ghi file trong match.
- [ ] Không dùng GPU bắt buộc.
- [ ] Không phụ thuộc file ngoài ZIP.

## Test local

- [ ] Chạy `run_local_match` headless pass.
- [ ] Chạy với baseline mạnh pass.
- [ ] Chạy `estimate_rankings` ít nhất 100 trận nếu có thời gian.
- [ ] Chạy `estimate_agent_time`.
- [ ] Visualize vài trận để kiểm tra hành vi.

## Chọn bản nộp

- [ ] Version này tốt hơn bản trước theo metric.
- [ ] Không chỉ thắng do may mắn vài seed.
- [ ] Ít self-kill.
- [ ] Không regression trước baseline yếu.
- [ ] Có ghi lại version/checkpoint đã nộp.

