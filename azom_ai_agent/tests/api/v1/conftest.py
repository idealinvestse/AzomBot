import sys
import os
import pytest

# Add the project root to the Python path to resolve import issues
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from fastapi.testclient import TestClient
from unittest.mock import AsyncMock

from app.main import app
from app.api.v1.chat import get_ai_service
from app.services.ai_service import AIService
from app.config import Settings


@pytest.fixture
def client():
    """
    Fixture to create a TestClient with a mock AIService dependency override.
    This fixture also ensures the app.state is correctly configured for tests.
    """
    # Manually set the settings on the app state for the test environment
    # This resolves the "'State' object has no attribute 'settings'" error
    app.state.settings = Settings()

    # Create the mock and set up the dependency override
    ai_service_mock = AsyncMock(spec=AIService)
    app.dependency_overrides[get_ai_service] = lambda: ai_service_mock

    # Create the TestClient and attach the mock
    with TestClient(app) as test_client:
        test_client.ai_service_mock = ai_service_mock
        yield test_client

    # Clean up everything to ensure test isolation
    app.dependency_overrides.clear()
    if hasattr(app.state, 'settings'):
        delattr(app.state, 'settings')
