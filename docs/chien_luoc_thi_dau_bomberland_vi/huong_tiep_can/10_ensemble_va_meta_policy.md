# Ensemble và meta-policy

Ensemble kết hợp nhiều agent/policy. Trong Bomberland, cách thực dụng nhất là dùng meta-policy chọn giữa các chiến thuật, không phải chạy nhiều model lớn cùng lúc.

## Ý tưởng

Có nhiều policy:

- Safety policy.
- Farming policy.
- Attack policy.
- RL policy.
- Endgame policy.

Meta-policy quyết định dùng policy nào theo state.

## Ví dụ rule meta-policy

```text
Nếu đang nguy hiểm:
    dùng safety policy
Nếu có item gần an toàn:
    dùng item policy
Nếu enemy bị kẹt và mình có escape:
    dùng attack policy
Nếu đầu game còn nhiều box:
    dùng farming policy
Ngược lại:
    dùng RL/hybrid policy
```

## Ensemble action voting

Có thể cho nhiều policy đề xuất action:

```text
rule_action
dqn_action
attack_action
```

Sau đó chọn bằng priority:

1. Nếu rule báo danger, ưu tiên safety.
2. Nếu action RL unsafe, bỏ.
3. Nếu nhiều action safe, chọn action có score heuristic cao nhất.

## Không chạy quá nhiều model

Evaluator CPU-only và 100ms. Không nên load nhiều neural network lớn. Nếu ensemble dùng model, giữ model nhỏ hoặc chỉ dùng một model neural cộng rule.

## Meta feature

Meta-policy có thể dựa trên:

- Mình đang trong danger không.
- Số enemy sống.
- Số box còn lại.
- Số item gần.
- Bombs left và radius.
- Enemy gần nhất.
- Step hiện tại.
- Safe space quanh mình.

## Dùng ensemble để giảm rủi ro RL

Cách mạnh:

```text
if safety_required:
    return safety_rule(obs)
rl_action = model(obs)
if safe(rl_action):
    return rl_action
return heuristic_best_safe_action(obs)
```

Như vậy model giúp trong state bình thường, còn rule cứu trong state nguy hiểm.

## Điểm mạnh

- Ổn định hơn policy đơn.
- Dễ giải thích.
- Có thể tận dụng nhiều hướng đã làm.
- Giảm rủi ro RL chọn action tự sát.

## Điểm yếu

- Meta-policy sai có thể làm agent rối.
- Khó debug nếu nhiều policy mâu thuẫn.
- Có thể chậm nếu chạy nhiều model/search.

## Khuyến nghị

Với đội mới, ensemble tốt nhất là:

- 1 safety rule bắt buộc.
- 1 heuristic scorer.
- 1 neural policy tùy chọn.
- 1 fallback đơn giản.

Không cần ensemble phức tạp hơn nếu chưa có bằng chứng cải thiện.

