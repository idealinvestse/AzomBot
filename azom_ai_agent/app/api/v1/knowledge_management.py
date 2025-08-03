from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks, Form
from fastapi.responses import JSONResponse
from typing import List, Optional
import shutil
from pathlib import Path
from datetime import datetime
import asyncio

from app.models.requests import KnowledgeUploadRequest, ManualUpdateRequest
from app.models.responses import UploadResponse, KnowledgeStatusResponse
from app.config import Settings
from app.logger import get_logger

settings = Settings()
logger = get_logger(__name__)

SUPPORTED_KNOWLEDGE_EXTENSIONS = [".csv", ".md", ".json"]

router = APIRouter(prefix="/knowledge", tags=["knowledge"])

def _is_supported_file(filename: str) -> bool:
    return any(filename.lower().endswith(ext) for ext in SUPPORTED_KNOWLEDGE_EXTENSIONS)

@router.post("/upload", response_model=UploadResponse)
async def upload_knowledge_files(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    category: str = Form("general"),
    description: Optional[str] = Form(None)
):
    uploaded_files = []
    total_size = 0
    category_path = settings.DATA_PATH / "knowledge_base" / category
    category_path.mkdir(parents=True, exist_ok=True)
    for file in files:
        if not _is_supported_file(file.filename):
            raise HTTPException(
                status_code=400,
                detail=f"Filtyp inte stödd: {file.filename}. Stödda format: {SUPPORTED_KNOWLEDGE_EXTENSIONS}"
            )
        file_content = await file.read()
        if len(file_content) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail=f"Filen {file.filename} är för stor. Maxgräns är 10MB.")
        file_path = category_path / file.filename
        if file_path.exists():
            # Lägg på tidsstämpel
            ts = datetime.now().strftime("-%Y%m%d-%H%M%S")
            file_path = file_path.with_stem(file_path.stem + ts)
        with open(file_path, "wb") as f:
            f.write(file_content)
        uploaded_files.append(str(file_path))
        total_size += len(file_content)
    logger.info(f"Knowledge files uploaded: {uploaded_files}")
    return UploadResponse(
        uploaded_files=uploaded_files,
        total_size=total_size,
        message="Alla filer har laddats upp och lagrats."
    )
@router.get("/status", response_model=KnowledgeStatusResponse)
def knowledge_status():
    """Hämta status för kunskapsbas (senaste uppdatering, tillgängliga kategorier)"""
    kb_dir = settings.DATA_PATH / "knowledge_base"
    if not kb_dir.exists():
        return KnowledgeStatusResponse(status="empty", last_update=None, categories=[])
    categories = [p.name for p in kb_dir.iterdir() if p.is_dir()]
    last_update = None
    files = list(kb_dir.glob('**/*'))
    if files:
        last_update = max([datetime.fromtimestamp(f.stat().st_mtime) for f in files]).isoformat()
    return KnowledgeStatusResponse(
        status="ok",
        last_update=last_update,
        categories=categories
    )

@router.post("/manual_update", response_model=KnowledgeStatusResponse)
def manual_update(req: ManualUpdateRequest):
    """Utför manuell uppdatering av kunskapsbasen."""
    # Placeholder för faktisk reload/analyslogik
    logger.info(f"Manual update triggered: {req.update_description}")
    return KnowledgeStatusResponse(status="update triggered", last_update=datetime.utcnow().isoformat(), categories=None)
