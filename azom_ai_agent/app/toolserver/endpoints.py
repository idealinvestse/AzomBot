from fastapi import APIRouter, Request
from .tool_logic import llm_diagnose, llm_lookup, llm_update_knowledge, llm_savememory

from app.config import Settings
from pathlib import Path
import json
from app.toolserver.tool_logic import llm

router = APIRouter()

# enkel runtime-cache istället för persistent lagring
_SETTINGS_FILE = Path("runtime_settings.json")

def _load_settings() -> Settings:
    if _SETTINGS_FILE.exists():
        try:
            data = json.loads(_SETTINGS_FILE.read_text())
            return Settings.model_validate(data, from_attributes=True)
        except Exception:
            pass
    return Settings()

runtime_settings = _load_settings()

@router.post("/diagnose")
async def tool_diagnose(data: dict, request: Request):
    context = data.get("context", {})
    user_prompt = data.get("user_prompt", "")
    result = llm_diagnose(user_prompt, context)
    return {"diagnosis": result}

@router.post("/lookup")
async def tool_lookup(data: dict, request: Request):
    context = data.get("context", {})
    user_prompt = data.get("user_prompt", "")
    result = llm_lookup(user_prompt, context)
    return {"lookup": result}

@router.post("/update_knowledge")
async def tool_update_knowledge(data: dict, request: Request):
    result = llm_update_knowledge(data)
    return {"update_knowledge": result}

@router.get("/settings")
async def get_settings():
    """Return current runtime settings as dict"""
    return runtime_settings.model_dump()

@router.post("/settings")
async def save_settings(data: dict):
    """Update runtime settings with provided keys (partial update)."""
    for key, value in data.items():
        key_upper = key.upper()
        if hasattr(runtime_settings, key_upper):
            setattr(runtime_settings, key_upper, value)
    # Uppdatera LLMService param
    backend = data.get("llmBackend")
    llm_kwargs = {
        "backend": backend,
        "groq_api_key": data.get("groqApiKey"),
        "groq_model": data.get("groqModel"),
        "openwebui_url": runtime_settings.OPENWEBUI_URL,
        "api_token": runtime_settings.OPENWEBUI_API_TOKEN,
        "model": runtime_settings.TARGET_MODEL,
    }
    llm.update_config(**llm_kwargs)
    # persist to disk
    try:
        _SETTINGS_FILE.write_text(json.dumps(runtime_settings.model_dump(), indent=2))
    except Exception:
        pass

    return {"saved": True, "settings": runtime_settings.model_dump()}

@router.post("/session/save")
async def tool_save_session(data: dict, request: Request):
    # Spara/förbättra minne för session - t.ex. i context/el datab
    session_id = data.get("session_id")
    memory = data.get("session_memory")
    resp = llm_savememory(session_id, memory)
    return {"session_saved": resp}
