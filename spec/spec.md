# SPEC Sản Phẩm: Chatbot Gợi Ý Món Ăn ShopeeFood (MVP)
---

## 1. Bằng chứng (Evidence)

Để giải quyết một cách thực chất vấn đề của người dùng, nhóm đã thu thập bằng chứng từ cả trải nghiệm trực tiếp và khảo sát người dùng thực tế.

### A. Trải nghiệm trực tiếp (Self-Use)
Nhóm tự dùng ứng dụng ShopeeFood hiện tại và phát hiện hai điểm gãy lớn:
1.  **Gợi ý mặc định bị phớt lờ:** Danh mục "Gợi ý cho bạn" hiển thị hoàn toàn tĩnh, mang tính quảng cáo tài trợ cao và không bám sát nhu cầu tức thời tại thời điểm đó (thèm món nước/nóng, giá rẻ, gần đây). Điều này dẫn đến việc người dùng mất niềm tin và bỏ qua hoàn toàn mục này.
    
    *Minh họa điểm nghẽn gợi ý mặc định:*
    <img width="725" height="367" alt="Lỗi gợi ý mặc định" src="https://github.com/user-attachments/assets/b9d61623-d40d-4c67-b76a-063894ec2cdc" />
    
2.  **Bộ lọc tìm kiếm cứng nhắc:** Thanh tìm kiếm của app chỉ nhận diện từ khóa chính xác (tên món, tên quán). Khi người dùng nhập ý định tự nhiên phức tạp hoặc mơ hồ (ví dụ: "dưới 50k, không cay, ăn nhẹ"), app không hiểu và trả về kết quả lỗi hoặc không liên quan.
    
    *Minh họa điểm nghẽn tìm kiếm:*
    <img width="712" height="315" alt="Lỗi search keyword" src="https://github.com/user-attachments/assets/ecce1fde-f721-448c-a03e-4f12169708c8" />

### B. Khảo sát thực tế ngoài nhóm ($N=15$)
Khảo sát được thực hiện trên đối tượng dân văn phòng và sinh viên thường đặt đồ ăn trưa (trong đó 10/15 là dân văn phòng thực tế):
*   **P1 — Tê liệt lựa chọn (Choice paralysis):** Có tới **13/15 người dùng mất từ 5-20+ phút** để chọn món ăn trưa. Đáng chú ý, **12/15 người thỉnh thoảng hoặc rất thường xuyên thoát app** mà không đặt món nào vì nản chí trước quá nhiều lựa chọn. Rào cản lớn nhất khi quyết định là: quán muốn ăn thì xa/ship cao, quán gần thì không có món hợp khẩu vị.
*   **P2 — Sự hoài nghi đối với gợi ý:** Chỉ **3/15 người thường xuyên xem gợi ý**. Điểm tin cậy trung bình của mục gợi ý đạt thấp kỷ lục: **2.93/5**. Người dùng coi gợi ý mặc định là "chạy quảng cáo" hoặc "quán ở xa".
*   **P3 — Sự thất bại của thanh tìm kiếm hiện tại:** **10/15 người chưa từng gõ câu mô tả tự nhiên** vì nghĩ app sẽ không hiểu; **4/15 người đã thử gõ nhưng thất bại**. 
*   **Cơ hội mở ra:** **15/15 người dùng sẵn sàng hoặc muốn dùng thử** một chatbot AI gợi ý để hỗ trợ chọn món ăn nhanh hơn.

### C. Đối chiếu đối thủ & Mô hình tương tự (Competitor & Analog)
*   **Spotify "Made For You" / Netflix:** Đề xuất số lượng giới hạn kèm dòng giải thích lý do cụ thể ("vì bạn đã nghe/xem X") -> Áp dụng: Giới hạn tối đa 3 gợi ý kèm 1 dòng lý do ngắn gọn (< 12 từ) để khôi phục lòng tin của người dùng.
*   **Domino's "Dom" / Starbucks Barista:** Chatbot nhận order bằng ngôn ngữ tự nhiên -> Áp dụng: Nhận intent tự nhiên, nhưng chỉ giữ vai trò **Augment (gợi ý)** chứ không tự động đặt đơn (Automate) để tránh rủi ro tài chính và khẩu vị.
*   **ChatGPT / Trợ lý LLM:** Hiểu ý định mơ hồ và clarify khi thiếu thông tin -> Áp dụng: Xây dựng cơ chế clarify khi chatbot nhận đầu vào quá mơ hồ.

---

## 2. Lát cắt để build (Build Slice)

> Cho **dân văn phòng bận rộn đặt cơm trưa cá nhân (11h30 - 12h00) chưa biết ăn gì**, prototype sử dụng AI để **hỗ trợ ra quyết định (Augment)** bằng cách cung cấp **3 gợi ý quán/món thực tế đang mở cửa gần đó kèm giá, khoảng cách và 1 dòng lý do ngắn gọn**, đồng thời xử lý các tình huống rủi ro (lạc đề, low-confidence, quán đóng cửa) bằng cách **yêu cầu làm rõ, từ chối khéo hoặc fallback về luồng gốc**.

---

## 3. AI Product Canvas

| Ô Canvas | Nội dung chi tiết |
|---|---|
| **Value**<br>*(Giá trị)* | - **Đối tượng:** Dân văn phòng ăn trưa một mình, nghỉ trưa ngắn (45-60 phút), ngân sách cố định (<60k).<br>- **Nỗi đau:** Choice paralysis (mất 5-20+ phút lướt app rồi thoát do quá tải thông tin và nghi ngờ quảng cáo).<br>- **Giải pháp AI:** Đọc hiểu ý định mơ hồ chứa nhiều ràng buộc cùng lúc (rẻ, gần, ngon) và đề xuất đúng 3 quán kèm dòng lý do thuyết phục để ra quyết định trong <2 phút. |
| **Trust**<br>*(Niềm tin)* | - **Cách phát hiện sai sót:** Người dùng thấy quán gợi ý không đúng ý định hoặc quán bị đóng cửa/link hỏng.<br>- **Cách khắc phục:** Cung cấp nút refine nhanh ("Khác đi", "Rẻ hơn", "Gần hơn") và nút fallback mở danh sách đầy đủ gốc của ShopeeFood.<br>- **Chặn rủi ro:** Backend kiểm tra chéo ID quán do LLM đề xuất với dữ liệu quán thực tế trước khi hiển thị để loại bỏ hoàn toàn ID ảo. |
| **Feasibility**<br>*(Tính khả thi)* | - **Rủi ro lớn nhất:** LLM ảo tưởng đề xuất món/quán không có thật hoặc đã đóng cửa.<br>- **Giải pháp:** Tiền lọc dữ liệu thực tế (bán kính <3km, giá <60k) rồi mới đưa cho LLM xếp hạng và viết lý do.<br>- **Ngưỡng dừng:** Giới hạn tối đa 3 lần bấm "Khác đi", sau đó chatbot đề xuất người dùng nhập lại yêu cầu cụ thể hơn hoặc chuyển sang danh mục khuyến mãi chung. |
| **Tín hiệu học**<br>*(Feedback loop)* | - Khi người dùng bấm refine hoặc chọn đặt quán nào, hệ thống log lại hành vi để học xem tiêu chí nào (khoảng cách, giá, loại món) được ưu tiên cao hơn.<br>- Ghi nhận các câu chat chỉnh sửa/lạc đề của người dùng làm tập test để tinh chỉnh prompt hệ thống. |

---

## 4. Tăng năng lực hay tự động hóa (Augmentation vs Automation)

Nhóm quyết định chọn hướng tiếp cận **Augmentation (Tăng năng lực)**: AI chỉ đóng vai trò gợi ý, chọn lọc và giải thích lý do; con người (người dùng) giữ quyền quyết định cuối cùng ở bước bấm mở quán và đặt đơn.

**Lý do lựa chọn:**
1.  **Khẩu vị & Tài chính:** Đặt đồ ăn liên quan trực tiếp đến tiền bạc và khẩu vị cá nhân rất nhạy cảm. AI tự động đặt món (Automation) chứa rủi ro rất cao nếu AI chọn sai món dễ gây dị ứng hoặc chọn quán quá xa làm trễ giờ làm của khách hàng.
2.  **Sự linh hoạt:** Khẩu vị con người thay đổi rất thất thường theo ngày hoặc theo tâm trạng. Phương án Augmentation hỗ trợ người dùng lọc bớt thông tin gây nhiễu nhưng vẫn giữ cho họ quyền kiểm soát tuyệt đối ở bước ra quyết định.
3.  **Nhu cầu kiểm soát của người dùng:** Dữ liệu khảo sát thực tế (Cụm 3) cho thấy người dùng muốn tự mình kiểm tra độ chính xác của AI gợi ý trước khi tin tưởng đặt hàng (Human-in-the-loop).

---

## 5. Bốn đường đi của trải nghiệm (Four Paths)

| Đường đi | Mô tả trải nghiệm | Cách hệ thống xử lý |
|---|---|---|
| **Đường thuận**<br>*(Happy Path)* | Người dùng nhập ý định rõ ràng (ví dụ: "nóng, dưới 50k, gần đây"). | Trả về tối đa 3 gợi ý quán thực tế kèm lý do ngắn gọn (<= 12 từ) và nút bấm 1-chạm mở quán. Cho phép refine 1 lần ("Rẻ hơn", "Khác đi"). |
| **Khi AI không chắc**<br>*(Low-confidence)* | Người dùng nhập câu quá mơ hồ (ví dụ: "ăn gì bây giờ", "đói quá"). | Chatbot hỏi lại đúng 1 câu clarify để thu hẹp lựa chọn ("Bạn muốn ăn cơm trưa chắc bụng, bún phở nóng hổi hay món ăn nhẹ nè?"). Nếu vẫn mơ hồ lần 2, đưa ra 3 gợi ý phổ biến nhất quanh đó kèm nhãn "Gợi ý chung". |
| **Khi AI sai**<br>*(Failure Path)* | 1. Thiếu dữ liệu/quán đóng cửa.<br>2. Ngân sách bất khả thi (sushi 15k).<br>3. LLM ảo tưởng ID quán. | - Nếu thiếu dữ liệu: Báo rõ lý do, gợi ý đổi địa chỉ/đợi giờ mở, hoặc hiển thị nút mở danh sách đầy đủ.<br>- Nếu ngân sách bất khả thi: Báo "quanh bạn chưa có món trong tầm giá này", gợi ý nới giá.<br>- Nếu ảo tưởng: Tầng backend lọc bỏ `restaurant_id` không tồn tại ở tầng code trước khi render. |
| **Khi người dùng sửa**<br>*(Correction Path)* | - Bấm refine nhiều lần.<br>- Nhập câu hỏi lạc đề.<br>- Hỏi về y tế/sức khỏe. | - Refine "Khác đi" quá 3 lần: Đề nghị nhập lại ý định.<br>- Lạc đề: Từ chối nhẹ, kéo về ăn uống ("Mình chỉ giúp chọn món thôi nha — bạn đang muốn ăn gì?").<br>- Hỏi y tế: Từ chối khéo, đề xuất món nhẹ bụng chung chung + khuyên hỏi bác sĩ. |

---

## 6. Những kiểu lỗi đáng lo nhất (Dangerous Failure Modes)

1.  **Ảo tưởng (Hallucination) về quán và món ăn (Không tồn tại trong DB thực tế):**
    *   *Khi nào xuất hiện:* Khi prompt lỏng lẻo hoặc LLM cố gắng đáp ứng một yêu cầu quá đặc biệt của user mà dữ liệu mock không có.
    *   *Hậu quả:* Người dùng bấm vào thẻ gợi ý bị lỗi đường dẫn hỏng (404), gây trải nghiệm cực kỳ tệ và mất uy tín app.
    *   *Prototype xử lý:* Backend thiết lập chế độ so khớp cứng (hard matching). LLM chỉ được phép trả về JSON có cấu trúc chứa các ID nằm trong danh sách DB được cung cấp sẵn. Tầng code backend sẽ lọc lại một lần nữa trước khi hiển thị ra giao diện.
2.  **Vi phạm ràng buộc cứng về Khoảng cách/Phí ship:**
    *   *Khi nào xuất hiện:* LLM không thể tính toán khoảng cách địa lý một cách chính xác qua prompt văn bản.
    *   *Hậu quả:* Đề xuất quán quá xa (> 5km), phí ship cao làm người dùng tức giận thoát app (đúng painpoint P1).
    *   *Prototype xử lý:* Tiền lọc (pre-filter) ở backend để loại bỏ tất cả các quán nằm ngoài bán kính quy định trước khi nạp dữ liệu vào context của LLM. LLM chỉ xếp hạng và viết lý do dựa trên danh sách đã được đảm bảo về khoảng cách.
3.  **Hỏi về tư vấn y tế/dinh dưỡng nghiêm trọng:**
    *   *Khi nào xuất hiện:* User hỏi "bị đau dạ dày/đang uống thuốc X nên ăn gì?".
    *   *Hậu quả:* Đề xuất món ăn không phù hợp gây ảnh hưởng sức khỏe, vi phạm trách nhiệm pháp lý.
    *   *Prototype xử lý:* Prompt hệ thống hướng dẫn LLM từ chối đưa ra lời khuyên y khoa chuyên sâu. Đề xuất các món ăn thanh đạm chung chung (cháo, súp) và khuyên người dùng tham khảo ý kiến bác sĩ.

---

## 7. Kế hoạch kiểm thử & Bằng chứng Demo

Để chứng minh được hiệu quả trong buổi demo, nhóm chuẩn bị sẵn bộ dữ liệu kiểm thử gồm các trường hợp sau:

*   **TC-01 (Happy Path):** Nhập "ăn trưa cơm sườn dưới 45k gần đây".  
    *Kỳ vọng:* Trả về 3 quán cơm sườn cách < 2km, có giá món dưới 45k kèm lý do như "Quán gần nhất (0.8km), giá chỉ 40k".
*   **TC-02 (Low-Confidence/Clarification):** Nhập "ăn gì bây giờ".  
    *Kỳ vọng:* Hệ thống hỏi lại để thu hẹp lựa chọn.
*   **TC-03 (Constraint Conflict):** Nhập "ăn phở bò 15k gần đây".  
    *Kỳ vọng:* Trả về thông báo không tìm thấy phở bò 15k, đề xuất các món ăn vặt 15k hoặc quán phở giá từ 35k gần đó.
*   **TC-04 (Out of Domain/Lạc đề):** Nhập "hôm nay thời tiết Hà Nội thế nào?".  
    *Kỳ vọng:* Chatbot từ chối khéo léo và hỏi người dùng muốn ăn bún hay cơm.
*   **TC-05 (Hallucination Test):** Cố tình hỏi một món siêu dị để ép LLM tự chế quán.  
    *Kỳ vọng:* Backend lọc và trả về thông báo lỗi thân thiện thay vì hiển thị thẻ quán hỏng.

---

## 8. Phân công thành viên (Naughty Girls)

| Thành viên | Vai trò | Công việc cụ thể | Bằng chứng đóng góp |
|---|---|---|---|
| **Nhật Anh** | UX Researcher | Thu thập dữ liệu khảo sát, phân tích insights người dùng, viết báo cáo evidence và đối chiếu đối thủ. | Bản kết quả khảo sát thực tế, tài liệu phân tích đối thủ cạnh tranh. |
| **Ngọc** | QA / Test Engineer | Thiết kế và chạy thử 12 testcases, phát hiện lỗi logic, viết bộ xử lý lỗi fallback ở backend. | Bảng kết quả kiểm thử testcases, code xử lý fallback logic. |
| **Minh** | Frontend Developer | Thiết kế giao diện chatbot trên web/mobile, tối ưu hóa các micro-interactions, tích hợp nút 1-chạm mở quán. | Mã nguồn giao diện chat, hiệu ứng gợi ý và chuyển trang mượt mà. |
| **Huy** | Backend & AI Engineer | Thiết kế database mock, xây dựng API kết nối LLM, viết prompt system và thực hiện tiền lọc dữ liệu. | Mã nguồn backend, cấu trúc prompt hệ thống và DB mock quán ăn. |
| **Nam** | Product Owner / Demo | Viết kịch bản demo, chuẩn bị slide thuyết trình, quay video demo và điều phối dự án. | Kịch bản demo, slide trình chiếu và video demo các luồng sản phẩm. |
