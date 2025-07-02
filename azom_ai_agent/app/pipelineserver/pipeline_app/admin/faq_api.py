import os
import json
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from fastapi.responses import FileResponse
from datetime import datetime
import shutil
from .auth import verify_credentials

router = APIRouter()

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data'))
FAQ_FILE = os.path.join(DATA_DIR, 'faq.json')
VERSIONS_DIR = os.path.join(DATA_DIR, 'versions_faq')

os.makedirs(VERSIONS_DIR, exist_ok=True)

def load_faq():
    if not os.path.exists(FAQ_FILE):
        return []
    with open(FAQ_FILE, encoding='utf-8') as f:
        return json.load(f)

def save_faq(data):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    if os.path.exists(FAQ_FILE):
        shutil.copy(FAQ_FILE, os.path.join(VERSIONS_DIR, f'faq_{timestamp}.json'))
    with open(FAQ_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@router.get('/faq')
def get_faq(user=Depends(verify_credentials)):
    return load_faq()

@router.post('/faq')
def add_faq(item: dict, user=Depends(verify_credentials)):
    data = load_faq()
    # Generate a unique ID for the new FAQ item
    new_id = max([f.get('id', 0) for f in data], default=0) + 1
    item['id'] = new_id
    data.append(item)
    save_faq(data)
    return item

@router.put('/faq/{idx}')
def update_faq(idx: int, item: dict, user=Depends(verify_credentials)):
    data = load_faq()
    if idx < 0 or idx >= len(data):
        raise HTTPException(status_code=404, detail="FAQ not found")
    data[idx] = item
    save_faq(data)
    return {"status": "ok"}

@router.delete('/faq/{idx}')
def delete_faq(idx: int, user=Depends(verify_credentials)):
    data = load_faq()
    if idx < 0 or idx >= len(data):
        raise HTTPException(status_code=404, detail="FAQ not found")
    del data[idx]
    save_faq(data)
    return {"status": "ok"}

@router.get('/faq/export')
def export_faq(user=Depends(verify_credentials)):
    return FileResponse(FAQ_FILE, filename='faq.json', media_type='application/json')

@router.post('/faq/bulk_import')
def bulk_import(file: UploadFile = File(...), user=Depends(verify_credentials)):
    content = file.file.read()
    try:
        new_data = json.loads(content)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    data = load_faq()
    data.extend(new_data)
    save_faq(data)
    return {"status": "ok", "imported": len(new_data)}

@router.get('/faq/versions')
def list_versions(user=Depends(verify_credentials)):
    files = sorted([f for f in os.listdir(VERSIONS_DIR) if f.endswith('.json')], reverse=True)
    return {"versions": files}

@router.get('/faq/versions/{version_file}')
def get_version(version_file: str, user=Depends(verify_credentials)):
    file_path = os.path.join(VERSIONS_DIR, version_file)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Version not found")
    with open(file_path, encoding='utf-8') as f:
        return json.load(f)

@router.post('/faq/undo')
def undo(user=Depends(verify_credentials)):
    files = sorted([f for f in os.listdir(VERSIONS_DIR) if f.endswith('.json')], reverse=True)
    if not files:
        raise HTTPException(status_code=400, detail="No versions to undo")
    latest = os.path.join(VERSIONS_DIR, files[0])
    shutil.copy(latest, FAQ_FILE)
    return {"status": "ok", "restored": files[0]}
