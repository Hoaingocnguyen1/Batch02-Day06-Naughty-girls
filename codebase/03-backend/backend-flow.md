# Luồng Xử Lý Backend - ShopeeFood Chatbot MVP

Tài liệu này mô tả chi tiết kiến trúc, các API endpoint, luồng dữ liệu (data flow), và cách tích hợp AI (LLM) ở tầng Backend nhằm giải quyết bài toán gợi ý món ăn thông minh cho ShopeeFood.

---

## 1. Sơ đồ Kiến trúc & Luồng tổng quan

Hệ thống hoạt động theo mô hình **Augmentation (Hỗ trợ ra quyết định)**. Luồng xử lý đi qua các bước chính sau:

```
[Người dùng] ──(1. Nhập ý định)──> [Frontend App]
                                          │
                                   (2. POST /api/chat)
                                          │
                                          ▼
                                   [Backend API]
                                          │
                    ┌─────────────────────┴─────────────────────┐
                    │ (3. Gửi prompt + DB Quán)                 │ (4. Truy vấn DB thật)
                    ▼                                           ▼
             [LLM Service]                               [Restaurant DB]
                    │                                     (mock_data.json)
            (Trả về đề xuất JSON)                               │
                    │                                           │
                    └─────────────────────┬─────────────────────┘
                                          │
                                          ▼
                                 [Code-level Validator]
                       (Xác thực ID quán & món ăn có tồn tại)
                                          │
                             (5. Trả về kết quả sạch)
                                          │
                                          ▼
[Người dùng] <──(6. Chọn món & Mở quán)─ [Frontend App]
```

---

## 2. Đặc tả API Endpoint

Backend cung cấp API duy nhất cho việc chat gợi ý món ăn:

### `POST /api/chat`
*   **Mục đích:** Xử lý câu chat của người dùng, phân tích ý định, tương tác với LLM và trả về danh sách gợi ý sạch hoặc câu hỏi làm rõ.

#### Request Body:
```json
{
  "message": "món gì nóng nóng, rẻ rẻ dưới 50k, gần đây",
  "history": [
    {"role": "user", "message": "đói quá"},
    {"role": "assistant", "message": "Bạn muốn ăn món nước hay khô, ngân sách bao nhiêu?"}
  ],
  "context": {
    "location": {
      "lat": 10.776,
      "lng": 106.701
    },
    "current_time": "12:30",
    "delivery_radius_km": 5.0
  }
}
```

#### Response Body (Trường hợp Trả gợi ý - Action: `suggest`):
```json
{
  "action": "suggest",
  "suggestions": [
    {
      "restaurant_id": "res_001",
      "restaurant_name": "Bún Bò Cô Ba",
      "dish_name": "Bún Bò Huế Đặc Biệt",
      "price": 45000,
      "distance_km": 1.2,
      "eta_mins": 15,
      "reason": "Món nước nóng hổi, giá 45k hợp ví dưới 50k của bạn."
    },
    {
      "restaurant_id": "res_005",
      "restaurant_name": "Phở Gia Truyền",
      "dish_name": "Phở Bò Chín",
      "price": 40000,
      "distance_km": 0.8,
      "eta_mins": 10,
      "reason": "Phở nóng hổi, quán siêu gần (0.8km) và giá rất rẻ."
    }
  ]
}
```

#### Response Body (Trường hợp Cần làm rõ - Action: `clarify`):
```json
{
  "action": "clarify",
  "clarify_question": "Bạn thích ăn món nước (như bún, phở) hay món khô (như cơm, bánh mì) để mình tìm dễ hơn nè?"
}
```

#### Response Body (Trường hợp Lỗi/Fallback - Action: `fallback`):
```json
{
  "action": "fallback",
  "message": "Quanh bạn hiện tại không tìm thấy quán nào mở cửa khớp với ví của bạn. Bạn có muốn xem toàn bộ danh sách quán đang mở không?",
  "fallback_url": "/restaurants/all"
}
```

---

## 3. Luồng Xử Lý Chi Tiết Tại Backend

Khi nhận được Request từ Client, Backend thực hiện quy trình sau:

### Bước 1: Lọc dữ liệu thô (Pre-filtering)
*   Từ tọa độ `location` và `current_time` của user, backend truy vấn `Restaurant DB` (file `mock_restaurants.json`) để lấy ra danh sách các quán **đang mở cửa** và **nằm trong bán kính giao hàng** (ví dụ < 5km).
*   *Mục đích:* Giảm thiểu số lượng token gửi lên LLM và đảm bảo LLM chỉ chọn quán có thực tế khả dụng.

### Bước 2: Gọi LLM Service với Context & System Prompt
*   Gửi danh sách các quán khả dụng (chỉ gửi thông tin tối giản: `restaurant_id`, `name`, `dishes` [tên món, giá]) kèm theo câu chat của user lên LLM.
*   **System Prompt** ép LLM trả về cấu trúc JSON nghiêm ngặt (không chứa chữ thừa) và tuân thủ các điều kiện:
    1. Chỉ được chọn quán từ danh sách được gửi lên.
    2. Nếu ý định quá mơ hồ, trả về hành động `clarify`.
    3. Không bịa thông tin (Hallucination).

### Bước 3: Hậu kiểm tầng Code (Post-validation / Anti-hallucination)
*   Backend nhận kết quả JSON từ LLM.
*   **Hành động quan trọng:** Backend duyệt qua danh sách `suggestions` của LLM, đối chiếu chéo `restaurant_id` và `dish_name` với Database thật.
*   *Xử lý lỗi:*
    *   Nếu LLM trả về ID quán không tồn tại hoặc đã đóng cửa -> **Code tự động lọc bỏ** gợi ý lỗi đó.
    *   Nếu sau khi lọc mà số lượng gợi ý còn lại `>= 1` -> Trả về các gợi ý hợp lệ.
    *   Nếu sau khi lọc mà danh sách rỗng -> Kích hoạt **Fallback Mode** (TC-04 / TC-07) trả về danh sách gợi ý mặc định bán chạy nhất của khu vực kèm thông báo rõ ràng cho user.

---

## 4. Danh Sách Các Case Cần Xử Lý (Kịch bản Test Backend)

| Mã Case | Tình huống | Cơ chế xử lý Backend |
|---|---|---|
| **TC-01** | Happy path: Đầy đủ thông tin | LLM phân tích khớp quán -> Code kiểm tra tồn tại -> Trả về 3 gợi ý. |
| **TC-02** | Bấm refine "Khác đi" | Backend nhận lịch sử chat cũ (đã có 3 gợi ý trước đó) -> Nhồi thêm câu lệnh *"Không chọn các restaurant_id: [res_x, res_y, res_z]"* vào Prompt -> Gọi LLM lấy 3 quán mới. |
| **TC-03** | Câu chat mơ hồ | LLM phát hiện thiếu thông tin cốt lõi -> Trả JSON có `action: "clarify"` -> Backend trả thẳng câu hỏi làm rõ về Frontend. |
| **TC-07** | LLM bịa ID quán | Code nhận JSON -> Đối chiếu Database -> Phát hiện ID không tồn tại -> Lọc bỏ. |
| **TC-08** | Lạc đề (hỏi thời tiết, chính trị) | LLM nhận dạng câu hỏi ngoài lề -> Trả JSON từ chối lịch sự, kéo về chủ đề đồ ăn. |
| **TC-11** | Hỏi tư vấn y tế/dinh dưỡng | LLM chặn từ chối đưa lời khuyên chuyên khoa -> Đề xuất món ăn nhẹ bụng chung chung + khuyên người dùng hỏi bác sĩ. |
