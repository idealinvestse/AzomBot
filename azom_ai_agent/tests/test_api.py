import pytest
from app.main import app
from fastapi.testclient import TestClient
client = TestClient(app)


def test_ping():
    r = client.get("/ping")
    assert r.status_code == 200
    assert "version" in r.json()

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "systemet är friskt"

def test_knowledge_status():
    r = client.get("/knowledge/status")
    assert r.status_code == 200
    assert "status" in r.json()
    assert "categories" in r.json()

def test_knowledge_upload_wrong_format():
    response = client.post(
        "/knowledge/upload",
        files={"files": ("feltyp.exe", b"data"),},
        data={"category": "testcat"}
    )
    assert response.status_code == 400
    assert "Filtyp inte stödd" in response.text

def test_knowledge_upload_too_large(monkeypatch):
    class DummyUpload:
        filename = "too_big.md"
        async def read(self):
            return b'a' * (11 * 1024 * 1024)  # 11MB
    r = client.post(
        "/knowledge/upload",
        files={"files": ("dummy.md", b'a' * (11 * 1024 * 1024))},
        data={"category": "testcat"}
    )
    assert r.status_code == 400
    assert "för stor" in r.text
