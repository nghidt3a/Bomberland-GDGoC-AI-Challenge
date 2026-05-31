# Đóng gói submission và debug

Submission nên tối giản, đúng interface và dễ kiểm tra. Đừng đưa toàn bộ project vào ZIP.

## Cấu trúc ZIP

```text
submission.zip
├── agent.py
├── model.pth      # nếu cần
└── config.json    # nếu cần
```

`agent.py` phải ở root ZIP.

## Trước khi zip

Kiểm tra:

- `Agent` class tồn tại.
- `Agent(0)` khởi tạo được.
- `act(obs)` trả int `0..5`.
- Không có train tự chạy khi import.
- Checkpoint path tương đối đúng.
- Không phụ thuộc path cloud/local.

## Không đưa vào ZIP

- Notebook.
- Dataset.
- Log.
- Nhiều checkpoint.
- `__pycache__`.
- Folder `.git`.
- Plot ảnh.
- File quá lớn không dùng.

## Debug lỗi load

Nếu agent không load:

- Kiểm tra tên file `agent.py`.
- Kiểm tra class `Agent`.
- Kiểm tra import helper file có trong ZIP không.
- Kiểm tra checkpoint có đúng tên không.
- Kiểm tra code train có nằm dưới `if __name__ == "__main__":` không.

## Debug lỗi act

Nếu `act()` lỗi:

- Bọc try/except và fallback.
- Kiểm tra `obs["bombs"]` có thể rỗng.
- Kiểm tra dtype numpy.
- Kiểm tra `agent_id` dùng đúng index.
- Sanitize action trước return.

## Debug hành vi sau submit

Khi leaderboard/log có trận thua:

1. Xem step chết.
2. Xem bomb owner và timer.
3. Xem action trước khi chết.
4. Xem có item/box bị bỏ qua không.
5. Xem agent có bị timeout fallback không.

Ghi lỗi vào experiment log để sửa có hệ thống.

## Checklist nộp cuối

- [ ] ZIP <= 100MB.
- [ ] Tối đa 20 file.
- [ ] `agent.py` ở root.
- [ ] Checkpoint tốt nhất duy nhất.
- [ ] Benchmark pass.
- [ ] Test mixed baseline pass.
- [ ] Không dùng network/LLM/file writing.
- [ ] Có fallback action.
- [ ] Có ghi chú version để biết bản nào đã nộp.

