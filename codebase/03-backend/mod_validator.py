from typing import List, Dict, Any
from datetime import datetime
from mod_db_prefilter import calculate_distance, is_shop_open

def is_valid_suggestion(suggestion: Dict[str, Any], raw_db: List[Dict[str, Any]]) -> bool:
    """
    Hàm kiểm tra tính đúng đắn của gợi ý từ LLM đối chiếu với DB thật.
    Tránh trường hợp LLM bịa ID quán hoặc tên món không có trong thực đơn.
    """
    # 1. Tìm quán ăn trong DB theo ID
    restaurant_id = suggestion.get("restaurant_id")
    matched_restaurant = next((r for r in raw_db if r["id"] == restaurant_id), None)
    if not matched_restaurant:
        return False
        
    # 2. Tìm món ăn trong quán (không phân biệt hoa thường)
    dish_name_lower = suggestion.get("dish_name", "").strip().lower()
    matched_dish = next(
        (d for d in matched_restaurant.get("dishes", []) 
         if d["name"].strip().lower() == dish_name_lower and d.get("is_available", True)), 
        None
    )
    if not matched_dish:
        return False
        
    # 3. Kiểm tra sai lệch giá (không lệch quá 10%)
    real_price = matched_dish["price"]
    suggested_price = suggestion.get("price", 0)
    if real_price <= 0:
        return False
    
    price_diff_percent = abs(real_price - suggested_price) / real_price
    if price_diff_percent > 0.1:
        return False
        
    return True

def validate_and_clean_suggestions(
    llm_suggestions: List[Dict[str, Any]],
    raw_db: List[Dict[str, Any]],
    user_location: Dict[str, float]
) -> List[Dict[str, Any]]:
    """
    Hậu kiểm danh sách gợi ý. 
    Nếu danh sách sạch bị rỗng -> Tự động Fallback lấy 3 quán gần nhất đang mở cửa.
    """
    # 1. Lọc bỏ gợi ý không hợp lệ
    clean_list = [s for s in llm_suggestions if is_valid_suggestion(s, raw_db)]
    
    # 2. Nếu danh sách sạch rỗng (LLM bịa toàn bộ hoặc lỗi cấu trúc JSON)
    if not clean_list:
        current_time = datetime.now().strftime("%H:%M")
        decorated_shops = []
        
        for shop in raw_db:
            # Chỉ gợi ý quán đang mở cửa làm fallback
            opening_hours = shop.get("opening_hours", {})
            open_time = opening_hours.get("open", "00:00")
            close_time = opening_hours.get("close", "23:59")
            if not is_shop_open(current_time, open_time, close_time):
                continue
                
            lat = shop.get("lat")
            lng = shop.get("lng")
            if lat is None or lng is None:
                continue
                
            dist = calculate_distance(
                user_location["lat"], user_location["lng"],
                lat, lng
            )
            decorated_shops.append({
                "shop": shop,
                "distance": dist
            })
            
        # Sắp xếp quán theo khoảng cách gần nhất
        decorated_shops.sort(key=lambda x: x["distance"])
        nearby_shops = decorated_shops[:3]
        
        fallback_suggestions = []
        for item in nearby_shops:
            shop = item["shop"]
            # Lấy món ăn đầu tiên có sẵn của quán
            available_dishes = [d for d in shop.get("dishes", []) if d.get("is_available", True)]
            dish_name = available_dishes[0]["name"] if available_dishes else "Món ăn đặc biệt"
            price = available_dishes[0]["price"] if available_dishes else 0
            
            fallback_suggestions.append({
                "restaurant_id": shop["id"],
                "restaurant_name": shop["name"],
                "dish_name": dish_name,
                "price": price,
                "distance_km": round(item["distance"], 2),
                "reason": "Gợi ý quán ăn phổ biến và gần bạn nhất đang mở cửa (Mặc định)."
            })
        return fallback_suggestions
        
    # 3. Map thêm thông tin tên quán và khoảng cách từ DB gốc để Frontend hiển thị đầy đủ
    final_suggestions = []
    for s in clean_list[:3]:
        matched_restaurant = next(r for r in raw_db if r["id"] == s["restaurant_id"])
        lat = matched_restaurant.get("lat")
        lng = matched_restaurant.get("lng")
        if lat is not None and lng is not None:
            dist = calculate_distance(
                user_location["lat"], user_location["lng"],
                lat, lng
            )
        else:
            dist = 1.0
            
        final_suggestions.append({
            "restaurant_id": s["restaurant_id"],
            "restaurant_name": matched_restaurant["name"],
            "dish_name": s["dish_name"],
            "price": s["price"],
            "distance_km": round(dist, 2),
            "reason": s["reason"]
        })
        
    return final_suggestions

