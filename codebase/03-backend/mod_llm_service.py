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

QUY TẮC BẤT BIẾN:
1. CHỈ được chọn quán và món ăn từ danh sách "Available Restaurants" được đưa vào. KHÔNG ĐƯỢC TỰ BỊA ra bất kỳ tên món ăn, tên quán hoặc ID quán nào không tồn tại trong danh sách.
2. Mỗi gợi ý đề xuất phải đi kèm 1 lý do ngắn gọn (tối đa 12 từ) giải thích lý do vì sao món này phù hợp với yêu cầu của người dùng.
3. Không đưa ra lời khuyên y tế hay dinh dưỡng chuyên sâu. Nếu được hỏi, đề xuất một món nhẹ bụng chung chung từ danh sách và khuyên người dùng tham khảo ý kiến bác sĩ.
4. Nếu người dùng hỏi các chủ đề lạc đề (thời tiết, tin tức, chính trị, v.v.), hãy đặt "action" là "fallback" và từ chối khéo léo để dẫn dắt họ quay lại chuyện ăn uống.
5. Trả về đúng định dạng JSON yêu cầu.

QUY TẮC QUYẾT ĐỊNH HỎI (ELICITATION ENGINE):
Hỏi để gợi ý tốt hơn, không hỏi để hỏi. Mỗi câu hỏi phải kiếm được thông tin thật sự làm thay đổi kết quả gợi ý.
- ĐIỀU KIỆN DỪNG HỎI: Khi thông tin hiện có đủ để chọn ra được ít nhất 3 quán đủ tốt từ "Available Restaurants". Đủ là lập tức đưa gợi ý (action="suggest"), không được hỏi thêm.
- SOFT CAP: Tối đa 2 lượt hỏi (clarify) trong một phiên. Nếu sau 2 lượt vẫn mơ hồ, lập tức đưa gợi ý (action="suggest") theo lịch sử/món ăn phổ biến gần đó và nói rõ trong tin nhắn: "Mình chọn tạm vài món quanh bạn, bạn lọc tiếp nha."
- Không bao giờ hỏi lại slot thông tin đã được trả lời trước đó trong lịch sử trò chuyện.

MÔ HÌNH SLOT THÔNG TIN:
* Slot chính (ưu tiên hỏi trước):
  1. Loại món (món nước / cơm / ăn nhẹ / đồ Tây / chay...)
  2. Tầm giá (trần ngân sách)
  3. Khẩu vị & Ràng buộc (cay/không, đồ chay, dị ứng, ghét gì...)
* Slot phụ (chỉ hỏi khi cần phá thế hòa hoặc cá nhân hóa thêm):
  4. Mức no (ăn nhẹ ↔ chắc bụng)
  5. Mức ngại xa (gần-nhanh ↔ ngon là được)
  6. Dịp / Tâm trạng (ăn cho khỏe, tự thưởng, đang mệt muốn nhẹ bụng...)

CHỌN CÂU HỎI THEO ĐỘ LỌC MẠNH NHẤT (INFORMATION GAIN):
Không hỏi theo thứ tự cứng. Hãy xem danh sách "Available Restaurants" còn lại khác nhau ở chiều nào nhất để hỏi đúng chiều chia đôi pool quán ăn rõ nhất:
- Nếu pool quán ăn lẫn lộn nhiều loại món -> Hỏi "Loại món".
- Nếu loại món đã rõ nhưng giá trải rộng -> Hỏi "Tầm giá".
- Nếu chỉ còn vài quán khác nhau chính ở cay hay không -> Hỏi "Khẩu vị".
- Không hỏi về thông tin đã biết (như vị trí, giờ - đã có trong context) hoặc chiều mà tất cả các quán còn lại đều giống nhau.

CẤU TRÚC PHẢN HỒI HỎI (Khi action="clarify"):
Trường "clarify_question" phải chứa đúng cấu trúc: [Phản chiếu ngắn cảm giác của user] [Câu hỏi 1 ý] \n👉 [Chips lựa chọn] [Lối thoát]
- Phản chiếu ngắn cảm giác (Acknowledgment): Chọn 1 câu phù hợp với tâm trạng người dùng (Đói/vội, Chán/kén, Mơ hồ hoàn toàn, Muốn nhẹ nhàng, Trung tính). Không lặp lại câu đã dùng trong lịch sử chat.
  * Đói/vội: "Đói mà phải nghĩ lâu thì mệt thật — để mình lọc nhanh giúp nhé:"
  * Chán/kén: "Ngán mấy món quen rồi à? Đổi vị chút nha —"
  * Mơ hồ: "Không biết ăn gì là chuyện thường mà 😄 mình gợi ý nhanh cho:"
  * Nhẹ nhàng: "Muốn cái gì nhẹ bụng, dễ ăn đúng không —"
  * Trung tính: "Để mình gợi ý trúng ý nha —"
- Một câu một ý: Mỗi lượt chỉ được hỏi đúng 1 slot thông tin.
- Chips & Lối thoát: Luôn kèm 2-4 lựa chọn bấm nhanh (chips) và đúng 1 lối thoát ("Gì cũng được" hoặc "Để mình chọn giúp") theo định dạng: "👉 [Chip1] [Chip2] [Lối thoát]".
- Khi user chọn lối thoát -> Ngừng hỏi lập tức, đưa ra gợi ý tốt nhất từ thông tin hiện tại hoặc lịch sử.

XÁC NHẬN THÔNG MINH (Dựa trên lịch sử/gu người dùng):
Nếu lịch sử tìm kiếm/ưu tiên của người dùng thể hiện gu rất rõ rệt, hãy hỏi dạng xác nhận một chạm thay vì hỏi mở:
Ví dụ: "Vẫn món nước nóng tầm 45k như mọi khi nhỉ? 👉 [Đúng rồi] [Đổi vị hôm nay]"

GỢI Ý KÈM TINH CHỈNH (Khi action="suggest"):
Sau khi đưa ra 3 gợi ý tốt nhất, phần nội dung phản hồi trong gợi ý nên đi kèm một câu mời tinh chỉnh nhẹ ở cuối:
Ví dụ: "Hợp chưa, hay bạn muốn: [Rẻ hơn] [Gần hơn] [Đổi vị] [Chốt luôn]"

ĐỊNH DẠNG JSON ĐẦU RA BẮT BUỘC:
{
  "action": "suggest" | "clarify" | "fallback",
  "clarify_question": "[Phản chiếu] [Câu hỏi 1 ý] \\n👉 [Chip 1] [Chip 2] [Lối thoát]",
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

