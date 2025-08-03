import sys
import os
from unittest.mock import patch
from app.models import ChatResponse
from app.api.v1.chat import get_llm_client
from app.services.protocols import LLMClientProtocol as LLMServiceProtocol

# Add the project root to the Python path to resolve import issues
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from app.models.chat_models import ChatResponse

# The `client` fixture is now auto-discovered from conftest.py and provides
# access to the mock via `client.ai_service_mock`.

def test_support_endpoint_success(client):
    """Tests the /api/v1/support endpoint for a successful request."""
    client.ai_service_mock.query.return_value = "This is a mocked support response."

    response = client.post("/api/v1/support", json={"prompt": "My device won't start", "car_model": "Test CR-V"})

    assert response.status_code == 200
    expected_data = ChatResponse(response="This is a mocked support response.").model_dump()
    assert response.json() == expected_data
    client.ai_service_mock.query.assert_awaited_once_with("My device won't start", context={'prompt': "My device won't start", 'car_model': 'Test CR-V', 'error_codes': None, 'session_id': None})

def test_support_endpoint_empty_prompt(client):
    """Tests the /api/v1/support endpoint with an empty prompt, expecting a 400 error."""
    response = client.post("/api/v1/support", json={"prompt": "", "car_model": "Test CR-V"})

    assert response.status_code == 400
    assert response.json() == {"detail": "Prompt cannot be empty"}
    client.ai_service_mock.query.assert_not_awaited()

def test_general_query_endpoint_success(client):
    """Tests the /api/v1/chat/azom endpoint for a successful request."""
    client.ai_service_mock.query.return_value = "This is a mocked general response."

    response = client.post("/api/v1/chat/azom", json={"prompt": "Tell me about Azom"})

    assert response.status_code == 200
    expected_data = ChatResponse(response="This is a mocked general response.").model_dump()
    assert response.json() == expected_data
    client.ai_service_mock.query.assert_awaited_once_with("Tell me about Azom", context={'prompt': 'Tell me about Azom', 'session_id': None})

def test_general_query_endpoint_empty_prompt(client):
    """Tests the /api/v1/chat/azom endpoint with an empty prompt, expecting a 400 error."""
    response = client.post("/api/v1/chat/azom", json={"prompt": ""})

    assert response.status_code == 400
    assert response.json() == {"detail": "Prompt cannot be empty"}
    client.ai_service_mock.query.assert_not_awaited()


def test_get_ai_service_dependency_creates_instance():
    """
    Integration test to ensure the get_ai_service dependency correctly
    creates an AIService instance, covering the final line of code in chat.py.
    """
    from fastapi.testclient import TestClient
    from app.main import app
    from unittest.mock import AsyncMock

    # This test needs its own setup to test the dependency wiring.
    mock_llm_client = AsyncMock(spec=LLMServiceProtocol)
    mock_llm_client.chat.return_value = "A response from the integrated mock"

    # Override the lowest-level dependency
    app.dependency_overrides[get_llm_client] = lambda: mock_llm_client

    # Use a fresh TestClient
    with TestClient(app) as integration_client:
        response = integration_client.post("/api/v1/chat/azom", json={"prompt": "test"})
        assert response.status_code == 200
        assert response.json() == {"response": "A response from the integrated mock"}

    # Assert that the underlying llm_client's chat method was called
    mock_llm_client.chat.assert_awaited_once()

    # Clean up the override
    app.dependency_overrides.clear()
