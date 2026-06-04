# Hướng Dẫn Xem Sơ Đồ Hệ Thống (PlantUML)

Thư mục này chứa các file đặc tả sơ đồ hệ thống dưới dạng code **PlantUML** giúp bạn dễ dàng hình dung và thiết kế cấu trúc backend trước khi bắt đầu code.

---

## 1. Danh sách các file sơ đồ
*   [backend-sequence.puml](file:///d:/Lab_AI_Thuc_Chien/Group_Project/2A202600728_BuiTuanMinh_Day05/04-backend-docs/backend-sequence.puml): Sơ đồ tuần tự (Sequence Diagram) mô tả chi tiết luồng chạy của dữ liệu giữa Người dùng, Frontend, API Controller, DB và dịch vụ AI (LLM). Sơ đồ chỉ rõ 3 kịch bản:
    1. **Happy Path:** Phân tích nhu cầu -> Gợi ý 3 món thành công -> Chuyển hướng đặt hàng.
    2. **Low-Confidence:** Ý định mơ hồ -> Chatbot tự động hỏi lại để thu hẹp phạm vi.
    3. **Anti-Hallucination:** Lọc bỏ các quán ảo do LLM bịa ra ở tầng code.
*   [architecture-overview.puml](file:///d:/Lab_AI_Thuc_Chien/Group_Project/2A202600728_BuiTuanMinh_Day05/04-backend-docs/architecture-overview.puml): Sơ đồ thành phần (Component Diagram) thể hiện mối quan hệ và sự tương tác giữa các thành phần phần mềm (Client App, API Controller, LLM Client Service, Local JSON DB, và Gemini API).

---

## 2. Cách hiển thị và xem sơ đồ trực quan (Rendering)

Bạn có thể hiển thị các file `.puml` này thành hình ảnh trực quan bằng một trong các cách sau:

### Cách 1: Sử dụng Extension "PlantUML" trên VS Code (Khuyên dùng)
1. Cài đặt extension **PlantUML** (của *jebbs*) trong chợ ứng dụng VS Code.
2. Mở file [backend-sequence.puml](file:///d:/Lab_AI_Thuc_Chien/Group_Project/2A202600728_BuiTuanMinh_Day05/04-backend-docs/backend-sequence.puml) hoặc [architecture-overview.puml](file:///d:/Lab_AI_Thuc_Chien/Group_Project/2A202600728_BuiTuanMinh_Day05/04-backend-docs/architecture-overview.puml).
3. Nhấn tổ hợp phím `Alt + D` (Windows) hoặc `Option + D` (macOS) để bật màn hình preview trực quan ngay bên cạnh code.

### Cách 2: Xem trực tuyến qua trang chủ PlantUML
1. Mở file `.puml` bất kỳ trong thư mục này và copy toàn bộ nội dung code.
2. Truy cập trang web: [http://www.plantuml.com/plantuml](http://www.plantuml.com/plantuml)
3. Dán đoạn code đã copy vào khung soạn thảo trực tuyến để render ra sơ đồ dạng ảnh.
4. Bạn có thể lưu ảnh về máy để đưa vào slide thuyết trình của nhóm.
