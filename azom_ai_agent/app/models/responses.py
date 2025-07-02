from pydantic import BaseModel
from typing import Any, Optional

class DiagnoseResponse(BaseModel):
    result: str
    details: Optional[Any]

class KnowledgeResponse(BaseModel):
    answer: str
    provenance: Optional[str]


class UploadResponse(BaseModel):
    uploaded_files: list[str]
    total_size: int
    message: str

class KnowledgeStatusResponse(BaseModel):
    status: str
    last_update: Optional[str]
    categories: Optional[list[str]]
