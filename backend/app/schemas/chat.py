from pydantic import BaseModel
from typing import List, Optional

class ChatRequest(BaseModel):
    query: str
    history: Optional[List[dict]] = []  # List of {"role": "user", "content": "..."}
    language: Optional[str] = "en"  # Optional override

class ChatResponse(BaseModel):
    response: str
    sources: List[str] = []
    detected_language: str
