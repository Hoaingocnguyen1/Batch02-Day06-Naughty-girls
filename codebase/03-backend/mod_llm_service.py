import os
import json
from typing import List, Dict, Any
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

# Cấu hình OpenAI API Key
api_key = os.getenv("OPENAI_API_KEY")
model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Khởi tạo AsyncOpenAI client nếu có api_key hợp lệ
client = None
if api_key and api_key != "your_openai_api_key_here":
    client = AsyncOpenAI(api_key=api_key)

SYSTEM_PROMPT = """Bạn là trợ lý ảo gợi ý món ăn thông minh của ứng dụng ShopeeFood.
Nhiệm vụ của bạn là phân tích ý định (prompt) của người dùng kết hợp với danh sách quán ăn khả dụng (Available Restaurants) được cung cấp dưới đây để đưa ra tối đa 3 đề xuất món/quán phù hợp nhất.

QUY TẮC BẮT BUỘC:
1. CHỈ được chọn quán và món ăn từ danh sách "Available Restaurants" được đưa vào. KHÔNG ĐƯỢC TỰ BỊA ra bất kỳ tên món ăn, tên quán hoặc ID quán nào không tồn tại trong danh sách.
   Đặc biệt, trong câu hỏi làm rõ (clarify_question), các phương án gợi ý hoặc phân loại đi kèm (ví dụ: các món ăn gợi ý trong ngoặc vuông [ ]) PHẢI THỰC SỰ CÓ trong danh sách "Available Restaurants". Tuyệt đối không gợi ý các thể loại hoặc món ăn không có quán nào bán trong danh sách khả dụng (ví dụ: không được gợi ý "[cơm chay]" nếu trong danh sách không có món chay nào).
2. Mỗi gợi ý đề xuất phải đi kèm 1 lý do ngắn gọn (tối đa 12 từ) giải thích lý do vì sao món này phù hợp với yêu cầu của người dùng.
3. Nếu yêu cầu của người dùng quá mơ hồ (ví dụ: chỉ nói "ăn gì bây giờ", hoặc chỉ nói danh mục chung chung như "ăn cơm", "ăn nhẹ" nhưng danh sách quán khả dụng có quá nhiều món/quán khác nhau mà chưa biết rõ mức giá hoặc khẩu vị mong muốn cụ thể), hãy đặt "action" là "clarify" và đưa ra câu hỏi làm rõ thân thiện để thu hẹp phạm vi.
   Chỉ chuyển sang "action": "suggest" khi thông tin người dùng cung cấp đã đủ thu hẹp phạm vi để bạn chọn được chính xác từ 1 đến 3 món cụ thể, phù hợp trong danh sách khả dụng. Nếu thông tin vẫn còn quá rộng, hãy tiếp tục đặt "action": "clarify".
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

def format_history_for_openai(chat_history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Chuyển đổi history từ dạng [{role: 'user', message: '...'}]
    sang định dạng của OpenAI Chat completion [{"role": "user"|"assistant", "content": "..."}]
    """
    openai_history = []
    for msg in chat_history:
        role = "user" if msg.get("role") == "user" else "assistant"
        openai_history.append({
            "role": role,
            "content": msg.get("message", "")
        })
    return openai_history

async def get_llm_suggestions(
    user_prompt: str,
    available_restaurants: List[Dict[str, Any]],
    chat_history: List[Dict[str, Any]] = []
) -> Dict[str, Any]:
    """
    Gọi OpenAI API để lấy đề xuất món ăn
    """
    global client, api_key
    # Nếu client chưa được khởi tạo, thử khởi tạo lại bằng biến môi trường mới nhất
    if not client:
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key and api_key != "your_openai_api_key_here":
            client = AsyncOpenAI(api_key=api_key)

    if not client:
        return {
            "action": "fallback",
            "message": "Hệ thống chưa cấu hình hoặc cấu hình sai OPENAI_API_KEY trong file .env."
        }

    # 1. Chuyển đổi danh sách quán khả dụng thành chuỗi JSON làm ngữ cảnh
    restaurants_context = json.dumps(available_restaurants, ensure_ascii=False, indent=2)
    
    # Đọc file mock_user.json để lấy context người dùng
    user_data = {}
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        user_path = os.path.join(base_dir, "mock_user.json")
        if os.path.exists(user_path):
            with open(user_path, "r", encoding="utf-8") as f:
                user_data = json.load(f)
    except Exception as e:
        print(f"Lỗi đọc mock_user.json trong LLM Service: {e}")

    user_context_str = ""
    if user_data:
        ctx = user_data.get("context", {})
        hist = user_data.get("history", {})
        user_context_str = (
            f"Thông tin Ngữ cảnh Người dùng (User Context):\n"
            f"- Vị trí: {ctx.get('location', {}).get('city', 'Hà Nội')} (Tọa độ: {ctx.get('location', {}).get('lat')}, {ctx.get('location', {}).get('lng')})\n"
            f"- Ý định hiện tại: {ctx.get('current_intent', 'find_food')}\n"
            f"- Bữa ăn/Thời gian: {ctx.get('current_time', 'lunch')}\n"
            f"- Lịch sử tìm kiếm gần đây: {', '.join(hist.get('queries', []))}\n"
            f"- ID các quán ăn đã bấm xem: {', '.join(hist.get('clicked_items', []))}\n"
            f"- ID các quán ăn đã bỏ qua: {', '.join(hist.get('skipped_items', []))}\n\n"
        )

    # 2. Xây dựng câu lệnh gửi kèm dữ liệu
    full_prompt = (
        f"{user_context_str}"
        f"Danh sách Available Restaurants:\n{restaurants_context}\n\n"
        f"Câu chat của người dùng: \"{user_prompt}\"\n"
        f"Hãy phân tích và trả về kết quả JSON phù hợp theo quy tắc."
    )
    
    try:
        # 3. Chuẩn bị danh sách messages cho OpenAI
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend(format_history_for_openai(chat_history))
        messages.append({"role": "user", "content": full_prompt})
        
        # 4. Gửi yêu cầu lấy gợi ý (Sử dụng JSON mode của OpenAI)
        response = await client.chat.completions.create(
            model=model_name,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.2 # Giảm sáng tạo để tăng tính chính xác
        )
        
        # 5. Phân tích kết quả JSON trả về
        result_text = response.choices[0].message.content
        if not result_text:
            raise ValueError("Phản hồi từ OpenAI bị rỗng.")
        result_data = json.loads(result_text)
        return result_data
    except Exception as e:
        print(f"Lỗi khi tương tác với OpenAI API: {e}")
        return {
            "action": "fallback",
            "message": f"Dịch vụ AI đang gặp sự cố: {str(e)}"
        }

