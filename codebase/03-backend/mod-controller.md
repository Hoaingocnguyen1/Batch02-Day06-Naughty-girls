# Sub-module 4: Điều phối chính (API Controller) [Python Version]

Module này đóng vai trò là "Nhạc trưởng", chịu trách nhiệm tạo HTTP Server bằng Python (sử dụng framework **FastAPI**), định nghĩa các API routes, tiếp nhận request từ Client (Frontend), gọi các dịch vụ con và điều phối luồng dữ liệu để trả về kết quả cuối cùng.

---

## 1. Thiết lập API Router (FastAPI làm mẫu)

Cài đặt các thư viện cần thiết cho Web Server Python:
```bash
pip install fastapi uvicorn pydantic
```

**Khung Code của Server (FastAPI):**

Chúng ta sẽ tạo file `main.py` để chạy server uvicorn lắng nghe các request.

```python
import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import các hàm xử lý từ các sub-module
from mod_db_prefilter import get_available_restaurants
from mod_llm_service import get_llm_suggestions
from mod_validator import validate_and_clean_suggestions

# Thiết lập log ghi nhận hoạt động
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("backend-server")

app = FastAPI(title="ShopeeFood Chatbot AI Backend")

# Cho phép Frontend gọi API chéo cổng (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Thay thế bằng domain cụ thể của Frontend khi deploy
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Khai báo cấu trúc Request bằng Pydantic ---
class Location(BaseModel):
    lat: float
    lng: float

class Context(BaseModel):
    location: Optional[Location] = None
    current_time: Optional[str] = None # Định dạng "HH:MM"

class ChatMessage(BaseModel):
    role: str # "user" hoặc "assistant" (Gemini hiểu assistant là "model")
    message: str

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = []
    context: Optional[Context] = None

# --- Đọc Database thô ---
DB_PATH = "mock_restaurants.json"
try:
    with open(DB_PATH, "r", encoding="utf-8") as f:
        raw_db = json.load(f)
except FileNotFoundError:
    raw_db = []
    logger.warning("Không tìm thấy file mock_restaurants.json!")

def get_current_time_formatted() -> str:
    now = datetime.now()
    return now.strftime("%H:%M")

# --- Định nghĩa Endpoint chính ---
@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        message = request.message
        history = [msg.model_dump() for msg in request.history] if request.history else []
        
        # 1. Trích xuất thông tin ngữ cảnh (Location & Time)
        user_location = {"lat": 10.776, "lng": 106.701} # Tọa độ mặc định (HCM)
        if request.context and request.context.location:
            user_location = {
                "lat": request.context.location.lat,
                "lng": request.context.location.lng
            }
            
        current_time = get_current_time_formatted()
        if request.context and request.context.current_time:
            current_time = request.context.current_time
            
        # 2. Bước 1: Lọc dữ liệu thô (Pre-filtering)
        available_shops = get_available_restaurants(
            user_location=user_location,
            current_time=current_time,
            db_path=DB_PATH
        )
        
        # Trường hợp biên: Không có quán nào mở cửa quanh bán kính giao hàng
        if not available_shops:
            return {
                "action": "fallback",
                "message": "Hiện tại quanh khu vực của bạn không có quán ăn nào đang hoạt động.",
                "fallback_url": "/restaurants/all"
            }
            
        # 3. Bước 2: Gọi AI gợi ý món (LLM Service)
        llm_result = await get_llm_suggestions(
            user_prompt=message,
            available_restaurants=available_shops,
            chat_history=history
        )
        
        # 4. Bước 3: Phân loại hành động (Action) từ LLM
        action = llm_result.get("action", "suggest")
        
        if action == "clarify":
            return {
                "action": "clarify",
                "clarify_question": llm_result.get("clarify_question", "Bạn muốn ăn món gì nè?")
            }
            
        if action == "fallback":
            return {
                "action": "fallback",
                "message": llm_result.get("message", "Mình chỉ giúp chọn món thôi nha. Bạn muốn ăn món gì?"),
                "fallback_url": "/restaurants/all"
            }
            
        # Luồng gợi ý món ăn (suggest)
        # 5. Bước 4: Hậu kiểm chống ảo tưởng (Validator)
        suggestions_raw = llm_result.get("suggestions", [])
        clean_suggestions = validate_and_clean_suggestions(
            llm_suggestions=suggestions_raw,
            raw_db=raw_db,
            user_location=user_location
        )
        
        return {
            "action": "suggest",
            "suggestions": clean_suggestions
        }
        
    except Exception as e:
        logger.error(f"Lỗi hệ thống: {e}")
        # Trả về fallback an toàn khi gặp sự cố máy chủ hoặc quá giới hạn API Key
        return {
            "action": "fallback",
            "message": "Hệ thống đang bận một chút, bạn có muốn duyệt danh sách quán ăn đang mở gần đây không?",
            "fallback_url": "/restaurants/all"
        }

# --- Lệnh khởi chạy server (Local test) ---
if __name__ == "__main__":
    import uvicorn
    # Khởi chạy server tại http://localhost:8000
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
```

---

## 2. Hướng dẫn chạy thử Backend Python
1.  Đảm bảo đã cài đặt Python 3.8 trở lên.
2.  Tạo môi trường ảo (virtual environment) để quản lý package:
    ```bash
    python -m venv venv
    venv\Scripts\activate  # Trên Windows
    ```
3.  Cài đặt các dependencies:
    ```bash
    pip install fastapi uvicorn pydantic google-generativeai python-dotenv
    ```
4.  Lưu file code chính là `main.py` và đặt file `mock_restaurants.json` trong cùng thư mục.
5.  Khởi chạy server:
    ```bash
    python main.py
    ```
    *(Server sẽ chạy tại `http://localhost:8000`. Bạn có thể truy cập `http://localhost:8000/docs` để test thử API bằng Swagger UI tích hợp sẵn).*
