import os
import json
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from .auth import verify_credentials

router = APIRouter()

# --- Paths ---
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data'))
MODELS_FILE = os.path.join(DATA_DIR, 'groq_models.json')
SETTINGS_FILE = os.path.join(DATA_DIR, 'llm_settings.json')
VERSIONS_DIR = os.path.join(DATA_DIR, 'versions_llm_settings')

os.makedirs(VERSIONS_DIR, exist_ok=True)

# --- Helper functions ---

def _load_models():
    if not os.path.exists(MODELS_FILE):
        raise HTTPException(status_code=500, detail="groq_models.json saknas")
    with open(MODELS_FILE, encoding='utf-8') as f:
        return json.load(f)

def _load_selected():
    if not os.path.exists(SETTINGS_FILE):
        # Fallback – välj första modellen som standard
        models = _load_models()
        return models[0]['model_id'] if models else None
    with open(SETTINGS_FILE, encoding='utf-8') as f:
        data = json.load(f)
        return data.get('model_id')

def _save_selected(model_id: str):
    # Spara version först
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    if os.path.exists(SETTINGS_FILE):
        os.makedirs(VERSIONS_DIR, exist_ok=True)
        dst = os.path.join(VERSIONS_DIR, f'llm_settings_{timestamp}.json')
        try:
            import shutil
            shutil.copy(SETTINGS_FILE, dst)
        except Exception:
            pass
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump({"model_id": model_id}, f, ensure_ascii=False, indent=2)

# --- Routes ---

@router.get('/llm/models')
def list_models(user=Depends(verify_credentials)):
    """Returnerar tillgängliga Groq-modeller."""
    return _load_models()


@router.get('/llm/selected')
def get_selected_model(user=Depends(verify_credentials)):
    """Returnerar för närvarande vald Groq-modell."""
    model_id = _load_selected()
    return {"model_id": model_id}


@router.put('/llm/selected')
def set_selected_model(payload: dict, user=Depends(verify_credentials)):
    """Sätter vald Groq-modell."""
    model_id = payload.get('model_id')
    if not model_id:
        raise HTTPException(status_code=400, detail="'model_id' saknas i payload")
    # Validera att modellen finns
    models = _load_models()
    if model_id not in [m['model_id'] for m in models]:
        raise HTTPException(status_code=404, detail="Okänd modell")
    _save_selected(model_id)
    return {"status": "ok", "model_id": model_id}


# --- Export current settings ---
@router.get('/llm/export_settings')
def export_settings(user=Depends(verify_credentials)):
    if not os.path.exists(SETTINGS_FILE):
        raise HTTPException(status_code=404, detail="Ingen settings-fil")
    return FileResponse(SETTINGS_FILE, filename='llm_settings.json', media_type='application/json')
