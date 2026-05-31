# Self-play trong game đối kháng

Self-play là train agent bằng cách cho nó đấu với chính nó hoặc các phiên bản cũ của nó. Trong game đối kháng, đây là cách quan trọng để tránh chỉ overfit vào một baseline cố định.

## Ý tưởng

Nếu agent chỉ train với `TacticalRuleAgent`, nó có thể học cách khai thác đúng đối thủ đó nhưng yếu trước agent khác. Self-play tạo đối thủ thay đổi liên tục:

```text
main_agent đấu với pool = [baseline, bản cũ, bản mới, rule mạnh]
```

Agent phải học chiến thuật tổng quát hơn.

## Opponent pool

Pool nên gồm:

- Baseline yếu: random/simple để học cơ bản.
- Baseline trung bình: box farmer/smarter.
- Baseline mạnh: tactical/genius.
- Bản cũ của chính mình.
- Bản tốt nhất hiện tại.
- Có thể thêm agent heuristic khác style.

Không nên chỉ train với bản mới nhất, vì agent có thể quên cách thắng đối thủ cũ.

## Curriculum

Train theo độ khó tăng dần:

1. Học sống sót trước random/simple.
2. Học farm trước box farmer.
3. Học né/tấn công trước tactical.
4. Học chống bản cũ của chính mình.
5. Trộn opponent theo xác suất.

Ví dụ xác suất:

```text
20% random/simple
30% tactical/smarter/genius
30% snapshot cũ
20% self-play mới nhất
```

## Self-play trong trận 4 agent

Bomberland có 4 agent, nên có vài cách:

1. Main agent + 3 baseline ngẫu nhiên.
2. Main agent + 1 snapshot cũ + 2 baseline.
3. 4 bản cùng policy nhưng random vị trí.
4. 4 policy khác nhau từ pool.

Cách thực dụng: luôn có ít nhất 1-2 baseline cố định để môi trường không quá hỗn loạn ở giai đoạn đầu.

## Chọn snapshot

Lưu snapshot định kỳ:

- Theo số episode.
- Khi win rate vượt mốc.
- Khi estimated rank tốt hơn.

Không lưu quá nhiều trong submission, nhưng trong train có thể giữ pool 5-20 snapshot.

## Rủi ro self-play

| Rủi ro | Cách xử lý |
|---|---|
| Overfit vào chính mình | Thêm baseline đa dạng |
| Quên kỹ năng cũ | Giữ snapshot cũ trong pool |
| Train chậm | Curriculum từ dễ đến khó |
| Policy kỳ quặc | Test với baseline độc lập |
| Reward exploit | Chọn checkpoint theo win/rank |

## Khi nào nên dùng

Nên dùng sau khi:

- Agent biết né bom.
- Agent farm được.
- Agent có reward và feature ổn.
- Local benchmark đã chạy được tự động.

Không nên self-play khi agent còn tự sát thường xuyên. Khi đó pool chỉ khuếch đại hành vi xấu.

