from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from .schemas import RecommendRequest, RecommendResponse
from .pre_filter import pre_filter_restaurants, load_db
from .ai_agent import get_recommendations

app = FastAPI(
    title="ShopeeFood Chatbot Backend API",
    description="FastAPI Backend for recommendation filtering and AI Agent coordination",
    version="1.0.0"
)

# Configure CORS so Frontend (Next.js) can connect seamlessly
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For Hackathon speed, permit all. Can specify Vercel domain later.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {
        "status": "online",
        "message": "ShopeeFood Chatbot Backend MVP is running!",
        "endpoints": {
            "recommend": "/api/recommend (POST)"
        }
    }

@app.post("/api/recommend", response_model=RecommendResponse)
def recommend_endpoint(request: RecommendRequest):
    try:
        # 1. Pre-filtering: Filter by status, distance (Haversine <= 3km), budget, and compute slider weight scores
        candidates = pre_filter_restaurants(
            user_loc=request.user_location,
            coords=request.coords,
            message=request.message
        )
        
        # 2. AI Agent Processing: Make structured decision (suggest or clarify)
        response = get_recommendations(
            candidates=candidates,
            message=request.message,
            history=request.history,
            coords=request.coords
        )
        
        # 3. Post-validation (TC-07: Hallucination filter in code, not trusting LLM blindly)
        full_db = load_db()
        valid_res_ids = {res["id"] for res in full_db}
        
        validated_suggestions = []
        for sugg in response.suggestions:
            # Verify the suggested restaurant exists in our actual database
            if sugg.restaurant_id in valid_res_ids:
                validated_suggestions.append(sugg)
                
        response.suggestions = validated_suggestions
        
        # Fallback if AI suggested restaurants that don't exist or were filtered out completely
        if response.action == "suggest" and not response.suggestions:
            response.action = "clarify"
            response.clarify_question = "Rất tiếc, mình chưa tìm thấy món ăn nào đang mở cửa và phù hợp trong bán kính 3km quanh bạn. Bạn thử nâng ngân sách hoặc đổi địa chỉ nha!"
            
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal Server Error: {str(e)}"
        )
