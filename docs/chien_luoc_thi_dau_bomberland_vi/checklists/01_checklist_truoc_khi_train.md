# Checklist trước khi train

## Luật và interface

- [ ] Đội đã hiểu action `0..5`.
- [ ] Đội đã hiểu `obs["map"]`, `obs["players"]`, `obs["bombs"]`.
- [ ] Đội đã biết timeout `act()` là 100ms.
- [ ] Đội đã biết chấm CPU-only.
- [ ] Đội đã biết submission không được dùng network, LLM, ghi file.

## Baseline

- [ ] Có rule-based safety chạy được.
- [ ] Có danger map.
- [ ] Có BFS tìm ô safe.
- [ ] Có kiểm tra escape sau khi đặt bom.
- [ ] Có fallback action.
- [ ] Agent không tự sát thường xuyên trong test nhỏ.

## Feature

- [ ] Encode map đúng giá trị `0..4`.
- [ ] Encode player đúng thứ tự `[x, y, alive, bombs_left, bomb_radius_bonus]`.
- [ ] Encode bomb đúng thứ tự `[x, y, timer, owner_id]`.
- [ ] Có feature danger/timer.
- [ ] Có feature item/box/enemy.
- [ ] Có action mask hoặc safety filter.

## Reward

- [ ] Reward thắng/thua rõ hơn reward phụ.
- [ ] Không thưởng spam bomb quá cao.
- [ ] Không thưởng đứng yên/sống sót quá cao.
- [ ] Có penalty chết.
- [ ] Có kiểm tra reward hacking bằng match thật.

## Experiment

- [ ] Có tên experiment.
- [ ] Có seed.
- [ ] Có opponent pool.
- [ ] Có nơi lưu checkpoint.
- [ ] Có log metric.
- [ ] Có plan test sau train.

## Cloud

- [ ] Repo clone được trên Kaggle/Colab.
- [ ] Dependency cài được.
- [ ] Checkpoint lưu định kỳ.
- [ ] Không hard-code path cloud vào agent submit.
- [ ] Biết cách tải checkpoint về.

