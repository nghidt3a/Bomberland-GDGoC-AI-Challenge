# GDGoC-HCMUS AI Challenge 2026 - BomberGame / Bomberland

> **Nguồn tổng hợp:** file `[AI&DS][AIC] BomberGame plan.pdf` do người dùng cung cấp.  
> **Đơn vị/nhóm tài liệu:** Team AI&DS - Ban Development.  
> **Chủ đề cuộc thi:** Học Tăng Cường (*Reinforcement Learning*).  
> **Ghi chú:** File này được biên soạn lại theo cấu trúc Markdown, giữ đầy đủ thông tin trong tài liệu gốc, đồng thời bổ sung các URL ẩn trong PDF vào đúng vị trí liên quan.

---

## 1. Giới thiệu chung

Câu lạc bộ **GDGoC - HCMUS** giới thiệu **AI Challenge 2026** như một sân chơi học thuật sáng tạo dành cho sinh viên đam mê **Trí tuệ Nhân tạo (AI)**. Cuộc thi là cơ hội để người tham gia:

- Thử thách bản thân.
- Trau dồi kỹ năng.
- Phát triển tư duy nghiên cứu trong lĩnh vực AI.

Chủ đề của năm nay là **Học Tăng Cường (Reinforcement Learning)**.

---

## 2. Thông tin cuộc thi

### 2.1. Mục tiêu

Mục tiêu của cuộc thi là xây dựng các **agent tự động** có khả năng:

- Đưa ra chiến thuật đặt bom.
- Né tránh nguy hiểm.
- Hoạt động trong môi trường đối kháng nhiều đội.
- Ra quyết định chiến thuật theo thời gian.
- Sinh tồn và loại bỏ đối thủ.

### 2.2. Hình thức thi

Cuộc thi mô phỏng trò chơi tuổi thơ **Bom IT**.

Các đặc điểm chính:

- Mỗi đội gồm tối đa **2 thành viên**.
- Mỗi trận đấu gồm **4 đội**.
- Mỗi đội điều khiển **1 agent**.
- Tổng cộng mỗi trận có **4 agent**.

Agent có thể thực hiện các hành động:

- Di chuyển.
- Đặt bom.
- Phá thùng.
- Thu thập vật phẩm hỗ trợ.

Điều kiện kết thúc trận đấu:

- Chỉ còn **1 đội duy nhất** còn agent trên bản đồ; hoặc
- Hết thời gian quy định của trận đấu.

### 2.3. Cách thức tham gia

- Đăng ký theo đội.
- Mỗi đội tối đa **2 người**.

---

## 3. Quy trình thi

### 3.1. Vòng 1 - Huấn luyện & Thi đấu

**Thời gian:** 21/5 - 21/6.

Ban tổ chức cung cấp cho thí sinh:

- Tài liệu hướng dẫn, bao gồm:
  - Baseline agent.
  - Hướng dẫn tương tác với môi trường.
  - Tài liệu học Reinforcement Learning.
- Bộ công cụ phát triển (**participant kit**), gồm:
  - Engine.
  - Visualizer.
  - Và các công cụ liên quan khác.
- Hướng dẫn sử dụng các nền tảng như **Kaggle/Colab** để huấn luyện mô hình.

Trong thời gian này:

- Ban tổ chức đóng vai trò mentor và hỗ trợ các đội.
- Các đội có thể nộp bài nhiều lần.
- Agent sẽ được tự động thi đấu với các đội khác hoặc baseline agents để cập nhật bảng xếp hạng.

### 3.2. Vòng 2 - Pitching online

**Thời gian:** 24/6.

- Top 5 đội có thứ hạng cao nhất vòng **Grand Finals** sẽ trình bày mô hình và phương pháp của mình.

---

## 4. Yêu cầu kỹ thuật

### 4.1. Thuật toán

- Không giới hạn phương pháp.
- Các hướng tiếp cận được chấp nhận gồm:
  - Reinforcement Learning.
  - Rule-based.
  - Hybrid.
  - Các phương pháp khác phù hợp.
- Không được phép sử dụng API gọi đến các mô hình bên ngoài trong quá trình thi đấu.

### 4.2. Công nghệ

Các công nghệ được khuyến khích sử dụng:

- PyTorch.
- TensorFlow.

### 4.3. Thách thức

Cuộc thi có các thách thức chính:

- Môi trường chơi phức tạp.
- Không gian tìm kiếm rộng lớn.
- Nhiều agent cùng tồn tại trong một trận đấu.
- Agent phải tương tác và phản ứng linh hoạt trước các hành vi khác nhau.
- Agent cần ra quyết định nhanh nhưng vẫn đảm bảo chiến thuật hiệu quả.
- Số lượng trạng thái lớn.
- Chiến thuật của các team đối thủ đa dạng.

---

## 5. Thông tin tổ chức

| Nội dung | Thông tin |
|---|---|
| Link đăng ký | <https://forms.gle/E3N6JWXLBsZXhRP26> |
| Thời gian mở đăng ký | 21/5 |
| Hình thức thi | Team tối đa 2 người |
| Tổng giải thưởng | 1.500.000 đồng |
| Hỗ trợ và hướng dẫn | `#Tổng quan` |

---

# PHẦN TỔNG QUAN CHI TIẾT

## 6. Thông tin tài liệu tổng quan

- Tác giả/ghi chú trong tài liệu: **Đạt, Tuấn**.
- Đơn vị: **Team AI&DS - Ban Development**.

### 6.1. Mục lục trong tài liệu gốc

1. Tổng quan về trò chơi.
2. Cơ chế game chi tiết.
3. Đăng ký & Nộp bài.
4. Cấu trúc Agent & Yêu cầu nộp bài.
5. Hệ thống chấm điểm & Bảng xếp hạng.
6. Các Baseline Agent.
7. Tài liệu RL.
8. Giải thưởng & Timeline.
9. Vòng chung kết (Grand Finals).
10. Cấu hình máy chấm.
11. Participant Kit.
12. Tính minh bạch.

---

## 7. Tổng quan về trò chơi

**Bomberland** là game chiến thuật theo lượt lấy cảm hứng từ **Bomberman**.

Thông tin chính:

- Có **4 agent** thi đấu.
- Bản đồ là lưới **13×13**.
- Vùng chơi hiệu dụng là **11×11**.
- Nhiệm vụ của agent:
  - Di chuyển.
  - Đặt bom.
  - Phá hộp.
  - Thu thập vật phẩm.
  - Tiêu diệt đối thủ.

### 7.1. Bản đồ

Đặc điểm bản đồ:

- Kích thước: **13×13 ô**.
- Viền ngoài là **tường cố định**.
- Vùng chơi hiệu dụng: **11×11**.
- Bản đồ được sinh ngẫu nhiên mỗi trận theo **seed**.
- Bản đồ đảm bảo kết nối toàn bộ ô, tức là không có vùng bị cô lập.

### 7.2. Các loại ô trên bản đồ

| Ký hiệu | Tên | Mô tả |
|---:|---|---|
| 0 | Grass (Cỏ) | Đi được, đặt bom được |
| 1 | Wall (Tường) | Không phá được, chặn vụ nổ |
| 2 | Box (Hộp) | Có thể phá bằng bom; khi phá có xác suất rơi vật phẩm |
| 3 | Item: Radius | Thu thập để tăng bán kính bom +1 |
| 4 | Item: Capacity | Thu thập để tăng số bom mang theo +1 |

### 7.3. Vị trí xuất phát

4 agent xuất phát tại 4 góc của bản đồ. Vị trí cố định theo ID 0-3:

| Agent | Vị trí xuất phát | Mô tả |
|---:|---|---|
| Agent 0 | `(1, 1)` | Góc trên trái |
| Agent 1 | `(11, 11)` | Góc dưới phải |
| Agent 2 | `(1, 11)` | Góc trên phải |
| Agent 3 | `(11, 1)` | Góc dưới trái |

Vùng **2×2** xung quanh mỗi góc luôn được đảm bảo trống:

- Không có hộp.
- Không có tường.
- Mục đích là để agent không bị kẹt ngay từ đầu.

---

## 8. Cơ chế game chi tiết

### 8.1. Thứ tự xử lý mỗi step

Mỗi step game được xử lý theo thứ tự sau:

1. Thu thập hành động.
2. Xử lý di chuyển.
3. Đặt bom.
4. Giảm timer bomb.
5. Kích nổ bom có `time = 0`.
6. Loại agent.
7. Spawn vật phẩm.
8. Kiểm tra kết thúc.

Dạng chuỗi xử lý trong tài liệu gốc:

```text
Thu thập hành động → Xử lý di chuyển → Đặt bom → Giảm timer bomb → Kích nổ bom có time = 0 → Loại agent → Spawn vật phẩm → Kiểm tra kết thúc
```

### 8.2. Hành động của Agent

Mỗi step, agent trả về **1 số nguyên**.

| Giá trị | Hành động | Ý nghĩa |
|---:|---|---|
| 0 | STOP | Đứng yên |
| 1 | LEFT | Đi trái |
| 2 | RIGHT | Đi phải |
| 3 | UP | Đi lên |
| 4 | DOWN | Đi xuống |
| 5 | PLACE_BOMB | Đặt bom |

### 8.3. Quy tắc di chuyển

- Agent không thể đi xuyên tường `1`.
- Agent không thể đi xuyên hộp `2`.
- Agent không thể đi xuyên bom của step trước, tức là bom đã tồn tại trên sàn.
- Ngoại lệ: nếu agent đang đứng đúng ô đó khi đặt bom thì vẫn có thể rời đi.
- Nhiều agent có thể đứng trên cùng một ô.
- Nếu 2 agent cùng bước vào ô có vật phẩm đồng thời thì vật phẩm bị hủy, không ai nhận.

### 8.4. Cơ chế Bom

#### 8.4.1. Thông số mặc định

| Thông số | Giá trị |
|---|---|
| Timer | 7 steps, đếm từ 7 xuống 0, nổ khi ≤ 0 |
| Bán kính mặc định | 1, tăng theo item thu thập được |
| Số bom ban đầu | 1, tăng theo item |
| Bán kính tối đa | 5 |
| Số bom đặt tối đa | 5 |

#### 8.4.2. Quy tắc đặt bom

- Chỉ đặt được bom nếu `bombs_left > 0`.
- Không đặt lên ô đã có bom từ step trước.
- Nếu nhiều agent đặt bom tại cùng một ô trong cùng một step:
  - Engine xử lý agent theo thứ tự ID tăng dần: `0 → 3`.
  - Bom của agent sau chỉ ghi đè bom trước nếu có bán kính lớn hơn.
- Kết quả cụ thể:
  - Nếu bán kính khác nhau: bom có bán kính lớn hơn được đặt, bất kể agent ID nào.
  - Nếu bán kính bằng nhau: bom của agent có ID nhỏ hơn được đặt.
- Chỉ agent sở hữu bom được đặt mới bị trừ `bombs_left`.
- Chỉ người đặt bom mới tiêu tốn `bombs_left`.
- Bom vẫn tồn tại và chờ nổ kể cả khi agent đặt bom đã bị tiêu diệt.

#### 8.4.3. Cơ chế nổ

- Bom nổ theo 4 hướng:
  - Lên.
  - Xuống.
  - Trái.
  - Phải.
- Vụ nổ dừng tại tường, không xuyên qua tường.
- Vụ nổ dừng tại hộp và phá hộp đó, không xuyên tiếp.
- Vụ nổ xuyên qua agent, không bị chặn bởi người chơi.
- Vụ nổ chỉ kéo dài **1 step**.
- **Chain reaction:** nếu vụ nổ chạm vào một bom khác, bom đó nổ ngay lập tức trong cùng step đó.

### 8.5. Khi hộp bị phá

Khi hộp bị phá bằng bom:

| Kết quả | Xác suất |
|---|---:|
| Rơi Item Radius (+1 bán kính bom) | 30% |
| Rơi Item Capacity (+1 bom mang theo) | 30% |
| Không rơi gì | 40% |

### 8.6. Vật phẩm tự spawn

Mỗi step, mỗi ô cỏ trống có xác suất nhỏ tự spawn vật phẩm.

Điều kiện ô có thể spawn:

- Là ô cỏ trống.
- Không có agent đứng trên ô đó.

Xác suất spawn tăng dần theo số step đã qua:

```text
P = 0.0003 × (step / 165)
```

Loại vật phẩm khi tự spawn:

- 50% là Radius.
- 50% là Capacity.

### 8.7. Khi agent bị tiêu diệt

- Bất kỳ agent nào đứng trên ô bị ảnh hưởng bởi vụ nổ sẽ bị loại ngay lập tức.
- Agent bị loại sẽ không thể hành động thêm.
- Tuy nhiên, các quả bom mà agent đó đã đặt trước khi bị tiêu diệt vẫn tồn tại trên bản đồ.
- Các quả bom đó tiếp tục đếm ngược timer và nổ bình thường.

### 8.8. Tự hủy

- Agent có thể tự tiêu diệt bản thân.
- Cơ chế này được gọi là **Self-destruct**.

### 8.9. Kết thúc trận đấu

Trận đấu kết thúc khi một trong hai điều kiện xảy ra:

- Còn **≤ 1 agent** sống sót; hoặc
- Đạt **500 steps**.

---

## 9. Đăng ký & Nộp bài

### 9.1. Bước 1 - Đăng ký đội

Người tham gia điền Form Đăng ký với các thông tin:

- Tên đội, phải khác các đội khác.
- Tên và email người liên hệ chính.
- Tên và email người liên hệ phụ, nếu có.
- Xác nhận đồng ý với quy định cuộc thi.

Link đăng ký trong tài liệu: <https://forms.gle/E3N6JWXLBsZXhRP26>

### 9.2. Email xác nhận sau khi đăng ký

Sau khi đăng ký thành công, hệ thống sẽ gửi email xác nhận về địa chỉ của người liên hệ chính.

Email bao gồm:

| Thông tin | Mô tả |
|---|---|
| Team Name | Tên đội đã đăng ký |
| Canonical Team ID | ID định danh duy nhất, dùng khi nộp bài |
| Submission Token | Mật khẩu xác thực khi nộp bài, không chia sẻ |
| Link Form Nộp bài | Form dùng để nộp agent |
| Link Discord/Liên hệ | Kênh hỗ trợ |

### 9.3. Lưu ý về đăng ký lại và email xác nhận

- Đăng ký lại cùng cặp thông tin **tên đội + email chính** sẽ tạo ra **Submission Token** mới.
- Token mới sẽ vô hiệu hóa token cũ.
- Nếu đã đăng ký hợp lệ nhưng không có email xác nhận, có khả năng đã có đội khác trùng tên đăng ký từ trước.
- Khi đó, cần đăng ký lại với tên đội khác.

### 9.4. Bước 2 - Nộp bài

Điền Form Nộp bài với các thông tin:

- Canonical Team ID, lấy từ email xác nhận.
- Submission Token, lấy từ email xác nhận.
- Mô tả thay đổi (**changelog**), không bắt buộc.
- File `.zip`.

Link Form Nộp bài được nhúng trong PDF: <https://forms.gle/zKNYUSz8doYTn34H8>

### 9.5. Hạn mức nộp bài

- Mỗi đội được nộp tối đa **3 lần/ngày**.
- Hạn mức reset lúc **7:00 sáng giờ Việt Nam**.

---

## 10. Cấu trúc Agent & Yêu cầu nộp bài

### 10.1. Cấu trúc file ZIP

File nộp bài phải là một file `.zip` chứa đúng **một file `agent.py`** ở bất kỳ cấp thư mục nào.

Cấu trúc minh họa:

```text
submission.zip
├── agent.py      ← Bắt buộc, duy nhất
├── model.pth     ← Tùy chọn, nếu dùng RL
└── ...           ← Tùy chọn, các file weights, config nhỏ lẻ khác
```

### 10.2. Giới hạn file

| Tiêu chí | Giới hạn |
|---|---|
| Kích thước file ZIP | ≤ 100 MB |
| Tổng kích thước sau giải nén | ≤ 300 MB |
| Kích thước một file đơn lẻ | ≤ 150 MB |
| Số file tối đa | ≤ 20 file |
| Phần mở rộng được phép | `.py`, `.txt`, `.pt`, `.pth`, `.pkl`, `.onnx`, `.bin`, `.json`, `.yaml`, `.yml`, `.md`, `.h5`, `.pb`, `.keras`, `.tflite` |

### 10.3. Class Agent bắt buộc

File `agent.py` phải định nghĩa class `Agent` với đúng interface sau:

```python
class Agent:
    def __init__(self, agent_id: int):
        # agent_id: 0, 1, 2, hoặc 3, được tự động gán bởi engine
        self.agent_id = agent_id

    def act(self, obs: dict) -> int:
        # obs: dict gồm 'map', 'players', 'bombs'
        # Trả về: int trong [0, 5]
        ...
```

### 10.4. Observation `obs` nhận được mỗi step

Mỗi step, agent nhận `obs` dạng dictionary:

```python
obs = {
    "map":     np.ndarray,  # shape (13, 13), dtype int
                            # 0=Grass, 1=Wall, 2=Box, 3=Item_Radius, 4=Item_Capacity
    "players": np.ndarray,  # shape (4, 5), dtype int8
                            # Mỗi hàng: [row, col, alive, bombs_left, bomb_radius_bonus]
    "bombs":   np.ndarray,  # shape (N, 4), dtype int8, N = số bom hiện có
                            # Mỗi hàng: [row, col, timer, owner_id]
}
```

Lưu ý:

- `alive`: `1` = còn sống, `0` = đã chết.
- `bomb_radius_bonus`: số bonus thêm vào.
- Bán kính thực của bom = `1 + bonus`.
- `bombs_left`: số bom có thể đặt thêm.
- Agent nhận **full state** như trên.

### 10.5. Yêu cầu về thời gian

| Yêu cầu | Giới hạn |
|---|---|
| Startup timeout | 20 giây |
| Inference timeout | `act()` phải trả về trong vòng 100ms |

Nếu `act()` không trả về trong vòng **100ms**, hệ thống mặc định agent thực hiện hành động:

```text
0 - STOP
```

### 10.6. Quy định quan trọng

Không được:

- Dùng LLM như GPT, Gemini, Claude,... bên trong class `Agent`.
- Copy code từ đội khác.
- Import thêm thư viện không có sẵn trong môi trường chấm. Cần xem `requirements.txt` ở Participant Kit.

Được phép:

- Load model từ file checkpoints đi kèm trong ZIP.
- Mỗi bài nộp được coi là một agent riêng biệt và dùng một lần nộp trong ngày.

---

## 11. Hệ thống chấm điểm & Bảng xếp hạng

### 11.1. Cách chấm điểm: TrueSkill

Hệ thống sử dụng thuật toán **TrueSkill** của Microsoft Research để ước tính kỹ năng thực sự của từng agent.

Link tham khảo TrueSkill được nhúng trong PDF: <https://trueskill.org/#:~:text=FalseSkill%20objects,is%20a%20half%20of%20sigma%20.>

Mỗi submission được đặc trưng bởi:

- `μ` (**mu**): ước tính kỹ năng trung bình.
- `σ` (**sigma**): độ không chắc chắn; sigma giảm khi chơi nhiều trận hơn.
- `Score = μ − 3σ`: điểm thật, dùng để xếp hạng.

Ý nghĩa của công thức `Score = μ − 3σ`:

- Đảm bảo các agent đã chơi đủ nhiều trận mới được xếp hạng cao.
- Agent có độ không chắc chắn cao sẽ bị trừ điểm nhiều hơn.

Giá trị khởi đầu mặc định:

| Đại lượng | Giá trị ban đầu |
|---|---:|
| `μ` | 100 |
| `σ` | 33.3333 |

### 11.2. Kết quả mỗi trận

Mỗi trận có **4 agent**.

Thứ hạng trong trận được xác định theo thứ tự bị tiêu diệt:

- Agent bị tiêu diệt cuối cùng hoặc còn sống đến hết game = hạng tốt nhất.
- Agent bị tiêu diệt sớm nhất = hạng tệ nhất.
- Nhiều agent bị tiêu diệt cùng step = cùng hạng, được tính là draw.

### 11.3. Tie-break ở Step 500

Nếu có nhiều agent còn sống tới **step 500**, các agent này không còn mặc định được tính là có cùng hạng tốt nhất.

Thay vào đó, thứ hạng giữa các agent còn sống được xác định dựa trên mức độ tham gia giao tranh và tương tác trong trận đấu, theo thứ tự ưu tiên:

1. Số lượng tiêu diệt (**Kills**).
2. Số lượng hộp phá hủy (**Boxes Destroyed**).
3. Số lượng vật phẩm nhặt được (**Items Collected**).
4. Số lượng bom đã đặt (**Bombs Placed**).

Các agent có giá trị hoàn toàn giống nhau ở cả 4 tiêu chí trên sẽ được tính là hòa.

### 11.4. Win / Draw / Loss

| Kết quả | Định nghĩa |
|---|---|
| Win | Khi hạng của agent là tốt nhất và là duy nhất |
| Draw | Cùng thứ hạng tốt nhất với các agent khác |
| Loss | Không đạt được hạng tốt nhất |

### 11.5. Bảng xếp hạng Leaderboard

Thứ tự ưu tiên xếp hạng, bao gồm tie-break:

1. `Score = μ − 3σ` cao hơn → xếp trước.
2. Nếu bằng: `μ` cao hơn → xếp trước.
3. Nếu vẫn bằng: `σ` thấp hơn → xếp trước.
4. Nếu vẫn bằng: nộp bài gần đây hơn → xếp trước.

### 11.6. Hệ thống đánh giá tự động sau khi nộp

Sau khi một đội nộp bài:

1. Server tải file ZIP từ Google Drive.
2. Hệ thống kiểm tra cấu trúc và cú pháp, sau đó chạy thử một trận.
3. Nếu hợp lệ, hệ thống chạy ngay một batch **12 trận** với các agent trong pool.
4. Đối thủ được chọn từ **Active Pool** theo tỉ lệ:
   - 40% điểm gần giống.
   - 30% top cao nhất.
   - 30% ngẫu nhiên.
5. Hệ thống cập nhật bảng xếp hạng Google Sheets.

### 11.7. Background job

Worker chạy liên tục theo chu kỳ:

- Mỗi chu kỳ chạy **5 trận**.
- Sau đó nghỉ **10 giây**.
- Rồi tiếp tục lặp lại.

Mỗi trận được chọn từ **Active Pool** và đảm bảo ít nhất **1 agent không phải baseline** tham gia.

### 11.8. Active Pool

Active Pool gồm:

| Tiêu chí | Mô tả |
|---|---|
| Tất cả Baseline | Luôn trong pool |
| Best per Team | Submission tốt nhất theo Score của mỗi đội |
| Recent per Team | 2 submission gần nhất của mỗi đội |
| Top Global | Top 10 submission toàn cuộc thi, điều kiện ≥ 10 trận |

---

## 12. Các Baseline Agent

Hệ thống có **6 rule-based baseline agent** với rating cố định, không thay đổi trong suốt cuộc thi.

| Tên agent | Chiến lược | Score (`μ − 3σ`) |
|---|---|---:|
| `tactical_rule_agent` | Né nguy hiểm, tìm vật phẩm, nhắm kẻ địch, đặt bom có tính toán | ~114.7 |
| `genius_rule_agent` | Cân bằng tấn công và phòng thủ, BFS tìm đường | ~112.5 |
| `smarter_rule_agent` | Ưu tiên phá hộp, né bom, đuổi kẻ địch | ~111.3 |
| `box_farmer_agent` | Tập trung phá hộp để thu item | ~107.9 |
| `simple_rule_agent` | Logic đơn giản: né bom, đặt bom | ~107.8 |
| `random_agent` | Hành động ngẫu nhiên | ~99.0 |

Ngoài ra, có **1 RL-based agent**:

- `dqn_agent`: dùng để tham khảo cách triển khai Reinforcement Learning.

---

## 13. Tài liệu Reinforcement Learning

Các tài liệu RL được cung cấp trong tài liệu gốc:

| Tài liệu | Link |
|---|---|
| RL Book, Sutton Barto | <http://incompleteideas.net/book/the-book-2nd.html> |
| RL Course Toronto University | <https://bereyhi-courses.github.io/rl-utoronto/> |
| Neuriton | <https://www.facebook.com/share/1B4BpDUbyx/> |
| RL Exercises, AI VIETNAM | <https://www.facebook.com/share/p/192LyNsvbp/> |
| Single-File RL Algorithms Code / CleanRL | <https://github.com/vwxyzjn/cleanrl> |

---

## 14. Giải thưởng & Timeline

### 14.1. Giải thưởng dự kiến

| Hạng | Giải thưởng |
|---|---:|
| 🥇 1 Giải Nhất | 500.000 VNĐ |
| 🥈 1 Giải Nhì | 400.000 VNĐ |
| 🥉 1 Giải Ba | 300.000 VNĐ |
| 🏅 1 Giải Tư | 200.000 VNĐ |
| 🎖️ 1 Giải Khuyến Khích | 100.000 VNĐ |

Tổng giải thưởng: **1.500.000 VNĐ**.

### 14.2. Timeline

| Mốc thời gian | Sự kiện |
|---|---|
| 21/5 | Mở đăng ký & nộp bài |
| 24/5 | Workshop hỏi đáp về cuộc thi & RL |
| 21/6 | Đóng nộp bài, freeze bảng xếp hạng |
| 21-22/6 | Chọn Top 8 → chạy Grand Finals → công bố kết quả |
| 24/6 | Pitching online & trao giải |

### 14.3. Quy mô dự kiến

- Dự kiến có **25-30 đội**.
- Mỗi đội tối đa **2 người**.
- Cuộc thi mở rộng cho cả người ngoài câu lạc bộ tham gia.

---

## 15. Vòng chung kết Grand Finals

### 15.1. Chọn Top K

Sau khi freeze bảng xếp hạng, hệ thống chọn **Top 8 đội**.

Căn cứ chọn:

- Dựa trên submission tốt nhất của mỗi đội.
- Submission phải có số trận đã chơi **>= 50 trận**.

Thứ tự ưu tiên khi chọn Top 8:

1. `Score = μ − 3σ` cao nhất.
2. Nếu bằng: `μ` cao hơn.
3. Nếu vẫn bằng: `σ` thấp hơn.

Ngoài Top 8 đội, sẽ có thêm **1 baseline agent tốt nhất** tham gia làm thước đo chuẩn.

### 15.2. Format Grand Finals: Round Robin

Format vòng Grand Finals là **Round Robin**.

Cách tổ chức:

- Tất cả tổ hợp 4-player từ pool finalist được liệt kê.
- Số tổ hợp là `C(9,4)`.
- Mỗi tổ hợp chạy **50 trận**.
- Mỗi trận shuffle vị trí góc ngẫu nhiên.

### 15.3. Cách tính điểm Grand Finals

Điểm tính theo hạng trong từng trận:

| Hạng | Điểm |
|---|---:|
| Hạng 1, tốt nhất | 3 điểm |
| Hạng 2 | 2 điểm |
| Hạng 3 | 1 điểm |
| Hạng 4, tệ nhất | 0 điểm |

### 15.4. Tie-break Grand Finals

Nếu tổng điểm bằng nhau, thứ tự tie-break là:

1. `Score = μ − 3σ` từ bảng xếp hạng khi freeze cao hơn sẽ thắng.
2. Nếu vẫn bằng: `μ` cao hơn sẽ thắng.
3. Nếu vẫn bằng: `σ` thấp hơn sẽ thắng.

### 15.5. Online pitching

- Đội **top 5 sau Grand Finals** sẽ thuyết trình về thuật toán của đội.

---

## 16. Cấu hình máy chấm

| Thông số | Chi tiết |
|---|---|
| Máy chủ | Google Cloud VM (`e2-standard-8`) |
| CPU | 8 vCPU, 4 core vật lý |
| RAM | 32 GB |
| Hệ điều hành | Ubuntu 22.04 LTS |
| Python | 3.11, Conda environment |
| Inference timeout | 100ms/step |
| Startup timeout | 20 giây |
| Max steps/trận | 500 steps |

---

## 17. Participant Kit

Participant Kit là repo công khai chứa mọi thứ cần thiết để phát triển agent.

Link repo được nhúng trong PDF:

- <https://github.com/VLTisME/Bomberland-GDGoC-AI-Challenge>

Participant Kit có thể bao gồm:

- Engine game.
- Visualizer.
- Baseline agents.
- `requirements.txt` của môi trường chấm.
- Các tài nguyên cần thiết để phát triển và kiểm thử agent.

---

## 18. Tính minh bạch

### 18.1. Seed cố định

- Mỗi trận được gán một seed ngẫu nhiên duy nhất khi chạy.
- Seed được lưu trong log JSON.
- Điều này đảm bảo có thể minh họa lại trận đấu bằng cách chạy engine với:
  - Cùng seed.
  - Cùng agent.

### 18.2. Logs công khai

Mỗi trận được lưu thành:

- File JSON:
  - Chứa toàn bộ lịch sử mỗi step.
  - Bao gồm map, players, bombs, actions.
  - Bao gồm seed.
  - Bao gồm xếp hạng.
- File GIF:
  - Animation trận đấu.

Các file này được upload lên Google Drive sau mỗi trận và link được ghi vào Google Sheets để có thể truy cập trực tiếp.

Link Google Drive logs được nhúng trong PDF:

- <https://drive.google.com/drive/folders/1FBNTDpOJh_eMOIoe18in_e1myBQuUm0i?usp=sharing>

### 18.3. Bảng xếp hạng

- Bảng xếp hạng được cập nhật lên Google Sheets ngay sau mỗi lần nộp bài.
- Bảng xếp hạng cũng được cập nhật thường xuyên trong ngày.
- Google Sheets còn dùng để hiển thị logs khi nộp bài.

Link Google Sheets bảng xếp hạng được nhúng trong PDF:

- <https://docs.google.com/spreadsheets/d/1caRS0zqKovKqsL5ozzqNAtSWhseTVBT1LNBr0AVDrBE/edit?usp=sharing>

### 18.4. Repo công khai

- Toàn bộ source code engine game và các baseline agent được public trên GitHub.
- Mục đích là để mọi người có thể kiểm tra logic game.

Repo công khai:

- <https://github.com/VLTisME/Bomberland-GDGoC-AI-Challenge>

### 18.5. Cập nhật tài liệu và liên hệ

- Tài liệu sẽ được cập nhật khi có thay đổi.
- Mọi thắc mắc liên hệ qua Discord hoặc email ban tổ chức.

---

## 19. Bảng tóm tắt nhanh các thông số quan trọng

| Nhóm thông tin | Giá trị / Quy định |
|---|---|
| Tên cuộc thi | GDGoC-HCMUS AI Challenge 2026 |
| Chủ đề | Reinforcement Learning |
| Game | Bomberland / mô phỏng Bom IT / lấy cảm hứng từ Bomberman |
| Số đội mỗi trận | 4 đội |
| Số agent mỗi trận | 4 agent |
| Thành viên mỗi đội | Tối đa 2 người |
| Bản đồ | 13×13, vùng chơi hiệu dụng 11×11 |
| Vị trí xuất phát | 4 góc bản đồ theo ID 0-3 |
| Max steps/trận | 500 steps |
| Timer bom | 7 steps |
| Bán kính bom mặc định | 1 |
| Bán kính bom tối đa | 5 |
| Số bom ban đầu | 1 |
| Số bom đặt tối đa | 5 |
| Hành động hợp lệ | 0-5 |
| Timeout `act()` | 100ms |
| Startup timeout | 20 giây |
| Kích thước ZIP tối đa | 100 MB |
| Tổng kích thước sau giải nén | 300 MB |
| Kích thước một file đơn lẻ | 150 MB |
| Số file tối đa | 20 file |
| Số lần nộp bài | 3 lần/ngày |
| Reset lượt nộp | 7:00 sáng giờ Việt Nam |
| Cách xếp hạng chính | TrueSkill, `Score = μ − 3σ` |
| Giá trị khởi đầu | `μ = 100`, `σ = 33.3333` |
| Batch sau khi nộp hợp lệ | 12 trận |
| Background job | 5 trận rồi nghỉ 10 giây, lặp liên tục |
| Top Grand Finals | Top 8 đội + 1 baseline agent tốt nhất |
| Điều kiện Top 8 | Submission tốt nhất mỗi đội và >= 50 trận |
| Format Grand Finals | Round Robin, các tổ hợp `C(9,4)` |
| Số trận mỗi tổ hợp Grand Finals | 50 trận |
| Top pitching | Top 5 sau Grand Finals |
| Tổng giải thưởng | 1.500.000 VNĐ |
| Quy mô dự kiến | 25-30 đội |

---

## 20. Checklist dành cho đội tham gia

### 20.1. Trước khi đăng ký

- [ ] Chọn tên đội không trùng đội khác.
- [ ] Chuẩn bị tên và email người liên hệ chính.
- [ ] Chuẩn bị tên và email người liên hệ phụ nếu có.
- [ ] Đọc và đồng ý với quy định cuộc thi.

### 20.2. Sau khi đăng ký

- [ ] Kiểm tra email xác nhận.
- [ ] Lưu lại `Team Name`.
- [ ] Lưu lại `Canonical Team ID`.
- [ ] Lưu lại `Submission Token` và không chia sẻ token này.
- [ ] Lưu lại link Form Nộp bài.
- [ ] Lưu lại kênh Discord/liên hệ.
- [ ] Nếu không nhận được email, cân nhắc đăng ký lại với tên đội khác.

### 20.3. Khi chuẩn bị nộp bài

- [ ] File nộp là `.zip`.
- [ ] ZIP chứa đúng một file `agent.py`.
- [ ] `agent.py` định nghĩa đúng class `Agent`.
- [ ] `Agent.__init__(self, agent_id: int)` đúng interface.
- [ ] `Agent.act(self, obs: dict) -> int` đúng interface.
- [ ] `act()` trả về số nguyên trong `[0, 5]`.
- [ ] Không dùng LLM bên trong class `Agent`.
- [ ] Không copy code từ đội khác.
- [ ] Không import thư viện ngoài môi trường chấm.
- [ ] Nếu dùng model, checkpoint được đặt trong ZIP.
- [ ] ZIP ≤ 100 MB.
- [ ] Tổng sau giải nén ≤ 300 MB.
- [ ] Mỗi file đơn lẻ ≤ 150 MB.
- [ ] Tổng số file ≤ 20.
- [ ] Phần mở rộng file thuộc danh sách được phép.
- [ ] `act()` chạy trong 100ms/step.
- [ ] Startup không vượt 20 giây.
- [ ] Không nộp quá 3 lần/ngày.

### 20.4. Khi theo dõi kết quả

- [ ] Kiểm tra bảng xếp hạng Google Sheets sau khi nộp.
- [ ] Xem kết quả batch 12 trận ban đầu nếu bài hợp lệ.
- [ ] Theo dõi Score, `μ`, `σ`.
- [ ] Kiểm tra logs JSON/GIF nếu cần phân tích trận đấu.
- [ ] Lưu ý agent cần đủ số trận để `σ` giảm và Score ổn định hơn.
- [ ] Nếu nhắm Grand Finals, cần submission tốt nhất của đội có ít nhất 50 trận.

---

## 21. Danh sách link trong tài liệu

| Mục đích | Link |
|---|---|
| Form đăng ký | <https://forms.gle/E3N6JWXLBsZXhRP26> |
| Form nộp bài | <https://forms.gle/zKNYUSz8doYTn34H8> |
| TrueSkill | <https://trueskill.org/#:~:text=FalseSkill%20objects,is%20a%20half%20of%20sigma%20.> |
| RL Book, Sutton Barto | <http://incompleteideas.net/book/the-book-2nd.html> |
| RL Course Toronto University | <https://bereyhi-courses.github.io/rl-utoronto/> |
| Neuriton | <https://www.facebook.com/share/1B4BpDUbyx/> |
| RL Exercises, AI VIETNAM | <https://www.facebook.com/share/p/192LyNsvbp/> |
| CleanRL | <https://github.com/vwxyzjn/cleanrl> |
| Participant Kit / Repo | <https://github.com/VLTisME/Bomberland-GDGoC-AI-Challenge> |
| Google Drive logs | <https://drive.google.com/drive/folders/1FBNTDpOJh_eMOIoe18in_e1myBQuUm0i?usp=sharing> |
| Google Sheets leaderboard | <https://docs.google.com/spreadsheets/d/1caRS0zqKovKqsL5ozzqNAtSWhseTVBT1LNBr0AVDrBE/edit?usp=sharing> |

---

## 22. Ghi chú cuối

Tài liệu gốc nêu rằng tài liệu sẽ được cập nhật khi có thay đổi. Vì vậy, các thông tin trong file Markdown này phản ánh nội dung có trong PDF tại thời điểm trích xuất. Nếu ban tổ chức cập nhật thể lệ, participant kit, leaderboard, link nộp bài hoặc quy định chấm điểm, cần đối chiếu lại với tài liệu/nguồn chính thức mới nhất.
