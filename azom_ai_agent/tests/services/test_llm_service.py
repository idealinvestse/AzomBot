import pytest

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from unittest.mock import patch, MagicMock
from app.services.llm_service import LLMService


def mock_groq_response(*args, **kwargs):
    class MockResponse:
        def json(self):
            return {"choices": [{"message": {"role": "assistant", "content": "Hello from Groq!"}}]}
        def raise_for_status(self):
            pass
    return MockResponse()


def mock_openwebui_response(*args, **kwargs):
    return "Hello from OpenWebUI!"


def test_llm_service_initialization():
    """Test LLMService initialization."""
    service = LLMService()
    assert service is not None

@pytest.mark.parametrize("backend,expected_response", [
    ("groq", "Hello from Groq!"),
    ("openwebui", "Hello from OpenWebUI!")
])
def test_llm_service_chat(monkeypatch, backend, expected_response):
    """Test chat method of LLMService with different backends."""
    if backend == "groq":
        def mock_groq_chat(*args, **kwargs):
            return {"choices": [{"message": {"role": "assistant", "content": expected_response}}]}

        monkeypatch.setattr("app.services.groq_service.GroqService.chat", mock_groq_chat)
        llm = LLMService(backend="groq", groq_api_key="dummy_key")
        messages = [{"role": "user", "content": "Hi!"}]
        result = llm.chat(messages)
        assert result["choices"][0]["message"]["content"] == expected_response
    else:
        def mock_openwebui_query(*args, **kwargs):
            return expected_response

        monkeypatch.setattr("app.services.ai_service.AIService.query", mock_openwebui_query)
        llm = LLMService(backend="openwebui", openwebui_url="http://example.com", api_token="dummy_token", model="dummy_model")
        messages = [{"role": "user", "content": "Hi!"}]
        result = llm.chat(messages)
        assert result["choices"][0]["message"]["content"] == expected_response


def test_llm_service_chat_empty_messages():
    """Test LLMService chat with empty messages list."""
    service = LLMService(backend="groq", groq_api_key="dummy_key")
    with pytest.raises(ValueError) as exc_info:
        service.chat([])
    assert str(exc_info.value) == "Messages cannot be empty"
