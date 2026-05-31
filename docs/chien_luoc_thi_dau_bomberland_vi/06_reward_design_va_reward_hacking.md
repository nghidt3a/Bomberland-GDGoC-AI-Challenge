# Reward design và reward hacking

Reward design là phần dễ làm RL hỏng nhất. Reward phải dẫn agent đến mục tiêu thật: sống sót, thắng trận, đạt rank tốt, không chỉ tối đa hóa một hành vi phụ.

## Reward mục tiêu

Reward chính nên phản ánh kết quả trận:

| Sự kiện | Reward gợi ý |
|---|---:|
| Thắng trận | `+2.0` đến `+10.0` |
| Bị chết | `-2.0` đến `-10.0` |
| Enemy chết | `+1.0` đến `+5.0` |
| Sống đến cuối nhưng không thắng rõ | nhỏ hơn thắng |

Vì reward cuối trận thưa, cần reward phụ để học nhanh hơn.

## Reward shaping

Reward phụ nên nhỏ hơn reward thắng/thua:

| Hành vi | Reward gợi ý |
|---|---:|
| Rời khỏi vùng nổ sắp tới | `+0.05` đến `+0.2` |
| Đi vào vùng nổ nguy hiểm | `-0.05` đến `-0.2` |
| Đặt bom gần box và có đường thoát | `+0.03` đến `+0.1` |
| Nhặt item | `+0.1` đến `+0.5` |
| Tiến gần enemy khi an toàn | `+0.01` đến `+0.05` |
| Đứng yên không lý do | `-0.005` đến `-0.02` |
| Mỗi step trôi qua | `-0.001` đến `-0.01` |

Không nên để reward phụ lớn hơn reward thắng, vì agent có thể farm reward phụ thay vì thắng.

## Reward cho Bomberland nên ưu tiên gì

Thứ tự ưu tiên:

1. Không chết.
2. Enemy chết.
3. Có đường thoát sau khi đặt bom.
4. Lấy item.
5. Phá box.
6. Kiểm soát vị trí.
7. Rút ngắn khoảng cách với enemy khi an toàn.

Không nên thưởng quá cao cho việc đặt bom, vì agent có thể spam bom và tự chết.

## Reward hacking thường gặp

| Hiện tượng | Nguyên nhân | Cách sửa |
|---|---|---|
| Agent đứng yên để sống | Survival reward quá cao | Thêm time penalty, thưởng mục tiêu |
| Agent spam bomb | Thưởng đặt bom quá cao | Chỉ thưởng khi phá box/hit enemy và có escape |
| Agent farm box nhưng không đánh | Box reward quá cao | Tăng reward enemy death/win |
| Agent chạy vào item dù sắp chết | Item reward quá cao | Hard mask danger |
| Agent né bom mãi không chơi | Danger reward quá cao | Giới hạn reward né bom, thêm mục tiêu farm/tấn công |
| Reward train tăng nhưng win giảm | Reward phụ lệch mục tiêu | Dùng win/rank làm metric chọn checkpoint |

## Chọn checkpoint

Không chọn checkpoint theo total reward duy nhất. Chọn theo:

- Win rate trước baseline mạnh.
- Average rank.
- Survival steps.
- Ít self-kill.
- Ít timeout.
- Estimated TrueSkill local.

Nếu reward tăng nhưng rank xấu đi, reward đang sai.

## Reward cho self-play

Self-play nên dùng reward đơn giản hơn:

```text
+1 nếu rank tốt nhất hoặc thắng
-1 nếu chết sớm
+0.2 nếu enemy chết
+0.05 nếu lấy item
-0.01 mỗi step để tránh kéo dài vô ích
```

Với trận 4 agent, rank reward hữu ích hơn win/loss nhị phân:

| Rank | Reward cuối |
|---:|---:|
| 0 | `+1.0` |
| 1 | `+0.3` |
| 2 | `-0.3` |
| 3 | `-1.0` |

## Nguyên tắc an toàn

Dù reward tốt, vẫn nên có safety layer:

- Không cho model chọn action invalid.
- Không cho đặt bom nếu không có escape.
- Không cho đi vào ô timer 1 nếu có lựa chọn khác.
- Nếu model lỗi, dùng rule fallback.

