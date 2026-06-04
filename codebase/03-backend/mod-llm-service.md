# Sub-module 2: Dịch vụ tích hợp AI (LLM Service) [Python Version]

Module này chịu trách nhiệm đóng gói logic prompt engineering, giao tiếp với API của mô hình ngôn ngữ lớn bằng Python thông qua thư viện `google-generativeai` của Google, quản lý lịch sử chat và định hình dữ liệu đầu ra dưới dạng JSON.

---

## 1. Thiết lập SDK & Cấu hình LLM (Python)

Cài đặt thư viện chính thức từ Google:
```bash
pip install google-generativeai python-dotenv
```

**Cấu hình tham khảo:**
```python
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Cấu hình API Key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Thiết lập tham số cho Model
generation_config = {
    "temperature": 0.2, # Giảm độ sáng tạo để tránh ảo tưởng thông tin
    "response_mime_type": "application/json", # Ép kết quả trả về là chuỗi JSON
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config
)
```

---

## 2. Thiết kế System Prompt

System Prompt cung cấp luật chơi và định dạng JSON nghiêm ngặt để Backend có thể dễ dàng gọi `json.loads()`.

**System Prompt:**
```text
Bạn là trợ lý ảo gợi ý món ăn thông minh của ứng dụng ShopeeFood.
Nhiệm vụ của bạn là phân tích ý định (prompt) của người dùng kết hợp với danh sách quán ăn khả dụng (Available Restaurants) được cung cấp dưới đây để đưa ra tối đa 3 đề xuất món/quán phù hợp nhất.

QUY TẮC BẮT BUỘC:
1. CHỈ được chọn quán và món ăn từ danh sách "Available Restaurants" được đưa vào. KHÔNG ĐƯỢC TỰ BỊA ra bất kỳ tên món ăn, tên quán hoặc ID quán nào không tồn tại trong danh sách.
2. Mỗi gợi ý đề xuất phải đi kèm 1 lý do ngắn gọn (tối đa 12 từ) giải thích lý do vì sao món này phù hợp với yêu cầu của người dùng.
3. Nếu câu chat của người dùng quá mơ hồ (thiếu cả 3 thông tin quan trọng: loại món muốn ăn, ngân sách, hoặc ràng buộc/khẩu vị cơ bản) khiến bạn không thể chọn món hợp lý, hãy đặt giá trị "action" là "clarify" và đưa ra duy nhất 1 câu hỏi làm rõ thân thiện tại trường "clarify_question".
4. Nếu người dùng hỏi các chủ đề lạc đề (thời tiết, tin tức, chính trị, v.v.), hãy đặt "action" là "fallback" và từ chối khéo léo để dẫn dắt họ quay lại chuyện ăn uống.
5. Không đưa ra lời khuyên y tế hay dinh dưỡng chuyên sâu. Nếu được hỏi, đề xuất một món nhẹ bụng chung chung từ danh sách và khuyên người dùng tham khảo ý kiến bác sĩ.
6. Trả về đúng định dạng JSON yêu cầu. Không bao quanh bởi markdown block ```json hay bất kỳ chữ thừa nào khác.
```

---

## 3. Định dạng JSON mong muốn trả về từ LLM
LLM bắt buộc phải trả về chuỗi JSON theo cấu trúc sau:
```json
{
  "action": "suggest" | "clarify" | "fallback",
  "clarify_question": "Câu hỏi làm rõ nếu cần thiết",
  "suggestions": [
    {
      "restaurant_id": "res_xxx",
      "dish_name": "Tên món",
      "price": 35000,
      "reason": "Lý do gợi ý ngắn gọn"
    }
  ]
}
```

---

## 4. Đầu ra của Sub-module (Hàm gọi LLM bằng Python)

Chúng ta cần chuyển đổi cấu trúc lịch sử trò chuyện sang định dạng mà Gemini API nhận dạng:

```python
import json
from typing import List, Dict, Any

def format_history_for_gemini(chat_history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Chuyển đổi history từ dạng [{role: 'user', message: '...'}] 
    sang định dạng của Gemini API [{role: 'user', parts: ['...']}]
    """
    gemini_history = []
    for msg in chat_history:
        role = "user" if msg["role"] == "user" else "model"
        gemini_history.append({
            "role": role,
            "parts": [msg["message"]]
        })
    return gemini_history

async def get_llm_suggestions(
    user_prompt: str,
    available_restaurants: List[Dict[str, Any]],
    chat_history: List[Dict[str, Any]] = []
) -> Dict[str, Any]:
    # 1. Tạo Context từ danh sách quán ăn khả dụng
    restaurants_context = json.dumps(available_restaurants, ensure_ascii=False, indent=2)
    
    # 2. Xây dựng prompt hoàn chỉnh
    full_prompt = (
        f"Danh sách Available Restaurants:\n{restaurants_context}\n\n"
        f"Câu chat hiện tại của người dùng: \"{user_prompt}\"\n"
        f"Hãy đưa ra đề xuất dưới dạng JSON theo đúng quy tắc."
    )
    
    # 3. Định cấu hình Chat Session để giữ lại ngữ cảnh hội thoại cũ
    gemini_history = format_history_for_gemini(chat_history)
    chat = model.start_chat(history=gemini_history)
    
    # 4. Gửi yêu cầu tới Gemini
    try:
        response = chat.send_message(full_prompt)
        
        # 5. Parse kết quả trả về
        result_data = json.loads(response.text)
        return result_data
    except Exception as e:
        print(f"Lỗi gọi Gemini API: {e}")
        return {
            "action": "fallback",
            "message": "Không thể kết nối dịch vụ AI."
        }
```
*Lưu ý: Luôn sử dụng `temperature` thấp (khoảng `0.1` đến `0.2`) để mô hình ưu tiên tính chính xác hơn sự sáng tạo.*
