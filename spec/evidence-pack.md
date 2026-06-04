# Evidence Pack — Chatbot gợi ý món ăn cho ShopeeFood

Nộp kèm thin SPEC cuối Day 05.

## 1. Nhóm và track

**Tên nhóm:** Naughty girls

**Track:** Food & Local Delivery

**Product/app đã chọn:** ShopeeFood  

**Build slice đang nghĩ:** Chatbot gợi ý món ăn / quán gần đây từ ý định mô tả bằng ngôn ngữ tự nhiên (vd: "đói, muốn món nóng dưới 50k gần đây"). AI trả về tối đa 3 gợi ý có thật kèm lý do ngắn; người dùng tự bấm 1-chạm để mở quán và đặt — AI gợi ý, người quyết (Augment).

## 2. Self-use evidence

Nhóm tự dùng app/workflow và ghi lại điểm gãy.

| Observation | Screenshot/link | Path liên quan | Điều học được |
|---|---|---|---|
| Danh sách "Gợi ý cho bạn" hiện tại không khớp với ý định mơ hồ của người dùng (ví dụ: muốn ăn món gì nóng, rẻ, gần đây). | <img width="725" height="367" alt="image" src="https://github.com/user-attachments/assets/b9d61623-d40d-4c67-b76a-063894ec2cdc" /> | Happy / Low-confidence | Đề xuất mặc định quá chung chung hoặc giống quảng cáo, làm người dùng mất lòng tin và mất thời gian lướt vô định. |
| Tính năng Search chỉ tìm theo keyword cứng, không hiểu ý định phức tạp/mơ hồ như "dưới 50k, không cay, ăn nhẹ". | <img width="712" height="315" alt="image" src="https://github.com/user-attachments/assets/ecce1fde-f721-448c-a03e-4f12169708c8" /> | Happy / Low-confidence | Cần cơ chế xử lý ngôn ngữ tự nhiên để hiểu ý định phi cấu trúc và kết hợp ngữ cảnh thực tế (vị trí, thời gian). |

## 3. User / review / social evidence

Nguồn có thể là review App Store/Play, group, comment, phỏng vấn nhanh, hoặc nguồn public khác.

| Quote / review / observation | Nguồn | User là ai? | Pain/failure mode |
|---|---|---|---|
| "Chạy quảng cáo ạ" (chấm độ tin cậy mục Gợi ý 1/5) | Khảo sát nhóm (Google Form, n=13) | NVVP, đặt 3–4 lần/tuần | P2 — Không tin mục gợi ý, coi là quảng cáo tài trợ |
| "Có khi gợi ý món thích ăn, có khi gợi ý món không thích" (tin cậy 3/5) | Khảo sát nhóm (n=13) | Sinh viên, đặt hằng ngày | P2 — Gợi ý thiếu nhất quán, không bám gu |
| "Vì gợi ý toàn quán ở xa" (tin cậy 4/5) | Khảo sát nhóm (n=13) | Sinh viên, đặt 3–4 lần/tuần | P2 — Gợi ý không tính bán kính giao |
| "Quán xa, nhiều món không hợp ý" | Khảo sát nhóm (n=13) | NVVP, đặt 1–2 lần/tuần | P2 — Gợi ý vừa xa vừa lệch gu |
| 10/13 người "thỉnh thoảng" đến "rất thường xuyên" mở app rồi thoát ra không đặt | Khảo sát nhóm, tổng hợp (n=13) | Hỗn hợp NVVP/SV | P1 — Bỏ giữa chừng do quá tải lựa chọn |
| 12/13 không thỏa mãn khi gõ câu mô tả tự nhiên (8 chưa thử vì nghĩ app không hiểu, 4 thử bị lỗi/lệch); chỉ 1 ra đúng | Khảo sát nhóm, tổng hợp (n=13) | Hỗn hợp NVVP/SV | P3 — Search keyword không xử lý được ý định mơ hồ |
| Lý do thoát app phổ biến nhất: "quán muốn ăn thì xa/ship cao, quán gần không có món ưng" và "quá nhiều quán, không biết chọn" | Khảo sát nhóm, tổng hợp (n=13) | Hỗn hợp NVVP/SV | P1 + ràng buộc khoảng cách/giá |

```text
Nguồn: khảo sát của nhóm (Google Form, n=13, mẫu thuận tiện, dữ liệu pilot — đang tiếp tục thu). Đây là phản hồi từ người dùng thật ngoài nhóm, không phải giả định. Trước M1 Day 06 sẽ bổ sung review App Store/CH Play, comment group Facebook và phỏng vấn sâu 5–7 người.
```

## 4. Competitor / analog evidence

| App / mô hình tham khảo | Họ xử lý task này thế nào? | Pattern học được | Có áp dụng trong 1 ngày không? |
|---|---|---|---|
| **Spotify "Made For You" / Netflix "Because you watched"** — analog đề xuất | Đề xuất số lượng giới hạn, kèm lý do ("vì bạn đã nghe/xem X") | Curated top-N + giải thích lý do → tăng niềm tin, bớt cảm giác quảng cáo (đúng pain P2) | CÓ — bắt LLM trả tối đa 3 gợi ý + 1 dòng lý do là việc của prompt |
| **Domino's "Dom" / Starbucks "My Starbucks Barista"** — analog bot đặt món | Bot nhận order bằng ngôn ngữ tự nhiên/giọng nói qua Messenger hoặc trong app ([Botpress](https://botpress.com/blog/chatbot-for-restaurants)), nhớ "món quen" | Hội thoại thay menu; "đặt món quen" = predictive reorder. Lưu ý: họ là 1 thương hiệu, đơn giản hơn marketplace nhiều quán | Một phần — luồng chat nhận intent: CÓ; tự đặt/thanh toán: KHÔNG (mình giữ Augment) |
| **ChatGPT / trợ lý LLM tổng quát** — chính là "động cơ" | Mô tả mơ hồ → LLM gợi ý + lý do, hỏi lại khi thiếu thông tin | Cơ chế clarify khi low-confidence (đúng SPEC). Nhược điểm: không biết quán nào CÓ THẬT quanh bạn | CÓ — đây chính là cách dựng MVP: LLM + feed danh sách quán thật + ràng buộc chỉ chọn trong danh sách |
| **ShopeeFood "Gợi ý cho bạn" hiện tại** — baseline cần vượt | Danh mục gợi ý tĩnh ở trang chủ, không nhận mô tả tự nhiên, không nêu lý do | (Phản diện) Bị xem như quảng cáo, ít tin — khảo sát: 10/13 chấm tin cậy ≤3/5 → khoảng trống để khác biệt | N/A (mốc so sánh) |
## 5. Evidence -> Insight

```text
Evidence nổi bật nhất (xếp theo độ mạnh):
1. ĐẦU VÀO hỏng — 92% (12/13) không diễn đạt được ý định mô tả tự nhiên: 8 người không buồn thử vì "biết app sẽ không hiểu", 4 người thử thì lỗi / ra quán không liên quan, chỉ 1 người thành công. (P3)
2. NIỀM TIN hỏng — 77% (10/13) chấm độ tin cậy mục "Gợi ý cho bạn" ≤3/5; quote: "Chạy quảng cáo ạ", "gợi ý toàn quán ở xa". (P2)
3. HỆ QUẢ — 77% (10/13) từng mở app rồi bỏ giữa chừng, không đặt. (P1)
4. Rào cản lặp nhiều nhất khi bỏ đơn: "quán muốn ăn thì xa/ship cao, quán gần thì không có món ưng ý" → khoảng cách + giá + khẩu vị phải xử lý CÙNG LÚC.
(Nguồn: khảo sát nhóm, Google Form, n=13 — pilot, mẫu thuận tiện.)

Insight:
Nhìn bề mặt giống bài toán "quá nhiều lựa chọn" (choice paralysis – P1). Nhưng evidence chỉ ra điểm gãy thật nằm ở HAI ĐẦU của hành trình, không phải khúc giữa:
- Đầu vào: user không có cách NÓI ra cơn thèm mơ hồ nhiều ràng buộc cùng lúc ("gần + rẻ + hợp gu") — search keyword không hiểu.
- Niềm tin: khi app có gợi ý sẵn, user lại KHÔNG TIN, coi như quảng cáo tài trợ.
=> Họ không "chọn mãi không xong"; họ bỏ cuộc vì vừa không diễn đạt được mong muốn, vừa không tin thứ được gợi ý.

Opportunity:
AI giải đúng hai đầu đó: (1) đọc hiểu ý định mơ hồ bằng ngôn ngữ tự nhiên + ngữ cảnh vị trí/thời gian, ưu tiên đúng bán kính giao và tầm giá; (2) trả tối đa 3 gợi ý kèm DÒNG LÝ DO minh bạch để khôi phục niềm tin (chống cảm giác "quảng cáo"). User vẫn tự bấm chọn — Augment
```

## 6. Evidence đổi SPEC như thế nào?

- [x] Đổi user chính.          (Thu hẹp: dân văn phòng bận rộn, ăn trưa một mình, giờ nghỉ ngắn)
- [x] Đổi pain statement.       (Cập nhật số liệu thực tế + bổ sung rào cản khoảng cách/giá)
- [ ] Đổi build slice.
- [ ] Đổi Auto/Aug decision.
- [ ] Đổi 4 paths.
- [x] Đổi failure mode.         (Tập trung chặn gợi ý quán xa / quán đóng cửa ở tầng code tiền lọc)
- [x] Đổi owner/test plan.      (Phân chia công việc theo vai trò thực tế)

*(Lưu ý: Đánh dấu [x] vào các mục tương ứng sau khi có kết quả research thực tế)*

Ghi rõ 1-2 thay đổi quan trọng:

```text
Trước evidence, nhóm định...
Xây chatbot gợi ý món cho người đặt đồ ăn nói chung, dựa trên giả thuyết người dùng bị tê liệt lựa chọn (P1) và không tìm được món theo ý định mơ hồ (P3).

Sau evidence, nhóm đổi thành...
(1) Thu hẹp đối tượng chính: dân văn phòng bận rộn, ăn trưa một mình trong khung nghỉ ngắn.
(2) Cập nhật pain statement theo số liệu: 77% (10/13) từng mở app rồi bỏ giữa chừng không đặt; 92% (12/13) thất bại khi gõ ý định tự nhiên vào search; và bổ sung rào cản "quán xa/ship cao – quán gần không hợp gu" làm ràng buộc cốt lõi.
(3) Thắt chặt failure mode: bắt buộc chặn gợi ý quán xa / quán đã đóng ngay ở tầng code tiền lọc, không để LLM tự quyết.

Lý do:
Kết quả khảo sát chỉ ra khoảng cách địa lý và giá cả là rào cản bỏ đơn phổ biến nhất, nên đây phải là ràng buộc chatbot xử lý đồng thời với khẩu vị. Phần lớn người trả lời là dân văn phòng, nên thu hẹp persona giúp MVP sắc nét hơn. Quyết định Augment giữ nguyên (nhiều người nói "dùng thử xem AI có chuẩn không" → muốn kiểm soát, không muốn tự động).
```
