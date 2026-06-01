# Vấn Đề Person B Strategy

## Tổng Hợp Strategy

| seed | rank | survival | unique | mobility | max STOP | pingpong | bombs | useful bombs | no-value bombs | issues |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 109659 | 3 | 92 | 18 | 0.196 | 5 | 13 | 4 | 3 | 1 | chết do bom mình / thoát bom kém, chết sớm, lặp A-B-A-B |
| 548846 | 2 | 500 | 79 | 0.158 | 74 | 14 | 29 | 19 | 8 | STOP quá dài, lặp A-B-A-B, sống 500 nhưng tie-break yếu |
| 156663 | 1 | 500 | 36 | 0.072 | 1 | 327 | 3 | 3 | 0 | lặp A-B-A-B, di chuyển ít, ít đặt bom |
| 83824 | 0 | 500 | 82 | 0.164 | 9 | 53 | 28 | 15 | 12 | lặp A-B-A-B |
| 290518 | 3 | 327 | 60 | 0.183 | 42 | 3 | 11 | 10 | 1 | chết do bom mình / thoát bom kém, STOP quá dài |
| 548409 | 1 | 500 | 74 | 0.148 | 25 | 38 | 21 | 11 | 7 | STOP quá dài, lặp A-B-A-B |
| 225587 | 2 | 223 | 30 | 0.135 | 115 | 45 | 3 | 3 | 0 | chết do bom mình / thoát bom kém, STOP quá dài, lặp A-B-A-B, ít đặt bom |
| 836037 | 3 | 63 | 13 | 0.206 | 20 | 9 | 1 | 1 | 0 | chết do bom đối thủ, chết sớm, STOP quá dài, lặp A-B-A-B, ít đặt bom |
| 585440 | 2 | 417 | 69 | 0.165 | 4 | 70 | 29 | 23 | 6 | chết do bom mình / thoát bom kém, lặp A-B-A-B |
| 648293 | 3 | 132 | 49 | 0.371 | 8 | 11 | 8 | 7 | 1 | chết do bom mình / thoát bom kém, chết sớm, lặp A-B-A-B |
| 126779 | 3 | 500 | 63 | 0.126 | 1 | 49 | 19 | 9 | 10 | lặp A-B-A-B, bom ít giá trị, sống 500 nhưng tie-break yếu |
| 609286 | 1 | 500 | 19 | 0.038 | 255 | 38 | 2 | 2 | 0 | STOP quá dài, lặp A-B-A-B, di chuyển ít, ít đặt bom |

## Phase Metrics

| seed | phase | alive steps | STOP | BOMB | unique cells | max STOP |
| --- | --- | --- | --- | --- | --- | --- |
| 109659 | early | 92 | 5 | 4 | 18 | 5 |
| 109659 | mid | 0 | 0 | 0 | 0 | 0 |
| 109659 | late | 0 | 0 | 0 | 0 | 0 |
| 548846 | early | 150 | 74 | 4 | 38 | 74 |
| 548846 | mid | 200 | 0 | 9 | 29 | 0 |
| 548846 | late | 151 | 2 | 16 | 67 | 2 |
| 156663 | early | 150 | 3 | 3 | 26 | 1 |
| 156663 | mid | 200 | 0 | 0 | 17 | 0 |
| 156663 | late | 151 | 0 | 0 | 2 | 0 |
| 83824 | early | 150 | 12 | 5 | 35 | 9 |
| 83824 | mid | 200 | 2 | 8 | 48 | 1 |
| 83824 | late | 151 | 4 | 15 | 61 | 1 |
| 290518 | early | 150 | 44 | 3 | 50 | 42 |
| 290518 | mid | 177 | 5 | 8 | 45 | 5 |
| 290518 | late | 0 | 0 | 0 | 0 | 0 |
| 548409 | early | 150 | 43 | 1 | 23 | 25 |
| 548409 | mid | 200 | 1 | 16 | 53 | 1 |
| 548409 | late | 151 | 1 | 4 | 31 | 1 |
| 225587 | early | 150 | 117 | 1 | 18 | 115 |
| 225587 | mid | 73 | 16 | 2 | 14 | 11 |
| 225587 | late | 0 | 0 | 0 | 0 | 0 |
| 836037 | early | 63 | 24 | 1 | 13 | 20 |
| 836037 | mid | 0 | 0 | 0 | 0 | 0 |
| 836037 | late | 0 | 0 | 0 | 0 | 0 |
| 585440 | early | 150 | 2 | 5 | 27 | 1 |
| 585440 | mid | 200 | 9 | 20 | 47 | 4 |
| 585440 | late | 67 | 2 | 4 | 27 | 1 |
| 648293 | early | 132 | 18 | 8 | 49 | 8 |
| 648293 | mid | 0 | 0 | 0 | 0 | 0 |
| 648293 | late | 0 | 0 | 0 | 0 | 0 |
| 126779 | early | 150 | 0 | 1 | 16 | 0 |
| 126779 | mid | 200 | 0 | 12 | 45 | 0 |
| 126779 | late | 151 | 6 | 6 | 47 | 1 |
| 609286 | early | 150 | 45 | 2 | 17 | 23 |
| 609286 | mid | 200 | 104 | 0 | 9 | 104 |
| 609286 | late | 151 | 151 | 0 | 1 | 255 |

## Vấn Đề Chính

- STOP/camping quá dài xuất hiện ở nhiều seed, làm agent mất tempo và dễ bị trap khi bom đối thủ áp sát.
- Có seed đặt rất ít bom hoặc bom giá trị thấp, nên step500 tie-break kém dù sống tới cuối trận.
- Một số seed chết ngay sau khi đặt bom rồi không thoát đủ xa; B cần giảm scoring cho bomb nếu action sau đó bị ép STOP.
- Mobility thấp trong các trận sống lâu là dấu hiệu target selection/anti-loop chưa đủ mạnh.

## Đề Xuất Rule_v2

- Giảm điểm STOP theo cấp số nhân khi `max_stop_streak` cục bộ >= 3, trừ khi STOP là action safe duy nhất.
- Tăng bonus progress nếu action làm giảm distance tới farm/item target; phạt quay lại ô vừa đứng nếu không có danger.
- Chỉ cộng `PLACE_BOMB` khi có `box_gain`, enemy pressure rõ ràng, hoặc current-code safety replay cho thấy có đường thoát sau bomb.
- Thêm phase late tie-break: nếu sống sau step 350 mà rank proxy thấp, tăng farm/item/pressure có kiểm soát thay vì camping.
