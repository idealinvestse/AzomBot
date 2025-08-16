import sys
import os
from unittest.mock import AsyncMock
import pytest
from fastapi.testclient import TestClient

# Ensure project root on path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from app.pipelineserver.pipeline_app.main import app  # noqa: E402
from app.pipelineserver.pipeline_app.services.llm_client import (  # noqa: E402
    get_llm_client,
    LLMServiceProtocol,
)

class DummyLLM(LLMServiceProtocol):
    async def chat(self, messages, model=None, stream=False):
        return "Detta är ett testsvar från mocken."

    async def aclose(self):
        return None

def override_get_llm_client():
    return DummyLLM()


@pytest.fixture(autouse=True)
def reset_mocks():
    # Placeholder for future resets; keeps behavior consistent across tests
    yield


@pytest.fixture
def client():
    # Install override and ensure restoration on teardown to avoid leakage
    previous = app.dependency_overrides.get(get_llm_client)
    app.dependency_overrides[get_llm_client] = override_get_llm_client
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        if previous is None:
            app.dependency_overrides.pop(get_llm_client, None)
        else:
            app.dependency_overrides[get_llm_client] = previous


def test_light_mode_payload_cap_exceeded_returns_413(client):
    payload = {"message": "a" * 9001}
    resp = client.post("/chat/azom", json=payload, headers={"X-AZOM-Mode": "LIGHT"})
    assert resp.status_code == 413


def test_full_mode_large_payload_allows_and_executes_rag(client, monkeypatch):
    # Mock RAG search
    mock_search = AsyncMock(return_value=[{"content": "ctx1"}, {"content": "ctx2"}])
    monkeypatch.setattr(
        "app.pipelineserver.pipeline_app.main.rag_service.search", mock_search
    )
    # Large but under FULL cap (~20KB)
    payload = {"message": "b" * 20000, "car_model": "Volvo"}
    resp = client.post("/chat/azom", json=payload, headers={"X-AZOM-Mode": "FULL"})

    assert resp.status_code == 200
    data = resp.json()
    assert data.get("assistant") == "Detta är ett testsvar från mocken."
    mock_search.assert_awaited_once()
    # Header echo from ModeMiddleware
    assert resp.headers.get("X-AZOM-Mode") == "FULL"


def test_light_mode_small_payload_disables_rag(client, monkeypatch):
    mock_search = AsyncMock(return_value=[{"content": "should-not-be-called"}])
    monkeypatch.setattr(
        "app.pipelineserver.pipeline_app.main.rag_service.search", mock_search
    )
    payload = {"message": "Hej", "car_model": "SAAB"}
    resp = client.post("/chat/azom", json=payload, headers={"X-AZOM-Mode": "LIGHT"})

    assert resp.status_code == 200
    # RAG should be disabled in LIGHT mode
    mock_search.assert_not_awaited()
    # Header echo from ModeMiddleware
    assert resp.headers.get("X-AZOM-Mode") == "LIGHT"


def test_full_mode_payload_too_large_returns_413(client):
    # > 32KB
    payload = {"message": "x" * 40000}
    resp = client.post("/chat/azom", json=payload, headers={"X-AZOM-Mode": "FULL"})
    assert resp.status_code == 413
