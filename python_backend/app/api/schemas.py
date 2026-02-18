from pydantic import BaseModel, Field
from typing import List, Optional

class ProcessRequest(BaseModel):
    text: str = Field(..., description="Input text to process")
    context: Optional[str] = Field(None, description="Previous context (for smart completion)")

class SuggestionItem(BaseModel):
    text: str
    confidence: float
    type: str  # 'correction', 'completion', 'next_word', 'ai_generation'
    score: float = 0.0
    source: str = "ai"
    description: str = ""

class ResponseModel(BaseModel):
    original: str
    suggestions: List[SuggestionItem]
    sentiment: Optional[str] = None
    corrected_text: Optional[str] = None
    processing_time_ms: Optional[float] = None
