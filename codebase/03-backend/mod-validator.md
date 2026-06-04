# Sub-module 3: Bộ Hậu Kiểm & Chống Ảo Tưởng (Code-level Validator) [Python Version]

Mặc dù có System Prompt nghiêm ngặt, mô hình ngôn ngữ lớn (LLM) vẫn có tỷ lệ nhỏ bị ảo tưởng (Hallucination) ra các ID quán hoặc tên món không có thật trong cơ sở dữ liệu. Module này chạy bằng Python ở tầng mã nguồn ứng dụng (application code) để rà soát toàn bộ kết quả trước khi gửi về client, bảo vệ độ tin cậy của hệ thống.

---

## 1. Cơ chế Hoạt động của Validator (Python)

Khi nhận được phản hồi dạng Dictionary từ LLM Service, Code-level Validator thực hiện đối chiếu chéo các trường `restaurant_id`, `dish_name` và `price` với Database JSON gốc.

```
                  ┌──────────────────────────────┐
                  │   Nhận suggestions từ LLM    │
                  └──────────────┬───────────────┘
                                 │
                                 ▼
                     Đối chiếu với DB gốc?
             [Duyệt qua từng gợi ý trong danh sách]
                                 │
         ┌───────────────────────┴───────────────────────┐
         ▼ (Hợp lệ)                                      ▼ (Không hợp lệ)
- restaurant_id tồn tại?                        - ID quán bịa?
- dish_name tồn tại trong quán?                 - Món ăn không thuộc quán?
- Giá khớp với DB thực tế?                      - Giá sai lệch lớn?
         │                                               │
         ▼                                               ▼
   [GIỮ LẠI ĐỀ XUẤT]                              [LOẠI BỎ ĐỀ XUẤT]
         │                                               │
         └───────────────────────┬───────────────────────┘
                                 │
                                 ▼
                   Kiểm tra mảng sau khi lọc?
                                 │
         ┌───────────────────────┴───────────────────────┐
         ▼ (Số lượng gợi ý >= 1)                         ▼ (Mảng rỗng = 0)
Trả về 3 gợi ý sạch cho Client                   Kích hoạt Fallback Mode
                                                 (Lấy 3 quán gần nhất trong DB)
```

---

## 2. Triển khai code logic bằng Python

### A. Hàm kiểm tra tính hợp lệ của đề xuất
Hàm so sánh từng món ăn và quán ăn do LLM đề cử xem có thực sự tồn tại trong file DB gốc và giá cả có trùng khớp hay không (cho phép sai lệch giá tối đa 10%).

```python
from typing import List, Dict, Any

def is_valid_suggestion(suggestion: Dict[str, Any], raw_db: List[Dict[str, Any]]) -> bool:
    # 1. Tìm kiếm quán ăn theo ID
    matched_restaurant = next((r for r in raw_db if r["id"] == suggestion.get("restaurant_id")), None)
    if not matched_restaurant:
        return False # Quán không tồn tại trong DB thật
        
    # 2. Tìm kiếm món ăn trong quán
    dish_name_lower = suggestion.get("dish_name", "").lower()
    matched_dish = next(
        (d for d in matched_restaurant.get("dishes", []) 
         if d["name"].lower() == dish_name_lower and d.get("is_available", True)), 
        None
    )
    if not matched_dish:
        return False # Món ăn không có trong quán hoặc đã hết hàng
        
    # 3. Kiểm tra sai lệch giá (không lệch quá 10%)
    real_price = matched_dish["price"]
    suggested_price = suggestion.get("price", 0)
    price_diff_percent = abs(real_price - suggested_price) / real_price
    
    if price_diff_percent > 0.1:
        return False # Sai lệch giá quá lớn
        
    return True
```

### B. Hàm Lọc & Bù đắp dữ liệu (Filter & Fallback)
Nếu tất cả gợi ý bị lọc sạch (danh sách trống), Validator tự động kích hoạt chế độ Fallback: lấy 3 quán ăn gần nhất trong DB đang hoạt động để bù đắp, tránh để giao diện chatbot hiển thị màn hình trắng lỗi.

```python
from mod_db_prefilter import calculate_distance # Import hàm tính khoảng cách từ sub-module 1

def validate_and_clean_suggestions(
    llm_suggestions: List[Dict[str, Any]],
    raw_db: List[Dict[str, Any]],
    user_location: Dict[str, float]
) -> List[Dict[str, Any]]:
    # 1. Lọc bỏ các gợi ý ảo
    clean_list = [s for s in llm_suggestions if is_valid_suggestion(s, raw_db)]
    
    # 2. Nếu danh sách sạch bị rỗng (do LLM lỗi hoặc bịa toàn bộ)
    if not clean_list:
        # Fallback: Tính khoảng cách tất cả các quán trong DB thật và sắp xếp gần nhất
        decorated_shops = []
        for shop in raw_db:
            dist = calculate_distance(
                user_location["lat"], user_location["lng"],
                shop["latitude"], shop["longitude"]
            )
            decorated_shops.append({
                "shop": shop,
                "distance": dist
            })
            
        # Sắp xếp theo khoảng cách tăng dần
        decorated_shops.sort(key=lambda x: x["distance"])
        nearby_shops = decorated_shops[:3]
        
        # Tạo dữ liệu gợi ý mặc định
        fallback_suggestions = []
        for item in nearby_shops:
            shop = item["shop"]
            first_dish = shop["dishes"][0] if shop["dishes"] else {"name": "Món ăn phổ biến", "price": 0}
            fallback_suggestions.append({
                "restaurant_id": shop["id"],
                "dish_name": first_dish["name"],
                "price": first_dish["price"],
                "reason": "Gợi ý quán ăn phổ biến và gần bạn nhất đang mở cửa (Mặc định)."
            })
        return fallback_suggestions
        
    # 3. Trả về tối đa 3 gợi ý sạch
    return clean_list[:3]
```
*(Lưu ý: Tên file import ở dòng 1 có thể thay đổi tùy thuộc cách đặt tên file code Python thực tế của nhóm bạn, ví dụ: `from mod_db_prefilter import calculate_distance`)*
