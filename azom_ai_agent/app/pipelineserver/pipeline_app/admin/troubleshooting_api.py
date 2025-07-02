import os
import json
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from fastapi.responses import FileResponse
from datetime import datetime
import shutil
from .auth import verify_credentials

router = APIRouter()

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data'))
TROUBLE_FILE = os.path.join(DATA_DIR, 'troubleshooting.json')
VERSIONS_DIR = os.path.join(DATA_DIR, 'versions_troubleshooting')

os.makedirs(VERSIONS_DIR, exist_ok=True)

def load_troubleshooting():
    if not os.path.exists(TROUBLE_FILE):
        return []
    with open(TROUBLE_FILE, encoding='utf-8') as f:
        return json.load(f)

def save_troubleshooting(data):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    if os.path.exists(TROUBLE_FILE):
        shutil.copy(TROUBLE_FILE, os.path.join(VERSIONS_DIR, f'troubleshooting_{timestamp}.json'))
    with open(TROUBLE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@router.get('/troubleshooting')
def get_troubleshooting(user=Depends(verify_credentials)):
    return load_troubleshooting()

@router.post('/troubleshooting')
def add_troubleshooting(step: dict, user=Depends(verify_credentials)):
    data = load_troubleshooting()
    # Generate a unique ID for the new troubleshooting step
    new_id = max([s.get('id', 0) for s in data], default=0) + 1
    step['id'] = new_id
    data.append(step)
    save_troubleshooting(data)
    return step

@router.put('/troubleshooting/{idx}')
def update_troubleshooting(idx: int, item: dict, user=Depends(verify_credentials)):
    data = load_troubleshooting()
    if idx < 0 or idx >= len(data):
        raise HTTPException(status_code=404, detail="Guide not found")
    data[idx] = item
    save_troubleshooting(data)
    return {"status": "ok"}

@router.delete('/troubleshooting/{idx}')
def delete_troubleshooting(idx: int, user=Depends(verify_credentials)):
    data = load_troubleshooting()
    if idx < 0 or idx >= len(data):
        raise HTTPException(status_code=404, detail="Guide not found")
    del data[idx]
    save_troubleshooting(data)
    return {"status": "ok"}

@router.get('/troubleshooting/export')
def export_troubleshooting(user=Depends(verify_credentials)):
    return FileResponse(TROUBLE_FILE, filename='troubleshooting.json', media_type='application/json')

@router.post('/troubleshooting/bulk_import')
def bulk_import(file: UploadFile = File(...), user=Depends(verify_credentials)):
    content = file.file.read()
    try:
        new_data = json.loads(content)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    data = load_troubleshooting()
    data.extend(new_data)
    save_troubleshooting(data)
    return {"status": "ok", "imported": len(new_data)}

@router.get('/troubleshooting/versions')
def list_versions(user=Depends(verify_credentials)):
    files = sorted([f for f in os.listdir(VERSIONS_DIR) if f.endswith('.json')], reverse=True)
    return {"versions": files}

@router.get('/troubleshooting/versions/{version_file}')
def get_version(version_file: str, user=Depends(verify_credentials)):
    file_path = os.path.join(VERSIONS_DIR, version_file)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Version not found")
    with open(file_path, encoding='utf-8') as f:
        return json.load(f)

@router.post('/troubleshooting/undo')
def undo(user=Depends(verify_credentials)):
    files = sorted([f for f in os.listdir(VERSIONS_DIR) if f.endswith('.json')], reverse=True)
    if not files:
        raise HTTPException(status_code=400, detail="No versions to undo")
    latest = os.path.join(VERSIONS_DIR, files[0])
    shutil.copy(latest, TROUBLE_FILE)
    return {"status": "ok", "restored": files[0]}
