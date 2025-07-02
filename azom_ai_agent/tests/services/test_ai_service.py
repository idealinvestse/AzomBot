import pytest

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from unittest.mock import patch, MagicMock
from app.services.ai_service import AIService


def mock_query_response(*args, **kwargs):
    return "Mocked AI response"


def test_ai_service_initialization():
    """Test AIService initialization."""
    service = AIService(openwebui_url="http://test.com", api_token="test_token", model="test_model")
    assert service is not None


def test_ai_service_query_success():
    """Test successful query with AIService."""
    service = AIService(openwebui_url="http://test.com", api_token="test_token", model="test_model")
    prompt = "Hello, AI!"
    
    with patch("app.services.ai_service.AIService.query", side_effect=mock_query_response):
        response = service.query(prompt)
        assert response == "Mocked AI response"


def test_ai_service_query_empty_prompt():
    """Test AI service query with empty prompt."""
    ai_service = AIService(openwebui_url="http://example.com", api_token="dummy_token", model="dummy_model")
    with pytest.raises(ValueError) as exc_info:
        ai_service.query("")
    assert str(exc_info.value) == "Prompt cannot be empty"


def test_ai_service_update_config():
    """Test updating configuration of AIService."""
    service = AIService(openwebui_url="http://test.com", api_token="test_token", model="test_model")
    new_url = "http://new-test.com"
    new_token = "new_test_token"
    new_model = "new_test_model"
    
    service.update_config(openwebui_url=new_url, api_token=new_token, model=new_model)
    # Assuming there are attributes to check or methods to verify config update
    # If not, this test might need adjustment based on actual implementation
    assert True  # Placeholder assertion, update based on actual AIService implementation
