from unittest.mock import AsyncMock
import pytest
from fastapi.testclient import TestClient

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Import the app and the dependency getter
from app.pipelineserver.pipeline_app.main import app
from app.pipelineserver.pipeline_app.services.llm_client import get_llm_client, LLMServiceProtocol

# --- Mocking Dependencies ---

# 1. Mock for LLM Client dependency
mock_llm_client = AsyncMock(spec=LLMServiceProtocol)

def override_get_llm_client():
    """Override for the get_llm_client dependency that returns our mock."""
    return mock_llm_client

# Apply the dependency override to the app instance
app.dependency_overrides[get_llm_client] = override_get_llm_client

@pytest.fixture(autouse=True)
def reset_mocks():
    """Reset mocks before each test to ensure test isolation."""
    mock_llm_client.reset_mock()
    # Set a default return value for the mock
    mock_llm_client.chat.return_value = "Detta är ett testsvar från mocken."


@pytest.fixture
def mock_rag_search(monkeypatch):
    """Fixture to mock the RAGService.search method."""
    mock_search = AsyncMock(return_value=[
        {'content': 'Test context 1'},
        {'content': 'Test context 2'}
    ])
    monkeypatch.setattr("app.pipelineserver.pipeline_app.main.rag_service.search", mock_search)
    return mock_search


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


# --- Tests ---

def test_chat_endpoint_returns_response(client, mock_rag_search):
    """
    Tests the /chat/azom endpoint.
    - Verifies it returns a 200 OK status.
    - Verifies the response contains the mocked LLM response.
    - Verifies the RAG service was called correctly.
    """
    payload = {"message": "Hur installerar jag?", "car_model": "Volvo"}
    response = client.post("/chat/azom", json=payload)

    # Assertions for the response
    assert response.status_code == 200
    data = response.json()
    
    # This test assumes the endpoint returns a dict with these keys.
    # Based on the original test.
    assert data.get("assistant") == "Detta är ett testsvar från mocken."
    assert "context_used" in data
    assert len(data["context_used"]) == 2

    # Assertions for the mock calls
    mock_rag_search.assert_awaited_once_with("Volvo Hur installerar jag?", top_k=3)
    mock_llm_client.chat.assert_awaited_once()
