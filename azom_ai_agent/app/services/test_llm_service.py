import os
import pytest
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

@pytest.mark.parametrize("backend,expected_response", [
    ("groq", "Hello from Groq!"),
    ("openwebui", "Hello from OpenWebUI!")
])
def test_llm_service_chat(monkeypatch, backend, expected_response):
    # Set environment variable for backend
    monkeypatch.setenv("LLM_BACKEND", backend)
    if backend == "groq":
        # Patch GroqService.chat
        with patch("app.services.groq_service.requests.post", side_effect=mock_groq_response):
            llm = LLMService()
            messages = [{"role": "user", "content": "Hi!"}]
            result = llm.chat(messages)
            # Extract content for OpenAI style response
            assert result["choices"][0]["message"]["content"] == expected_response
    else:
        # Patch AIService.query
        with patch("app.services.ai_service.AIService.query", side_effect=mock_openwebui_response):
            llm = LLMService()
            messages = [{"role": "user", "content": "Hi!"}]
            result = llm.chat(messages)
            assert result == expected_response
