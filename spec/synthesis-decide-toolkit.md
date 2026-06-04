# Toolkit — Từ Evidence Đến Build Slice (cập nhật theo khảo sát n=13)

Dùng sau khi nhóm đã có evidence. Mục tiêu: chốt một build slice đủ nhỏ cho Day 06.
Số liệu trong tài liệu lấy từ khảo sát nhóm (Google Form, n=13 — pilot, mẫu thuận tiện).

## 1. Gom evidence thành cụm

Gom theo **workflow/pain**, không gom theo tên feature. Ba cụm dưới đây phản ánh một insight chung: hành trình "đói → đặt được" gãy ở **hai đầu** (đầu vào + niềm tin), kéo theo hệ quả là bỏ app.

- **Cụm 1 — ĐẦU VÀO gãy: không diễn đạt được ý định mơ hồ.** 92% (12/13) thất bại khi gõ ý định tự nhiên: 8 người "chưa từng thử vì biết app sẽ không hiểu", 4 người "thử nhưng lỗi / ra quán không liên quan", chỉ 1 người thành công. Ràng buộc lặp nhiều nhất là phải xử lý đồng thời **"gần + rẻ + hợp gu"** ("quán muốn ăn thì xa/ship cao, quán gần thì không có món ưng ý").
- **Cụm 2 — NIỀM TIN gãy: không tin danh sách gợi ý sẵn.** 77% (10/13) chấm độ tin cậy mục "Gợi ý cho bạn" ≤3/5; quote: "Chạy quảng cáo ạ", "gợi ý toàn quán ở xa".
- **Cụm 3 — KIỂM SOÁT: muốn tự kiểm tra rồi mới tin.** Nhiều người chọn "có thể dùng thử xem AI gợi ý có chuẩn không" → ủng hộ hướng Augment (AI gợi ý, người quyết), không tự động đặt.

*(Hệ quả thấy được của Cụm 1 + Cụm 2: 77% (10/13) từng mở app rồi bỏ giữa chừng, không đặt gì.)*

## 2. Viết insight

```text
User [dân văn phòng bận rộn, ăn trưa một mình trên ShopeeFood, chưa biết ăn gì] không chỉ cần [thêm các danh sách gợi ý ngẫu nhiên hay quảng cáo].
Họ thật ra cần [một cách NÓI ra cơn thèm mơ hồ bằng ngôn ngữ tự nhiên, và nhận lại vài gợi ý CÓ GIẢI THÍCH, đáng tin, đúng tầm giá/khoảng cách],
vì [hành trình hỏng ở hai đầu: không diễn đạt được mong muốn (92% thất bại với search), và không tin gợi ý sẵn (77% chấm tin cậy ≤3) — nên phần lớn bỏ cuộc giữa chừng, không phải vì "chọn mãi không xong"].
```

## 3. Viết opportunity

```text
Cơ hội là dùng AI để [augment việc lọc & chọn quán bằng chat tự nhiên, giải đúng HAI ĐẦU: hiểu ý định mơ hồ + giải thích lý do để khôi phục niềm tin],
giúp user [nói "nóng, dưới 50k, gần đây" và nhận tối đa 3 gợi ý món/quán kèm dòng lý do ngắn, mở trang đặt đơn chỉ bằng một chạm],
trong khi vẫn kiểm soát [rủi ro ảo tưởng thông tin hoặc đề xuất quán xa / quán đóng cửa, bằng cách xác thực lại danh sách ở tầng code TRƯỚC khi hiển thị].
```

## 4. Chọn build slice

Build slice tốt phải qua 5 câu hỏi:

| Câu hỏi | Đạt khi | Đánh giá cho ShopeeFood Chatbot MVP |
|---|---|---|
| **User cụ thể chưa?** | Nói được ai dùng, trong bối cảnh nào. | **Đạt:** Dân văn phòng bận rộn, ăn trưa một mình, giờ nghỉ ngắn, đang mở ShopeeFood mà chưa biết ăn gì. |
| **Task đủ hẹp chưa?** | Demo được trong 3-5 phút. | **Đạt:** Chỉ 1 luồng: nhập ý định mơ hồ → nhận 3 gợi ý kèm lý do → bấm 1-chạm để mở quán. |
| **AI decision rõ chưa?** | AI gợi ý/tự làm một việc cụ thể. | **Đạt:** AI chọn tối đa 3 món/quán phù hợp nhất từ danh sách quán thật, ưu tiên đúng bán kính giao và tầm giá, kèm 1 dòng lý do. |
| **Failure path rõ chưa?** | Có một case AI không chắc hoặc sai để test. | **Đạt:** TC-03 (low-confidence → hỏi lại) và TC-07 (ảo tưởng / quán xa - quán đóng cửa → chặn ở tầng code tiền lọc). |
| **Có evidence không?** | Có bằng chứng từ self-use/review/user/competitor. | **Đạt:** Khảo sát n=13 (pilot) củng cố cả ba cụm; mạnh nhất là **92% (12/13) thất bại với search ý định tự nhiên**. Sẽ mở rộng mẫu + phỏng vấn sâu 5-7 người để chốt. |

## 5. Quyết định: giữ, giảm scope, hay đổi hướng?

| Tình huống | Quyết định | Phân tích dự án ShopeeFood Chatbot MVP |
|---|---|---|
| Evidence yếu, user mơ hồ | Dừng build sâu; quay lại research 20 phút. | Không còn ở trạng thái này: pilot n=13 đủ để giữ hướng. Vẫn nên phỏng vấn sâu 5-7 người và tăng mẫu để củng cố. |
| Ý tưởng quá rộng | Giữ domain, cắt xuống một flow. | Giữ scope tối giản: Augment chọn quán, không can thiệp đặt đơn/thanh toán. |
| AI không cần thiết | Dùng rule/manual prototype; ghi rõ vì sao không dùng AI sâu. | AI là cần thiết để hiểu ngôn ngữ tự nhiên phi cấu trúc ("nóng nóng, rẻ rẻ") — đúng pain Cụm 1 (92% thất bại với keyword search). |
| Rủi ro cao | Chọn augmentation hoặc conditional automation. | Chọn **Augmentation** vì đặt món liên quan tiền bạc & khẩu vị; evidence cũng cho thấy user muốn tự kiểm tra (Cụm 3). |
| Không demo được trong 1 ngày | Đưa phần lớn vào backlog, giữ một path nhỏ. | Bỏ thanh toán/profile dài hạn; dùng danh sách quán giả lập (mock data / Wizard-of-Oz) để demo trải nghiệm trong 1 ngày. |

## 6. Câu chốt cuối

```text
Dựa trên [khảo sát n=13: 92% không tìm được món bằng ý định tự nhiên, 77% không tin gợi ý sẵn, 77% từng bỏ app giữa chừng],
nhóm sẽ build [chatbot gợi ý món ăn — MVP 3 thẻ gợi ý + lý do + 1-chạm mở quán],
cho [dân văn phòng bận rộn ăn trưa một mình trên ShopeeFood, chưa biết ăn gì],
để giải quyết [việc không nói được mong muốn mơ hồ và không tin gợi ý sẵn, dẫn tới bỏ app không đặt],
bằng cách AI [augment ra quyết định: hiểu NL intent + chọn tối đa 3 quán CÓ THẬT kèm lý do, đúng tầm giá/khoảng cách],
và sẽ test failure path [AI ảo tưởng đề xuất món không có / quán xa - quán đóng cửa, được chặn bằng code xác thực danh sách ở tầng tiền lọc].
```

## 7. Backlog

Những thứ **không build trong Day 06**:

- Tự động đặt đơn / thanh toán (Automate order).
- Đặt đơn nhóm, chia tiền.
- Gợi ý dinh dưỡng/y tế chuyên sâu.
- Lưu trữ lịch sử khẩu vị dài hạn (trí nhớ đa phiên).
- Tìm kiếm bằng giọng nói, hình ảnh hoặc đa ngôn ngữ.
- Tích hợp dữ liệu quán thật của ShopeeFood (Day 06 dùng mock data).
