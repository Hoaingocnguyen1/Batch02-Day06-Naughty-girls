import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Import các sub-module xử lý
from mod_db_prefilter import get_available_restaurants, load_json_db
from mod_llm_service import get_llm_suggestions
from mod_validator import validate_and_clean_suggestions

# Tải cấu hình biến môi trường
load_dotenv()

# Thiết lập log ghi nhận hoạt động
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("backend-server")

app = FastAPI(
    title="ShopeeFood Chatbot AI Backend",
    description="API Server hỗ trợ gợi ý món ăn thông minh tích hợp AI cho ShopeeFood (MVP)",
    version="1.0.0"
)

# Cho phép Frontend gọi API chéo cổng (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Có thể điều chỉnh lại thành các domain cụ thể khi deploy thực tế
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

# --- Đọc Database thô để làm tham chiếu cho Validator ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "mock_data.json")
USER_PATH = os.path.join(BASE_DIR, "mock_user.json")

# Tải thông tin user để làm context mặc định
try:
    with open(USER_PATH, "r", encoding="utf-8") as f:
        raw_user = json.load(f)
    logger.info(f"Đã tải thành công thông tin user từ {USER_PATH}")
except Exception as e:
    raw_user = {}
    logger.error(f"Lỗi đọc file mock_user.json: {e}")

try:
    raw_db = load_json_db(DB_PATH)
    logger.info(f"Đã tải thành công database gồm {len(raw_db)} quán ăn.")
except Exception as e:
    raw_db = []
    logger.error(f"Lỗi đọc file database: {e}")

def get_current_time_formatted() -> str:
    now = datetime.now()
    return now.strftime("%H:%M")

# --- Định nghĩa các Endpoint ---

@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "ShopeeFood Chatbot AI Backend",
        "docs": "/docs"
    }

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        message = request.message
        # Chuyển đổi Pydantic Models trong history thành danh sách dict để gửi cho LLM Service
        history = [msg.model_dump() for msg in request.history] if request.history else []
        
        # 1. Trích xuất thông tin tọa độ và thời gian người dùng gửi lên
        # Lấy tọa độ mặc định từ mock_user.json (Hà Nội) nếu có, nếu không lấy Hà Nội mặc định
        default_lat = 21.0285
        default_lng = 105.8542
        if raw_user and "context" in raw_user and "location" in raw_user["context"]:
            loc_ctx = raw_user["context"]["location"]
            default_lat = loc_ctx.get("lat", 21.0285)
            default_lng = loc_ctx.get("lng", 105.8542)

        user_location = {"lat": default_lat, "lng": default_lng}
        if request.context and request.context.location:
            user_location = {
                "lat": request.context.location.lat,
                "lng": request.context.location.lng
            }
            
        current_time = get_current_time_formatted()
        if request.context and request.context.current_time:
            current_time = request.context.current_time
            
        logger.info(f"Yêu cầu từ client: '{message}' | Vị trí: {user_location} | Giờ: {current_time}")
            
        # 2. Bước 1: Lọc dữ liệu thô (Pre-filtering)
        available_shops = get_available_restaurants(
            user_location=user_location,
            current_time=current_time,
            db_path=DB_PATH
        )
        
        logger.info(f"Tìm thấy {len(available_shops)} quán mở cửa khả dụng trong bán kính giao hàng.")
        
        # Tối ưu hóa: Chỉ gửi tối đa 10 quán ăn gần nhất cho Gemini để giảm kích thước prompt và tăng tốc độ xử lý của AI
        available_shops = available_shops[:10]
        logger.info(f"Giới hạn gửi cho Gemini còn {len(available_shops)} quán gần nhất.")
        
        # Trường hợp biên: Không có quán nào mở cửa quanh bán kính giao hàng
        if not available_shops:
            logger.info("Không tìm thấy quán nào khả dụng -> Kích hoạt fallback không có quán.")
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
        logger.info(f"LLM trả về Action: {action}")
        
        if action == "clarify":
            return {
                "action": "clarify",
                "clarify_question": llm_result.get("clarify_question", "Bạn muốn ăn món nước hay món khô nè?")
            }
            
        if action == "fallback":
            return {
                "action": "fallback",
                "message": llm_result.get("message", "Mình chỉ có thể gợi ý chọn món ăn trên ShopeeFood thôi nha."),
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
        
        # Tính toán ETA (Thời gian giao hàng ước tính) và phí giao hàng cơ bản
        # Giả định: 1km mất 3 phút giao + 5 phút chuẩn bị; Phí giao hàng: 5000đ/km (tối thiểu 15000đ)
        for s in clean_suggestions:
            dist = s.get("distance_km", 1.0)
            s["eta_mins"] = int(dist * 3 + 5)
            s["delivery_fee"] = int(max(15000, round(dist * 5000, -3)))
        
        logger.info(f"Trả về danh sách gồm {len(clean_suggestions)} gợi ý sạch đã xác thực.")
        
        return {
            "action": "suggest",
            "suggestions": clean_suggestions
        }
        
    except Exception as e:
        logger.error(f"Lỗi nghiêm trọng khi xử lý API: {e}")
        # Trả về fallback an toàn khi gặp sự cố máy chủ
        return {
            "action": "fallback",
            "message": "Hệ thống đang bận một chút, bạn có muốn duyệt danh sách quán ăn đang mở gần đây không?",
            "fallback_url": "/restaurants/all"
        }

# --- Khởi chạy server local ---
if __name__ == "__main__":
    import uvicorn
    # Đọc cấu hình Port từ .env, mặc định là 8000
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Đang khởi chạy uvicorn tại cổng {port}...")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
