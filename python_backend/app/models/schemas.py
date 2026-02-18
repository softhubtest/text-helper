from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class StandardErrorResponse(BaseModel):
    """Standart Hata Yanıtı Modeli"""
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = datetime.now()

class PredictionRequest(BaseModel):
    text: str
    context_message: Optional[str] = None
    max_suggestions: Optional[int] = 80
    use_ai: Optional[bool] = True
    use_search: Optional[bool] = True
    user_id: Optional[str] = "default"

class Suggestion(BaseModel):
    text: str
    type: str  # 'ai', 'dictionary', 'fuzzy', 'history'
    score: float
    description: str
    source: str

class PredictionResponse(BaseModel):
    suggestions: List[Suggestion]
    corrected_text: Optional[str] = None
    processing_time_ms: float
    sources_used: List[str]

class FeedbackRequest(BaseModel):
    text: str
    selected_suggestion: str
    user_id: str = "default"

class CorrectionRequest(BaseModel):
    text: str
    user_id: Optional[str] = "default"
