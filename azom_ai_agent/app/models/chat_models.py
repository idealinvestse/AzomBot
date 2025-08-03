from pydantic import BaseModel
from typing import Optional, List

class GeneralQuery(BaseModel):
    prompt: str
    session_id: Optional[str] = None

class TroubleshootRequest(BaseModel):
    prompt: str
    car_model: Optional[str] = None
    error_codes: Optional[List[str]] = None
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
