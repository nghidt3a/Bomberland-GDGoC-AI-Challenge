# AI Challenge GDGoC HCMUS - Hướng dẫn siêu chi tiết

> **Nguồn:** File PDF `AI Challenge GDGoC HCMUS - Hướng dẫn.pdf`  
> **Đơn vị:** Google Developer Group on Campus - University of Science, VNUHCM  
> **Team:** AI&DS - Ban Development  
> **Tác giả trong tài liệu:** Đạt, Tuấn  
> **Chủ đề chính:** Hướng dẫn cơ chế game Bomberland/Bomberman và các hướng tiếp cận xây dựng agent AI: rule-based, adversarial search, reinforcement learning, DQN, PPO, self-play, behavior cloning và MCTS.

---

## 0. Tổng quan nội dung tài liệu

Tài liệu hướng dẫn này có hai nhóm nội dung lớn:

1. **Phần luật và cơ chế cuộc thi/game**: mô tả cách engine xử lý mỗi step, tập hành động của agent, quy tắc di chuyển, cơ chế bom, vật phẩm, điều kiện loại agent và điều kiện kết thúc trận đấu.
2. **Phần hướng dẫn thuật toán**: giới thiệu nhiều hướng tiếp cận có thể dùng để xây dựng agent, từ đơn giản đến nâng cao:
   - Rule-based agent.
   - Adversarial Search: Minimax và Alpha-Beta Pruning.
   - Reinforcement Learning nền tảng: MP, MRP, MDP, Monte Carlo, Temporal Difference.
   - Deep Q-Learning/DQN.
   - Policy Gradient và PPO.
   - Self-Play.
   - Behavior Cloning.
   - Monte Carlo Tree Search/MCTS và biến thể hiện đại PUCT.

---

## 1. Mục lục gốc của tài liệu

Tài liệu gốc gồm các mục sau:

1. **Về cuộc thi**
   - 1.1. Thứ tự xử lý mỗi Step
   - 1.2. Hành động của Agent
   - 1.3. Cơ chế Bom
   - 1.4. Vật phẩm (Items)
   - 1.5. Điều kiện loại bỏ và Kết thúc
2. **Rule-based**
   - 2.1. Cơ chế hoạt động
   - 2.2. Ưu điểm
   - 2.3. Nhược điểm
3. **Các thuật toán cơ bản**
   - 3.1. Đối kháng và Tìm kiếm có đối thủ (Adversarial Search)
   - 3.1.1. Thuật toán Minimax
   - 3.1.2. Cắt tỉa Alpha-Beta (Alpha-Beta Pruning)
4. **Học tăng cường**
   - 4.1. Từ Markov Process đến Model-free Evaluation
   - 4.2. Deep Q-Learning
   - 4.2.1. Nguồn gốc, lý thuyết nền tảng và bài toán hội tụ
   - 4.2.2. Thuật toán chi tiết và mã giả DQN
   - 4.3. Policy Gradient Methods
   - 4.3.1. Hạn chế của DQN và triết lý tối ưu trực tiếp chính sách
   - 4.3.2. Thuật toán PPO (Proximal Policy Optimization)
   - 4.3.3. Đánh giá và so sánh thực tiễn
   - 4.4. Self-Play
   - 4.4.1. Nguồn gốc và ý tưởng cơ bản
   - 4.4.2. Các bước chi tiết và mã giả
   - 4.5. Behaviour Cloning
   - 4.5.1. Nguồn gốc và ý tưởng cơ bản
   - 4.5.2. Các bước chi tiết và mã giả
   - 4.5.3. Monte Carlo Tree Search (MCTS)
5. **Nguồn tham khảo**

---

# PHẦN I. CƠ CHẾ GAME VÀ LUẬT TƯƠNG TÁC

## 2. Về cuộc thi và cơ chế game

Tài liệu mở đầu bằng phần tóm tắt cơ chế game. Đây là phần rất quan trọng vì mọi thuật toán/agent đều phải tuân theo cách engine xử lý trạng thái, hành động, bom, vật phẩm và điều kiện kết thúc.

### 2.1. Thứ tự xử lý mỗi Step

Mỗi bước (`step`) của trò chơi được engine xử lý tuần tự theo pipeline sau:

```text
[Thu thập hành động]
→ [Xử lý di chuyển]
→ [Đặt bom]
→ [Giảm timer bom]
→ [Giải quyết nổ]
→ [Loại agent]
→ [Spawn vật phẩm]
→ [Kiểm tra kết thúc]
```

Ý nghĩa từng giai đoạn:

| Thứ tự | Giai đoạn | Ý nghĩa |
|---:|---|---|
| 1 | Thu thập hành động | Engine nhận hành động do các agent trả về ở step hiện tại. |
| 2 | Xử lý di chuyển | Agent được di chuyển theo hành động đã chọn nếu ô đích hợp lệ. |
| 3 | Đặt bom | Nếu agent chọn `PLACE_BOMB` và đủ điều kiện, bom được đặt tại vị trí hiện tại. |
| 4 | Giảm timer bom | Timer của các quả bom đang tồn tại được giảm dần. |
| 5 | Giải quyết nổ | Các bom có timer về 0 hoặc nhỏ hơn sẽ nổ; chain reaction có thể kích hoạt bom khác. |
| 6 | Loại agent | Agent đứng trong vùng nổ bị loại ngay lập tức. |
| 7 | Spawn vật phẩm | Vật phẩm có thể xuất hiện trên ô cỏ trống theo xác suất. |
| 8 | Kiểm tra kết thúc | Trận đấu kết thúc nếu còn không quá 1 agent sống hoặc đạt giới hạn step. |

Điểm cần chú ý: thứ tự xử lý ảnh hưởng trực tiếp đến chiến thuật. Ví dụ, hành động di chuyển được xử lý trước đặt bom, còn loại agent chỉ xảy ra sau khi bom nổ.

---

## 3. Hành động của Agent

Tại mỗi step, mỗi agent phải gửi về **một số nguyên** biểu diễn hành động.

| Giá trị | Hành động | Mô tả |
|---:|---|---|
| `0` | `STOP` | Đứng yên tại vị trí hiện tại. |
| `1` | `LEFT` | Di chuyển sang trái 1 ô. |
| `2` | `RIGHT` | Di chuyển sang phải 1 ô. |
| `3` | `UP` | Di chuyển lên trên 1 ô. |
| `4` | `DOWN` | Di chuyển xuống dưới 1 ô. |
| `5` | `PLACE_BOMB` | Đặt bom tại vị trí hiện tại. |

### 3.1. Quy tắc di chuyển

Các quy tắc di chuyển được nêu trong tài liệu:

- Agent **không thể đi vào ô có tường** (`Wall`, mã `1`).
- Agent **không thể đi vào ô có hộp** (`Box`, mã `2`).
- Agent **không thể đi vào ô đã có bom từ các step trước**.
- Ngoại lệ liên quan đến bom: nếu agent vừa đặt bom tại ô hiện tại trong step đó, agent vẫn có thể rời khỏi ô đặt bom.
- Nhiều agent **có thể đứng cùng một ô**.
- Nếu từ 2 agent trở lên cùng bước vào một ô có vật phẩm, vật phẩm đó bị hủy và **không agent nào nhận được**.

### 3.2. Ý nghĩa chiến thuật của quy tắc di chuyển

Những quy tắc trên tạo ra một số hệ quả chiến thuật:

- Tường và hộp tạo thành vật cản trong bài toán tìm đường.
- Bom trên sàn tạo thành vật cản tạm thời.
- Vì nhiều agent có thể cùng đứng trên một ô, agent không thể chỉ dựa vào va chạm vật lý để chặn đối thủ.
- Cơ chế vật phẩm bị hủy khi nhiều agent cùng nhặt khiến việc tranh vật phẩm không chỉ là bài toán đường đi ngắn nhất mà còn cần dự đoán hành động đối thủ.

---

## 4. Cơ chế Bom

### 4.1. Thông số mặc định

| Thông số | Giá trị mặc định | Giới hạn/ghi chú |
|---|---:|---|
| Timer | `7 steps` | Đếm ngược về `0`, bom nổ khi timer `≤ 0`. |
| Radius/Bán kính | `1` | Tối đa `5`. |
| Capacity/Số lượng bom | `1` | Tối đa `5`. |

### 4.2. Quy tắc đặt bom

Agent chỉ đặt được bom khi thỏa mãn điều kiện:

```text
bombs_left > 0
và ô hiện tại chưa có bom từ step trước
```

Nếu nhiều agent đặt bom tại cùng một ô, engine xử lý theo quy tắc ưu tiên:

1. Ưu tiên bom có **bán kính lớn hơn**.
2. Nếu bán kính bằng nhau, ưu tiên agent có **ID nhỏ hơn**.
3. Chỉ người đặt bom cuối cùng theo quy tắc trên mới bị trừ `bombs_left`.

### 4.3. Cơ chế nổ

Khi bom nổ:

- Vụ nổ lan theo **4 hướng**: lên, xuống, trái, phải.
- Hình dạng vụ nổ giống hình **thập tự**.
- Tường chặn hoàn toàn vụ nổ.
- Hộp chặn vụ nổ và bị phá hủy.
- Agent không chặn vụ nổ.
- Nếu vụ nổ chạm vào quả bom khác, quả bom đó nổ ngay lập tức trong cùng step. Đây là **chain reaction**.

### 4.4. Hàm ý chiến thuật của bom

Bom là công cụ tấn công, phá hộp, mở đường, kiểm soát vùng và bẫy đối thủ. Tuy nhiên, bom cũng gây nguy hiểm cho chính agent, vì agent có thể bị loại bởi vụ nổ do chính mình tạo ra.

Một agent tốt cần xử lý đồng thời:

- Đặt bom ở vị trí tạo lợi ích cao.
- Dự đoán vùng nổ sau vài step.
- Tìm đường thoát trước khi bom nổ.
- Tránh chain reaction bất lợi.
- Tận dụng chain reaction để tấn công hoặc phá hộp nhanh.

---

## 5. Vật phẩm (Items)

Vật phẩm giúp tăng sức mạnh agent, gồm hai loại chính:

| Loại vật phẩm | Tác dụng |
|---|---|
| `Item Radius` | Tăng bán kính bom. |
| `Item Capacity` | Tăng số lượng bom agent có thể mang/đặt. |

### 5.1. Vật phẩm rơi từ hộp

Khi hộp bị phá, có xác suất rơi vật phẩm:

| Kết quả sau khi phá hộp | Xác suất |
|---|---:|
| Rơi `Item Radius` | `30%` |
| Rơi `Item Capacity` | `30%` |
| Không rơi gì | `40%` |

Tổng xác suất có vật phẩm sau khi phá hộp là `60%`.

### 5.2. Vật phẩm tự xuất hiện

Mỗi ô cỏ trống có thể tự sinh vật phẩm theo xác suất:

$$
P = 0.0003 \times \left(\frac{step}{165}\right)
$$

Trong đó:

- `step` là số step hiện tại của trận đấu.
- Khi vật phẩm tự spawn, xác suất loại vật phẩm là:
  - `50%` Radius.
  - `50%` Capacity.

### 5.3. Hàm ý chiến thuật của vật phẩm

Vật phẩm tạo động lực để agent phá hộp và di chuyển chủ động. Agent càng thu thập được nhiều vật phẩm thì càng có khả năng:

- Đặt nhiều bom hơn.
- Tạo vùng nổ rộng hơn.
- Kiểm soát bản đồ tốt hơn.
- Gây áp lực lên đối thủ mạnh hơn.

Tuy nhiên, đi nhặt vật phẩm cũng có rủi ro vì có thể đi vào vùng nguy hiểm hoặc bị đối thủ bẫy.

---

## 6. Điều kiện loại bỏ và kết thúc

### 6.1. Điều kiện loại agent

Agent bị loại ngay lập tức nếu đứng trong ô bị ảnh hưởng bởi vụ nổ, kể cả trường hợp tự đặt bom rồi tự trúng vụ nổ.

Điểm quan trọng:

- Agent đã bị loại **không còn hành động**.
- Tuy nhiên, các quả bom cũ mà agent đã đặt **vẫn còn trên sân** và vẫn có thể nổ theo timer/chain reaction.

### 6.2. Điều kiện kết thúc trận đấu

Trận đấu kết thúc khi xảy ra một trong hai điều kiện:

1. Chỉ còn `≤ 1` agent sống sót.
2. Trận đấu đạt giới hạn `500 steps`.

---

# PHẦN II. HƯỚNG TIẾP CẬN RULE-BASED

## 7. Rule-based Agent

Rule-based là cách xây dựng agent bằng các **heuristic** và quy tắc được lập trình sẵn. Agent không học từ trải nghiệm mà hành động theo tập điều kiện đã viết trước.

Ví dụ:

- Nếu phía trước là tường thì không đi tiếp.
- Nếu gần đối thủ và còn bom thì đặt bom.
- Nếu thấy vật phẩm trên đường thì đi lấy.
- Nếu đang trong vùng nguy hiểm thì ưu tiên chạy đến vùng an toàn.

---

## 8. Cơ chế hoạt động của rule-based

Agent rule-based quan sát trạng thái hiện tại, gồm:

- Vị trí vật cản.
- Vị trí bom.
- Vị trí đối thủ.
- Vị trí vật phẩm.
- Mức độ nguy hiểm của các ô.

Sau đó agent áp dụng chuỗi điều kiện `if-else` để quyết định hành động.

### 8.1. Các chiến lược thường dùng

Tài liệu nêu các thành phần chiến lược thường có trong agent rule-based:

- Tìm kiếm tuyến tính để định vị đối thủ gần nhất.
- Tìm kiếm vật phẩm có giá trị cao nhất.
- Ưu tiên hành động dựa trên khoảng cách.
- Ưu tiên hành động dựa trên mức độ nguy hiểm.
- Tránh các vùng có bom.
- Tránh tường/vật cản.
- Mã hóa cứng kiến thức về cách di chuyển an toàn sau khi đặt bom.

---

## 9. Ưu điểm của rule-based

Rule-based có các ưu điểm chính:

- Dễ triển khai nhanh.
- Không cần dữ liệu huấn luyện.
- Không cần thời gian tính toán để huấn luyện mô hình.
- Agent có thể chạy được ngay.
- Hành vi dễ giải thích vì mọi quyết định đều đến từ quy tắc rõ ràng.

---

## 10. Nhược điểm của rule-based

Rule-based có các hạn chế chính:

- Quy tắc bị code cứng, khó tổng quát hóa.
- Dễ thất bại trước tình huống nằm ngoài phạm vi `if-else` đã viết.
- Agent không học được từ thất bại.
- Agent hành động theo heuristic cứng nhắc.
- Khó đối phó với đối thủ có chiến thuật thay đổi hoặc hành vi phức tạp.

---

# PHẦN III. CÁC THUẬT TOÁN CƠ BẢN: ADVERSARIAL SEARCH

## 11. Đối kháng và tìm kiếm có đối thủ

Bomberland/Bomberman là trò chơi chiến thuật theo lượt có 4 agent trên bản đồ lưới `13 × 13`. Vì có nhiều đối thủ cạnh tranh trực tiếp, bài toán không chỉ là tìm đường ngắn nhất mà còn là:

- Dự đoán hành động của đối thủ.
- Đối phó với chiến thuật của đối thủ.
- Tìm hành động tốt trong môi trường đối kháng.

Các thuật toán tìm kiếm có đối thủ như **Minimax** là lựa chọn cốt lõi cho dạng bài này.

---

## 12. Thuật toán Minimax

### 12.1. Ý tưởng

Minimax là thuật toán đệ quy dùng để chọn hành động tối ưu cho một người chơi, gọi là **Max**, với giả định đối thủ, gọi là **Min**, cũng chơi tối ưu để chống lại Max.

Trong Bomberland có 4 agent, về lý thuyết có thể mở rộng thành thuật toán **Max-N**. Tuy nhiên, một cách tiếp cận đơn giản hơn là xem bài toán theo dạng:

```text
1 vs All
```

Tức là:

- Agent của ta là `Max`.
- Môi trường và 3 agent còn lại được gộp thành `Min`.

### 12.2. Tập hành động

Mỗi bước, agent chọn một hành động:

$$
a \in \{0, 1, 2, 3, 4, 5\}
$$

Tương ứng với:

```text
STOP, LEFT, RIGHT, UP, DOWN, PLACE_BOMB
```

### 12.3. Công thức Minimax cơ bản

Với bài toán 2 người chơi, giá trị trạng thái `s` trong cây Minimax được mô tả bởi:

$$
V(s) = \max_{a \in A} \min_{a' \in A'} V(Result(s, a, a'))
$$

Trong đó:

- `A` là tập hành động của Agent/Max.
- `A'` là tập hành động dự kiến của đối thủ/Min.
- `Result(s, a, a')` là trạng thái tiếp theo sau khi các hành động được thực hiện.

### 12.4. Hàm đánh giá Heuristic E(s)

Do thời gian xử lý mỗi step chỉ `100ms`, agent không thể duyệt cây Minimax đến cuối ván đấu vì ván đấu có thể kéo dài đến `500 steps`.

Vì vậy, cây tìm kiếm phải dừng ở một độ sâu `d`, sau đó trạng thái tại các nút lá được đánh giá bằng hàm heuristic `E(s)`.

Một heuristic tốt cho Bomberland nên cân nhắc:

#### 12.4.1. An toàn

Phạt nặng nếu agent nằm trong tầm nổ của bom ở các step tiếp theo, vì bom có timer đếm ngược từ `7`.

#### 12.4.2. Phá hộp/Farming

Thưởng điểm khi đặt bom ở vị trí có thể phá nhiều hộp (`Box`, ký hiệu `2`). Lý do: hộp có tổng `60%` xác suất rơi vật phẩm, gồm `30% Radius` và `30% Capacity`.

#### 12.4.3. Khoảng cách

Đánh giá khoảng cách Manhattan hoặc A* từ agent đến:

- Vật phẩm an toàn gần nhất.
- Vùng an toàn để né bom.
- Có thể mở rộng thêm đến vị trí đối thủ tùy chiến thuật.

---

## 13. Cắt tỉa Alpha-Beta

### 13.1. Lý do cần Alpha-Beta

Duyệt toàn bộ cây Minimax gây bùng nổ tổ hợp. Trong game này, mỗi agent có 6 hành động có thể thực hiện ở mỗi step. Khi xét nhiều agent và nhiều độ sâu, số nhánh tăng rất nhanh.

Alpha-Beta Pruning là kỹ thuật tối ưu cho Minimax giúp giảm số lượng nút cần đánh giá mà không làm thay đổi kết quả cuối cùng.

### 13.2. Hai giá trị α và β

Trong quá trình duyệt cây, thuật toán duy trì:

| Ký hiệu | Ý nghĩa |
|---|---|
| `α` | Giá trị tốt nhất/cao nhất mà Max có thể đảm bảo đạt được trên đường hiện tại. |
| `β` | Giá trị tốt nhất/thấp nhất mà Min có thể đảm bảo đạt được trên đường hiện tại. |

### 13.3. Điều kiện cắt tỉa

Tại nút Min:

- Nếu giá trị hiện tại `v ≤ α`, Max sẽ không chọn nhánh này vì đã có lựa chọn tốt hơn ở nơi khác.
- Nhánh có thể bị cắt bỏ.

Tại nút Max:

- Nếu giá trị hiện tại `v ≥ β`, Min sẽ không cho phép Max đạt trạng thái này.
- Nhánh có thể bị cắt bỏ.

Điều kiện cắt tỉa tổng quát:

$$
\alpha \ge \beta
$$

### 13.4. Công thức cập nhật

Tại nút Max:

$$
\alpha = \max(\alpha, v)
$$

Tại nút Min:

$$
\beta = \min(\beta, v)
$$

Cắt tỉa xảy ra khi:

$$
\alpha \ge \beta
$$

### 13.5. Áp dụng thực tế trong cuộc thi

Vì giới hạn thời gian chỉ `100ms/step`, tài liệu khuyến nghị kết hợp Alpha-Beta với:

- **Iterative Deepening**: tăng dần độ sâu tìm kiếm cho đến khi hết thời gian.
- **Move Ordering**: sắp xếp thứ tự xét hành động để tăng hiệu quả cắt tỉa.

Ví dụ move ordering:

- Nếu agent đang bị đe dọa bởi bom sắp nổ, ưu tiên xét hành động “di chuyển đến vùng an toàn” trước hành động “đặt bom”.
- Việc xét nhánh tốt trước giúp nhanh chóng tìm được α/β tốt hơn, từ đó cắt nhiều nhánh vô ích hơn.

---

# PHẦN IV. HỌC TĂNG CƯỜNG

## 14. Tổng quan Reinforcement Learning

Học tăng cường, hay **Reinforcement Learning (RL)**, là phương pháp giúp agent tự tìm chính sách hành động tối ưu thông qua quá trình tương tác trực tiếp với môi trường.

Thay vì lập trình sẵn kịch bản hành động, agent:

1. Quan sát trạng thái.
2. Chọn hành động.
3. Nhận phần thưởng.
4. Cập nhật hành vi để tối đa hóa tổng phần thưởng kỳ vọng trong tương lai.

RL phù hợp với trò chơi Bomberland vì agent phải đưa ra quyết định trong môi trường động, có đối thủ, có rủi ro và có phần thưởng dài hạn.

---

## 15. Markov Decision Process (MDP)

Bài toán RL thường được chuẩn hóa bằng khung **Markov Decision Process (MDP)**. MDP mở rộng từ Markov Process và Markov Reward Process bằng cách thêm yếu tố hành động của agent.

### 15.1. Các đại lượng cơ bản

| Ký hiệu | Tên | Ý nghĩa |
|---|---|---|
| `S` | State space | Tập hợp hữu hạn các trạng thái khả dĩ của môi trường. |
| `A` | Action space | Tập hợp hữu hạn các hành động agent có thể thực hiện. |
| `V(s)` | State Value Function | Hàm giá trị trạng thái, biểu diễn phần thưởng kỳ vọng tích lũy nếu bắt đầu từ trạng thái `s`. |
| `Q(s,a)` | State-Action Value Function | Hàm giá trị trạng thái-hành động, đo lợi ích kỳ vọng dài hạn khi thực hiện hành động `a` tại trạng thái `s`. |
| `P(s'|s,a)` | State Transition Probability | Xác suất chuyển sang trạng thái kế tiếp `s'` sau khi thực hiện hành động `a` tại `s`. |
| `R(s,a)` | Reward Function | Phần thưởng kỳ vọng khi thực hiện hành động `a` tại trạng thái `s`. |
| `G_t` | Discounted return | Tổng phần thưởng có chiết khấu từ thời điểm `t`. |
| `π(a|s)` | Policy | Chính sách xác định xác suất chọn hành động `a` tại trạng thái `s`. |

### 15.2. Reward Function

Reward function trong tài liệu được mô tả:

$$
R(s,a) = \mathbb{E}[r_t \mid s_t = s, a_t = a]
$$

Tức là phần thưởng kỳ vọng nhận được khi agent thực hiện hành động `a` tại trạng thái `s`.

### 15.3. Discounted Return

Tổng phần thưởng có chiết khấu từ thời điểm `t`:

$$
G_t = r_t + \gamma r_{t+1} + \gamma^2 r_{t+2} + \cdots
$$

Trong đó:

- `γ` là hệ số chiết khấu.
- `γ` điều chỉnh mức ưu tiên giữa lợi ích hiện tại và lợi ích tương lai.

### 15.4. Policy

Chính sách có thể là:

- **Stochastic policy**: chính sách ngẫu nhiên, ký hiệu `π(a|s)`.
- **Deterministic policy**: chính sách tất định, ký hiệu `π(s) = a`.

---

## 16. Từ Markov Process đến Model-free Evaluation

### 16.1. Markov Process (MP)

Markov Process mô tả chuỗi trạng thái chuyển đổi theo xác suất cố định.

Đặc điểm:

- Chưa có hành động.
- Chưa có phần thưởng.
- Dựa trên giả định Markov: trạng thái hiện tại chứa đủ thông tin cần thiết từ quá khứ, nên tương lai chỉ phụ thuộc vào trạng thái hiện tại thay vì toàn bộ lịch sử.

### 16.2. Markov Reward Process (MRP)

MRP bổ sung phần thưởng vào Markov Process.

Giá trị trạng thái được định nghĩa:

$$
V(s) = \mathbb{E}[G_t \mid s_t = s]
= \mathbb{E}[r_t + \gamma r_{t+1} + \gamma^2 r_{t+2} + \cdots \mid s_t = s]
$$

Nếu biết xác suất chuyển trạng thái `P(s'|s)` và phần thưởng `R(s)`, phương trình Bellman cho MRP là:

$$
V(s) = R(s) + \gamma \sum_{s' \in S} P(s'|s)V(s')
$$

Dạng ma trận:

$$
V = R + \gamma PV
$$

Suy ra:

$$
V = (I - \gamma P)^{-1}R
$$

Tuy nhiên, cách giải trực tiếp này có chi phí lớn và đòi hỏi biết trước mô hình môi trường.

### 16.3. Markov Decision Process (MDP)

MDP mở rộng MRP bằng cách thêm hành động của agent.

Nếu biết trước:

- `R(s,a)`
- `P(s'|s,a)`

thì agent có thể tìm chính sách tốt bằng cách chọn hành động làm cực đại giá trị kỳ vọng trong phương trình Bellman tối ưu.

Với hàm giá trị hành động `Q(s,a)`, nguyên tắc ra quyết định rất trực tiếp:

```text
Tại trạng thái s, chọn hành động a sao cho Q(s,a) lớn nhất.
```

### 16.4. Vì sao cần model-free?

Trong Bomberman/Bomberland, ta thường không biết chính xác:

- Hàm chuyển trạng thái `P`.
- Hàm phần thưởng toàn bộ `R`.

Vì vậy cần dùng **model-free policy evaluation**, tức học giá trị từ dữ liệu tương tác thay vì từ mô hình chuyển trạng thái có sẵn.

### 16.5. Monte Carlo (MC)

Monte Carlo ước lượng `V(s)` hoặc `Q(s,a)` bằng trung bình phần thưởng thu được sau nhiều episode hoàn chỉnh.

Ưu điểm:

- Không cần biết `P(s'|s,a)`.
- Học trực tiếp từ dữ liệu trải nghiệm.

Nhược điểm:

- Phải chờ episode kết thúc mới cập nhật.
- Cập nhật chậm nếu ván chơi dài.

### 16.6. Temporal Difference (TD)

Temporal Difference cập nhật ngay sau từng bước bằng cách kết hợp:

- Phần thưởng quan sát được.
- Ước lượng hiện tại của trạng thái kế tiếp.

Đặc điểm:

- Dùng bootstrapping.
- Có phương sai thấp hơn MC.
- Phù hợp với tiến trình dài.
- Có thể tạo bias do dựa trên ước lượng chưa hoàn hảo.

### 16.7. So sánh tổng quát

| Phương pháp | Cần biết mô hình môi trường? | Cập nhật khi nào? | Ghi chú |
|---|---|---|---|
| Dynamic Programming | Có | Theo mô hình đã biết | Cần biết transition model. |
| Monte Carlo | Không | Sau episode hoàn chỉnh | Học từ trải nghiệm, nhưng chậm. |
| Temporal Difference | Không | Sau từng bước | Kết hợp ưu điểm của MC và DP. |

---

# PHẦN V. DEEP Q-LEARNING / DQN

## 17. Deep Q-Learning

### 17.1. Nguồn gốc Q-Learning

Q-Learning được Christopher Watkins nghiên cứu và phát triển vào những năm 1980. Bản chất là học hàm giá trị hành động tối ưu để chỉ ra mức độ “tốt” của một quyết định trong một hoàn cảnh cụ thể.

### 17.2. Công thức cập nhật Q-Learning

Phương trình Bellman dạng cập nhật gia tăng:

$$
Q(s,a) \leftarrow Q(s,a) + \alpha \left[r + \gamma \max_{a'}Q(s',a') - Q(s,a)\right]
$$

Trong đó:

| Ký hiệu | Ý nghĩa |
|---|---|
| `r` | Phần thưởng tức thời nhận được từ môi trường. |
| `s'` | Trạng thái kế tiếp. |
| `α` | Learning rate, thuộc `(0,1]`. |
| `γ` | Discount factor, thuộc `[0,1]`. |
| `r + γ max Q(s',a')` | TD target. |
| `r + γ max Q(s',a') - Q(s,a)` | TD error. |

### 17.3. Điều kiện hội tụ trong tabular setting

Trong không gian bảng rời rạc, mỗi cặp `(s,a)` là một ô nhớ độc lập. Q-Learning được chứng minh hội tụ về `Q*(s,a)` nếu thỏa hai điều kiện nền tảng.

#### 17.3.1. GLIE

GLIE là viết tắt của **Greedy in the Limit of Infinite Exploration**.

Điều kiện này yêu cầu:

- Tất cả cặp trạng thái-hành động được ghé thăm vô hạn lần.

$$
\lim_{i \to \infty} N_i(s,a) \to \infty
$$

- Chính sách hành vi tiệm cận về chính sách tham lam hoàn toàn.

$$
\lim_{i \to \infty} \pi(a|s) \to \arg\max_a Q(s,a)
$$

Một cách thực tế để đạt GLIE là dùng `ε-greedy` và giảm dần `ε` theo thời gian, ví dụ:

$$
\epsilon_i = \frac{1}{i}
$$

#### 17.3.2. Điều kiện Robbins-Monro cho learning rate

Learning rate `α_t` cần thỏa:

$$
\sum_{t=1}^{\infty} \alpha_t = \infty
\quad \text{và} \quad
\sum_{t=1}^{\infty} \alpha_t^2 < \infty
$$

Một ví dụ đáp ứng điều kiện này:

$$
\alpha_t = \frac{1}{T}
$$

### 17.4. Vì sao chuyển sang Deep DQN?

Tabular Q-Learning không khả thi với môi trường lớn như Bomberman/Atari vì không gian trạng thái quá lớn. Bảng Q sẽ phình to và không thể lưu trữ/huấn luyện hiệu quả.

Giải pháp là dùng mạng nơ-ron xấp xỉ hàm giá trị:

$$
Q(s,a;\theta)
$$

Trong đó `θ` là tham số/trọng số mạng nơ-ron.

---

## 18. Deadly Triad trong Deep Q-Learning

Khi đưa mạng nơ-ron vào Q-Learning, quá trình học có thể mất ổn định và phân kỳ do **Deadly Triad**.

Deadly Triad gồm 3 yếu tố:

| Yếu tố | Giải thích |
|---|---|
| Function Approximation | Dùng mô hình tham số như mạng nơ-ron thay cho bảng Q rời rạc. |
| Bootstrapping | Cập nhật ước lượng hiện tại dựa trên ước lượng khác của trạng thái kế tiếp. |
| Off-policy learning | Huấn luyện chính sách mục tiêu tối ưu trong khi agent đang hành động theo chính sách khám phá khác. |

---

## 19. Hai cơ chế ổn định trong DQN

### 19.1. Experience Replay

Trong game, dữ liệu liên tiếp thường tương quan mạnh vì các frame/trạng thái kế tiếp giống nhau. Điều này vi phạm giả định dữ liệu độc lập và cùng phân phối (`i.i.d`).

DQN xử lý bằng cách:

1. Lưu các transition `(s, a, r, s')` vào Replay Buffer `D`.
2. Khi cập nhật mạng, lấy ngẫu nhiên một minibatch từ buffer.
3. Việc lấy mẫu ngẫu nhiên phá vỡ tương quan tuần tự.

### 19.2. Fixed Q-Targets / Target Network

Nếu chỉ dùng một mạng nơ-ron, TD target thay đổi liên tục sau mỗi bước cập nhật, làm quá trình học bất ổn.

DQN dùng thêm một mạng mục tiêu:

- Mạng chính có tham số `θ`.
- Mạng mục tiêu có tham số `θ^-`.
- `θ^-` được giữ cố định trong một khoảng thời gian.
- Sau mỗi chu kỳ `C`, sao chép tham số:

$$
\theta^- \leftarrow \theta
$$

Nhược điểm: cần nhiều bộ nhớ hơn vì phải lưu hai mạng.

### 19.3. Double DQN

Double DQN giải quyết xu hướng **overestimation bias** của Q-Learning.

Ý tưởng:

- Dùng mạng chính `θ` để chọn hành động tốt nhất ở trạng thái kế tiếp.
- Dùng mạng mục tiêu `θ^-` để lượng hóa giá trị của hành động đó.

---

## 20. Thuật toán DQN chi tiết

### 20.1. Các bước chính

1. Khởi tạo Q-network chính với tham số ngẫu nhiên `θ`.
2. Tạo target network với tham số `θ^- ← θ`.
3. Tạo replay buffer `D`.
4. Với mỗi episode:
   - Nhận trạng thái ban đầu `s`.
   - Lặp đến terminal:
     1. Chọn hành động bằng `ε-greedy`.
     2. Thực thi hành động trong môi trường.
     3. Nhận reward `r` và trạng thái kế tiếp `s'`.
     4. Lưu `(s, a, r, s')` vào replay buffer.
     5. Lấy minibatch ngẫu nhiên từ replay buffer.
     6. Tính target `y_i`.
     7. Cập nhật mạng chính bằng gradient descent.
     8. Gán `s ← s'`.
   - Định kỳ đồng bộ target network.

### 20.2. Chính sách ε-greedy

$$
a =
\begin{cases}
\arg\max_{a'} Q(s,a';\theta), & \text{với xác suất } 1-\epsilon \\
\text{hành động ngẫu nhiên}, & \text{với xác suất } \epsilon
\end{cases}
$$

Ý nghĩa:

- `1 - ε`: khai thác tri thức đã học.
- `ε`: khám phá hành động mới.

### 20.3. Target huấn luyện

$$
y_i =
\begin{cases}
r_i, & \text{nếu } s'_i \text{ là terminal} \\
r_i + \gamma \max_{a'} Q(s'_i, a'; \theta^-), & \text{nếu } s'_i \text{ chưa terminal}
\end{cases}
$$

### 20.4. Hàm mất mát

$$
Loss = \frac{1}{|B|}\sum_{i \in B}[y_i - Q(s_i,a_i;\theta)]^2
$$

Trong đó `B` là minibatch.

### 20.5. Mã giả DQN trong tài liệu

```python
Initialize Q-network theta and target network theta_minus
Initialize replay buffer D = []

for each episode:
    s = initial_state()

    while not terminal(s):
        if random() < epsilon:
            a = random_action()
        else:
            a = argmax_a Q(s, a; theta)

        r, s_prime = environment.step(a)
        D.append((s, a, r, s_prime))

        if len(D) > batch_size:
            batch = sample_minibatch(D, batch_size)
            loss = 0

            for (s_i, a_i, r_i, s_prime_i) in batch:
                if terminal(s_prime_i):
                    target = r_i
                else:
                    # Use target network theta_minus for stable target
                    target = r_i + gamma * max_a Q(s_prime_i, a; theta_minus)

                loss += (target - Q(s_i, a_i; theta)) ** 2

            Update theta using gradient descent on loss

        s = s_prime

    if episode % update_interval == 0:
        theta_minus = theta
```

---

## 21. Thiết kế trạng thái và phần thưởng cho Bomberman

### 21.1. Biểu diễn trạng thái

Trong Bomberman, trạng thái `s` có thể được cấu hình theo hai hướng:

1. **Mảng/ma trận pixel thô** trích xuất từ màn hình hoặc bản đồ.
2. **Vector đặc trưng thủ công**, gồm:
   - Tọa độ agent.
   - Vị trí bom.
   - Khoảng cách đến đối thủ.
   - Khoảng cách đến vật phẩm.
   - Các ô nguy hiểm/an toàn.

### 21.2. Ví dụ reward trong tài liệu

Tài liệu đưa ví dụ hệ thống reward:

| Sự kiện | Reward ví dụ |
|---|---:|
| Giành chiến thắng | `+10` |
| Agent bị tử trận | `-10` |
| Sống sót qua mỗi bước | `+1` |
| Ăn được vật phẩm | `+5` |

### 21.3. Đánh giá tổng quan DQN

Ưu điểm:

- Có khả năng tự khai phá cấu trúc không gian phức tạp từ dữ liệu thô.
- Giảm nhu cầu thiết kế đặc trưng thủ công.

Nhược điểm:

- Rất tốn dữ liệu huấn luyện.
- Tốc độ tối ưu chậm.
- Nhạy cảm với siêu tham số.
- Dễ bất ổn nếu learning rate, kiến trúc mạng, replay buffer không phù hợp.

### 21.4. Reward Hacking

Reward hacking là hiện tượng agent tìm ra “kẽ hở” trong hàm thưởng để tối đa hóa điểm số nhưng không thực sự chơi đúng ý đồ thiết kế.

Ví dụ trong Bomberman:

- Nếu agent bị phạt nặng khi chết (`-10`) nhưng được thưởng sống sót mỗi bước (`+1`), agent có thể học cách đứng yên ở góc an toàn đến hết giờ.
- Hành vi này giúp agent tránh chết và tích lũy điểm sống sót, nhưng từ chối chơi chủ động, không đặt bom, không phá hộp, không tấn công.

Do đó, thiết kế reward cần cân bằng giữa sống sót, tấn công, phá hộp, ăn vật phẩm và chiến thắng.

---

# PHẦN VI. POLICY GRADIENT VÀ PPO

## 22. Policy Gradient Methods

### 22.1. Hạn chế của DQN

DQN mạnh với không gian trạng thái lớn nhưng có hai hạn chế lớn trong một số môi trường.

#### 22.1.1. Không gian hành động liên tục

DQN cần tính:

$$
\max_a Q(s,a)
$$

Nếu tập hành động liên tục/vô hạn, việc tối ưu này rất khó hoặc bất khả thi.

Ví dụ:

- Điều khiển góc quay vô lăng của xe tự hành.
- Điều khiển lực đẩy liên tục của robot.

#### 22.1.2. Chính sách tối ưu cần ngẫu nhiên

Trong trò chơi đối kháng có thông tin bất toàn hoặc có tính triệt tiêu chiến thuật, chính sách tất định dễ bị đối thủ bắt bài.

Ví dụ kiểu oẳn tù tì: một chính sách tất định sẽ bị khai thác. Chính sách tối ưu cần là phân phối xác suất ngẫu nhiên cân bằng.

DQN dùng `argmax`, nên không cung cấp chính sách ngẫu nhiên tối ưu một cách ổn định.

### 22.2. Triết lý của Policy Gradient

Policy Gradient không học gián tiếp qua `Q(s,a)` rồi suy ra hành động. Thay vào đó, nó trực tiếp mô hình hóa chính sách:

$$
\pi(a|s;\theta)
$$

Trong đó:

- `θ` là tham số mạng nơ-ron.
- `π(a|s;θ)` là xác suất sinh hành động `a` tại trạng thái `s`.

Điều kiện: chính sách cần khả vi theo `θ`, và gradient `∇_θπ(a|s;θ)` tồn tại, hữu hạn.

### 22.3. Mục tiêu tối ưu

Mục tiêu là tìm `θ` để tối đa hóa hiệu năng kỳ vọng:

$$
J(\theta)
$$

Trong episodic case, có thể hiểu `J(θ)` là kỳ vọng tổng reward của toàn bộ episode do chính sách hiện tại sinh ra.

### 22.4. Định lý Policy Gradient

Gradient của hàm hiệu năng có thể viết:

$$
\nabla_\theta J(\theta) = \mathbb{E}\left[\nabla_\theta \log \pi(a|s;\theta) \cdot A(s,a)\right]
$$

Trong đó `A(s,a)` là **Advantage function**.

### 22.5. Advantage Function

Advantage đo xem hành động `a` tại trạng thái `s` tốt hơn hay tệ hơn mức kỳ vọng trung bình tại trạng thái đó:

$$
A(s,a) = Q(s,a) - V(s)
$$

Ý nghĩa:

- Nếu `A(s,a) > 0`, hành động tốt hơn trung bình, tăng xác suất chọn hành động đó trong tương lai.
- Nếu `A(s,a) < 0`, hành động tệ hơn trung bình, giảm xác suất chọn hành động đó.

### 22.6. Các mức triển khai Policy Gradient

#### 22.6.1. All-actions method

Nếu có thể xét toàn bộ không gian hành động, cập nhật chính sách bằng cách cộng đóng góp gradient của mọi hành động theo xác suất của chúng.

Ưu điểm: rõ về lý thuyết.

Nhược điểm: tốn kém khi số hành động lớn.

#### 22.6.2. REINFORCE

Lấy mẫu hành động từ chính sách hiện tại rồi cập nhật theo quỹ đạo đã quan sát.

Cập nhật trực giác:

$$
\theta \leftarrow \theta + \alpha G_t \nabla_\theta \log \pi(a_t|s_t;\theta)
$$

Ý nghĩa:

- Tăng xác suất các hành động dẫn đến return cao.
- Giảm xác suất các hành động dẫn đến return thấp.

#### 22.6.3. REINFORCE with baseline

Trừ đi một baseline, thường là `V(s_t)`, để giảm phương sai mà không làm lệch kỳ vọng gradient:

$$
\theta \leftarrow \theta + \alpha (G_t - V(s_t))\nabla_\theta \log \pi(a_t|s_t;\theta)
$$

#### 22.6.4. Actor-Critic

Actor-Critic kết hợp:

- **Actor**: học chính sách `π(a|s;θ)`.
- **Critic**: học hàm giá trị `V(s;φ)` hoặc `Q(s,a;φ)`.

Critic cung cấp tín hiệu advantage ổn định hơn cho actor. Đây là nền tảng cho các thuật toán hiện đại như PPO.

---

## 23. PPO - Proximal Policy Optimization

### 23.1. Ý tưởng chính

PPO được OpenAI giới thiệu năm 2017. Đây là một trong những thuật toán Policy Gradient phổ biến và hiệu quả vì giảm rủi ro cập nhật chính sách quá lớn.

Vấn đề của Policy Gradient truyền thống:

- Một bước cập nhật quá lớn có thể phá hủy chính sách đã học.
- Sau khi chính sách bị phá hủy, quá trình học có thể khó phục hồi.

PPO dùng cơ chế **clipping** để giới hạn mức thay đổi giữa chính sách cũ `π_old` và chính sách mới `π_θ`.

### 23.2. Clipped Surrogate Objective

Hàm mục tiêu đặc trưng của PPO:

$$
L^{CLIP}(\theta) = \mathbb{E}\left[\min\left(r_t(\theta)A_t,\ clip(r_t(\theta),1-\epsilon,1+\epsilon)A_t\right)\right]
$$

Trong đó:

$$
r_t(\theta) = \frac{\pi(a_t|s_t;\theta)}{\pi(a_t|s_t;\theta_{old})}
$$

Ý nghĩa:

- `r_t(θ)` là tỷ lệ xác suất giữa chính sách mới và chính sách cũ.
- Nếu tỷ lệ dịch chuyển quá xa khỏi khoảng an toàn `[1-ε, 1+ε]`, hàm clip giới hạn thay đổi.
- `ε` thường được đặt khoảng `0.1` hoặc `0.2`.

### 23.3. Cấu trúc Actor-Critic trong PPO

PPO khởi tạo:

- Mạng Actor: `π(a|s;θ)` để ra quyết định.
- Mạng Critic: `V(s;φ)` để đánh giá trạng thái.

### 23.4. Chu trình thuật toán PPO

#### Bước 1. Collect Rollouts

Chạy chính sách hiện tại tương tác với môi trường.

PPO thường chạy nhiều môi trường song song (`num_envs parallel environments`) để tăng hiệu năng và đa dạng dữ liệu.

Agent chọn hành động bằng cách lấy mẫu từ phân phối xác suất của `π(a|s;θ)`.

Dữ liệu thu được gồm:

```text
(s, a, r, s', π_old)
```

#### Bước 2. Compute Advantages bằng GAE

Với mỗi thời điểm `t`, advantage được ước lượng bằng **Generalized Advantage Estimation (GAE)**:

$$
\hat{A}_t = \sum_{l=0}^{\infty}(\gamma\lambda)^l \delta_{t+l}
$$

Trong đó:

$$
\delta_t = r_t + \gamma V(s_{t+1};\phi) - V(s_t;\phi)
$$

`λ ∈ [0,1]` kiểm soát trade-off giữa bias và variance.

#### Bước 3. Actor Update

Thực hiện `K` lần trên minibatch từ rollout để tối ưu policy loss:

$$
L^{PPO} = -\mathbb{E}_t\left[\min(r_t\hat{A}_t,\ clip(r_t,1-\epsilon,1+\epsilon)\hat{A}_t)\right]
$$

Sau đó cập nhật `θ` bằng gradient descent.

#### Bước 4. Critic Update

Thực hiện `K'` lần để tối ưu value loss:

$$
L^V = \mathbb{E}_t\left[(V(s_t;\phi) - (r_t + \gamma V(s_{t+1};\phi)))^2\right]
$$

Sau đó cập nhật `φ` bằng gradient descent.

### 23.5. Mã giả PPO trong tài liệu

```python
Initialize policy pi(a|s; theta) and value function V(s; phi)

for each epoch:
    # Step 1: Collect rollouts from parallel environments
    trajectories = []

    for env in parallel_environments:
        s = env.reset()

        while not terminal(s):
            # Sample action from probability distribution
            a ~ pi(a|s; theta)
            r, s_prime = env.step(a)
            trajectories.append((s, a, r, s_prime, log_prob))
            s = s_prime

    # Step 2: Estimate Advantage using GAE
    for each (s, a, r, s_prime) in trajectories:
        A = 0
        for t in trajectory_length downto 0:
            delta = r[t] + gamma * V(s[t+1]; phi) - V(s[t]; phi)
            A = delta + gamma * lambda * A
            advantage[t] = A

    # Step 3: Update Actor K times
    for k in range(K):
        for minibatch in trajectories:
            r_t = pi(a|s; theta) / pi_old(a|s)
            surrogate1 = r_t * advantage
            surrogate2 = clip(r_t, 1-eps, 1+eps) * advantage
            loss_policy = -min(surrogate1, surrogate2)
            Update theta using gradient descent on loss_policy

    # Step 4: Update Critic K_prime times
    for k_prime in range(K_prime):
        for minibatch in trajectories:
            target = r + gamma * V(s_prime; phi)
            loss_value = (V(s; phi) - target) ** 2
            Update phi using gradient descent on loss_value
```

### 23.6. Đánh giá PPO

Ưu điểm:

- Huấn luyện ổn định nhờ clipping.
- Giảm rủi ro chính sách bị phá hủy đột ngột.
- Dễ cấu hình siêu tham số.
- Tương thích tốt với cả không gian hành động rời rạc và liên tục.

Nhược điểm:

- Kém hiệu quả về mặt sử dụng mẫu so với các thuật toán off-policy như DQN.
- Vì PPO là on-policy/gần on-policy, mỗi epoch cần thu thập lượng lớn rollout mới.
- Phải lưu thông tin rollout cũ để tính advantage và cập nhật chính sách.

---

# PHẦN VII. SELF-PLAY

## 24. Self-Play

### 24.1. Nguồn gốc và ý tưởng

Self-play được dùng rộng rãi trong các trò chơi như cờ vua, AlphaGo và các trò chơi hành động.

Ý tưởng:

- Thay vì chỉ huấn luyện agent chống lại đối thủ cố định hoặc ngẫu nhiên, ta cho agent chơi với các phiên bản cải thiện của chính nó.
- Khi agent mạnh hơn, đối thủ cũng mạnh hơn.
- Quá trình này tạo áp lực cạnh tranh liên tục.

Tài liệu gọi đây là vòng lặp kiểu **evolutionary arms race**:

```text
agent v_n được huấn luyện bằng cách chơi với agent v_{n-1}
→ v_n mạnh hơn
→ v_n trở thành đối thủ cho agent v_{n+1}
```

### 24.2. Các bước Self-Play

1. Khởi tạo agent chính `π_main` với tham số ngẫu nhiên.
2. Khởi tạo pool đối thủ:

$$
\pi_{pool} = \{\pi_1, \pi_2, \ldots\}
$$

3. Với mỗi epoch:
   - Chọn ngẫu nhiên một agent từ `π_pool` làm đối thủ.
   - Đối thủ có thể là chính `π_main` hoặc phiên bản cũ.
   - Chạy một hoặc nhiều trận giữa `π_main` và đối thủ.
   - Thu thập dữ liệu `(s_i, a_i, r_i, s'_i)`.
   - Cập nhật agent chính bằng PPO hoặc DQN.
   - Định kỳ thêm phiên bản hiện tại của `π_main` vào pool.
   - Nếu pool quá lớn, có thể loại bỏ phiên bản yếu nhất hoặc giữ các phiên bản gần đây.

### 24.3. Reward ví dụ trong Self-Play

Tài liệu nêu reward có thể dùng:

| Tình huống | Reward |
|---|---:|
| Agent sống sót và đối thủ chết | `+1` |
| Agent chết | `-1` |
| Agent sống sót mỗi bước | `+0.1` |
| Agent thu thập vật phẩm | `+0.5` |

### 24.4. Mã giả Self-Play trong tài liệu

```python
Initialize pi_main with random parameters
pi_pool = [pi_main]  # Opponent pool
win_rates = {}

for epoch in range(num_epochs):
    # Select opponent
    opponent_id = random.choice(range(len(pi_pool)))
    pi_opponent = pi_pool[opponent_id]

    # Play games
    for game in range(num_games_per_epoch):
        # Randomize agent order to reduce positional bias
        if random.random() < 0.5:
            agent1, agent2 = pi_main, pi_opponent
            collect_from_main = True
        else:
            agent1, agent2 = pi_opponent, pi_main
            collect_from_main = False

        trajectories = play_game(agent1, agent2)

        # Extract main agent data
        if collect_from_main:
            main_data = trajectories[0]
        else:
            main_data = trajectories[1]

        # Reward: +1 if won, -1 if lost, +0.1 per step alive
        game_result = determine_winner(agent1, agent2)

        if collect_from_main:
            if game_result == 1:  # agent1/main won
                reward = 1.0
            else:
                reward = -1.0
        else:
            if game_result == 2:  # agent2/main won
                reward = 1.0
            else:
                reward = -1.0

        # Accumulate training data
        training_data.extend(main_data)

    # Update pi_main using collected data
    train_agent(pi_main, training_data)

    # Periodically add current policy to opponent pool
    if epoch % update_pool_interval == 0:
        pi_pool.append(copy(pi_main))
        if len(pi_pool) > max_pool_size:
            # Remove weakest from pool, optional
            pi_pool = pi_pool[-max_pool_size:]

    # Periodically test against fixed opponents
    if epoch % eval_interval == 0:
        for test_opponent in pi_pool:
            win_rate = evaluate(pi_main, test_opponent, num_eval_games)
            print(f"Win rate vs opponent: {win_rate}")
```

### 24.5. Mở rộng Self-Play cho Bomberman 4 agent

Self-play cơ bản thường xét 2 agent. Trong Bomberman có thể có 4 agent cùng lúc, nên cần mở rộng.

Hai hướng trong tài liệu:

1. Thêm hai agent fixed, chẳng hạn random hoặc rule-based, làm “environment obstacles”.
2. Huấn luyện bốn agent song song, mỗi agent học cách chơi chống lại ba đối thủ thích nghi.

### 24.6. Ưu điểm và thách thức của Self-Play

Ưu điểm:

- Giúp agent phát triển chiến lược tinh vi để đối phó với đối thủ thích nghi.
- Tự động tạo dữ liệu huấn luyện liên quan.
- Đối thủ ngày càng mạnh, tránh việc agent chỉ học cách đánh bại random agent.

Thách thức:

- Vòng lặp có thể không ổn định.
- Agent có thể rơi vào local optima.
- Ví dụ: agent chỉ học một chiến lược lạ nhưng hiệu quả với một đối thủ cụ thể.
- Một phiên bản yếu trong pool có thể vô tình được chọn quá thường xuyên, làm giảm áp lực huấn luyện.

---

# PHẦN VIII. BEHAVIOR CLONING

## 25. Behaviour/Behavior Cloning

Tài liệu dùng tiêu đề **Behaviour Cloning** nhưng trong nội dung cũng viết **Behavior Cloning**. Đây là một hướng học từ demo dựa trên học có giám sát.

### 25.1. Ý tưởng cơ bản

Behavior Cloning lấy một tập demo từ chuyên gia, có thể là:

- Người chơi giỏi.
- Agent tốt có sẵn.

Sau đó huấn luyện mô hình dự đoán hành động chuyên gia chọn tại mỗi trạng thái.

Về bản chất, đây là bài toán supervised learning:

```text
Input: trạng thái s
Output: hành động a của chuyên gia
```

### 25.2. Vì sao Behavior Cloning hữu ích?

Behavior Cloning là cách nhanh nhất để tạo agent tương đối hợp lý vì:

- Không cần định nghĩa hàm thưởng phức tạp.
- Không cần chờ RL hội tụ lâu.
- Có thể tận dụng dữ liệu người chơi hoặc agent tốt.

Nó thường được dùng trong:

- Robotics.
- Driving simulators.
- Learning from demonstrations.

### 25.3. Vấn đề cố hữu

Nếu agent hành động khác chuyên gia ở một thời điểm nào đó, nó có thể rơi vào trạng thái chuyên gia chưa từng gặp trong dữ liệu demo.

Khi đó agent phải dự đoán hành động trong trạng thái **out-of-distribution**, dẫn đến lỗi tích lũy theo thời gian.

---

## 26. Các bước Behavior Cloning

### 26.1. Bước 1 - Thu thập demo

Ghi lại các trận đấu từ người chơi Bomberman khéo léo.

Với mỗi frame, lưu:

| Thành phần | Ý nghĩa |
|---|---|
| `s` | Trạng thái, có thể biểu diễn bằng pixel hoặc feature vector. |
| `a` | Hành động, là số nguyên từ `0` đến `5`. |

Hành động tương ứng:

```text
0 = STOP
1 = LEFT
2 = RIGHT
3 = UP
4 = DOWN
5 = PLACE_BOMB
```

Số lượng frame tốt theo tài liệu: ít nhất vài chục nghìn frame, tương đương hàng trăm trò chơi.

### 26.2. Bước 2 - Xây dựng dataset

Tổ chức dữ liệu thành cặp:

$$
(s_i, a_i)
$$

Chia dữ liệu thành:

- Training set: ví dụ `80%`.
- Validation set: ví dụ `20%`.

### 26.3. Bước 3 - Xây dựng mô hình

Tạo mạng nơ-ron:

$$
\pi_\theta(a|s)
$$

Mạng nhận trạng thái làm đầu vào và xuất phân bố xác suất trên các hành động.

Kiến trúc thường dùng:

| Dạng trạng thái | Mô hình phù hợp |
|---|---|
| Ảnh/pixel | CNN - Convolutional Neural Network |
| Feature vector | MLP - Fully connected layers |

### 26.4. Bước 4 - Huấn luyện

Với mỗi batch:

1. Dự đoán hành động:

$$
\hat{a}_i = \pi_\theta(s_i)
$$

2. Tính cross-entropy loss:

$$
L = -\sum_i \log \pi_\theta(a_i|s_i)
$$

3. Cập nhật `θ` bằng gradient descent, ví dụ Adam optimizer.

Huấn luyện đến khi accuracy/loss trên validation set không cải thiện, tức dùng early stopping.

### 26.5. Bước 5 - Đánh giá

Đánh giá theo hai cách:

1. Kiểm tra độ chính xác trên test set.
2. Cho agent chơi vài trận để xem hành vi có hợp lý hay không.

---

## 27. Mã giả Behavior Cloning trong tài liệu

```python
# Data collection phase
demonstrations = []

for each human_game in recorded_games:
    for each frame in human_game:
        state = extract_state(frame)
        action = extract_action(frame)  # What human did
        demonstrations.append((state, action))

# Split data
train_data, val_data = split(demonstrations, test_size=0.2)

# Build model
model = NeuralNetwork(input_dim=state_dim, output_dim=num_actions)
optimizer = Adam(learning_rate=0.001)

# Training
best_val_loss = infinity
patience_counter = 0
max_patience = 10

for epoch in range(max_epochs):
    total_train_loss = 0

    for batch in train_data:
        states, actions = batch

        # Forward pass
        logits = model.forward(states)  # Shape: [batch_size, num_actions]

        # Cross-entropy loss
        loss = cross_entropy_loss(logits, actions)

        # Backward pass
        grads = compute_gradients(loss)

        # Update
        model.update(grads, optimizer)

        total_train_loss += loss

    avg_train_loss = total_train_loss / len(train_data)

    # Validation
    val_loss = 0
    val_correct = 0

    for batch in val_data:
        states, actions = batch
        logits = model.forward(states)
        loss = cross_entropy_loss(logits, actions)
        val_loss += loss

        predicted_actions = argmax(logits, axis=1)
        val_correct += sum(predicted_actions == actions)

    avg_val_loss = val_loss / len(val_data)
    val_accuracy = val_correct / total_val_samples

    print(f"Epoch {epoch}: train_loss={avg_train_loss:.4f}, "
          f"val_loss={avg_val_loss:.4f}, val_acc={val_accuracy:.4f}")

    # Early stopping
    if avg_val_loss < best_val_loss:
        best_val_loss = avg_val_loss
        patience_counter = 0
        save_model(model)  # Save best model
    else:
        patience_counter += 1

        if patience_counter >= max_patience:
            print("Early stopping")
            break

# Load best model
model = load_best_model()

# Deployment: agent plays games
for game in range(num_test_games):
    s = game.reset()

    while not terminal(s):
        logits = model.forward(s)
        a = argmax(logits)  # Greedy action selection
        s = game.step(a)
```

---

## 28. Ưu điểm, nhược điểm và DAgger

### 28.1. Ưu điểm của Behavior Cloning

- Nhanh chóng.
- Dễ triển khai.
- Không cần định nghĩa hàm phần thưởng.
- Có thể tận dụng dữ liệu demo có sẵn.

### 28.2. Nhược điểm của Behavior Cloning

- Phụ thuộc mạnh vào chất lượng demo.
- Agent không thể vượt quá kỹ năng chuyên gia nếu chỉ bắt chước.
- Dễ gặp distribution shift.
- Lỗi có thể tích lũy theo thời gian.

### 28.3. Distribution Shift và Error Compounding

Nếu agent đưa ra quyết định khác chuyên gia tại bước `t`, nó rơi vào trạng thái `s'_t` mà chuyên gia chưa từng gặp trong dữ liệu demo.

Khi agent dự đoán hành động ở `s'_t`, nó dựa vào trạng thái ngoài phân phối huấn luyện. Lỗi có thể tiếp tục tích lũy ở các bước sau.

### 28.4. DAgger - Dataset Aggregation

DAgger là cải tiến giúp giảm vấn đề distribution shift.

Quy trình:

1. Huấn luyện Behavior Cloning trên dữ liệu demo ban đầu.
2. Chạy agent và ghi lại các trạng thái agent gặp phải.
3. Yêu cầu chuyên gia gán hành động đúng tại các trạng thái mới này.
4. Thêm dữ liệu mới vào dataset.
5. Huấn luyện lại.
6. Lặp lại nhiều lần.

---

# PHẦN IX. MONTE CARLO TREE SEARCH / MCTS

## 29. Monte Carlo Tree Search

### 29.1. Vai trò của MCTS

MCTS thuộc nhóm phương pháp hoạch định trực tuyến (**online planning**) trong nhánh học tăng cường dựa trên mô hình (**model-based RL**).

MCTS là thuật toán xấp xỉ đồ thị quyết định mạnh, phù hợp khi:

- Không gian trạng thái quá lớn.
- Không thể duyệt cạn toàn bộ cây.
- Có thể mô phỏng tương lai bằng forward model/game engine.

MCTS kết hợp:

- Cây quyết định.
- Mô phỏng ngẫu nhiên Monte Carlo.
- Cập nhật thống kê qua nhiều lượt mô phỏng.

### 29.2. Bốn bước cốt lõi của MCTS

MCTS lặp lại 4 bước:

```text
Selection → Expansion → Simulation/Playout → Backpropagation
```

---

## 30. Bước 1 - Selection

Selection bắt đầu từ nút gốc `v_0`, đại diện cho trạng thái hiện tại của môi trường.

Thuật toán đi xuống các nút con bằng tree policy. Mục tiêu là cân bằng:

- **Exploitation**: khai thác nhánh đã cho kết quả tốt.
- **Exploration**: khám phá nhánh chưa được thử đủ.

### 30.1. Công thức UCT

UCT là viết tắt của **Upper Confidence Bounds for Trees**. Công thức:

$$
UCT(v) = \frac{Q(v)}{N(v)} + C\sqrt{\frac{\ln N(parent)}{N(v)}}
$$

Trong đó:

| Ký hiệu | Ý nghĩa |
|---|---|
| `Q(v)` | Tổng phần thưởng tích lũy tại nút `v` qua các mô phỏng trước. |
| `N(v)` | Số lần nút `v` được ghé thăm. |
| `N(parent)` | Số lần nút cha của `v` được duyệt qua. |
| `C` | Hằng số điều hòa khám phá. Theo lý thuyết thường dùng `√2` khi reward chuẩn hóa về `[0,1]`. |

### 30.2. Ý nghĩa hai thành phần UCT

Công thức UCT gồm hai phần:

1. `Q(v)/N(v)`: giá trị kỳ vọng trung bình, ưu tiên nhánh có hiệu suất cao.
2. `C sqrt(ln N(parent)/N(v))`: độ bất định/khám phá, ưu tiên nhánh ít được thăm.

Thuật toán liên tục chọn nút con có UCT lớn nhất cho đến khi chạm nút lá `v_l`, tức nút chưa mở rộng hoàn toàn hoặc còn hành động chưa khám phá.

---

## 31. Bước 2 - Expansion

Khi Selection dừng tại nút lá `v_l`:

- Nếu trạng thái chưa terminal, thuật toán mở rộng cây.
- Một hoặc nhiều nút con mới `v_c` được tạo.
- Các nút con tương ứng với hành động hợp lệ từ trạng thái `v_l`.

Trong môi trường có branching factor lớn, thường chỉ thêm một nút con cho mỗi chu kỳ để tiết kiệm tài nguyên.

---

## 32. Bước 3 - Simulation / Playout

Từ nút con mới `v_c`, thuật toán chạy một phiên mô phỏng giả lập đến khi:

- Trò chơi kết thúc.
- Hoặc đạt độ sâu giới hạn.

Giai đoạn này dùng **default policy**, có thể là:

- Chọn hành động ngẫu nhiên đều.
- Bán ngẫu nhiên kết hợp heuristic đơn giản.

Mục tiêu là thu được ước lượng nhanh về giá trị lâu dài của nhánh vừa chọn mà không cần thiết kế hàm đánh giá trạng thái phức tạp.

---

## 33. Bước 4 - Backpropagation

Khi mô phỏng kết thúc và trả về reward, kết quả được truyền ngược từ nút mô phỏng `v_c` lên nút gốc `v_0`.

Với mỗi nút `v` trên đường truyền ngược, cập nhật:

$$
N(v) \leftarrow N(v) + 1
$$

$$
Q(v) \leftarrow Q(v) + reward
$$

Tùy môi trường, reward có thể cấu hình khác nhau:

- Đơn tác nhân.
- Đa tác nhân hợp tác.
- Đối kháng.

Trong zero-sum hai người chơi, giá trị cập nhật có thể đảo dấu theo tầng để phản ánh tư duy Minimax.

---

## 34. Ra quyết định cuối cùng trong MCTS

MCTS là **anytime algorithm**, tức có thể dừng bất kỳ lúc nào theo giới hạn tài nguyên.

Khi dừng, agent chọn hành động thực tế bằng một trong hai tiêu chí:

| Tiêu chí | Cách chọn |
|---|---|
| Robust Child | Chọn nút con trực tiếp của gốc có số lần ghé thăm cao nhất `max N(v)`. |
| Max Child | Chọn nút con có giá trị trung bình cao nhất `max Q(v)/N(v)`. |

---

## 35. Tính hội tụ của MCTS

Một bảo chứng quan trọng của MCTS/UCT là hội tụ tiệm cận.

Khi số lượt mô phỏng tiến tới vô hạn:

$$
N \to \infty
$$

xác suất chọn nhánh suboptimal sẽ hội tụ về `0`, nhờ thành phần exploration của UCT.

Cây tìm kiếm tăng trưởng bất đối xứng, tập trung sâu vào vùng chiến lược tốt. Giá trị ước lượng:

$$
\frac{Q(v)}{N(v)}
$$

sẽ hội tụ về:

- Giá trị trò chơi lý thuyết Minimax trong game đối kháng.
- Hoặc nghiệm phương trình tối ưu Bellman.

---

## 36. Ứng dụng MCTS trong Bomberman

Khi triển khai MCTS cho Bomberman, cây tìm kiếm mô phỏng các chuỗi hành động tương lai:

- Di chuyển lên.
- Di chuyển xuống.
- Di chuyển trái.
- Di chuyển phải.
- Đứng yên/chờ đợi.
- Đặt bom.

Ưu điểm trong ngữ cảnh Bomberman:

- Không cần dữ liệu huấn luyện.
- Thích ứng linh hoạt với thay đổi động của bản đồ.
- Không cần mô hình deep learning đã huấn luyện trước.
- Chỉ cần forward model/game engine để tính trạng thái kế tiếp nhanh.
- Mỗi bước đi có thể xây lại cây từ trạng thái hiện tại, giúp phản ứng trước dịch chuyển bất ngờ của đối thủ hoặc chain reaction của bom.

### 36.1. Rào cản kỹ thuật

#### 36.1.1. Simulation Bottleneck

Bomberman có hệ số rẽ nhánh lớn và bom có độ trễ nổ nhiều step. Để quyết định tốt, MCTS cần rất nhiều mô phỏng sâu.

Điều này tạo áp lực lớn lên CPU và khó đáp ứng thời gian real-time, thường dưới `100ms` mỗi step/frame.

#### 36.1.2. Tactical Blindness

Nếu playout dùng chính sách ngẫu nhiên, agent mô phỏng thường di chuyển không mục đích.

Hệ quả:

- Vị trí đặt bom tốt có thể bị đánh giá thấp vì playout ngẫu nhiên khiến agent tự sát.
- Nhánh nguy hiểm có thể bị đánh giá cao do may mắn trong mô phỏng không kích hoạt bẫy.

---

## 37. PUCT và kết hợp mạng nơ-ron

Các hệ thống AI hiện đại lấy cảm hứng từ AlphaGo/AlphaZero thường thay thế playout ngẫu nhiên bằng mạng nơ-ron.

### 37.1. Công thức PUCT

$$
PUCT(v) = \frac{Q(v)}{N(v)} + C \cdot P(s,a) \cdot \frac{\sqrt{N(parent)}}{1 + N(v)}
$$

Trong đó:

- `P(s,a)` là prior probability do Policy Network cung cấp.
- Policy Network giúp định hướng tìm kiếm vào hành động triển vọng.
- Value Network `V(s)` dự đoán giá trị nút lá, thay cho playout ngẫu nhiên kéo dài.

### 37.2. Ý nghĩa của PUCT

PUCT biến MCTS từ tìm kiếm mù quáng thành hoạch định có định hướng:

- Giảm số nhánh cần thử.
- Giảm chi phí tính toán.
- Tập trung vào hành động có khả năng tốt.
- Nâng cao tư duy chiến thuật của agent.

---

# PHẦN X. NGUỒN THAM KHẢO TRONG TÀI LIỆU

Tài liệu liệt kê 6 nguồn tham khảo:

1. Khóa **CS234 của Stanford** về Reinforcement Learning.
2. **RL Book, Sutton Barto**.
3. **RL Course Toronto University**.
4. **Neuriton**.
5. **RL Exercises, AI VIETNAM**.
6. **Single-File RL Algorithms Code**.

---

# PHẦN XI. CHECKLIST NỘI DUNG QUAN TRỌNG KHÔNG NÊN BỎ SÓT

## 38. Checklist cơ chế game

- [x] Step order của engine.
- [x] 6 hành động của agent.
- [x] Quy tắc không đi vào tường/hộp/bom cũ.
- [x] Ngoại lệ rời khỏi ô vừa đặt bom.
- [x] Nhiều agent có thể đứng cùng ô.
- [x] Vật phẩm bị hủy nếu nhiều agent cùng nhặt.
- [x] Bom timer 7 steps.
- [x] Radius và capacity bắt đầu từ 1, tối đa 5.
- [x] Quy tắc ưu tiên khi nhiều agent đặt bom cùng ô.
- [x] Vụ nổ hình thập tự.
- [x] Tường chặn nổ, hộp chặn nổ và bị phá, agent không chặn nổ.
- [x] Chain reaction.
- [x] Item Radius/Capacity.
- [x] Xác suất rơi vật phẩm khi phá hộp: 30/30/40.
- [x] Xác suất auto-spawn item.
- [x] Agent bị loại nếu đứng trong vùng nổ.
- [x] Bom cũ của agent bị loại vẫn tồn tại.
- [x] Kết thúc khi còn ≤ 1 agent sống hoặc đạt 500 steps.

## 39. Checklist thuật toán

- [x] Rule-based: cơ chế, ưu điểm, nhược điểm.
- [x] Minimax: ý tưởng, 1-vs-All, công thức, heuristic.
- [x] Alpha-Beta: α, β, điều kiện cắt tỉa, iterative deepening, move ordering.
- [x] RL/MDP: S, A, V, Q, P, R, G, policy.
- [x] MP, MRP, MDP, Bellman equation, dạng ma trận.
- [x] Model-free evaluation: MC và TD.
- [x] Q-Learning: update rule, TD error, GLIE, Robbins-Monro.
- [x] DQN: Deadly Triad, replay buffer, target network, Double DQN.
- [x] DQN pseudocode.
- [x] Reward hacking.
- [x] Policy Gradient: hạn chế DQN, gradient theorem, advantage.
- [x] REINFORCE, baseline, Actor-Critic.
- [x] PPO: clipping, ratio, GAE, actor update, critic update.
- [x] PPO pseudocode.
- [x] Self-play: pool đối thủ, reward, mã giả, mở rộng cho 4 agent.
- [x] Behavior Cloning: demo, dataset, model, loss, mã giả, DAgger.
- [x] MCTS: UCT, selection, expansion, simulation, backpropagation, robust/max child.
- [x] MCTS trong Bomberman: ưu điểm, bottleneck, tactical blindness.
- [x] PUCT và kết hợp policy/value network.

---

# PHỤ LỤC A. BẢN TRÍCH XUẤT ĐẦY ĐỦ THEO TRANG TỪ PDF

Phụ lục này giữ lại nội dung trích xuất theo từng trang từ file PDF gốc để đối chiếu. Một số khoảng trắng/ký hiệu có thể chưa đẹp do đặc thù trích xuất văn bản từ PDF, nhưng phần này giúp kiểm tra lại rằng file Markdown đã bao phủ toàn bộ nội dung tài liệu.

## Trang 1

```text
Google Developer Group on Campus
University of Science – VNUHCM
Team AI&DS – Ban Development
AI Challenge - Hướng dẫn
Đạt, Tuấn
Mục lục
1
Vềcuộc thi
2
1.1
Thứtựxửlý mỗi Step
. . . . . . . . . . . . . . . . . . . . . . . . . . . .
2
1.2
Hành động của Agent . . . . . . . . . . . . . . . . . . . . . . . . . . . .
2
1.3
Cơ chếBom . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
2
1.4
Vật phẩm (Items) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
3
1.5
Điều kiện loại bỏvà Kết thúc
. . . . . . . . . . . . . . . . . . . . . . . .
3
2
Rule-based
3
2.1
Cơ chếhoạt động
. . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
4
2.2
Ưu điểm . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
4
2.3
Nhược điểm . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
4
3
Các thuật toán cơ bản
4
3.1
Đối kháng và Tìm kiếm có đối thủ(Adversarial Search) . . . . . . . . . .
4
3.1.1
Thuật toán Minimax
. . . . . . . . . . . . . . . . . . . . . . . . .
4
3.1.2
Cắt tỉa Alpha-Beta (Alpha-Beta Pruning) . . . . . . . . . . . . . .
5
4
Học tăng cường
6
4.1
TừMarkov Process đến Model-free Evaluation
. . . . . . . . . . . . . .
7
4.2
Deep Q-Learning . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
8
4.2.1
Nguồn gốc, lý thuyết nền tảng và bài toán hội tụ
. . . . . . . . .
8
4.2.2
Thuật toán chi tiết và mã giảDQN
. . . . . . . . . . . . . . . . .
9
4.3
Policy Gradient Methods . . . . . . . . . . . . . . . . . . . . . . . . . . .
12
4.3.1
Hạn chếcủa DQN và Triết lý tối ưu trực tiếp chính sách . . . . .
12
4.3.2
Thuật toán PPO (Proximal Policy Optimization) . . . . . . . . . .
13
4.3.3
Đánh giá và so sánh thực tiễn . . . . . . . . . . . . . . . . . . . .
15
4.4
Self-Play . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
15
4.4.1
Nguồn gốc và ý tưởng cơ bản . . . . . . . . . . . . . . . . . . . .
15
4.4.2
Các bước chi tiết và mã giả. . . . . . . . . . . . . . . . . . . . .
16
4.5
Behaviour Cloning . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
18
4.5.1
Nguồn gốc và ý tưởng cơ bản . . . . . . . . . . . . . . . . . . . .
18
4.5.2
Các bước chi tiết và mã giả. . . . . . . . . . . . . . . . . . . . .
18
4.5.3
Monte Carlo Tree Search (MCTS)
. . . . . . . . . . . . . . . . .
21
5
Nguồn tham khảo
24
1
```

## Trang 2

```text
Google Developer Group on Campus
University of Science – VNUHCM
Team AI&DS – Ban Development
1. Vềcuộc thi
Dưới đây là tóm tắt chi tiết vềcơ chếgame:
1.1
Thứtựxửlý mỗi Step
Mỗi bước (step) của trò chơi được engine xửlý tuần tựtheo các giai đoạn sau:
[Thu thập hành động] →[Xửlý di chuyển] →[Đặt bom] →[Giảm timer bom] →[Giải
quyết nổ] →[Loại agent] →[Spawn vật phẩm] →[Kiểm tra kết thúc]
1.2
Hành động của Agent
Tại mỗi step, mỗi Agent gửi vềmột sốnguyên tương ứng với hành động:
Giá trị
Hành động
Mô tả
0
STOP
Đứng yên tại vịtrí hiện tại
1
LEFT
Di chuyển sang trái 1 ô
2
RIGHT
Di chuyển sang phải 1 ô
3
UP
Di chuyển lên trên 1 ô
4
DOWN
Di chuyển xuống dưới 1 ô
5
PLACE_BOMB
Đặt bom tại vịtrí hiện tại
Quy tắc di chuyển:
• Không thểđi vào ô có Tường (mã 1) hoặc Hộp (mã 2).
• Không thểđi vào ô đã có Bom từcác step trước. Ngoại lệ: Nếu Agent vừa đặt
bom tại ô đó trong step hiện tại thì vẫn có thểdi chuyển ra ngoài.
• Nhiều Agent có thểđứng cùng một ô.
• Nếu ≥2 Agent cùng bước vào một ô có vật phẩm: Vật phẩm bịhủy, không Agent
nào nhận được.
1.3
Cơ chếBom
Thông sốmặc định:
• Timer: 7 steps (đếm ngược về0, nổkhi ≤0).
• Bán kính (Radius): Bắt đầu là 1, tối đa là 5.
• Sốlượng bom (Capacity): Bắt đầu là 1, tối đa là 5.
Quy tắc đặt bom:
• Điều kiện: bombs_left > 0 và ô hiện tại chưa có bom từstep trước.
• Xửlý trùng lặp (nhiều Agent đặt bom cùng 1 ô): Ưu tiên bom có bán kính lớn
hơn. Nếu bán kính bằng nhau, ưu tiên Agent có ID nhỏhơn.
2
```

## Trang 3

```text
Google Developer Group on Campus
University of Science – VNUHCM
Team AI&DS – Ban Development
• Chỉngười đặt bom cuối cùng (theo quy tắc trên) mới bịtrừbombs_left.
Cơ chếnổ:
• Vụnổlan theo 4 hướng (Thập tự).
• Vật cản: Tường chặn hoàn toàn vụnổ. Hộp chặn vụnổvà bịphá hủy. Agent
không chặn được vụnổ.
• Phản ứng dây chuyền (Chain reaction): Nếu vụnổchạm vào một quảbom
khác, quảbom đó sẽnổngay lập tức trong cùng step đó.
1.4
Vật phẩm (Items)
Vật phẩm giúp tăng sức mạnh cho Agent (Radius hoặc Capacity).
• Từviệc phá hộp:
– 30% rơi Item Radius
– 30% rơi Item Capacity
– 40% không rơi gì.
• Tựđộng xuất hiện (Auto-spawn): Tại mỗi ô cỏtrống, xác suất P xuất hiện vật
phẩm mỗi step là:
P = 0.0003 ×
step
165

Trong đó: 50% là Radius, 50% là Capacity.
1.5
Điều kiện loại bỏvà Kết thúc
• Loại Agent: Agent bịloại ngay lập tức nếu đứng trong ô bịảnh hưởng bởi vụnổ
(kểcảtựđặt bom). Agent đã bịloại vẫn đểlại các quảbom cũ trên sân.
• Kết thúc trận đấu:
1. Khi chỉcòn ≤1 Agent sống sót.
2. Khi đạt giới hạn 500 steps.
2. Rule-based
Cách tiếp cận này sẽxây dựng agent thông qua các heuristic được đặt sẵn. Thay vì học
từtrải nghiệm, agent chạy theo một tập hợp các quy tắc được lập trình sẵn đểxửlý các
tình huống khác nhau trên bản đồ.
3
```

## Trang 4

```text
Google Developer Group on Campus
University of Science – VNUHCM
Team AI&DS – Ban Development
2.1
Cơ chếhoạt động
Agent đánh giá trạng thái hiện tại (vịtrí các vật cản, bom, đối thủ, vật phẩm) và áp dụng
một chuỗi điều kiện if-else đểquyết định hành động tiếp theo. Ví dụ, nếu phía trước
có tường thì không đi, nếu gần đối thủmà có bom sẵn sàng thì đặt bom, nếu thấy vật
phẩm giữa đường thì đi lấy.
Chiến lược thường bao gồm:
• Tìm kiếm tuyến tính đểđịnh vịđối thủgần nhất, vật phẩm có giá trịcao nhất
• Ưu tiên các hành động dựa trên khoảng cách hoặc mức độnguy hiểm
• Tránh các vùng có bom hoặc tường
• Kiến thức cứng vềcách di chuyển an toàn sau khi đặt bom
2.2
Ưu điểm
Dễtriển khai nhanh chóng. Không cần dữliệu huấn luyện hay thời gian tính toán để
thiết lập mô hình. Agent có thểchạy được ngay, và hành vi của agent có thểđược giải
thích dễdàng.
2.3
Nhược điểm
Quy tắc được code cứng không thểtổng quát hóa cho các tình huống khác nhau. Agent
sẽthất bại trước những tình huống ngoài phạm vi các if-else đã viết. Agent không học
từthất bại mà chỉhành động theo một heuristic cứng nhắc.
3. Các thuật toán cơ bản
3.1
Đối kháng và Tìm kiếm có đối thủ(Adversarial Search)
Bomberland là một trò chơi chiến thuật theo lượt với sựtham gia của 4 agent trên một
bản đồlưới 13 × 13. Do sựhiện diện của các đối thủcạnh tranh trực tiếp, bài toán không
chỉdừng lại ởviệc tìm đường đi ngắn nhất mà còn là việc dựđoán và đối phó với hành
động của các agent khác. Các thuật toán tìm kiếm có đối thủnhư Minimax là lựa chọn
cốt lõi đểgiải quyết vấn đềnày.
3.1.1
Thuật toán Minimax
Minimax là một thuật toán đệquy được sửdụng đểchọn hành động tối ưu cho một
người chơi (Max) với giảđịnh rằng đối thủ(Min) cũng đang chơi tối ưu đểchống lại họ.
Mặc dù Bomberland có 4 agent (có thểyêu cầu mởrộng thành thuật toán Max-N), một
cách tiếp cận đơn giản và hiệu quảlà coi bài toán dưới dạng ”1 vs All” (Agent của ta là
Max, môi trường và 3 agent còn lại gộp chung thành Min).
Mỗi bước trong game, agent phải chọn một hành động a ∈{0, 1, 2, 3, 4, 5} tương ứng với
Đứng yên, Trái, Phải, Lên, Xuống, và Đặt bom.
4
```

## Trang 5

```text
Google Developer Group on Campus
University of Science – VNUHCM
Team AI&DS – Ban Development
Công thức tính giá trịcủa một trạng thái s trong cây Minimax cơ bản (2 người chơi):
V (s) = max
a∈A min
a′∈A′ V (Result(s, a, a′))
Trong đó:
• A là tập hành động của Agent (Max).
• A′ là tập hành động dựkiến của đối thủ(Min).
• Result(s, a, a′) là trạng thái tiếp theo sau khi các hành động được thực hiện.
Hàm đánh giá Heuristic E(s) trong Bomberland:
Do giới hạn thời gian xửlý (inference timeout) của mỗi bước chỉlà 100ms, thuật toán
không thểduyệt cây Minimax đến cuối ván đấu (tối đa 500 bước). Vì vậy, việc duyệt cây
phải dừng lại ởmột độsâu d nhất định, và trạng thái tại các nút lá được đánh giá thông
qua một hàm Heuristic E(s).
Một hàm Heuristic tốt cho Bomberland cần cân nhắc các yếu tố:
• An toàn: Phạt điểm nặng nếu agent nằm trong tầm nổcủa bom ởcác step tiếp
theo (bom có timer đếm ngược từ7).
• Phá hộp (Farming): Thưởng điểm khi đặt bom ởvịtrí có thểphá hủy nhiều hộp
(Box - ký hiệu 2), vì hộp có 60% tỷlệrơi vật phẩm (30% Radius và 30% Capacity).
• Khoảng cách: Đánh giá khoảng cách Manhattan hoặc A* từagent đến vật phẩm
an toàn gần nhất (Radius hoặc Capacity) hoặc vùng an toàn đểné bom.
3.1.2
Cắt tỉa Alpha-Beta (Alpha-Beta Pruning)
Việc duyệt toàn bộcây Minimax sẽbùng nổtổhợp, đặc biệt khi mỗi agent có tới 6 hành
động có thểthực hiện tại mỗi step. Cắt tỉa Alpha-Beta là một kỹthuật tối ưu hóa cho
Minimax giúp giảm thiểu đáng kểsốlượng nút cần đánh giá mà không làm thay đổi kết
quảcuối cùng.
Thuật toán duy trì hai giá trịtrong quá trình duyệt cây:
• α: Giá trịtốt nhất (cao nhất) mà Max có thểđảm bảo đạt được trên con đường
hiện tại.
• β: Giá trịtốt nhất (thấp nhất) mà Min có thểđảm bảo đạt được trên con đường
hiện tại.
Điều kiện cắt tỉa:
Tại bất kỳnút Min nào, nếu giá trịhiện tại v ≤α, Max sẽkhông bao giờchọn đi theo
nhánh này (vì Max đã có một lựa chọn α tốt hơn ởnơi khác). Nhánh này có thểbịcắt
bỏ(Pruning). Tương tự, tại nút Max, nếu v ≥β, Min sẽkhông bao giờcho phép Max
đạt được trạng thái này.
Công thức cập nhật:
• Tại nút Max: α = max(α, v)
5
```

## Trang 6

```text
Google Developer Group on Campus
University of Science – VNUHCM
Team AI&DS – Ban Development
• Tại nút Min: β = min(β, v)
• Cắt tỉa xảy ra khi: α ≥β
Áp dụng thực tếtrong cuộc thi:
Với thời gian giới hạn khắt khe 100ms/step, Alpha-Beta Pruning kết hợp với kỹthuật
Iterative Deepening (tăng dần độsâu tìm kiếm cho đến khi hết thời gian) là cực kỳcần
thiết. Hơn nữa, ta có thểkết hợp việc sắp xếp các hành động (Move Ordering) đểtăng
hiệu quảcắt tỉa. Ví dụ: ưu tiên xét các hành động ”Di chuyển đến vùng an toàn” trước
hành động ”Đặt bom” nếu trạng thái hiện tại đang bịđe dọa bởi bom có timer sắp về0.
Điều này giúp nhánh Alpha-Beta nhanh chóng tìm thấy các giá trịα, β tốt, từđó cắt tỉa
được nhiều nhánh vô ích hơn.
4. Học tăng cường
Trong bối cảnh phát triển các tác nhân thông minh cho trò chơi, học tăng cường (Rein-
forcement Learning - RL) nổi lên như một phương pháp tiếp cận mạnh mẽ, cho phép
agent tựtìm kiếm chính sách hành động tối ưu thông qua quá trình ”thửvà sai” (trial
and error) nhờtương tác trực tiếp với môi trường. Khác với các hướng tiếp cận truyền
thống, tác nhân RL không cần một kịch bản lập trình sẵn hay quá trình tiến hóa nhân
tạo; thay vào đó, nó tựđiều chỉnh hành vi dựa trên tín hiệu phần thưởng (reward) nhận
được sau mỗi hành động với mục tiêu tối cao là tối đa hóa tổng phần thưởng kỳvọng
trong tương lai.
Vềmặt toán học, bài toán này được chuẩn hóa thông qua khung lý thuyết Markov
Decision Process (MDP), mởrộng từchuỗi Markov và Markov Reward Process (MRP)
bằng việc tích hợp thêm yếu tốhành động chủquan của tác nhân. Mô hình MDP được
định nghĩa bởi một bộcác đại lượng cơ bản:
• S: Tập hợp hữu hạn các trạng thái khảdĩ của môi trường.
• A: Tập hợp hữu hạn các hành động mà agent có thểthực hiện.
• V (s) (State Value Function): Hàm giá trịtrạng thái, biểu diễn phần thưởng kỳvọng
tích lũy khi tác nhân bắt đầu từtrạng thái s.
• Q(s, a) (State-Action Value Function): Hàm giá trịtrạng thái - hành động, lượng
hóa lợi ích kỳvọng dài hạn nếu tác nhân thực hiện hành động a ngay tại trạng thái
s.
• P(s′|s, a) (State Transition Probability): Xác suất môi trường chuyển sang trạng
thái kếtiếp s′ sau khi agent thực hiện hành động a tại trạng thái s.
• R(s, a) (Reward Function): Phần thưởng kỳvọng nhận được khi thực hiện hành
động a tại trạng thái s, tức R(s, a) = E[rt|st = s, at = a].
• Gt: Tổng phần thưởng có chiết khấu từthời điểm t, thường viết Gt = rt + γrt+1 +
γ2rt+2 + · · · , trong đó γ điều chỉnh mức ưu tiên giữa lợi ích hiện tại và tương lai.
• π(a|s) (Policy): Chính sách hành động, xác định xác suất tác nhân lựa chọn hành
động a khi đối mặt với trạng thái s. Chính sách này có thểmang tính ngẫu nhiên
6
```

## Trang 7

```text
Google Developer Group on Campus
University of Science – VNUHCM
Team AI&DS – Ban Development
(Stochastic policy) ký hiệu là π(a|s) hoặc mang tính tất định (Deterministic policy)
ký hiệu là π(s) = a.
4.1
TừMarkov Process đến Model-free Evaluation
Trước khi đi vào Deep Q-Learning, cần nắm chuỗi xây dựng lý thuyết từMarkov Process
(MP), Markov Reward Process (MRP), đến Markov Decision Process (MDP). Markov
Process chỉmô tảchuỗi trạng thái chuyển đổi theo xác suất cốđịnh, chưa có hành động
và chưa có phần thưởng. Giảđịnh Markov yêu cầu trạng thái hiện tại đã chứa đủthông
tin cần thiết từquá khứ, nên tương lai chỉphụthuộc vào trạng thái hiện tại thay vì toàn
bộlịch sử.
Khi bổsung phần thưởng, ta có Markov Reward Process. Giá trịtrạng thái được định
nghĩa là kỳvọng của tổng phần thưởng chiết khấu:
V (s) = E[Gt|st = s] = E[rt + γrt+1 + γ2rt+2 + · · · |st = s].
Nếu biết xác suất chuyển trạng thái P(s′|s) và phần thưởng R(s), phương trình Bellman
cho MRP là:
V (s) = R(s) + γ
X
s′∈S
P(s′|s)V (s′).
Dạng ma trận tương ứng là V = R + γPV , suy ra V = (I −γP)−1R. Tuy nhiên, cách
giải trực tiếp này có chi phí lớn và đòi hỏi biết trước mô hình môi trường, nên trong thực
tếthường chuyển sang quy hoạch động hoặc các phương pháp học từmẫu.
MDP mởrộng MRP bằng cách thêm hành động của agent. Khi biết trước R(s, a) và
P(s′|s, a), agent có thểtìm chính sách tốt bằng cách chọn hành động làm cực đại giá trị
kỳvọng trong phương trình Bellman tối ưu. Với hàm giá trịhành động, nguyên tắc ra
quyết định trởnên trực tiếp hơn: tại trạng thái s, chọn hành động a sao cho Q(s, a) lớn
nhất.
Trong các trò chơi như Bomberman, ta thường không biết chính xác R và P của toàn bộ
môi trường. Vì vậy cần dùng model-free policy evaluation, tức học giá trịtừdữliệu
tương tác thay vì từmô hình chuyển trạng thái có sẵn. Hai hướng cơ bản là:
• Monte Carlo (MC): Ước lượng V (s) hoặc Q(s, a) bằng trung bình phần thưởng
thu được sau nhiều episode hoàn chỉnh. MC không cần biết P(s′|s, a), nhưng phải
chờepisode kết thúc nên cập nhật chậm và tốn thời gian nếu ván chơi dài.
• Temporal Difference (TD): Cập nhật ngay sau từng bước bằng cách kết hợp
phần thưởng quan sát được với ước lượng hiện tại của trạng thái kếtiếp. TD dùng
bootstrapping, có phương sai thấp hơn MC và phù hợp với tiến trình có thểkéo
dài rất lâu, nhưng có thểtạo bias do dựa trên ước lượng chưa hoàn hảo.
Tóm lại, Dynamic Programming cần biết mô hình chuyển trạng thái, Monte Carlo học từ
episode hoàn chỉnh, còn Temporal Difference kết hợp ưu điểm của cảhai: học trực tiếp
từtrải nghiệm như MC nhưng cập nhật từng bước như DP.
7
```

## Trang 8

```text
Google Developer Group on Campus
University of Science – VNUHCM
Team AI&DS – Ban Development
4.2
Deep Q-Learning
4.2.1
Nguồn gốc, lý thuyết nền tảng và bài toán hội tụ
Thuật toán Q-Learning ban đầu được nghiên cứu và phát triển bởi Christopher Watkins
vào những năm 1980. Bản chất của phương pháp này là học một hàm giá trịhành động
tối ưu nhằm chỉra mức độ”tốt” của một quyết định cụthểtrong một hoàn cảnh cụthể.
Trọng tâm toán học của thuật toán xoay quanh phương trình Bellman dưới dạng cập
nhật gia tăng sau mỗi bước chuyển đổi:
Q(s, a) ←Q(s, a) + α
h
r + γ max
a′
Q(s′, a′) −Q(s, a)
i
Trong đó, r là phần thưởng tức thời nhận được từmôi trường; s′ là trạng thái kếtiếp;
α ∈(0, 1] đóng vai trò là tốc độhọc (learning rate); và hằng sốchiết khấu γ ∈[0, 1] xác
định mức độưu tiên của tác nhân đối với các phần thưởng hiện tại so với lợi ích lâu dài
trong tương lai. Thành phần nằm trong dấu ngoặc vuông [r + γ maxa′ Q(s′, a′) −Q(s, a)]
chính là sai sốhiệu sốthời gian (TD error) , phản ánh khoảng cách giữa ước lượng hiện
tại và mục tiêu TD cải tiến (TD target).
Điều kiện hội tụtrong không gian tabular: Khi được biểu diễn dưới dạng bảng rời rạc
(Tabular Settings) - tức là mỗi cặp (s, a) là một ô nhớđộc lập trong bộdữliệu - thuật
toán Q-Learning được chứng minh một cách nghiêm ngặt rằng sẽhội tụchắc chắn về
hàm giá trịtối ưu Q∗(s, a) , vượt qua các phương pháp ước lượng khác như Monte Carlo
vốn đòi hỏi phải chạy hết toàn bộepisode mới có thểcập nhật , miễn là thỏa mãn đồng
thời hai điều kiện nền tảng:
1. Chính sách thỏa mãn thuộc tính GLIE (Greedy in the Limit of Infinite Explo-
ration): Đảm bảo rằng tất cảcác cặp trạng thái - hành động đều được tác nhân
ghé thăm vô hạn lần (limi→∞Ni(s, a) →∞) đểkhông bỏsót nghiệm, đồng thời
chính sách hành vi của tác nhân phải tiệm cận vềchính sách tham lam hoàn toàn
(limi→∞π(a|s) →arg maxa Q(s, a) với xác suất bằng 1). Một chiến lược thực tế
phổbiến đểđạt được GLIE là áp dụng ϵ-greedy và giảm dần giá trịϵ theo thời gian
theo tỷlệϵi = 1/i.
2. Tốc độhọc αt tuân thủcác điều kiện Robbins-Monro: Chuỗi các hệsốhọc
phải đủlớn đểtriệt tiêu ảnh hưởng của các giá trịkhởi tạo ban đầu nhưng cũng
phải đủnhỏđểtriệt tiêu các nhiễu loạn ngẫu nhiên từmôi trường:
∞
X
t=1
αt = ∞
và
∞
X
t=1
α2
t < ∞
Một ví dụđiển hình đáp ứng quy luật này là đặt αt = 1/T.
Deadly Triad và sựchuyển dịch sang Deep DQN: Dù có bảo chứng hội tụtrong không
gian tabular, việc ứng dụng bảng Q vào các môi trường thực tếnhư Bomberman hay
Atari là bất khảthi, bởi không gian trạng thái quá lớn khiến bảng lưu trữphình to vô hạn.
Giải pháp tất yếu là chuyển sang xấp xỉgiá trịbảng bằng một mạng nơ-ron có tham số
trọng sốθ, gọi là Q(s, a; θ).
8
```

## Trang 9

```text
Google Developer Group on Campus
University of Science – VNUHCM
Team AI&DS – Ban Development
Tuy nhiên, việc tích hợp mạng nơ-ron vào Q-Learning sẽkích hoạt hiện tượng mất ổn
định và phân kỳnghiêm trọng được các nhà nghiên cứu gọi là Deadly Triad. Sựmất ổn
định này xảy ra khi hệthống học hội tụđồng thời 3 yếu tố:
1. Function Approximation (Xấp xỉhàm): Sửdụng mô hình tham số(như mạng
nơ-ron đại lượng lớn) thay cho bảng lưu rời rạc.
2. Bootstrapping (Tựlấy điểm tựa): Cập nhật ước lượng hiện tại dựa trên một ước
lượng khác của trạng thái kếtiếp (TD learning) thay vì sửdụng phần thưởng thực
tếtrọn vẹn.
3. Off-policy learning (Học ngoài chính sách): Huấn luyện và đánh giá một chính
sách mục tiêu tối ưu tối đa trong khi tác nhân lại đang hành động theo một chính
sách hành vi khám phá khác.
Đểchếngự”Bộba chết chóc”, kiến trúc mạng Deep Q-Network (DQN) hiện đại bắt
buộc phải tích hợp hai cơ chếthen chốt nhằm ổn định hóa quá trình hội tụđồthịhọc:
• Experience Replay (Bộnhớphát lại trải nghiệm): Trong quá trình chơi game
liên tục, dữliệu thu thập được mang tính tương quan chuỗi rất mạnh do các khung
hình kếtiếp hầu như giống hệt nhau, vi phạm giảđịnh dữliệu độc lập và phân
phối chuẩn (i.i.d) của học có giám sát. DQN giải quyết bằng cách lưu trữcác bộ
chuyển đổi (s, a, r, s′) vào một bộđệm lưu trữcốđịnh (Replay Buffer) D. Khi cập
nhật mạng, ta lấy ra ngẫu nhiên từng batch nhỏ(minibatch) từbộđệm này đểphá
vỡtính tương quan tuần tự.
• Fixed Q-Targets (Mạng mục tiêu cốđịnh): Nếu chỉdùng một mạng nơ-ron duy
nhất, mục tiêu học (TD target) sẽliên tục thay đổi sau mỗi bước cập nhật trọng số,
giống như việc ta vừa chạy bắn cung vừa dịch chuyển tấm bia. DQN khắc phục
bằng cách thiết lập một mạng nơ-ron độc lập thứhai gọi là Target Network với
bộtham sốθ−biệt lập. Trọng sốθ−sẽđược giữđóng băng cốđịnh và chỉđược
đồng bộ, sao chép lại từmạng chính θ một cách định kỳsau mỗi chu kỳC bước di
chuyển. Đổi lại sựổn định này, nhược điểm vềmặt tài nguyên là hệthống yêu cầu
dung lượng bộnhớtăng gấp đôi đểlưu giữsong song hai mô hình tham số.
Bên cạnh đó, biến thểtinh chỉnh Double DQN (DDQN) thường được triển khai nhằm
giải quyết triệt đểtật xấu cốhữu của Q-Learning là xu hướng đánh giá quá cao giá trị
hành động (overestimation bias). DDQN thực hiện điều này bằng cách tách biệt vai trò:
dùng trọng sốmạng chính θ đểlựa chọn hành động tham lam tốt nhất ởtrạng thái tiếp
theo, nhưng lại dùng trọng sốcủa mạng mục tiêu θ−đểlượng hóa chính xác giá trịcủa
hành động đó.
4.2.2
Thuật toán chi tiết và mã giảDQN
1. Khởi tạo cấu trúc: Tạo lập mạng nơ-ron Q-network chính với bộtham sốngẫu
nhiên θ và sao chép cấu trúc sang mạng mục tiêu target network với trọng số
θ−←θ. Cài đặt bộđệm lưu trữtrải nghiệm D với kích thước tối đa cho phép.
2. Chu trình huấn luyện qua các Episode: Với mỗi vòng lặp trò chơi:
• Tiếp nhận trạng thái ban đầu s trực tiếp từmôi trường.
9
```

## Trang 10

```text
Google Developer Group on Campus
University of Science – VNUHCM
Team AI&DS – Ban Development
• Duy trì vòng lặp cho đến khi trạng thái đạt điều kiện kết thúc (terminal):
(a) Ra quyết định chọn hành động a tuân theo cơ chếϵ-greedy policy:
a =
(
arg maxa′ Q(s, a′; θ)
với xác suất 1 −ϵ
hành động chọn ngẫu nhiên hoàn toàn
với xác suất ϵ
đảm bảo phân phối hợp lý giữa khai thác tri thức (exploit) và khám phá
không gian mới (explore).
(b) Thực thi hành động a trong môi trường, thu hồi tín hiệu phần thưởng tức
thời r cùng trạng thái tiếp diễn s′.
(c) Đóng gói và lưu trữbộtứtrải nghiệm (s, a, r, s′) vào bộđệm Replay Buffer
D.
(d) Trích xuất ngẫu nhiên một minibatch chứa các bộmẫu đồng dạng từD
đểtính toán loss độc lập.
(e) Xác định giá trịmục tiêu huấn luyện yi cho từng mẫu trong minibatch:
yi =
(
ri
nếu s′ là trạng thái kết thúc (terminal)
ri + γ maxa′ Q(s′
i, a′; θ−)
nếu s′ là trạng thái tiếp diễn
(f) Cập nhật bộtham sốmạng chính θ thông qua thuật toán Lan truyền
ngược và Gradient Descent nhằm cực tiểu hóa hàm mất mát bình phương
sai sốtrung bình (MSE Loss):
Loss =
1
|B|
X
i∈B
[yi −Q(si, ai; θ)]2
(g) Chuyển đổi trạng thái hiện tại sang trạng thái tiếp theo: s ←s′.
• Đồng bộđịnh kỳ: Sau khi trải qua một sốlượng C bước cập nhật (hoặc số
lượng episode chỉđịnh), tiến hành cập nhật lại mạng mục tiêu bằng cách sao
chép nguyên bản tham số: θ−←θ.
Mã giảDQN chi tiết dưới dạng Python:
1 Initialize Q-network theta and target network theta_minus
2 Initialize replay buffer D = []
3 for each episode:
4
s = initial_state ()
5
while not terminal(s):
6
if random () < epsilon:
7
a = random_action ()
8
else:
9
a = argmax_a Q(s, a; theta)
10
11
r, s_prime = environment.step(a)
10
```

## Trang 11

```text
Google Developer Group on Campus
University of Science – VNUHCM
Team AI&DS – Ban Development
12
D.append ((s, a, r, s_prime))
13
14
if len(D) > batch_size:
15
batch = sample_minibatch(D, batch_size)
16
loss = 0
17
for (s_i , a_i , r_i , s_prime_i) in batch:
18
if terminal(s_prime_i):
19
target = r_i
20
else:
21
# Su dung mang target network theta_minus
de tinh muc tieu on dinh
22
target = r_i + gamma * max_a Q(s_prime_i ,
a; theta_minus)
23
loss += (target - Q(s_i , a_i; theta))**2
24
25
Update theta using gradient descent on loss
26
27
s = s_prime
28
29
if episode % update_interval == 0:
30
theta_minus = theta
Code 1. Deep Q-Learning pseudocode
Khi đặt thuật toán vào môi trường cụthểnhư trò chơi Bomberman, việc cấu hình trạng
thái s có thểsửdụng mảng ma trận pixel thô trích xuất từmàn hình trò chơi hoặc sử
dụng một vector đặc trưng được thiết kếthủcông tinh gọn (bao gồm tọa độcủa tác
nhân, vịtrí đặt bom, khoảng cách đến kẻđịch hay các ô vật phẩm nâng cấp). Hệthống
phân phối phần thưởng có thểđược quy định mẫu như sau: +10 điểm nếu giành chiến
thắng chung cuộc, −10 điểm nếu tác nhân bịtửtrận, +1 điểm khích lệduy trì sựsống
sót qua mỗi bước di chuyển, và +5 điểm thưởng khi ăn được vật phẩm.
Đánh giá tổng quan: Lợi thếvượt trội của cấu trúc DQN là năng lực tựđộng khai phá
các cấu trúc không gian hình ảnh đặc trưng phức tạp từnguồn dữliệu thô mà không
cần sựcan thiệp thủcông từchuyên gia. Tuy nhiên, hạn chếlớn nhất của nó là cực kỳ
tiêu tốn tài nguyên dữliệu huấn luyện, tốc độtối ưu rất chậm, và quá trình huấn luyện
nhạy cảm cao, dễrơi vào trạng thái bất ổn định nếu các siêu tham số(như kiến trúc
mạng, learning rate, kích thước replay buffer) không được thiết lập chuẩn xác.
Hơn thếnữa, lập trình viên cần đặc biệt lưu ý bẫy ”Reward Hacking” trong giai đoạn
thiết kếhàm thưởng. Đây là hiện tượng tác nhân phát hiện ra kẽhởtoán học đểlặp đi
lặp lại một hành vi vô nghĩa nào đó nhằm trục lợi điểm sốởmức an toàn thay vì thực
hiện đúng ý đồchiến lược ban đầu của nhà thiết kế. Ví dụcụthểtrong Bomberman: do
tác nhân ởgiai đoạn đầu chưa học được kỹnăng né tránh sóng nổ, việc tựý di chuyển
đặt bom thường dẫn đến tựsát và bịphạt điểm nặng (−10). Hệquảlà mạng nơ-ron sẽ
chọn giải pháp tiêu cực: điều khiển tác nhân đứng bất động tuyệt đối ởgóc an toàn cho
đến khi hết giờtrận đấu nhằm bảo toàn điểm sốởmức chấp nhận được (+1 điểm sống
sót mỗi bước), từchối hoàn toàn việc chơi game chủđộng.
11
```

## Trang 12

```text
Google Developer Group on Campus
University of Science – VNUHCM
Team AI&DS – Ban Development
4.3
Policy Gradient Methods
4.3.1
Hạn chếcủa DQN và Triết lý tối ưu trực tiếp chính sách
Mặc dù DQN giải quyết rất tốt bài toán không gian trạng thái lớn, thuật toán này lại bộc
lộnhững điểm yếu chí mạng khi đối mặt với hai kịch bản môi trường đặc thù:
1. Không gian hành động liên tục (Continuous Action Spaces): Ví dụnhư việc
điều khiển góc quay vô lăng chính xác của xe tựhành hoặc lực đẩy liên tục của
khớp robot. DQN đòi hỏi phải tính toán toán tửmaxa Q(s, a), một tác vụcực kỳ
tốn kém và bất khảthi khi tập hành động là vô hạn và liên tục.
2. Chính sách tối ưu bắt buộc phải mang tính ngẫu nhiên (Stochastic Policies):
Trong các trò chơi đối kháng có thông tin bất toàn hoặc mang tính triệt tiêu chiến
thuật (như oẳn tù tì), bất kỳmột chính sách tất định nào cũng dễdàng bịđối
phương bắt bài. Chính sách tối ưu lúc này bắt buộc phải là một phân phối xác
suất ngẫu nhiên cân bằng, điều mà cơ chếtham lam argmax của DQN không thể
cung cấp ổn định.
Đểvượt qua giới hạn đó, họphương pháp Policy Gradient Methods được nghiên cứu
và phát triển mạnh mẽtừnhững năm 1990. Thay vì đi đường vòng bằng cách học hàm
giá trịQ rồi suy diễn ra hành động, triết lý cốt lõi của Policy Gradient là sửdụng mạng
nơ-ron trực tiếp mô hình hóa và tối ưu hóa chính sách π(a|s; θ) (với θ là các tham số
trọng sốquy định xác suất sinh hành động). Đểcập nhật bằng gradient descent, chính
sách π(a|s; θ) cần khảvi theo θ, đồng thời gradient ∇θπ(a|s; θ) phải tồn tại và hữu hạn.
Mục tiêu cốt lõi của chúng ta là tìm bộtham sốθ đểtối đa hóa hàm mục tiêu hiệu năng
kỳvọng J(θ). Trong episodic case, có trạng thái dừng và bỏqua discounting đểđơn
giản, J(θ) có thểhiểu là kỳvọng tổng reward của toàn bộepisode do chính sách hiện tại
sinh ra. Nhờvào Định lý Policy Gradient, việc tính toán gradient của hàm hiệu năng
theo tham sốθ được quy giản vềdạng biểu thức toán học rất đẹp mà không phụthuộc
vào đạo hàm của hàm chuyển trạng thái môi trường vô hình:
∇θJ(θ) = E [∇θ log π(a|s; θ) · A(s, a)]
Trong biểu thức trên, đại lượng A(s, a) chính là hàm Lợi thế(Advantage function). Hàm
này đóng vai trò như một chiếc cân đo lường, đánh giá xem hành động a vừa được thực
hiện tốt hơn hay tệhơn mức kỳvọng trung bình của trạng thái s hiện tại:
A(s, a) = Q(s, a) −V (s)
Nếu một hành động mang lại kết quảtốt hơn trung bình (A(s, a) > 0), gradient sẽkéo
tham sốθ dịch chuyển theo hướng làm tăng xác suất chọn lại hành động đó trong tương
lai và ngược lại.
Có thểphân biệt ba mức triển khai Policy Gradient trước khi đi đến PPO:
• All-actions method: Nếu có thểxét toàn bộkhông gian hành động, ta cập nhật
chính sách bằng cách cộng đóng góp gradient của mọi hành động theo xác suất
của chúng. Cách này rõ vềmặt lý thuyết nhưng tốn kém khi sốhành động lớn.
12
```

## Trang 13

```text
Google Developer Group on Campus
University of Science – VNUHCM
Team AI&DS – Ban Development
• REINFORCE: Lấy mẫu hành động từchính sách hiện tại rồi cập nhật theo quỹ
đạo đã quan sát. Dạng trực giác của cập nhật là tăng xác suất các hành động
dẫn đến return cao và giảm xác suất các hành động dẫn đến return thấp:
θ ←θ + αGt∇θ log π(at|st; θ).
• REINFORCE with baseline: Trừđi một baseline, thường là V (st), đểgiảm phương
sai mà không làm lệch kỳvọng gradient:
θ ←θ + α(Gt −V (st))∇θ log π(at|st; θ).
• Actor-Critic: Kết hợp actor học chính sách π(a|s; θ) và critic học hàm giá trịV (s; φ)
hoặc Q(s, a; φ). Critic cung cấp tín hiệu lợi thếA(s, a) ổn định hơn cho actor, tạo
nền tảng cho các thuật toán hiện đại như PPO.
4.3.2
Thuật toán PPO (Proximal Policy Optimization)
Thuật toán PPO, được giới thiệu bởi OpenAI vào năm 2017, hiện đang là một trong
những thuật toán Policy Gradient phổbiến và hiệu quảnhất nhờkhắc phục được nhược
điểm của các phương pháp Policy Gradient truyền thống (thường có bước cập nhật quá
lớn khiến chính sách bịphá hủy hoàn toàn và không thểphục hồi). PPO giải quyết vấn
đềnày bằng một cơ chếtinh tếgọi là Clipping nhằm giới hạn biên độthay đổi giữa
chính sách cũ (πold) và chính sách mới (πθ) vừa được cập nhật, đảm bảo tác nhân duy
trì quá trình học mượt mà, ổn định và không bị”quên” các tri thức quan trọng đã tích lũy.
Hàm mục tiêu Clipped Surrogate Objective đặc trưng của PPO được định nghĩa như
sau:
LCLIP(θ) = E [min(rt(θ)At, clip(rt(θ), 1 −ϵ, 1 + ϵ)At)]
Trong đó, rt(θ) =
π(at|st;θ)
π(at|st;θold) đại diện cho tỷlệxác suất giữa chính sách mới và chính sách
cũ. Nếu tỷlệnày dịch chuyển quá xa khỏi khoảng an toàn [1 −ϵ, 1 + ϵ] (với ϵ thường
được thiết lập quanh mức 0.1 hoặc 0.2), hàm clip sẽlập tức kích hoạt đểcắt bớt phần
thay đổi quá đà, triệt tiêu động lực cập nhật cực đoan.
Chu trình thuật toán và kiến trúc mã giảcủa PPO:
1. Khởi tạo cấu trúc mô hình Actor-Critic: Tạo lập mạng chính sách π(a|s; θ)
(mạng Actor đảm nhận vai trò ra quyết định) và mạng hàm giá trịV (s; φ) (mạng
Critic đảm nhận vai trò đánh giá trạng thái) với các tham sốkhởi tạo ngẫu nhiên θ
và φ.
2. Vòng lặp huấn luyện theo Epoch: Tại mỗi vòng lặp lớn:
• Giai đoạn thu thập dữliệu (Collect Rollouts): Chạy chính sách tác nhân
hiện tại tương tác trực tiếp với môi trường. Đểtối ưu hóa hiệu năng tính
toán và gia tăng tính đa dạng dữliệu, PPO thường được cấu hình huấn
luyện đồng thời trên nhiều môi trường song song độc lập (num_envs parallel
environments). Tác nhân sẽchọn hành động bằng cách lấy mẫu ngẫu nhiên
dựa trên phân phối xác suất sinh ra từmô hình π(a|s; θ) và đóng gói toàn bộ
quỹđạo dữliệu thu được bao gồm các bộdữliệu chuyển đổi trạng thái cùng
log xác suất cũ: (s, a, r, s′, πold).
13
```

## Trang 14

```text
Google Developer Group on Campus
University of Science – VNUHCM
Team AI&DS – Ban Development
• Giai đoạn tính toán lợi thế(Compute Advantages): Với mỗi bước thời gian
t trong chuỗi dữliệu thu thập, ta ước lượng giá trịlợi thếˆAt thông qua cơ chế
GAE (Generalized Advantage Estimation):
ˆAt =
∞
X
l=0
(γλ)lδt+l
Trong đó, δt = rt + γV (st+1; φ) −V (st; φ) là sai sốTD Error đo đạc bởi mạng
Critic. Tham sốđiều hòa λ ∈[0, 1] đóng vai trò kiểm soát, cân bằng linh hoạt
giữa độlệch (bias) và phương sai (variance) của mô hình ước lượng.
• Giai đoạn cập nhật chính sách (Actor Update): Thực hiện vòng lặp K lần
trên các minibatch trích xuất ngẫu nhiên từquỹđạo dữliệu đểtối ưu hóa
tham sốmạng Actor:
(a) Tính toán giá trịhàm mất mát PPO Loss: LPPO = −Et
h
min(rt ˆAt, clip(rt, 1 −ϵ, 1 + ϵ) ˆAt)
i
(b) Cập nhật bộtrọng sốθ thông qua phương pháp thúc đẩy gradient descent.
• Giai đoạn cập nhật hàm giá trị(Critic Update): Thực hiện vòng lặp K′ lần
song song đểtối ưu hóa tham sốmạng Critic:
(a) Tính toán sai sốbình phương trung bình (MSE Loss) giữa giá trịmạng
Critic dựđoán với giá trịmục tiêu thực tếthu hồi từmôi trường: LV =
Et [(V (st; φ) −(rt + γV (st+1; φ)))2].
(b) Cập nhật bộtrọng sốφ bằng thuật toán gradient descent nhằm thu hẹp
khoảng cách đánh giá.
Mã giảPPO dạng cấu trúc thuật toán Python:
1 Initialize policy pi(a|s; theta) and value function V(s; phi)
2 for each epoch:
3
# Buoc 1: Thu thap rollouts tu cac moi truong song song
4
trajectories = []
5
for env in parallel_environments:
6
s = env.reset ()
7
while not terminal(s):
8
# Lay mau hanh dong dua tren phan phoi xac suat
9
a ~ pi(a|s; theta)
10
r, s_prime = env.step(a)
11
trajectories.append ((s, a, r, s_prime , log_prob))
12
s = s_prime
13
14
# Buoc 2: Uoc luong ham loi the Advantage bang GAE
15
for each (s, a, r, s_prime) in trajectories:
16
A = 0
17
for t in trajectory_length downto 0:
18
delta = r[t] + gamma * V(s[t+1]; phi) - V(s[t]; phi)
19
A = delta + gamma * lambda * A
20
advantage[t] = A
14
```

## Trang 15

```text
Google Developer Group on Campus
University of Science – VNUHCM
Team AI&DS – Ban Development
21
22
# Buoc 3: Cap nhat mang chinh sach Actor K lan
23
for k in range(K):
24
for minibatch in trajectories:
25
r_t = pi(a|s; theta) / pi_old(a|s)
26
surrogate1 = r_t * advantage
27
surrogate2 = clip(r_t , 1-eps , 1+eps) * advantage
28
loss_policy = -min(surrogate1 , surrogate2)
29
Update theta using gradient descent on loss_policy
30
31
# Buoc 4: Cap nhat mang danh gia Critic K_prime lan
32
for k_prime in range(K_prime):
33
for minibatch in trajectories:
34
target = r + gamma * V(s_prime; phi)
35
loss_value = (V(s; phi) - target)**2
36
Update phi using gradient descent on loss_value
Code 2. PPO pseudocode
4.3.3
Đánh giá và so sánh thực tiễn
Ưu điểm vượt trội: Thuật toán PPO sởhữu độổn định huấn luyện rất cao nhờcó biên
giới giới hạn clipping che chắn, giảm thiểu rủi ro đổvỡchính sách đột ngột. Thuật toán
này rất dễcấu hình hệthống siêu tham sốvà có khảnăng tương thích xuất sắc với cả
không gian hành động rời rạc lẫn không gian hành động liên tục phức tạp.
Nhược điểm cốt lõi: Điểm hạn chếlớn nhất của PPO nằm ởtính kém hiệu quảvềmặt
sửdụng mẫu (sample inefficient) khi đặt lên bàn cân so sánh với các thuật toán off-policy
như DQN. Do bản chất là một phương pháp học on-policy (hoặc gần on-policy), PPO
yêu cầu hệthống phải liên tục thu thập một lượng khổng lồcác mẫu rollout mới hoàn
toàn tại mỗi epoch đểphục vụhuấn luyện, đồng thời bắt buộc phải lưu giữtoàn bộthông
tin các rollout cũ tương ứng chỉđểphục vụcho tác vụtính toán hàm lợi thế.
4.4
Self-Play
4.4.1
Nguồn gốc và ý tưởng cơ bản
Self-play được sửdụng rộng rãi trong các trò chơi như cờvua (AlphaGo) và các trò chơi
hành động. Ý tưởng là: thay vì huấn luyện agent chỉchống lại các chiến lược cốđịnh
hoặc ngẫu nhiên, thì ta cho nó chơi với các phiên bản cải thiện của chính nó. Khi agent
mạnh hơn, đối thủcũng phải mạnh hơn đểtạo ra áp lực cạnh tranh.
Điều này tạo ra một vòng lặp tích cực: agent vn được huấn luyện bằng cách chơi với
agent vn−1 (phiên bản trước). Khi vn đạt một chất lượng nhất định, nó trởthành đối thủ
cho agent tiếp theo vn+1. Quá trình này dẫn đến một ”evolutionary arms race” nơi các
agent liên tục phát triển đểđánh bại đối thủ.
15
```

## Trang 16

```text
Google Developer Group on Campus
University of Science – VNUHCM
Team AI&DS – Ban Development
4.4.2
Các bước chi tiết và mã giả
1. Khởi tạo: Tạo agent chính πmain với tham sốngẫu nhiên. Khởi tạo một bộcác
agent cũ πpool = {π1, π2, . . .} đểđóng vai trò đối thủ.
2. Lặp cho mỗi epoch:
• Chọn đối thủ: Chọn ngẫu nhiên một agent từπpool làm đối thủ. Có thểlà
bản thân agent chính (πmain) hoặc một phiên bản cũ.
• Chơi trò chơi: Chạy một trận đấu (hoặc nhiều trận) giữa πmain (vai trò agent
1) và agent đối thủ(vai trò agent 2, 3, hoặc 4 trong Bomberman). Thu thập
dữliệu: (si, ai, ri, s′i) cho agent 1 và (sj, aj, rj, s′j) cho agent khác.
• Cập nhật agent chính: Sửdụng dữliệu từtrò chơi (ví dụvới PPO hoặc
DQN) đểhuấn luyện πmain. Phần thưởng có thể:
– r = +1 nếu agent sống sót và đối thủchết
– r = −1 nếu agent chết
– r = 0.1 nếu agent sống sót mỗi bước (survive bonus)
– r = +0.5 nếu agent thu thập vật phẩm
• Cập nhật pool: Sau mỗi K epoch (ví dụK = 10), lưu phiên bản hiện tại của
πmain vào πpool. Nếu pool quá lớn, có thểloại bỏcác phiên bản yếu nhất.
Mã giảSelf-Play:
1 Initialize pi_main with random parameters
2 pi_pool = [pi_main]
# Opponent pool
3 win_rates = {}
4
5 for epoch in range(num_epochs):
6
# Select opponent
7
opponent_id = random.choice(range(len(pi_pool)))
8
pi_opponent = pi_pool[opponent_id]
9
10
# Play games
11
for game in range(num_games_per_epoch):
12
# Randomize agent order to reduce positional bias
13
if random.random () < 0.5:
14
agent1 , agent2 = pi_main , pi_opponent
15
collect_from_main = True
16
else:
17
agent1 , agent2 = pi_opponent , pi_main
18
collect_from_main = False
19
20
trajectories = play_game(agent1 , agent2)
21
22
# Extract main agent data
23
if collect_from_main:
16
```

## Trang 17

```text
Google Developer Group on Campus
University of Science – VNUHCM
Team AI&DS – Ban Development
24
main_data = trajectories [0]
25
else:
26
main_data = trajectories [1]
27
28
# Reward: +1 if won , -1 if lost , +0.1 per step alive
29
game_result = determine_winner(agent1 , agent2)
30
if collect_from_main:
31
if game_result == 1:
# agent1 (main) won
32
reward = 1.0
33
else:
34
reward = -1.0
35
else:
36
if game_result == 2:
# agent2 (main) won
37
reward = 1.0
38
else:
39
reward = -1.0
40
41
# Accumulate training data
42
training_data.extend(main_data)
43
44
# Update pi_main using collected data
45
train_agent(pi_main , training_data)
46
47
# Periodically add current policy to opponent pool
48
if epoch % update_pool_interval == 0:
49
pi_pool.append(copy(pi_main))
50
if len(pi_pool) > max_pool_size:
51
# Remove weakest from pool (optional)
52
pi_pool = pi_pool[-max_pool_size :]
53
54
# Periodically test against fixed opponents
55
if epoch % eval_interval == 0:
56
for test_opponent in pi_pool:
57
win_rate = evaluate(pi_main , test_opponent ,
num_eval_games)
58
print(f"Win rate vs opponent: {win_rate}")
Code 3. Self-Play training pseudocode
Một điểm quan trọng: trong Bomberman, có thểcó 4 agent cùng lúc. Self-play cơ bản
chỉxem xét 2 agent. Đểmởrộng, có thể:
• Thêm hai agent fixed (chơi ngẫu nhiên hoặc rule-based) làm “environment obsta-
cles”.
• Hoặc huấn luyện bốn agent song song, mỗi agent phải học cách chơi chống lại ba
đối thủthích nghi.
Self-play giúp agent phát triển các chiến lược tinh vi đểđối phó với các đối thủthích
17
```

## Trang 18

```text
Google Developer Group on Campus
University of Science – VNUHCM
Team AI&DS – Ban Development
nghi. Nó tựđộng gen dữliệu huấn luyện liên quan. Thách thức là vòng lặp có thểtrở
nên không ổn định: agent có thểrơi vào các ”local optima” (ví dụchỉbiết một chiến lược
lạnhưng hiệu quảchống lại một đối thủcụthể), hoặc một phiên bản yếu trong pool vô
tình được chọn quá thường xuyên.
4.5
Behaviour Cloning
4.5.1
Nguồn gốc và ý tưởng cơ bản
Behavior Cloning được khái niệm từhọc có giám sát cơ bản. Ý tưởng là: cho một tập
hợp demo từchuyên gia (expert, có thểlà con người hoặc các agent tốt có sẵn), huấn
luyện một mô hình đểdựđoán hành động được chọn bởi chuyên gia ởmỗi trạng thái.
Nó là cách nhanh nhất đểtạo một agent tương đối hợp lý mà không cần định nghĩa hàm
phần thưởng phức tạp hoặc chờRL hội tụ.
Cách tiếp cận này được sửdụng trong robotics, driving simulators, và các tác vụhọc từ
demo (learning from demonstrations). Tuy nhiên, nó có một vấn đềcốhữu: nếu agent
hoạt động khác so với chuyên gia tại bất kỳthời điểm nào, nó có thểrơi vào các trạng
thái chuyên gia chưa bao giờgặp phải (out-of-distribution states), và nó phải tựđưa ra
hành động tiếp theo.
4.5.2
Các bước chi tiết và mã giả
1. Thu thập demo: Ghi lại các trận đấu từnhững con người chơi Bomberman khéo
léo. Với mỗi frame, lưu trữ:
• Trạng thái s: biểu diễn bản đồ(ví dụ: pixel, feature vector)
• Hành động a: sốnguyên từ0-5 tương ứng với STOP, LEFT, RIGHT, UP,
DOWN, PLACE_BOMB
Sốlượng frames tốt: ít nhất vài chục nghìn frames (tương đương hàng trăm trò
chơi).
2. Xây dựng dataset: Tổchức dữliệu thành cặp (si, ai) và chia thành tập training
(ví dụ80%) và tập validation (20%).
3. Xây dựng mô hình: Tạo một mạng nơ-ron πθ(a|s) nhận trạng thái làm đầu vào và
xuất ra phân bốxác suất trên các hành động. Kiến trúc thường dùng:
• Nếu trạng thái là ảnh: CNN (Convolutional Neural Network)
• Nếu trạng thái là feature vector: MLP (fully connected layers)
4. Huấn luyện: Lặp qua dữliệu training theo batch. Với mỗi batch:
• Dựđoán: ˆai = πθ(si) (chọn hành động có xác suất cao nhất)
• Tính loss (cross-entropy):
L = −
X
i
log πθ(ai|si)
18
```

## Trang 19

```text
Google Developer Group on Campus
University of Science – VNUHCM
Team AI&DS – Ban Development
• Cập nhật θ bằng gradient descent (ví dụ: Adam optimizer)
Huấn luyện cho đến khi accuracy trên tập validation không cải thiện (early stopping).
5. Đánh giá: Kiểm tra độchính xác trên tập test. Ngoài ra, cho agent chơi vài trận
đấu đểxem hành vi có hợp lý không.
Mã giảBehavior Cloning:
1 # Data collection phase
2 demonstrations = []
3 for each human_game in recorded_games:
4
for each frame in human_game:
5
state = extract_state(frame)
6
action = extract_action(frame)
# What human did
7
demonstrations.append ((state , action))
8
9 # Split data
10 train_data , val_data = split(demonstrations , test_size =0.2)
11
12 # Build model
13 model = NeuralNetwork(input_dim=state_dim ,
output_dim=num_actions)
14 optimizer = Adam(learning_rate =0.001)
15
16 # Training
17 best_val_loss = infinity
18 patience_counter = 0
19 max_patience = 10
20
21 for epoch in range(max_epochs):
22
total_train_loss = 0
23
for batch in train_data:
24
states , actions = batch
25
26
# Forward pass
27
logits = model.forward(states)
# Shape: [batch_size ,
num_actions]
28
29
# Cross -entropy loss
30
loss = cross_entropy_loss(logits , actions)
31
32
# Backward pass
33
grads = compute_gradients(loss)
34
35
# Update
36
model.update(grads , optimizer)
37
38
total_train_loss += loss
39
19
```

## Trang 20

```text
Google Developer Group on Campus
University of Science – VNUHCM
Team AI&DS – Ban Development
40
avg_train_loss = total_train_loss / len(train_data)
41
42
# Validation
43
val_loss = 0
44
val_correct = 0
45
for batch in val_data:
46
states , actions = batch
47
logits = model.forward(states)
48
loss = cross_entropy_loss(logits , actions)
49
val_loss += loss
50
51
predicted_actions = argmax(logits , axis =1)
52
val_correct += sum(predicted_actions == actions)
53
54
avg_val_loss = val_loss / len(val_data)
55
val_accuracy = val_correct / total_val_samples
56
57
print(f"Epoch {epoch }: train_loss ={ avg_train_loss :.4f}, "
58
f"val_loss ={ avg_val_loss :.4f},
val_acc ={ val_accuracy :.4f}")
59
60
# Early stopping
61
if avg_val_loss < best_val_loss:
62
best_val_loss = avg_val_loss
63
patience_counter = 0
64
save_model(model)
# Save best model
65
else:
66
patience_counter += 1
67
if patience_counter >= max_patience:
68
print("Early stopping")
69
break
70
71 # Load best model
72 model = load_best_model ()
73
74 # Deployment: agent plays games
75 for game in range(num_test_games):
76
s = game.reset ()
77
while not terminal(s):
78
logits = model.forward(s)
79
a = argmax(logits)
# Greedy action selection
80
s = game.step(a)
Code 4. Behavior Cloning pseudocode
Ưu điểm của BC: nhanh chóng, dễtriển khai, không cần định nghĩa hàm phần thưởng.
Nhược điểm: phụthuộc vào chất lượng demo, agent không thểvượt quá kỹnăng chuyên
gia, dễgặp distribution shift.
20
```

## Trang 21

```text
Google Developer Group on Campus
University of Science – VNUHCM
Team AI&DS – Ban Development
Nhược điểm: BC dễgặp phải vấn đềlà nếu agent đưa ra quyết định khác so với chuyên
gia ởbước t, nó rơi vào trạng thái s′
t mà chuyên gia chưa bao giờgặp trong dữliệu
demo (Distribution shift). Khi agent dựđoán hành động ởs′
t, nó dựa vào một trạng thái
out-of-distribution, lỗi có thểtích lũy theo thời gian (error compounding).
Một cải tiến gọi là DAgger (Dataset Aggregation) có thểgiải quyết vấn đềnày:
• Huấn luyện BC trên dữliệu demo ban đầu.
• Chạy agent và ghi lại các trạng thái nó gặp phải.
• Yêu cầu chuyên gia ghi lại hành động tại các trạng thái mới này.
• Thêm dữliệu mới vào dataset và huấn luyện lại.
• Lặp lại.
4.5.3
Monte Carlo Tree Search (MCTS)
Trong sốcác phương pháp hoạch định trực tuyến (online planning) thuộc nhánh học
tăng cường dựa trên mô hình (Model-based RL), Tìm kiếm cây Monte Carlo (Monte
Carlo Tree Search - MCTS) đóng vai trò là một thuật toán xấp xỉđồthịquyết định cực
kỳmạnh mẽ. Khác với các thuật toán tìm kiếm duyệt cạn truyền thống vốn bịgiới hạn
bởi bùng nổtổhợp do không gian trạng thái quá lớn, MCTS kết hợp linh hoạt khảnăng
định hướng của cây quyết định với tính chất ngẫu nhiên mang tính thống kê của các
mô phỏng Monte Carlo. Thuật toán tiến hành xây dựng một cây tìm kiếm bất đối xứng
một cách tăng trưởng thông qua chu kỳlặp đi lặp lại của bốn bước cốt lõi: Lựa chọn
(Selection), Mởrộng (Expansion), Mô phỏng (Simulation/Playout), và Lan truyền ngược
(Backpropagation).
Quy trình thuật toán chi tiết và nền tảng toán học:
1. Selection (Lựa chọn): Tiến trình bắt đầu từnút gốc v0 (đại diện cho trạng thái
hiện tại của môi trường). Thuật toán duyệt qua các nút con nội bộcủa cây bằng
cách áp dụng một chính sách chọn lọc cây (tree policy). Đểgiải quyết bài toán cốt
lõi vềviệc cân bằng giữa khai thác tri thức hiện tại (exploitation) và khám phá các
vùng không gian mới (exploration), thuật toán UCT (Upper Confidence Bounds for
Trees) - một nhánh mởrộng của bài toán Multi-armed Bandit áp dụng tiêu chuẩn
UCB1 - thường được sửdụng phổbiến nhất:
UCT(v) = Q(v)
N(v) + C
s
ln N(parent)
N(v)
Trong đó:
• Q(v) là tổng giá trịphần thưởng tích lũy thu được tại nút v qua các lượt mô
phỏng trước đó.
• N(v) là tổng sốlần nút v đã được ghé thăm trong toàn bộtiến trình tìm kiếm.
• N(parent) biểu diễn sốlần nút cha trực tiếp của nút v được duyệt qua.
21
```

## Trang 22

```text
Google Developer Group on Campus
University of Science – VNUHCM
Team AI&DS – Ban Development
• C là hằng sốđiều hòa khám phá (thường được thiết lập vềmặt lý thuyết là
C =
√
2 khi giá trịphần thưởng được chuẩn hóa vềkhoảng [0, 1]).
Ý nghĩa toán học của biểu thức UCT chia làm hai thành phần tường minh: sốhạng
đầu tiên Q(v)
N(v) đại diện cho giá trịkỳvọng trung bình (giá trịkhai thác), ưu tiên các
nhánh đi có hiệu suất cao; sốhạng thứhai chứa căn thức đại diện cho độbất định
toán học (giá trịkhám phá), tỷlệnghịch với sốlần nút đó được thăm. Thuật toán
liên tục chọn nút con có chỉsốUCT lớn nhất cho đến khi chạm vào một nút lá vl
(nút chưa được mởrộng hoàn toàn hoặc chứa các hành động chưa từng được
khám phá).
2. Expansion (Mởrộng): Khi tiến trình lựa chọn dừng lại tại nút lá vl, nếu trạng thái
này chưa phải là trạng thái kết thúc trận đấu (terminal state), thuật toán sẽtiến
hành mởrộng cây tìm kiếm. Một hoặc nhiều nút con mới vc sẽđược khởi tạo và
liên kết vào cây, tương ứng với các hành động hợp lệkhảthi mà tác nhân có thể
thực hiện từtrạng thái của vl. Đểtối ưu hóa tài nguyên tính toán trong các môi
trường có hệsốrẽnhánh (branching factor) lớn, hệthống thông thường chỉthêm
một nút con duy nhất cho mỗi chu kỳ.
3. Simulation (Mô phỏng / Playout): Từnút con mới được thiết lập vc, một phiên
chơi thửnghiệm giảlập (rollout) sẽđược kích hoạt và chạy liên tục cho đến khi trò
chơi đạt điều kiện kết thúc hoặc chạm tới một độsâu giới hạn quy định. Trong giai
đoạn này, một chính sách mặc định (default policy) - có thểlà chọn hành động
ngẫu nhiên hoàn toàn (uniform random) hoặc bán ngẫu nhiên kết hợp các luật
heuristic đơn giản - sẽđiều khiển các thực thểdi chuyển. Mục tiêu của bước này
là thu vềmột ước lượng nhanh, dù có thểchứa nhiều nhiễu thống kê, vềgiá trị
tiềm năng lâu dài của nhánh quyết định vừa chọn mà không cần cấu hình hàm
đánh giá trạng thái phức tạp.
4. Backpropagation (Lan truyền ngược): Ngay khi phiên mô phỏng kết thúc và trả
vềtín hiệu kết quả(reward), dữliệu thống kê này sẽđược truyền ngược theo lộ
trình tuyến tính từnút mô phỏng vc lên tới tận nút gốc v0. Với mỗi nút v nằm trên
trục đường truyền ngược này, hệthống tiến hành cập nhật đồng thời các đại lượng:
N(v) ←N(v) + 1
Q(v) ←Q(v) + reward
Tùy thuộc vào bản chất môi trường (đơn tác nhân, đa tác nhân hợp tác hay đối
kháng), hàm phần thưởng (reward) có thểđược cấu hình linh hoạt. Trong kịch bản
đối kháng zero-sum hai người chơi, giá trịcập nhật thường đảo dấu tuần tựgiữa
các tầng đểphản ánh tư duy Minimax, hoặc sửdụng hàm điểm sốphức tạp liên
tục dựa trên các tiêu chí cụthể.
5. Chu kỳlặp và Ra quyết định cuối cùng: Toàn bộchuỗi bốn bước từ(1) đến (4)
được vận hành liên tục dưới dạng một vòng lặp anytime algorithm. Tiến trình tìm
kiếm có thểdừng lại ởbất kỳthời điểm nào tùy thuộc vào giới hạn tài nguyên (như
giới hạn thời gian tính toán real-time hoặc sốlượt lặp cốđịnh). Khi vòng lặp kết
thúc, tác nhân sẽchính thức đưa ra quyết định hành động thực tếbằng cách chọn
22
```

## Trang 23

```text
Google Developer Group on Campus
University of Science – VNUHCM
Team AI&DS – Ban Development
nút con trực tiếp của nút gốc sởhữu sốlần ghé thăm cao nhất (max N(v) - Robust
Child) hoặc sởhữu giá trịhiệu suất trung bình lớn nhất (max Q(v)
N(v) - Max Child).
Tính hội tụtoán học của MCTS: Một trong những bảo chứng lý thuyết quan trọng nhất
của MCTS (đặc biệt là biến thểUCT) là tính hội tụtiệm cận. Khi sốlượt mô phỏng tiến
dần đến vô hạn (N →∞), xác suất tác nhân lựa chọn các nhánh đi suboptimal (dưới
tối ưu) sẽhội tụvề0 nhờcó thành phần khám phá của UCT che chắn. Cây tìm kiếm
MCTS sẽtăng trưởng bất đối xứng, tập trung sâu vào các vùng không gian chiến lược
tối ưu, và giá trịước lượng Q(v)
N(v) sẽhội tụchính xác vềgiá trịtrò chơi lý thuyết Minimax
(đối với game đối kháng) hoặc phương trình tối ưu Bellman.
Ứng dụng trong môi trường chiến thuật Bomberman:
Khi triển khai MCTS cho trò chơi Bomberman, đồthịcây sẽmô phỏng các chuỗi hành
động kết hợp tuần tựtrong tương lai của tác nhân bao gồm: Di chuyển (Lên, Xuống,
Trái, Phải), Đứng yên (Chờđợi), hoặc Đặt bom. Ưu điểm cốt lõi của MCTS trong ngữ
cảnh này là tính độc lập dữliệu huấn luyện (training data-free) và khảnăng thích ứng
linh hoạt với các thay đổi động của bản đồ. Thuật toán không đòi hỏi một mô hình học
sâu được huấn luyện trước tốn kém mà chỉcần tích hợp một bộgiảlập công cụtrò chơi
(forward model/game engine) có khảnăng tính toán trạng thái kếtiếp cực nhanh. Tại
mỗi bước đi thực tế, cây tìm kiếm được tái cấu trúc hoàn toàn từtrạng thái hiện tại, giúp
tác nhân phản ứng nhạy bén trước sựdịch chuyển bất ngờcủa kẻđịch hay các chuỗi
nổdây chuyền của bom.
Tuy nhiên, cấu trúc thuần túy của MCTS vấp phải những rào cản kỹthuật nghiêm trọng
khi đối mặt với tính chất thời gian thực và độtrễnổcủa bom:
• Điểm nghẽn tính toán mô phỏng (Simulation Bottleneck): Đểđưa ra quyết
định có độchính xác cao trong môi trường có hệsốrẽnhánh lớn và thời gian nổ
kéo dài (bom hẹn giờcần nhiều bước đểkích nổ), MCTS cần phải thực hiện hàng
ngàn đến hàng triệu lượt mô phỏng ngẫu nhiên sâu. Điều này tạo áp lực cực lớn
lên CPU và khó lòng đáp ứng tần suất ra quyết định real-time (thường dưới 100ms
mỗi khung hình).
• Tật mù quáng của Playout ngẫu nhiên (Tactical Blindness): Do bước mô
phỏng sửdụng chính sách ngẫu nhiên, các tác nhân giảlập trong Playout thường
di chuyển không mục đích. Điều này dẫn đến việc ước lượng sai lệch: một vịtrí
đặt bom chiến thuật có thểbịđánh giá thấp chỉvì chính sách ngẫu nhiên trong
Playout điều khiển tác nhân tựsát; hoặc ngược lại, một nhánh đi nguy hiểm bị
đánh giá cao do sựmay mắn ngẫu nhiên của phiên Playout không kích hoạt bẫy
nổ.
Xu hướng tinh chỉnh hiện đại - PUCT và Sựkết hợp Mạng nơ-ron:
Đểkhắc phục các nhược điểm trên, các hệthống AI hiện đại (được truyền cảm hứng từ
kiến trúc AlphaGo/AlphaZero) thường loại bỏbước Playout ngẫu nhiên truyền thống và
thay thếbằng việc kết hợp với các mạng nơ-ron tham số. Khi đó, biểu thức lựa chọn
UCT được chuyển đổi thành thuật toán PUCT (Predictor + UCB for Trees):
23
```

## Trang 24

```text
Google Developer Group on Campus
University of Science – VNUHCM
Team AI&DS – Ban Development
PUCT(v) = Q(v)
N(v) + C · P(s, a) ·
p
N(parent)
1 + N(v)
Trong đó, P(s, a) đóng vai trò là phân phối xác suất tiên nghiệm (prior probability) được
cung cấp từmột mạng chính sách (Policy Network) đã qua huấn luyện. Mạng chính
sách này giúp thu hẹp lập tức hệsốrẽnhánh bằng cách chỉhướng xung lực tìm kiếm
vào các hành động có triển vọng cao. Song song đó, giá trịphần thưởng cuối cùng tại
nút lá thay vì chạy Playout ngẫu nhiên kéo dài sẽđược dựđoán trực tiếp thông qua một
mạng giá trị(Value Network) V (s). Sựkết hợp hoàn hảo này biến MCTS từmột thuật
toán tìm kiếm mù quáng thành một tiến trình hoạch định có định hướng cao, giải phóng
đáng kểnăng lực tính toán và nâng tầm tư duy chiến thuật của tác nhân lên mức độ
chuyên nghiệp.
5. Nguồn tham khảo
1. Khóa CS234 của Stanford vềReinforcement Learning
2. RL Book, Sutton Barto
3. RL Course Toronto University
4. Neuriton
5. RL Exercises, AI VIETNAM
6. Single-File RL Algorithms Code
24
```
