import math
import json
import os
from typing import List, Dict, Any

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Tính khoảng cách giữa hai tọa độ vĩ độ/kinh độ bằng công thức Haversine (km)
    """
    R = 6371.0 # Bán kính Trái Đất tính bằng km
    
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    
    a = (math.sin(d_lat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
         math.sin(d_lon / 2) ** 2)
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def is_shop_open(current_time: str, open_time: str, close_time: str) -> bool:
    """
    Kiểm tra xem current_time (HH:MM) có nằm trong khoảng open_time đến close_time không.
    Hỗ trợ cả quán mở xuyên đêm (ví dụ: mở từ 10:00 hôm trước tới 02:00 hôm sau).
    """
    try:
        curr_h, curr_m = map(int, current_time.split(':'))
        open_h, open_m = map(int, open_time.split(':'))
        close_h, close_m = map(int, close_time.split(':'))
        
        curr = curr_h * 60 + curr_m
        open_val = open_h * 60 + open_m
        close_val = close_h * 60 + close_m
        
        if open_val <= close_val:
            # Quán mở và đóng trong cùng một ngày
            return open_val <= curr <= close_val
        else:
            # Quán mở xuyên đêm (ví dụ 10:00 -> 02:00 hôm sau)
            return curr >= open_val or curr <= close_val
    except Exception:
        return False

def load_json_db(db_path: str) -> List[Dict[str, Any]]:
    """
    Đọc file database thô và bọc lại thành mảng JSON nếu file gốc chưa được bọc [].
    """
    try:
        with open(db_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        if not content:
            return []
        if not content.startswith("["):
            content = "[" + content + "]"
        return json.loads(content)
    except Exception as e:
        print(f"Lỗi đọc Database file {db_path}: {e}")
        return []

def get_available_restaurants(
    user_location: Dict[str, float],
    current_time: str,
    max_radius_km: float = 5.0,
    db_path: str = "mock_data.json"
) -> List[Dict[str, Any]]:
    """
    Lọc danh sách các quán trong mock_data.json thỏa mãn:
    1. Khoảng cách địa lý <= max_radius_km
    2. Đang mở cửa vào giờ current_time
    3. Có ít nhất một món ăn sẵn sàng bán (is_available = True)
    """
    # Nếu đường dẫn không tuyệt đối, tìm cùng thư mục với file code này
    if not os.path.isabs(db_path):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(base_dir, db_path)
        
    restaurants = load_json_db(db_path)
    if not restaurants:
        return []
        
    available_restaurants = []
    
    for shop in restaurants:
        lat = shop.get("lat")
        lng = shop.get("lng")
        if lat is None or lng is None:
            continue
            
        distance = calculate_distance(
            user_location["lat"], user_location["lng"],
            lat, lng
        )
        
        # 1. Kiểm tra khoảng cách
        if distance > max_radius_km:
            continue
            
        # 2. Kiểm tra trạng thái đóng/mở cửa
        opening_hours = shop.get("opening_hours", {})
        open_time = opening_hours.get("open", "00:00")
        close_time = opening_hours.get("close", "23:59")
        if not is_shop_open(current_time, open_time, close_time):
            continue
            
        # 3. Lọc danh sách món ăn đang có sẵn
        available_dishes = [
            d for d in shop.get("dishes", []) 
            if d.get("is_available", True)
        ]
        if not available_dishes:
            continue
            
        # Thêm quán ăn thỏa mãn điều kiện
        available_restaurants.append({
            "id": shop["id"],
            "name": shop["name"],
            "distance_km": round(distance, 2),
            "dishes": available_dishes
        })
        
    # Sắp xếp quán theo khoảng cách gần nhất
    available_restaurants.sort(key=lambda x: x["distance_km"])
    return available_restaurants

