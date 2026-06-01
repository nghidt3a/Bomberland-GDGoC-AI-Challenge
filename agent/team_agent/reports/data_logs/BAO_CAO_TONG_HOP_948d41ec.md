# Báo Cáo Tổng Hợp Data Logs

- Team id: `948d41ec-3dbd-4840-9ee5-f0d01cc1b6c0`
- Log dir: `agent\data_logs`
- Generated at: `2026-06-01 18:22:40`
- Số trận có team id: 12/12
- Average rank: 2.00 (rank càng nhỏ càng tốt)
- Average survival: 354.5 steps
- Sống tới step 500: 6/12
- Chết trước step 500: 6/12
- Chết sớm trước step 150: 3/12
- Trận có STOP streak >= 20: 6/12

## Bảng Tổng Hợp Trận

| file | seed | idx | rank | survival | death | alive500 | bombs | max STOP | unique cells | issues |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| match_20260601_094346_109659.json | 109659 | 3 | 3 | 92 | 92 | no | 4 | 5 | 18 | chết do bom mình / thoát bom kém, chết sớm, lặp A-B-A-B, safety replay flag |
| match_20260601_094349_548846.json | 548846 | 0 | 2 | 500 | - | yes | 29 | 74 | 79 | STOP quá dài, lặp A-B-A-B, sống 500 nhưng tie-break yếu |
| match_20260601_094351_156663.json | 156663 | 0 | 1 | 500 | - | yes | 3 | 1 | 36 | lặp A-B-A-B, di chuyển ít, ít đặt bom |
| match_20260601_094356_83824.json | 83824 | 2 | 0 | 500 | - | yes | 28 | 9 | 82 | lặp A-B-A-B |
| match_20260601_094357_290518.json | 290518 | 3 | 3 | 327 | 327 | no | 11 | 42 | 60 | chết do bom mình / thoát bom kém, STOP quá dài, safety replay flag |
| match_20260601_094400_548409.json | 548409 | 3 | 1 | 500 | - | yes | 21 | 25 | 74 | STOP quá dài, lặp A-B-A-B |
| match_20260601_094452_225587.json | 225587 | 3 | 2 | 223 | 223 | no | 3 | 115 | 30 | chết do bom mình / thoát bom kém, STOP quá dài, lặp A-B-A-B, ít đặt bom |
| match_20260601_094453_836037.json | 836037 | 0 | 3 | 63 | 63 | no | 1 | 20 | 13 | chết do bom đối thủ, chết sớm, STOP quá dài, lặp A-B-A-B |
| match_20260601_094457_585440.json | 585440 | 1 | 2 | 417 | 417 | no | 29 | 4 | 69 | chết do bom mình / thoát bom kém, lặp A-B-A-B, safety replay flag |
| match_20260601_094501_648293.json | 648293 | 3 | 3 | 132 | 132 | no | 8 | 8 | 49 | chết do bom mình / thoát bom kém, chết sớm, lặp A-B-A-B, safety replay flag |
| match_20260601_094510_126779.json | 126779 | 1 | 3 | 500 | - | yes | 19 | 1 | 63 | lặp A-B-A-B, bom ít giá trị, sống 500 nhưng tie-break yếu |
| match_20260601_094632_609286.json | 609286 | 3 | 1 | 500 | - | yes | 2 | 255 | 19 | STOP quá dài, lặp A-B-A-B, di chuyển ít, ít đặt bom |

## Tần Suất Vấn Đề

| issue | matches |
| --- | --- |
| lặp A-B-A-B | 11 |
| safety replay flag | 6 |
| STOP quá dài | 6 |
| chết do bom mình / thoát bom kém | 5 |
| ít đặt bom | 4 |
| chết sớm | 3 |
| di chuyển ít | 2 |
| sống 500 nhưng tie-break yếu | 2 |
| chết do bom đối thủ | 1 |
| bom ít giá trị | 1 |

## Nhận Định Nhanh

- Runtime log hiện tại không ghi nhận timeout/error/invalid action nổi bật.
- Vấn đề lớn nhất là survival không ổn định: một nửa số trận chết trước step 500.
- Nhiều trận có STOP streak dài, làm giảm progress và có thể làm agent bị trap.
- Một số trận sống đến step 500 nhưng rank vẫn thấp, cần cải thiện tie-break bằng box/item/kill/progress.
