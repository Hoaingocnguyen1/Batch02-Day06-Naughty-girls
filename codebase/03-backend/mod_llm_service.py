import os
import json
from typing import List, Dict, Any
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Cấu hình Google Gemini API Key
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

SYSTEM_PROMPT = """Bạn là trợ lý ảo gợi ý món ăn thông minh của ứng dụng ShopeeFood.
Nhiệm vụ của bạn là phân tích ý định (prompt) của người dùng kết hợp với danh sách quán ăn khả dụng (Available Restaurants) được cung cấp dưới đây để đưa ra tối đa 3 đề xuất món/quán phù hợp nhất.

QUY TẮC BẮT BUỘC:
1. CHỈ được chọn quán và món ăn từ danh sách "Available Restaurants" được đưa vào. KHÔNG ĐƯỢC TỰ BỊA ra bất kỳ tên món ăn, tên quán hoặc ID quán nào không tồn tại trong danh sách.
2. Mỗi gợi ý đề xuất phải đi kèm 1 lý do ngắn gọn (tối đa 12 từ) giải thích lý do vì sao món này phù hợp với yêu cầu của người dùng.
3. Nếu câu chat của người dùng quá mơ hồ (thiếu cả 3 thông tin quan trọng: loại món muốn ăn, ngân sách, hoặc ràng buộc/khẩu vị cơ bản) khiến bạn không thể chọn món hợp lý, hãy đặt giá trị "action" là "clarify" và đưa ra duy nhất 1 câu hỏi làm rõ thân thiện tại trường "clarify_question".
4. Nếu người dùng hỏi các chủ đề lạc đề (thời tiết, tin tức, chính trị, v.v.), hãy đặt "action" là "fallback" và từ chối khéo léo để dẫn dắt họ quay lại chuyện ăn uống.
5. Không đưa ra lời khuyên y tế hay dinh dưỡng chuyên sâu. Nếu được hỏi, đề xuất một món nhẹ bụng chung chung từ danh sách và khuyên người dùng tham khảo ý kiến bác sĩ.
6. Trả về đúng định dạng JSON yêu cầu. Không bao quanh bởi markdown block ```json hay bất kỳ chữ thừa nào khác.

ĐỊNH DẠNG JSON ĐẦU RA BẮT BUỘC:
{
  "action": "suggest" | "clarify" | "fallback",
  "clarify_question": "Câu hỏi làm rõ (chỉ dùng khi action=clarify)",
  "message": "Tin nhắn từ chối lịch sự (chỉ dùng khi action=fallback)",
  "suggestions": [
    {
      "restaurant_id": "ID quán ăn",
      "dish_name": "Tên món ăn cụ thể",
      "price": 35000,
      "reason": "Lý do ngắn gọn (< 12 từ)"
    }
  ]
}"""

# Cấu hình GenerativeModel
generation_config = {
    "temperature": 0.2, # Giảm sáng tạo để tăng tính chính xác
    "response_mime_type": "application/json" # Ép kết quả định dạng JSON
}

# Khởi tạo model một lần
model = genai.GenerativeModel(
    model_name="gemini-3.5-flash",
    generation_config=generation_config,
    system_instruction=SYSTEM_PROMPT
)

def format_history_for_gemini(chat_history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Chuyển đổi history từ dạng [{role: 'user', message: '...'}]
    sang định dạng của Gemini API [{role: 'user'/'model', parts: ['...']}]
    """
    gemini_history = []
    for msg in chat_history:
        role = "user" if msg.get("role") == "user" else "model"
        gemini_history.append({
            "role": role,
            "parts": [msg.get("message", "")]
        })
    return gemini_history

async def get_llm_suggestions(
    user_prompt: str,
    available_restaurants: List[Dict[str, Any]],
    chat_history: List[Dict[str, Any]] = []
) -> Dict[str, Any]:
    """
    Gọi Gemini API để lấy đề xuất món ăn
    """
    if not os.getenv("GEMINI_API_KEY"):
        return {
            "action": "fallback",
            "message": "Hệ thống chưa cấu hình GEMINI_API_KEY trong file .env."
        }

    # 1. Chuyển đổi danh sách quán khả dụng thành chuỗi JSON làm ngữ cảnh
    restaurants_context = json.dumps(available_restaurants, ensure_ascii=False, indent=2)
    
    # 2. Xây dựng câu lệnh gửi kèm dữ liệu
    full_prompt = (
        f"Danh sách Available Restaurants:\n{restaurants_context}\n\n"
        f"Câu chat của người dùng: \"{user_prompt}\"\n"
        f"Hãy phân tích và trả về kết quả JSON phù hợp theo quy tắc."
    )
    
    try:
        # 3. Tạo Chat Session và nạp lịch sử trò chuyện
        gemini_history = format_history_for_gemini(chat_history)
        chat = model.start_chat(history=gemini_history)
        
        # 4. Gửi yêu cầu lấy gợi ý
        response = chat.send_message(full_prompt)
        
        # 5. Phân tích kết quả JSON trả về
        result_data = json.loads(response.text)
        return result_data
    except Exception as e:
        print(f"Lỗi khi tương tác với Gemini API: {e}")
        return {
            "action": "fallback",
            "message": f"Dịch vụ AI đang gặp sự cố: {str(e)}"
        }
