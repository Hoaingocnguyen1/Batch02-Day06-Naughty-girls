import sys
from app.pre_filter import pre_filter_restaurants
from app.ai_agent import get_recommendations
from app.schemas import Coords, UserLocation, HistoryItem

# Reconfigure stdout to use UTF-8 to prevent encoding errors on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def print_help():
    print("""
====================================================================
               HƯỚNG DẪN LỆNH CHAT CLI (MOCK AI AGENT)
====================================================================
- Gõ tin nhắn bình thường để trò chuyện với trợ lý ShopeeFood.
- Lệnh đặc biệt:
    /help       : Xem lại hướng dẫn này.
    /clear      : Xóa lịch sử hội thoại hiện tại.
    /weights H C N : Thay đổi cần gạt (Ví dụ: /weights 0.8 0.9 0.4)
                  (H: Nóng sốt, C: Siêu rẻ, N: Gần đây - Khoảng 0.0 đến 1.0)
    exit / quit : Thoát chương trình.
====================================================================
""")

def run_chat_cli():
    print_help()
    
    # Tọa độ mặc định: Cao Thắng, Quận 10, TP.HCM
    user_location = UserLocation(lat=10.762622, lng=106.660172)
    
    # Cần gạt mặc định (trung bình)
    coords = Coords(hot=0.5, cheap=0.5, near=0.5)
    
    # Lịch sử hội thoại rỗng
    history = []
    
    while True:
        try:
            print(f"\n[Cần gạt hiện tại - Nóng: {coords.hot} | Rẻ: {coords.cheap} | Gần: {coords.near}]")
            user_input = input("Bạn: ").strip()
            
            if not user_input:
                continue
                
            # Xử lý các lệnh đặc biệt
            lower_input = user_input.lower()
            if lower_input in ["exit", "quit"]:
                print("Tạm biệt bạn!")
                break
                
            if lower_input == "/help":
                print_help()
                continue
                
            if lower_input == "/clear":
                history = []
                print("--- Đã xóa lịch sử hội thoại ---")
                continue
                
            if lower_input.startswith("/weights"):
                parts = user_input.split()
                if len(parts) == 4:
                    try:
                        h = float(parts[1])
                        c = float(parts[2])
                        n = float(parts[3])
                        coords = Coords(hot=h, cheap=c, near=n)
                        print(f"--- Đã cập nhật cần gạt thành công! ---")
                    except ValueError:
                        print("[Lỗi] Cần gạt phải là các số thực từ 0.0 đến 1.0. Ví dụ: /weights 0.8 0.9 0.4")
                else:
                    print("[Lỗi] Sai cú pháp lệnh. Thử lại: /weights 0.8 0.9 0.4")
                continue
                
            # 1. Chạy tiền lọc lấy danh sách 10 ứng viên từ database
            candidates = pre_filter_restaurants(user_location, coords, user_input)
            
            # 2. Gọi AI Agent đưa ra quyết định gợi ý hoặc hỏi làm rõ
            response = get_recommendations(candidates, user_input, history, coords)
            
            # 3. Hiển thị kết quả trả về từ Agent
            print("\nTrợ lý ShopeeFood:")
            if response.action == "suggest":
                print(f"  [Quyết định: GỢI Ý MÓN ĂN - Tìm thấy {len(response.suggestions)} món]")
                for idx, sugg in enumerate(response.suggestions, 1):
                    print(f"  {idx}. {sugg.restaurant_name} | {sugg.dish_name} | Giá: {sugg.price:,}đ | Khoảng cách: {sugg.distance_km}km (Giao: ~{sugg.eta_minutes} phút)")
                    print(f"     => Lý do: \"{sugg.reason}\"")
                
                # Cập nhật lịch sử hội thoại (lấy món đầu tiên làm đại diện ghi nhớ câu trả lời của trợ lý)
                if response.suggestions:
                    assistant_msg = f"Mình gợi ý bạn món {response.suggestions[0].dish_name} từ {response.suggestions[0].restaurant_name} nha."
                else:
                    assistant_msg = "Không tìm thấy món ăn nào phù hợp quanh bạn."
            else:
                print(f"  [Quyết định: HỎI LÀM RÕ]")
                print(f"  => \"{response.clarify_question}\"")
                assistant_msg = response.clarify_question
                
            # Thêm lượt chat hiện tại vào history để duy trì ngữ cảnh
            history.append(HistoryItem(role="user", content=user_input))
            history.append(HistoryItem(role="assistant", content=assistant_msg))
            
        except KeyboardInterrupt:
            print("\nTạm biệt bạn!")
            break
        except Exception as e:
            print(f"\n[Lỗi hệ thống] {str(e)}")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    run_chat_cli()
