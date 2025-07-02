import pytest

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from unittest.mock import patch, MagicMock
from app.services.ai_service import AIService
import requests


def mock_query_response(*args, **kwargs):
    return "Mocked AI response"


def mock_query_error(*args, **kwargs):
    raise Exception("API connection failed")


def test_ai_service_initialization():
    """Test AIService initialization."""
    service = AIService(openwebui_url="http://test.com", api_token="test_token", model="test_model")
    assert service is not None
    assert service.url == "http://test.com"
    assert service.token == "test_token"
    assert service.model == "test_model"


def test_ai_service_query_success():
    """Test successful query with AIService."""
    service = AIService(openwebui_url="http://test.com", api_token="test_token", model="test_model")
    prompt = "Hello, AI!"
    
    with patch("requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.json.return_value = {'response': 'Mocked AI response'}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        response = service.query(prompt)
        assert response == "Mocked AI response"
        mock_post.assert_called_once()


def test_ai_service_query_empty_prompt():
    """Test AI service query with empty prompt."""
    ai_service = AIService(openwebui_url="http://example.com", api_token="dummy_token", model="dummy_model")
    with pytest.raises(ValueError) as exc_info:
        ai_service.query("")
    assert str(exc_info.value) == "Prompt cannot be empty"


def test_ai_service_query_error():
    """Test AI service query handling of API errors."""
    service = AIService(openwebui_url="http://test.com", api_token="test_token", model="test_model")
    prompt = "Hello, AI!"
    
    with patch("requests.post") as mock_post:
        mock_post.side_effect = Exception("API connection failed")
        response = service.query(prompt)
        assert response == "Tyvärr kan vi inte svara automatiskt just nu. Vänligen kontakta support eller prova igen senare."


def test_ai_service_query_timeout():
    """Test AI service query handling of request timeout."""
    service = AIService(openwebui_url="http://test.com", api_token="test_token", model="test_model")
    prompt = "Hello, AI!"
    
    with patch("requests.post") as mock_post:
        mock_post.side_effect = requests.exceptions.RequestException("Request timed out")
        response = service.query(prompt)
        assert response == "Tyvärr kan vi inte svara automatiskt just nu. Vänligen kontakta support eller prova igen senare."


def test_ai_service_update_config():
    """Test updating configuration of AIService."""
    service = AIService(openwebui_url="http://test.com", api_token="test_token", model="test_model")
    new_url = "http://new-test.com"
    new_token = "new_test_token"
    new_model = "new_test_model"
    
    service.update_config(openwebui_url=new_url, api_token=new_token, model=new_model)
    assert service.url == new_url
    assert service.token == new_token
    assert service.model == new_model

    # Test partial update
    newer_url = "http://newer-test.com"
    service.update_config(openwebui_url=newer_url)
    assert service.url == newer_url
    assert service.token == new_token  # unchanged
    assert service.model == new_model  # unchanged
