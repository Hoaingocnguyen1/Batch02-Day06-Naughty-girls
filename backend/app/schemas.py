from pydantic import BaseModel, Field
from typing import List, Optional

class Coords(BaseModel):
    hot: float = Field(..., description="Weight for food hotness, 0.0 to 1.0")
    cheap: float = Field(..., description="Weight for food cheapness, 0.0 to 1.0")
    near: float = Field(..., description="Weight for restaurant closeness, 0.0 to 1.0")

class HistoryItem(BaseModel):
    role: str = Field(..., description="Role in chat history: 'user' or 'assistant'")
    content: str = Field(..., description="Text content of the message")

class UserLocation(BaseModel):
    lat: float = Field(..., description="Latitude of user's current location")
    lng: float = Field(..., description="Longitude of user's current location")

class RecommendRequest(BaseModel):
    message: str = Field(..., description="User's input text")
    coords: Coords = Field(..., description="Preference sliders for hot, cheap, near")
    history: List[HistoryItem] = Field(default=[], description="Conversation history")
    user_location: UserLocation = Field(..., description="User's geographic location")

class SuggestionItem(BaseModel):
    restaurant_id: str
    restaurant_name: str
    dish_name: str
    price: int
    distance_km: float
    eta_minutes: int
    reason: str

class RecommendResponse(BaseModel):
    action: str = Field(..., description="Action to take: 'suggest' or 'clarify'")
    clarify_question: str = Field(default="", description="Question to ask if action is 'clarify'")
    suggestions: List[SuggestionItem] = Field(default=[], description="List of 3 recommended dishes if action is 'suggest'")
