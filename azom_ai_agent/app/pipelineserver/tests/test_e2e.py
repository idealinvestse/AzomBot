import pytest
from fastapi.testclient import TestClient
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from app.pipelineserver.pipeline_app.main import app

client = TestClient(app)

def test_health_check():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"

def test_install_pipeline_groq():
    # This will hit the full pipeline using the Groq backend as per .env
    payload = {
        "user_input": "Hur installerar jag DLR på Volvo XC60?",
        "car_model": "Volvo XC60"
    }
    resp = client.post("/pipeline/install", json=payload)
    assert resp.status_code == 200
    result = resp.json()["result"]
    assert "recommended_product" in result
    assert "installation_steps" in result
    assert isinstance(result["installation_steps"], list)

def test_support_pipeline_groq():
    payload = {"question": "Hur fungerar DLR produkten?"}
    resp = client.post("/api/v1/support", json=payload)
    assert resp.status_code == 200
    answer = resp.json().get("answer")
    assert answer is not None
    assert isinstance(answer, str)
    # Optionally check for expected keywords, e.g. 'DLR' or 'produkt'
    assert "DLR" in answer or "produkt" in answer
