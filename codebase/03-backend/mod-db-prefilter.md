# Sub-module 1: Database & Bộ lọc thô (Pre-filtering) [Python Version]

Module này chịu trách nhiệm quản lý dữ liệu quán ăn giả lập và thực hiện bộ lọc địa lý/thời gian bằng Python trước khi gửi dữ liệu lên LLM để tối ưu chi phí token và tính chính xác.

---

## 1. Cơ sở dữ liệu mẫu (`mock_restaurants.json`)

Chúng ta sẽ tạo một file JSON chứa khoảng 10-20 quán ăn giả lập quanh khu vực người dùng mục tiêu. 

**Cấu trúc dữ liệu mong muốn:**
```json
[
  {
    "id": "res_001",
    "name": "Bún Bò Cô Ba",
    "latitude": 10.7765,
    "longitude": 106.7008,
    "opening_time": "06:00",
    "closing_time": "22:00",
    "dishes": [
      {"name": "Bún Bò Huế Đặc Biệt", "price": 45000, "is_available": true},
      {"name": "Bún Bò Giò Heo", "price": 38000, "is_available": true}
    ]
  },
  {
    "id": "res_002",
    "name": "Cơm Tấm Bụi Sài Gòn",
    "latitude": 10.7780,
    "longitude": 106.7025,
    "opening_time": "07:00",
    "closing_time": "21:00",
    "dishes": [
      {"name": "Cơm Tấm Sườn Bì Chả", "price": 42000, "is_available": true},
      {"name": "Cơm Sườn Non Nướng", "price": 55000, "is_available": true}
    ]
  }
]
```

---

## 2. Các hàm logic cần triển khai (Python)

### A. Tính khoảng cách địa lý (Công thức Haversine)
Cần viết một hàm tính khoảng cách giữa tọa độ của người dùng và quán ăn để xác định xem quán đó có nằm trong bán kính giao hàng (ví dụ dưới 5km) hay không.

**Hàm Python đề xuất:**
```python
import math

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0 # Bán kính Trái Đất tính bằng km
    
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    
    a = (math.sin(d_lat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
         math.sin(d_lon / 2) ** 2)
    
    c = 2 * math.atan2(math.sqrt(a), Math.sqrt(1 - a))
    return R * c # Trả về khoảng cách (km)
```

### B. Kiểm tra trạng thái đóng/mở cửa
Hàm kiểm tra xem thời điểm người dùng đặt hàng (`current_time`, định dạng `"HH:MM"`) có nằm trong khoảng hoạt động `opening_time` và `closing_time` của quán hay không.

```python
def is_shop_open(current_time: str, open_time: str, close_time: str) -> bool:
    curr_h, curr_m = map(int, current_time.split(':'))
    open_h, open_m = map(int, open_time.split(':'))
    close_h, close_m = map(int, close_time.split(':'))
    
    curr = curr_h * 60 + curr_m
    open_val = open_h * 60 + open_m
    close_val = close_h * 60 + close_m
    
    return open_val <= curr <= close_val
```

---

## 3. Đầu ra của Sub-module (Hàm lọc chính)

Hàm chính sẽ đọc file JSON DB, duyệt qua tất cả các quán để lọc ra danh sách quán thỏa mãn điều kiện hoạt động:
*   Đang mở cửa.
*   Bán kính giao hàng $\le$ `max_radius_km`.
*   Có ít nhất 1 món ăn đang ở trạng thái `is_available` là `True`.

```python
import json

def get_available_restaurants(
    user_location: dict, # {"lat": float, "lng": float}
    current_time: str,   # "HH:MM"
    max_radius_km: float = 5.0,
    db_path: str = "mock_restaurants.json"
) -> list:
    # 1. Đọc file mock_restaurants.json
    with open(db_path, 'r', encoding='utf-8') as f:
        restaurants = json.load(f)
        
    available_restaurants = []
    
    # 2. Duyệt qua từng quán để lọc
    for shop in restaurants:
        distance = calculate_distance(
            user_location["lat"], user_location["lng"],
            shop["latitude"], shop["longitude"]
        )
        
        # Kiểm tra khoảng cách
        if distance > max_radius_km:
            continue
            
        # Kiểm tra giờ hoạt động
        if not is_shop_open(current_time, shop["opening_time"], shop["closing_time"]):
            continue
            
        # Lọc danh sách món ăn đang có sẵn
        available_dishes = [d for d in shop["dishes"] if d.get("is_available", True)]
        if not available_dishes:
            continue
            
        # 3. Thêm quán thỏa mãn điều kiện vào kết quả trả về
        available_restaurants.append({
            "id": shop["id"],
            "name": shop["name"],
            "distance_km": round(distance, 2),
            "dishes": available_dishes
        })
        
    return available_restaurants
```
