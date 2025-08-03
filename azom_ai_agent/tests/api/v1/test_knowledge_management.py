import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import io
import shutil

from app.main import app
from app.config import Settings

@pytest.fixture
def client(tmp_path, monkeypatch):
    """Pytest fixture to provide a TestClient with a temporary data path."""
    kb_path = tmp_path / "knowledge_base"
    kb_path.mkdir(exist_ok=True)

    test_settings = Settings(_env_file=None, DATA_PATH=tmp_path)
    monkeypatch.setattr('app.api.v1.knowledge_management.settings', test_settings)

    with TestClient(app) as c:
        yield c

def test_upload_successful(client: TestClient, tmp_path: Path):
    """Test a successful file upload."""
    file_content = b"some,csv,data"
    file_to_upload = ("test.csv", io.BytesIO(file_content), "text/csv")
    
    response = client.post(
        "/knowledge/upload",
        data={"category": "test_cat", "description": "A test file"},
        files=[("files", file_to_upload)]
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Alla filer har laddats upp och lagrats."
    assert len(data["uploaded_files"]) == 1
    
    uploaded_file_path = Path(data["uploaded_files"][0])
    assert uploaded_file_path.name == "test.csv"
    assert uploaded_file_path.parent.name == "test_cat"
    assert uploaded_file_path.read_bytes() == file_content

def test_upload_unsupported_file_type(client: TestClient):
    """Test uploading a file with an unsupported extension."""
    unsupported_file = ("test.txt", io.BytesIO(b"some text data"), "text/plain")
    response = client.post("/knowledge/upload", files=[("files", unsupported_file)])
    assert response.status_code == 400
    assert "Filtyp inte stödd" in response.json()["detail"]

def test_upload_too_large_file(client: TestClient):
    """Test uploading a file that exceeds the size limit."""
    large_content = b"a" * (11 * 1024 * 1024)
    large_file = ("large.csv", io.BytesIO(large_content), "text/csv")
    response = client.post("/knowledge/upload", files=[("files", large_file)])
    assert response.status_code == 400
    assert "för stor" in response.json()["detail"]

def test_upload_filename_collision(client: TestClient, tmp_path: Path):
    """Test that a timestamp is added when uploading a file that already exists."""
    file_content = b"first version"
    file_to_upload = ("test.csv", io.BytesIO(file_content), "text/csv")

    # Upload it the first time
    # Upload it the first time
    response1 = client.post("/knowledge/upload", files=[("files", file_to_upload)])
    assert response1.status_code == 200
    
    category_path = tmp_path / "knowledge_base" / "general"
    original_file_path = category_path / "test.csv"
    assert original_file_path.exists()

    # Upload a file with the same name again
    file_content_2 = b"second version"
    file_to_upload_2 = ("test.csv", io.BytesIO(file_content_2), "text/csv")
    response2 = client.post("/knowledge/upload", files=[("files", file_to_upload_2)])
    assert response2.status_code == 200

    files_in_dir = list(category_path.glob("test*.csv"))
    assert len(files_in_dir) == 2
    
    new_file = next((f for f in files_in_dir if f.stem != "test"), None)
    assert new_file is not None
    assert new_file.read_bytes() == file_content_2

def test_knowledge_status_empty(client: TestClient, tmp_path: Path):
    """Test the knowledge status endpoint when the knowledge base directory does not exist."""
    kb_path = tmp_path / "knowledge_base"
    if kb_path.exists():
        shutil.rmtree(kb_path)

    response = client.get("/knowledge/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "empty"
    assert data["last_update"] is None
    assert data["categories"] == []

def test_manual_update(client: TestClient):
    """Test the manual_update endpoint."""
    response = client.post(
        "/knowledge/manual_update",
        json={"update_description": "Testing manual update"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "update triggered"
    assert "last_update" in data
