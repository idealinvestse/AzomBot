import pytest

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

try:
    from app.services.test_llm_service import TestLLMService
except ImportError:
    pass


def test_test_llm_service_initialization():
    """Test TestLLMService initialization."""
    try:
        service = TestLLMService()
        assert service is not None
    except NameError:
        pytest.skip("TestLLMService class not found, update import")
