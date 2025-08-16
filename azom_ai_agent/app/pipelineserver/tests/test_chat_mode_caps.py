import os
import sys
import pytest

"""Endpoint-level tests for /chat/azom payload caps and mode propagation."""

# Ensure import paths:
# - project root (so 'app' package is importable)
# - pipelineserver dir (so 'pipeline_app' is importable)
_HERE = os.path.dirname(__file__)
_PROJECT_ROOT = os.path.abspath(os.path.join(_HERE, '..', '..', '..'))
_PIPELINESERVER_DIR = os.path.abspath(os.path.join(_HERE, '..'))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)
if _PIPELINESERVER_DIR not in sys.path:
    sys.path.insert(0, _PIPELINESERVER_DIR)

from pipeline_app.main import app
from pipeline_app.services.llm_client import get_llm_client


class DummyLLM:
    async def chat(self, messages, model=None, stream=False):
        # Return a simple response to keep endpoint logic flowing
        return "DUMMY_RESPONSE"

    async def aclose(self):
        return None


@pytest.fixture
def client_with_dummy_llm(test_client, monkeypatch):
    """Provide a TestClient with LLM dependency overridden to dummy."""
    # Override the LLM dependency to avoid real HTTP calls
    _prev = app.dependency_overrides.get(get_llm_client)
    app.dependency_overrides[get_llm_client] = lambda: DummyLLM()
    try:
        yield test_client
    finally:
        if _prev is not None:
            app.dependency_overrides[get_llm_client] = _prev
        else:
            app.dependency_overrides.pop(get_llm_client, None)


@pytest.mark.parametrize("payload_size, header_mode, expected_status", [
    (8001, "light", 413),  # > 8KB in light => 413
])
def test_chat_payload_cap_light_mode_returns_413(client_with_dummy_llm, payload_size, header_mode, expected_status):
    msg = "x" * payload_size
    resp = client_with_dummy_llm.post(
        "/chat/azom",
        headers={"X-AZOM-Mode": header_mode},
        json={"message": msg, "car_model": "Volvo"},
    )
    assert resp.status_code == expected_status, resp.text


def test_chat_full_mode_allows_larger_payload_and_calls_rag(test_client, monkeypatch):
    # Arrange: override LLM dependency to dummy
    _prev = app.dependency_overrides.get(get_llm_client)
    app.dependency_overrides[get_llm_client] = lambda: DummyLLM()

    # Arrange: monkeypatch rag_service.search to verify it's called in FULL mode
    calls = {"count": 0}

    async def fake_search(query: str, top_k: int = 3):
        calls["count"] += 1
        return [
            {"content": "ctx1"},
            {"content": "ctx2"},
            {"content": "ctx3"},
        ]

    monkeypatch.setattr("pipeline_app.main.rag_service.search", fake_search)

    # Payload ~ 20KB (< 32KB cap)
    msg = "y" * (20 * 1024)

    # Act
    resp = test_client.post(
        "/chat/azom",
        headers={"X-AZOM-Mode": "full"},
        json={"message": msg, "car_model": "Volvo"},
    )

    # Assert response ok and context used (since FULL mode enables RAG)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data.get("assistant") == "DUMMY_RESPONSE"
    assert isinstance(data.get("context_used"), list) and len(data["context_used"]) == 3
    assert calls["count"] == 1

    # Cleanup
    if _prev is not None:
        app.dependency_overrides[get_llm_client] = _prev
    else:
        app.dependency_overrides.pop(get_llm_client, None)


def test_chat_light_mode_small_payload_ok_and_rag_disabled(test_client, monkeypatch):
    # Arrange: override LLM dependency to dummy
    _prev = app.dependency_overrides.get(get_llm_client)
    app.dependency_overrides[get_llm_client] = lambda: DummyLLM()

    # Track RAG calls to ensure it's NOT called in LIGHT mode
    calls = {"count": 0}

    async def fake_search(query: str, top_k: int = 3):
        calls["count"] += 1
        return []

    monkeypatch.setattr("pipeline_app.main.rag_service.search", fake_search)

    # Payload ~ 2KB (< 8KB cap)
    msg = "z" * (2 * 1024)

    # Act
    resp = test_client.post(
        "/chat/azom",
        headers={"X-AZOM-Mode": "light"},
        json={"message": msg, "car_model": "Volvo"},
    )

    # Assert: 200 OK, assistant present, but no context used and RAG not called
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data.get("assistant") == "DUMMY_RESPONSE"
    assert data.get("context_used") == []
    assert calls["count"] == 0

    # Cleanup
    if _prev is not None:
        app.dependency_overrides[get_llm_client] = _prev
    else:
        app.dependency_overrides.pop(get_llm_client, None)


def test_chat_full_mode_over_cap_returns_413(client_with_dummy_llm):
    # Payload 33KB (> 32KB cap in FULL)
    msg = "w" * (33 * 1024)
    resp = client_with_dummy_llm.post(
        "/chat/azom",
        headers={"X-AZOM-Mode": "full"},
        json={"message": msg, "car_model": "Volvo"},
    )
    assert resp.status_code == 413, resp.text


@pytest.mark.parametrize("mode", ["light", "full"])
def test_chat_mode_header_echo_with_header(client_with_dummy_llm, mode):
    # Small payload to avoid caps
    msg = "ok"
    resp = client_with_dummy_llm.post(
        "/chat/azom",
        headers={"X-AZOM-Mode": mode},
        json={"message": msg, "car_model": "Volvo"},
    )
    assert resp.status_code == 200, resp.text
    # Middleware should echo the resolved mode in uppercase
    assert resp.headers.get("X-AZOM-Mode") == mode.upper()


@pytest.mark.parametrize("mode", ["light", "full"])
def test_chat_mode_header_echo_with_query_param(client_with_dummy_llm, mode):
    # Small payload to avoid caps
    msg = "ok"
    resp = client_with_dummy_llm.post(
        f"/chat/azom?mode={mode}",
        json={"message": msg, "car_model": "Volvo"},
    )
    assert resp.status_code == 200, resp.text
    assert resp.headers.get("X-AZOM-Mode") == mode.upper()
