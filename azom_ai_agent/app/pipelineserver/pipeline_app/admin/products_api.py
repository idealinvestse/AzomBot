import os
import json
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from fastapi.responses import FileResponse
from datetime import datetime
import shutil
from .auth import verify_credentials

router = APIRouter()

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data'))
PRODUCTS_FILE = os.path.join(DATA_DIR, 'products.json')
VERSIONS_DIR = os.path.join(DATA_DIR, 'versions_products')

os.makedirs(VERSIONS_DIR, exist_ok=True)

# --- Helper functions ---
def load_products():
    if not os.path.exists(PRODUCTS_FILE):
        return []
    with open(PRODUCTS_FILE, encoding='utf-8') as f:
        return json.load(f)

def save_products(data):
    # Spara version först
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    if os.path.exists(PRODUCTS_FILE):
        shutil.copy(PRODUCTS_FILE, os.path.join(VERSIONS_DIR, f'products_{timestamp}.json'))
    with open(PRODUCTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# --- CRUD ---
@router.get('/products')
def get_products(user=Depends(verify_credentials)):
    return load_products()

@router.post('/products')
def add_product(product: dict, user=Depends(verify_credentials)):
    data = load_products()
    # Generate a unique ID for the new product
    new_id = max([p.get('id', 0) for p in data], default=0) + 1
    product['id'] = new_id
    data.append(product)
    save_products(data)
    return product

@router.put('/products/{idx}')
def update_product(idx: int, product: dict, user=Depends(verify_credentials)):
    data = load_products()
    if idx < 0 or idx >= len(data):
        raise HTTPException(status_code=404, detail="Product not found")
    data[idx] = product
    save_products(data)
    return {"status": "ok"}

@router.delete('/products/{idx}')
def delete_product(idx: int, user=Depends(verify_credentials)):
    data = load_products()
    if idx < 0 or idx >= len(data):
        raise HTTPException(status_code=404, detail="Product not found")
    del data[idx]
    save_products(data)
    return {"status": "ok"}

# --- Export ---
@router.get('/products/export')
def export_products(user=Depends(verify_credentials)):
    return FileResponse(PRODUCTS_FILE, filename='products.json', media_type='application/json')

# --- Bulk import ---
@router.post('/products/bulk_import')
def bulk_import(file: UploadFile = File(...), user=Depends(verify_credentials)):
    content = file.file.read()
    try:
        new_data = json.loads(content)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    data = load_products()
    data.extend(new_data)
    save_products(data)
    return {"status": "ok", "imported": len(new_data)}

# --- Versionshistorik ---
@router.get('/products/versions')
def list_versions(user=Depends(verify_credentials)):
    files = sorted([f for f in os.listdir(VERSIONS_DIR) if f.endswith('.json')], reverse=True)
    return {"versions": files}

@router.get('/products/versions/{version_file}')
def get_version(version_file: str, user=Depends(verify_credentials)):
    file_path = os.path.join(VERSIONS_DIR, version_file)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Version not found")
    with open(file_path, encoding='utf-8') as f:
        return json.load(f)

# --- Undo (återställ senaste version) ---
@router.post('/products/undo')
def undo(user=Depends(verify_credentials)):
    files = sorted([f for f in os.listdir(VERSIONS_DIR) if f.endswith('.json')], reverse=True)
    if not files:
        raise HTTPException(status_code=400, detail="No versions to undo")
    latest = os.path.join(VERSIONS_DIR, files[0])
    shutil.copy(latest, PRODUCTS_FILE)
    return {"status": "ok", "restored": files[0]}
