from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from app.pipelineserver.pipeline_app.main import app, llm_client


@pytest.fixture(autouse=True)
def _patch_llm_client(monkeypatch):
    # Patch chat method to avoid real LLM call
    monkeypatch.setattr(llm_client, "chat", AsyncMock(return_value="Detta är ett testsvar."))


def test_chat_endpoint_returns_response():
    client = TestClient(app)
    payload = {"message": "Hur installerar jag?", "car_model": "Volvo"}
    response = client.post("/chat/azom", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["assistant"] == "Detta är ett testsvar."
    assert "context_used" in data
