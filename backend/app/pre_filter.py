import os
import json
import math
import re
from typing import List, Dict, Any, Optional
from .schemas import Coords, UserLocation

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(CURRENT_DIR, "mock_db.json")

def load_db() -> List[Dict[str, Any]]:
    if not os.path.exists(DB_PATH):
        return []
    with open(DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def calculate_haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    # Earth's radius in kilometers
    R = 6371.0
    
    rad_lat1 = math.radians(lat1)
    rad_lng1 = math.radians(lng1)
    rad_lat2 = math.radians(lat2)
    rad_lng2 = math.radians(lng2)
    
    dlat = rad_lat2 - rad_lat1
    dlng = rad_lng2 - rad_lng1
    
    a = math.sin(dlat / 2)**2 + math.cos(rad_lat1) * math.cos(rad_lat2) * math.sin(dlng / 2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    return round(R * c, 2)

def parse_budget_limit(message: str) -> Optional[int]:
    message = message.lower()
    # Patterns to match budget limit, e.g., "dưới 50k", "<= 50000", "tầm 30.000đ"
    # Pattern 1: matching words indicating limit followed by a number
    patterns = [
        r'(?:dưới|<|<=|tầm|khoảng|\bmax\b)\s*(\d+(?:\.\d+)?)\s*(k|đ|đồng|ngàn|nghìn)?',
        r'(\d+(?:\.\d+)?)\s*(k|đ|đồng|ngàn|nghìn)?\s*(?:đổ lại|trở xuống|dưới)',
        r'\b(\d+(?:\.\d+)?)\s*(k|đ|đồng|ngàn|nghìn)\b'
    ]
    for pattern in patterns:
        match = re.search(pattern, message)
        if match:
            val_str = match.group(1).replace('.', '')
            unit = match.group(2)
            try:
                val = int(val_str)
                # Convert small numbers representing thousands, e.g., 50 -> 50000
                if unit == 'k' or (not unit and val < 500):
                    return val * 1000
                elif unit in ['ngàn', 'nghìn']:
                    return val * 1000
                else:
                    return val
            except ValueError:
                continue
    return None

def pre_filter_restaurants(
    user_loc: UserLocation,
    coords: Coords,
    message: str
) -> List[Dict[str, Any]]:
    restaurants = load_db()
    candidates = []
    
    # 1. Parse budget limit from user message
    budget_limit = parse_budget_limit(message)
    
    # 2. Extract category keywords to filter semantically (e.g., 'cơm', 'chè', 'phở')
    keywords = ["cơm", "bún", "phở", "hủ tiếu", "bánh mì", "chè", "súp", "trà sữa", "gà", "nem", "há cảo", "xíu mại", "kem"]
    active_keywords = [kw for kw in keywords if kw in message.lower()]
    
    for res in restaurants:
        # Step 2.1: Only active/open restaurants
        if not res.get("is_open", False):
            continue
            
        # Step 2.2: Compute Haversine distance
        res_lat = res.get("lat")
        res_lng = res.get("lng")
        if res_lat is None or res_lng is None:
            continue
            
        distance = calculate_haversine(user_loc.lat, user_loc.lng, res_lat, res_lng)
        
        # Exclude restaurants > 3km
        if distance > 3.0:
            continue
            
        # ETA calculation: 10 mins baseline + 8 mins per km, rounded
        eta = 10 + int(distance * 8)
        
        # Scopes: near score (closer is better, max 3km)
        score_near = max(0.0, 1.0 - (distance / 3.0))
        
        # Hotness score based on restaurant tags
        res_tags = [t.lower() for t in res.get("tags", [])]
        if "nóng" in res_tags or "nước" in res_tags:
            score_hot = 1.0
        elif "lạnh" in res_tags:
            score_hot = 0.0
        else:
            score_hot = 0.5
            
        for dish in res.get("dishes", []):
            dish_name = dish.get("name")
            price = dish.get("price")
            
            # Step 2.3: Budget filtering (if user explicitly set one)
            if budget_limit is not None and price > budget_limit:
                continue
                
            # Category keyword filtering (if user explicitly typed one like 'cơm', 'chè')
            if active_keywords:
                match_keyword = False
                for kw in active_keywords:
                    if (kw in dish_name.lower() or 
                        kw in res.get("name", "").lower() or 
                        any(kw in tag.lower() for tag in res_tags)):
                        match_keyword = True
                        break
                if not match_keyword:
                    continue
                
            # Cheapness score (relative to 100,000 VND max)
            score_cheap = max(0.0, 1.0 - (price / 100000.0))
            
            # Multi-objective weighted score based on sliders
            total_score = (
                coords.hot * score_hot +
                coords.cheap * score_cheap +
                coords.near * score_near
            )
            
            candidates.append({
                "restaurant_id": res.get("id"),
                "restaurant_name": res.get("name"),
                "dish_name": dish_name,
                "price": price,
                "distance_km": distance,
                "eta_minutes": eta,
                "tags": res_tags,
                "score": round(total_score, 4)
            })
            
    # Sort candidates by score descending
    candidates.sort(key=lambda x: x["score"], reverse=True)
    
    # Return top 10 candidates
    return candidates[:10]
