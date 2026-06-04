# Thin SPEC — Chatbot gợi ý món ăn cho ShopeeFood (MVP)

Thin SPEC không phải PRD đầy đủ. Đây là bản cam kết đủ rõ để sáng Day 06 nhóm build ngay.

## 1. Track, product/app và user

**Track:** AI Product Design (Mini-Hackathon)  
**Product/app thật:** ShopeeFood  
**User cụ thể:** Dân văn phòng bận rộn đặt cơm trưa cá nhân trong khung giờ 11h30-12h00, áp lực thời gian nghỉ trưa ngắn (45-60 phút), ngân sách cố định (<60k) và ăn một mình.  
**Nhóm có phải user thật không? Nếu không, khác ở đâu?** Có, 10/15 đối tượng khảo sát là dân văn phòng thực tế, có hành vi đặt cơm trưa cá nhân và thời gian nghỉ trưa hạn chế từ 45-60 phút.  

## 2. Evidence summary

| Evidence | Nguồn | User/pain nói lên điều gì? | SPEC phải đổi gì? |
|---|---|---|---|
| **P1:** Tê liệt vì quá nhiều lựa chọn | Khảo sát thực tế ($N=15$) | 13/15 người dùng mất từ 5-20+ phút để chọn món; 12/15 người thỉnh thoảng/rất thường xuyên thoát app không đặt gì vì nản chí trước các lựa chọn. | Giới hạn kết quả gợi ý tối đa 3 quán phù hợp nhất. AI phải ưu tiên tiền lọc quán gần và giá rẻ trước (do lý do thoát app hàng đầu là quán xa/phí ship cao). |
| **P2:** Gợi ý tối nghĩa / như quảng cáo | Khảo sát thực tế ($N=15$) | Chỉ 3/15 người dùng thường xuyên xem gợi ý. Điểm tin cậy trung bình là 2.93/5. Người dùng coi gợi ý mặc định là "chạy quảng cáo", "quán ở xa". | Mỗi gợi ý phải có thêm 1 dòng lý do thuyết phục ngắn gọn (< 12 từ) giải thích lý do quán này được chọn (phù hợp khoảng cách, giá cả). |
| **P3:** Không có cách diễn đạt ý định mơ hồ | Khảo sát thực tế ($N=15$) | 10/15 người chưa từng gõ từ khóa tự nhiên vì nghĩ app không hiểu; 4/15 người thử gõ nhưng thất bại. 15/15 người sẵn sàng hoặc muốn dùng thử chatbot AI gợi ý. | Cung cấp giao diện chat tự nhiên để nhập ý định mơ hồ và dùng AI xử lý, hiển thị 3 thẻ gợi ý rõ ràng kèm nút 1-chạm mở quán. |

## 3. Pain statement

```text
User [dân văn phòng bận rộn đặt cơm trưa cá nhân] đang gặp khó ở [bước tìm kiếm và quyết định chọn món trong khung giờ nghỉ trưa ngắn],
vì [danh sách "Gợi ý cho bạn" thiếu tin cậy/nghi chạy quảng cáo và ô search chỉ nhận keyword cứng],
dẫn tới [họ tốn nhiều thời gian lướt mỏi mắt (13/15 mất >5-20+ phút) và đôi khi bỏ cuộc thoát app không đặt hàng nữa (12/15)].
Bằng chứng chính là [kết quả khảo sát 15 người dùng tại file Khao_Sat_Hanh_Vi_Dat_Do_An_Trua.md: 12/15 người gặp choice paralysis và thoát app, điểm tin cậy gợi ý đạt 2.93/5, 14/15 tìm kiếm thất bại khi nhập ý định tự nhiên].
```

## 4. Build slice

```text
Cho [người dùng đang mở ShopeeFood nhưng chưa biết ăn gì] đang [muốn tìm món ăn nhanh chóng phù hợp nhu cầu mơ hồ],
prototype sẽ dùng AI để [augment việc chọn món/quán],
tạo ra [3 thẻ gợi ý quán/món thực tế đang mở cửa kèm giá, khoảng cách và 1 dòng giải thích lý do ngắn gọn],
và xử lý [các lỗi rủi ro như low-confidence, lạc đề, hoặc không có quán] bằng [yêu cầu làm rõ (clarify), từ chối lịch sự và fallback về gợi ý chung hoặc luồng gốc của app].
```

## 5. Auto/Aug decision

Chọn một:

- [x] **Augmentation:** AI gợi ý/draft/phân loại, user quyết cuối.
- [ ] **Conditional automation:** AI tự làm trong case hẹp; case mơ hồ/rủi ro chuyển người.
- [ ] **Automation:** AI tự quyết và tự hành động.

**Lý do chọn:**
- Đặt đồ ăn gắn liền với khẩu vị cá nhân, chi tiêu tiền nong và lòng tin. Nếu AI tự đặt (Automate) sai sẽ làm mất lòng tin nghiêm trọng của người dùng.
- Khẩu vị cá nhân rất đa dạng và thay đổi liên tục theo tâm trạng/ngữ cảnh mà AI khó đoán định chính xác hoàn toàn.
- Phương án Augmentation cho phép sai số nhất định: AI chỉ cần gợi ý đủ tốt để hỗ trợ người dùng đưa ra quyết định cuối cùng một cách nhanh chóng và tự tin nhất.

**Human role:** decider

## 6. Four paths

| Path | Prototype phải thể hiện gì? |
|---|---|
| **Happy** | Người dùng nhập ý định rõ ràng (ví dụ: "nóng, dưới 50k, gần đây"). Hệ thống trả về tối đa 3 gợi ý quán thực tế kèm lý do ngắn gọn (<= 12 từ) và nút bấm 1-chạm mở quán. Cho phép refine 1 lần ("Rẻ hơn", "Khác đi"). |
| **Low-confidence** | Người dùng nhập câu quá mơ hồ (ví dụ: "đặt gì giờ"). AI không đoán bừa mà hỏi lại đúng 1 câu làm rõ. Nếu người dùng vẫn mơ hồ lần 2, đưa ra 3 gợi ý phổ biến nhất quanh đó kèm ghi chú "gợi ý chung". |
| **Failure** | Gồm các case lỗi hệ thống/dữ liệu: <br>1. Thiếu dữ liệu/quán đóng cửa (TC-04, TC-05): Báo rõ lý do, gợi ý đổi địa chỉ/đợi giờ mở, hoặc hiển thị nút mở danh sách đầy đủ. <br>2. Ngân sách bất khả thi (TC-06): Báo "quanh bạn chưa có món trong tầm giá này", gợi ý nới giá. <br>3. LLM ảo tưởng (TC-07): Lọc bỏ `restaurant_id` không tồn tại ở tầng code. |
| **Correction** | Xử lý khi user sửa đổi hoặc lạc đề:<br>1. Bấm refine "Khác đi" nhiều lần: Đổi gợi ý mỗi lần, sau 3 lần đề nghị nhập lại ý định.<br>2. Lạc đề (TC-08): Từ chối nhẹ, kéo về ăn uống ("Mình chỉ giúp chọn món thôi nha — bạn đang muốn ăn gì?").<br>3. Hỏi y tế (TC-11): Từ chối khéo, đề xuất món nhẹ bụng chung chung + khuyên hỏi bác sĩ. |

## 7. Failure mode nguy hiểm nhất

```text
Nếu user [gửi ý định và kích hoạt AI gợi ý quán],
AI có thể [ảo tưởng (hallucination) ra các món ăn hoặc restaurant_id không có thật trong cơ sở dữ liệu],
hậu quả là [người dùng bấm vào thẻ gợi ý bị lỗi hệ thống (link hỏng, lỗi 404) hoặc dẫn tới quán đã đóng cửa/ngoài phạm vi giao, gây mất uy tín dịch vụ].
Prototype sẽ xử lý bằng [lọc ở tầng code: sau khi nhận JSON từ LLM, đối chiếu chéo danh sách thực tế của hệ thống; loại bỏ ngay các ID ảo; nếu danh sách sau lọc trống thì kích hoạt fallback ít dữ liệu (TC-04)].
```
Owner kiểm thử path này là Ngọc

## 8. Owner plan cho sáng Day 06

| Thành viên | Việc phụ trách | Bằng chứng cần có trong repo |
|---|---|---|
| Nhật Anh | Research / evidence | Bảng kết quả khảo sát thực tế |
| Nhật Anh và Ngọc | SPEC | Hoàn thiện file `thin-spec.md` và `evidence-pack.md`. |
| Minh & Huy & Nam  | Prototype | Source code giao diện chat gợi ý, prompt system và danh sách quán mẫu giả lập (10-20 quán). |
| Ngọc | Test / failure path | Bảng chạy 12 testcase và code xử lý các kịch bản fallback. |
| Cả nhóm | Demo script / repo | Tài liệu kịch bản demo và video quay thử các luồng. |
