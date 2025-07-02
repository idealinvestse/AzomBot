import pytest

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from app.services.test_llm_service import TestLLMService


def test_test_llm_service_initialization():
    """Test TestLLMService initialization."""
    service = TestLLMService()
    assert service is not None


def test_generate_response():
    """Test generate_response method of TestLLMService."""
    service = TestLLMService()
    response = service.generate_response("Hello")
    assert response == "This is a test response."
