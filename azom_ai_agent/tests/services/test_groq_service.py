import pytest

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from unittest.mock import patch, MagicMock
from app.services.groq_service import GroqService
import requests


def mock_post_response(*args, **kwargs):
    class MockResponse:
        def json(self):
            return {
                "choices": [{"message": {"role": "assistant", "content": "Mocked Groq response"}}]
            }
        def raise_for_status(self):
            pass
    return MockResponse()


def test_groq_service_initialization():
    """Test GroqService initialization."""
    service = GroqService(api_key="test_key")
    assert service is not None
    assert service.api_key == "test_key"


def test_groq_service_chat_success():
    """Test successful chat request with GroqService."""
    service = GroqService(api_key="test_key")
    messages = [{"role": "user", "content": "Hello"}]
    
    with patch("requests.post", side_effect=mock_post_response):
        response = service.chat(messages, model="test-model")
        assert response["choices"][0]["message"]["content"] == "Mocked Groq response"


def test_groq_service_chat_empty_messages(monkeypatch):
    def mock_post(*args, **kwargs):
        raise requests.exceptions.HTTPError("400 Client Error: Bad Request")

    monkeypatch.setattr(requests, "post", mock_post)
    groq_service = GroqService(api_key="dummy_key")
    with pytest.raises(ValueError) as exc_info:
        groq_service.chat([])
    assert str(exc_info.value) == "Messages cannot be empty"


def test_groq_service_chat_no_api_key():
    with pytest.raises(ValueError) as exc_info:
        GroqService(api_key="")
    assert str(exc_info.value) == "API key cannot be empty"
