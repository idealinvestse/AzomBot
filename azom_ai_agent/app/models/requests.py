from pydantic import BaseModel
from typing import Optional

class DiagnoseRequest(BaseModel):
    error_code: Optional[str]
    vin: Optional[str]

class KnowledgeQueryRequest(BaseModel):
    query: str


class KnowledgeUploadRequest(BaseModel):
    category: Optional[str]
    description: Optional[str]

class ManualUpdateRequest(BaseModel):
    update_description: str
