import sys
import os
import pytest

# Ensure project root on path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))


def test_core_api_echoes_mode_header(client):
    # client fixture from tests/api/v1/conftest.py
    # Configure the AI service mock to return predictable value
    client.ai_service_mock.query.return_value = "Mocked core response"

    resp = client.post(
        "/api/v1/chat/azom",
        json={"prompt": "Hej"},
        headers={"X-AZOM-Mode": "LIGHT"},
    )

    assert resp.status_code == 200
    assert resp.headers.get("X-AZOM-Mode") == "LIGHT"


def test_core_api_default_mode_header_is_full(client):
    client.ai_service_mock.query.return_value = "Mocked core response"

    resp = client.post(
        "/api/v1/chat/azom",
        json={"prompt": "Hej"},
    )

    assert resp.status_code == 200
    # Default is FULL per ModeMiddleware
    assert resp.headers.get("X-AZOM-Mode") == "FULL"
