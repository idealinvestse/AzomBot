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


def test_groq_service_initialization_with_env_vars(monkeypatch):
    """Test GroqService initialization using environment variables."""
    monkeypatch.setenv("GROQ_API_KEY", "env_test_key")
    monkeypatch.setenv("GROQ_API_URL", "https://api.test.com/custom_endpoint")
    monkeypatch.setenv("GROQ_MODEL", "env-test-model")
    service = GroqService(api_key="dummy_key")
    assert service.api_key == "dummy_key"
    assert service.api_url == "https://api.test.com/custom_endpoint"
    assert service.model == "env-test-model"


def test_groq_service_initialization_with_json_config(monkeypatch):
    """Test GroqService initialization with model override from JSON config."""
    settings_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'app', 'pipelineserver', 'pipeline_app', 'data', 'llm_settings.json'))
    mock_json_data = {"model_id": "json-test-model"}
    
    def mock_open(*args, **kwargs):
        class MockFile:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
            def read(self):
                import json
                return json.dumps(mock_json_data)
        return MockFile()
    
    monkeypatch.setattr("builtins.open", mock_open)
    monkeypatch.setattr("os.path.exists", lambda x: True)
    service = GroqService(api_key="test_key")
    assert service.model == "json-test-model"


def test_groq_service_initialization_with_json_config_error(monkeypatch):
    """Test GroqService initialization when JSON config loading fails."""
    def mock_open_error(*args, **kwargs):
        raise Exception("File read error")
    
    monkeypatch.setattr("builtins.open", mock_open_error)
    monkeypatch.setattr("os.path.exists", lambda x: True)
    service = GroqService(api_key="test_key")
    assert service.model == "llama3-70b-8192"  # Default model since JSON load failed


def test_groq_service_chat_success():
    """Test successful chat request with GroqService."""
    service = GroqService(api_key="test_key")
    messages = [{"role": "user", "content": "Hello"}]
    
    with patch("requests.post", side_effect=mock_post_response):
        response = service.chat(messages, model="test-model")
        assert response["choices"][0]["message"]["content"] == "Mocked Groq response"


def test_groq_service_chat_empty_messages(monkeypatch):
    """Test chat request with empty messages list."""
    def mock_post(*args, **kwargs):
        raise requests.exceptions.HTTPError("400 Client Error: Bad Request")
    
    monkeypatch.setattr(requests, "post", mock_post)
    groq_service = GroqService(api_key="dummy_key")
    with pytest.raises(ValueError) as exc_info:
        groq_service.chat([])
    assert str(exc_info.value) == "Messages cannot be empty"


def test_groq_service_chat_api_error():
    """Test chat request handling of API errors."""
    service = GroqService(api_key="test_key")
    messages = [{"role": "user", "content": "Hello"}]
    
    with patch("requests.post") as mock_post:
        mock_post.side_effect = Exception("API connection failed")
        with pytest.raises(Exception) as exc_info:
            service.chat(messages)
        assert str(exc_info.value) == "API connection failed"


def test_groq_service_chat_timeout():
    """Test chat request handling of request timeout."""
    service = GroqService(api_key="test_key")
    messages = [{"role": "user", "content": "Hello"}]
    
    with patch("requests.post") as mock_post:
        mock_post.side_effect = requests.exceptions.RequestException("Request timed out")
        with pytest.raises(requests.exceptions.RequestException) as exc_info:
            service.chat(messages)
        assert str(exc_info.value) == "Request timed out"


def test_groq_service_chat_no_api_key():
    """Test initialization with no API key."""
    with pytest.raises(ValueError) as exc_info:
        GroqService(api_key="")
    assert str(exc_info.value) == "API key cannot be empty"
