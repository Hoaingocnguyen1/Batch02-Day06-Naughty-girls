import os
import re
import sys
import json
from typing import List, Dict, Any, Optional
from .schemas import RecommendResponse, SuggestionItem, Coords, HistoryItem, UserLocation
from .pre_filter import parse_budget_limit

# We try importing the SDKs, letting it fall back gracefully if packages are not fully loaded
try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

SYSTEM_PROMPT = """Bạn là trợ lý gợi ý món ăn trong app giao đồ ăn ShopeeFood.
Nhiệm vụ của bạn: Dựa trên ý định người dùng, cần gạt tùy chọn (coords) và DANH SÁCH QUÁN hợp lệ (đã lọc khoảng cách và giá), hãy chọn tối đa 3 gợi ý phù hợp nhất.

QUY TẮC BẮT BUỘC:
1. CHỈ chọn từ DANH SÁCH QUÁN ĂN HỢP LỆ được cung cấp. KHÔNG tự bịa tên món ăn hay tên quán không có trong danh sách.
2. Trả về tối đa 3 gợi ý. Mỗi gợi ý phải kèm 1 dòng giải thích lý do ngắn gọn (<= 12 từ) nhấn mạnh đúng thứ người dùng quan tâm (ví dụ: nóng hổi, giá rẻ, giao nhanh).
3. Nếu ý định của người dùng quá mơ hồ (thiếu cả loại món, ngân sách, và khẩu vị, ví dụ "đặt gì giờ", "hello", "hi"), hãy đặt "action": "clarify" và đặt câu hỏi làm rõ vào "clarify_question" (ví dụ: "Chào bạn! Bạn muốn ăn món nước nóng hổi hay món khô tiện lợi, và ngân sách khoảng bao nhiêu nè?").
   - Tuy nhiên, nếu trong lịch sử hội thoại đã có câu hỏi làm rõ từ trợ lý, người dùng vẫn tiếp tục mơ hồ ("gì cũng được", "đại đi"), đừng hỏi tiếp. Hãy đặt "action": "suggest" và gợi ý 3 món ăn bất kỳ phổ biến nhất từ danh sách.
4. Nếu người dùng hỏi các câu hỏi lạc đề (thời tiết, tin tức, chính trị, code...) hoặc yêu cầu tư vấn y tế/dinh dưỡng nặng (chữa bệnh đau dạ dày, béo phì...), hãy đặt "action": "clarify" và trả về lời từ chối nhẹ nhàng, kéo họ lại việc ăn uống trong "clarify_question".
5. Nếu người dùng yêu cầu AI đặt đơn hộ hoặc thanh toán hộ (out of scope), hãy đặt "action": "clarify" và giải thích bạn chỉ là trợ lý gợi ý, hướng dẫn họ bấm vào các thẻ bên dưới để tự đặt trên app gốc.
6. Luôn luôn trả về kết quả ở định dạng JSON thô duy nhất theo cấu trúc bên dưới. Tuyệt đối không thêm bất cứ ký tự nào ngoài JSON (như ```json ... ``` hoặc văn bản giải thích).

ĐỊNH DẠNG JSON ĐẦU RA:
{
  "action": "suggest" | "clarify",
  "clarify_question": "câu hỏi làm rõ hoặc câu từ chối (chỉ dùng khi action là clarify)",
  "suggestions": [
    {
      "restaurant_id": "res_xxx",
      "restaurant_name": "Tên quán",
      "dish_name": "Tên món",
      "price": 45000,
      "distance_km": 0.8,
      "eta_minutes": 15,
      "reason": "Lý do ngắn gọn <= 12 từ."
    }
  ]
}
"""

def clean_llm_json(raw_text: str) -> str:
    """Helper to strip markdown fence syntax if returned by the LLM."""
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\n", "", cleaned)
        cleaned = re.sub(r"\n```$", "", cleaned)
    return cleaned.strip()

def call_gemini_api(api_key: str, user_prompt: str) -> str:
    if not HAS_GEMINI:
        raise RuntimeError("google-generativeai SDK is not installed")
    genai.configure(api_key=api_key)
    # Using gemini-1.5-flash as default fast model
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=SYSTEM_PROMPT
    )
    response = model.generate_content(
        user_prompt,
        generation_config={"response_mime_type": "application/json"}
    )
    return response.text

def call_openai_api(api_key: str, user_prompt: str) -> str:
    if not HAS_OPENAI:
        raise RuntimeError("openai SDK is not installed")
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        response_format={"type": "json_object"}
    )
    return response.choices[0].message.content

def run_local_mock_fallback(
    candidates: List[Dict[str, Any]],
    message: str,
    history: List[HistoryItem],
    coords: Coords
) -> RecommendResponse:
    """Fallback logic using mock behavior when API keys are not set or API calls fail."""
    msg_lower = message.lower().strip()
    
    # TC-08: Out of topic
    out_of_topic_keywords = ["thời tiết", "nhiệt độ", "mưa", "nắng", "ngày mai", "tin tức", "thể thao", "bóng đá"]
    if any(kw in msg_lower for kw in out_of_topic_keywords):
        return RecommendResponse(
            action="clarify",
            clarify_question="Mình chỉ giúp chọn món thôi nha — bạn đang muốn ăn gì?",
            suggestions=[]
        )
        
    # TC-11: Medical query
    medical_keywords = ["đau dạ dày", "đau bao tử", "giảm cân", "béo phì", "chữa bệnh", "thuốc"]
    if any(kw in msg_lower for kw in medical_keywords):
        return RecommendResponse(
            action="clarify",
            clarify_question="Mình chỉ gợi ý món ăn thôi nè. Nếu bạn mệt hoặc đau dạ dày, mình gợi ý cháo hoặc súp nhẹ bụng nha! Bạn nên hỏi thêm ý kiến bác sĩ nhé.",
            suggestions=[]
        )
        
    # TC-10: Out of scope (AI tự đặt đơn)
    order_keywords = ["đặt giúp", "đặt hộ", "thanh toán hộ", "order giúp", "mua giùm"]
    if any(kw in msg_lower for kw in order_keywords):
        return RecommendResponse(
            action="clarify",
            clarify_question="Mình chỉ đóng vai trò trợ lý gợi ý thôi nè. Bạn hãy chọn món mình thích trong các thẻ bên dưới rồi bấm để tự đặt trên app ShopeeFood nha!",
            suggestions=[]
        )

    # TC-05 / TC-06: Empty candidates (No restaurants / Budget impossible)
    if not candidates:
        budget_limit = parse_budget_limit(message)
        if budget_limit is not None and budget_limit < 20000:
            return RecommendResponse(
                action="clarify",
                clarify_question=f"Quanh bạn chưa có món nào giá dưới {budget_limit:,}đ hết trơn. Bạn thử nâng ngân sách lên khoảng 40k-50k nha!",
                suggestions=[]
            )
        else:
            return RecommendResponse(
                action="clarify",
                clarify_question="Tiếc quá, hiện tại quanh bạn không có quán nào đang mở cửa hoặc nằm trong bán kính 3km cả. Bạn thử đổi địa chỉ hoặc quay lại sau nha!",
                suggestions=[]
            )

    # TC-03: Vague Intent
    vague_keywords = ["đặt gì giờ", "ăn gì giờ", "hello", "hi", "xin chào", "ăn gì ngon", "đói quá"]
    is_vague = msg_lower == "" or any(kw == msg_lower for kw in vague_keywords)
    
    if is_vague:
        has_previous_clarify = any(
            h.role == "assistant" and "muốn ăn" in h.content 
            for h in history
        )
        if has_previous_clarify:
            selected_items = candidates[:min(3, len(candidates))]
            suggestions = []
            for item in selected_items:
                suggestions.append(SuggestionItem(
                    restaurant_id=item["restaurant_id"],
                    restaurant_name=item["restaurant_name"],
                    dish_name=item["dish_name"],
                    price=item["price"],
                    distance_km=item["distance_km"],
                    eta_minutes=item["eta_minutes"],
                    reason="Món cơm nóng ngon phù hợp khẩu vị của bạn." if "cơm" in item["dish_name"].lower() else "Món bán chạy quanh bạn, được nhiều người dùng tin cậy."
                ))
            return RecommendResponse(
                action="suggest",
                clarify_question="",
                suggestions=suggestions
            )
        else:
            return RecommendResponse(
                action="clarify",
                clarify_question="Chào bạn! Bạn đang muốn ăn món nước nóng hổi hay món khô tiện lợi, và ngân sách khoảng bao nhiêu nè?",
                suggestions=[]
            )

    # TC-01 & TC-02 & TC-04: Happy Path (1 to 3 suggestions)
    num_suggestions = min(3, len(candidates))
    selected_candidates = candidates[:num_suggestions]
    
    suggestions = []
    for cand in selected_candidates:
        price = cand["price"]
        dist = cand["distance_km"]
        dish = cand["dish_name"]
        
        if coords.hot > 0.6 and ("nóng" in cand["tags"] or "nước" in cand["tags"]):
            reason = f"Món nước nóng hổi đúng ý bạn, giá {price//1000}k và cách {dist}km."
        elif coords.cheap > 0.6:
            reason = f"Món ngon giá hời chỉ {price//1000}k, cách bạn {dist}km."
        elif coords.near > 0.6:
            reason = f"Quán cực gần chỉ {dist}km, giao nhanh ăn liền!"
        else:
            reason = f"Món {dish} nóng ngon, giá {price//1000}k phù hợp khẩu vị của bạn."
            
        suggestions.append(SuggestionItem(
            restaurant_id=cand["restaurant_id"],
            restaurant_name=cand["restaurant_name"],
            dish_name=dish,
            price=price,
            distance_km=dist,
            eta_minutes=cand["eta_minutes"],
            reason=reason
        ))
        
    return RecommendResponse(
        action="suggest",
        clarify_question="",
        suggestions=suggestions
    )

def get_recommendations(
    candidates: List[Dict[str, Any]],
    message: str,
    history: List[HistoryItem],
    coords: Coords
) -> RecommendResponse:
    # 1. Fetch API keys from environment
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
    openai_key = os.getenv("OPENAI_API_KEY", "").strip()
    
    use_gemini = gemini_key and not gemini_key.startswith("YOUR_")
    use_openai = openai_key and not openai_key.startswith("YOUR_")
    
    # Only run LLM if a key is configured, otherwise skip directly to fallback
    if use_gemini or use_openai:
        try:
            # Construct User Prompt
            user_prompt = f"""
Ý định người dùng: "{message}"
Cần gạt tùy chọn (Trọng số từ 0.0 đến 1.0):
- Nóng sốt (hot): {coords.hot}
- Siêu rẻ (cheap): {coords.cheap}
- Gần đây (near): {coords.near}

Lịch sử hội thoại:
{json.dumps([{"role": h.role, "content": h.content} for h in history], ensure_ascii=False, indent=2)}

Danh sách quán ăn hợp lệ gần đây (Đã được tiền lọc):
{json.dumps(candidates, ensure_ascii=False, indent=2)}
"""
            raw_response = ""
            success = False
            
            # 1. Try Gemini first
            if use_gemini:
                try:
                    print(">>> Calling Google Gemini API...", file=sys.stderr)
                    raw_response = call_gemini_api(gemini_key, user_prompt)
                    success = True
                except Exception as g_err:
                    print(f"[Gemini API Failed] {str(g_err)}. Trying OpenAI as fallback...", file=sys.stderr)
            
            # 2. Try OpenAI next if Gemini wasn't run or failed
            if not success and use_openai:
                try:
                    print(">>> Calling OpenAI API...", file=sys.stderr)
                    raw_response = call_openai_api(openai_key, user_prompt)
                    success = True
                except Exception as o_err:
                    print(f"[OpenAI API Failed] {str(o_err)}", file=sys.stderr)
                    
            if not success:
                raise RuntimeError("Both Gemini and OpenAI API calls failed")
                
            # Parse response
            clean_json_str = clean_llm_json(raw_response)
            parsed_data = json.loads(clean_json_str)
            
            # Map Pydantic suggestions safely
            suggestions_list = []
            if parsed_data.get("action") == "suggest":
                for s in parsed_data.get("suggestions", []):
                    # Ensure safety of reason length
                    reason_text = s.get("reason", "Món ngon thích hợp cho bạn.")
                    if len(reason_text.split()) > 12:
                        reason_text = " ".join(reason_text.split()[:11]) + "..."
                        
                    suggestions_list.append(SuggestionItem(
                        restaurant_id=s.get("restaurant_id"),
                        restaurant_name=s.get("restaurant_name"),
                        dish_name=s.get("dish_name"),
                        price=s.get("price"),
                        distance_km=s.get("distance_km"),
                        eta_minutes=s.get("eta_minutes", 15),
                        reason=reason_text
                    ))
            
            return RecommendResponse(
                action=parsed_data.get("action", "suggest"),
                clarify_question=parsed_data.get("clarify_question", ""),
                suggestions=suggestions_list
            )
            
        except Exception as e:
            # Log error and fall back to local mock
            print(f"[LLM Error] API call or JSON parsing failed: {str(e)}. Falling back to mock decision...", file=sys.stderr)
            
    # Fallback to local mock decision logic
    return run_local_mock_fallback(candidates, message, history, coords)

if __name__ == "__main__":
    # Script test truc tiep tu terminal
    from dotenv import load_dotenv
    load_dotenv()
    
    import sys
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')

    print("=== KIỂM THỬ ĐỘC LẬP AI AGENT ===")
    
    mock_candidates = [
        {
            "restaurant_id": "res_001",
            "restaurant_name": "Bún Bò Cô Ba",
            "dish_name": "Bún Bò Nạm Lớn",
            "price": 45000,
            "distance_km": 0.8,
            "eta_minutes": 15,
            "tags": ["nóng", "nước", "mặn"]
        },
        {
            "restaurant_id": "res_002",
            "restaurant_name": "Cơm Tấm Phúc Lộc Thọ",
            "dish_name": "Cơm Sườn Bì Chả",
            "price": 48000,
            "distance_km": 1.2,
            "eta_minutes": 18,
            "tags": ["nóng", "khô", "mặn"]
        }
    ]
    
    test_coords = Coords(hot=0.8, cheap=0.9, near=0.7)
    
    # Test case 1: Happy Path
    print("\nCase 1: Happy Path ('Món gì nóng rẻ gần đây')")
    res1 = get_recommendations(mock_candidates, "Món gì nóng rẻ gần đây", [], test_coords)
    print(f"Action: {res1.action}")
    for s in res1.suggestions:
        print(f"  - {s.restaurant_name} | {s.dish_name} | {s.price}đ | Lý do: {s.reason}")
        
    # Test case 2: Lạc đề
    print("\nCase 2: Lạc đề ('Thời tiết mai ra sao')")
    res2 = get_recommendations(mock_candidates, "Thời tiết mai ra sao", [], test_coords)
    print(f"Action: {res2.action} | Câu hỏi: {res2.clarify_question}")
