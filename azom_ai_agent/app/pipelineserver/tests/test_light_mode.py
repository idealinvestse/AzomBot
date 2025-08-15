import json
from unittest.mock import MagicMock

import pytest


@pytest.mark.asyncio
def test_chat_light_mode_disables_rag(test_client, monkeypatch):
    # Patch rag_service.search to track calls
    import pipeline_app.main as main_mod

    mock_search = MagicMock()
    mock_search.return_value = []  # no context
    monkeypatch.setattr(main_mod.rag_service, "search", mock_search)

    payload = {
        "message": "Testar att light mode inte gör RAG",
        "car_model": ""
    }

    response = test_client.post(
        "/chat/azom",
        json=payload,
        headers={"X-AZOM-Mode": "light"},
    )

    # Regardless of LLM availability, RAG should not be called in light mode
    assert mock_search.call_count == 0
    assert response.status_code in [200, 500]
    if response.status_code == 200:
        data = response.json()
        # In our implementation, successful response includes context_used
        assert "context_used" in data
        assert data["context_used"] == []


@pytest.mark.asyncio
def test_chat_light_mode_payload_cap_enforced(test_client):
    # Use a safely large payload known to exceed Light mode cap (8KB)
    overlong_message = ("a" * 10000)

    payload = {
        "message": overlong_message,
        "car_model": ""
    }

    response = test_client.post(
        "/chat/azom",
        json=payload,
        headers={"X-AZOM-Mode": "light"},
    )

    assert response.status_code == 413
    data = response.json()
    assert "too large" in (data.get("detail") or "").lower()
