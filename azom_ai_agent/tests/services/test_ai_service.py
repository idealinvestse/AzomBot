import pytest
from unittest.mock import AsyncMock
from fastapi import HTTPException

from app.services.ai_service import AIService
from app.services.protocols import LLMClientProtocol

# --- Fixtures ---

@pytest.fixture
def mock_llm_client():
    """Provides a mock LLM client that conforms to the LLMService."""
    mock = AsyncMock(spec=LLMClientProtocol)
    # Mock the 'chat' method, as that's what AIService uses
    mock.chat = AsyncMock(return_value="Mocked LLM response.")
    return mock

@pytest.fixture
def ai_service(mock_llm_client):
    """Provides an AIService instance with a mocked LLM client."""
    # AIService constructor only takes an llm_client
    return AIService(llm_client=mock_llm_client)

# --- AI Service Tests (Refactored) ---

@pytest.mark.asyncio
async def test_ai_service_initialization(ai_service, mock_llm_client):
    """Tests that the AIService initializes correctly with its LLM client."""
    assert ai_service.llm_client is mock_llm_client

@pytest.mark.asyncio
async def test_ai_service_query_success(ai_service, mock_llm_client):
    """Tests a successful query flow through the AI service."""
    user_prompt = "What is the test about?"
    response = await ai_service.query(user_prompt)

    # Verify that the llm_client's chat method was called correctly
    expected_messages = [{"role": "user", "content": user_prompt}]
    mock_llm_client.chat.assert_awaited_once_with(messages=expected_messages)
    
    # Verify the final output
    assert response == "Mocked LLM response."

@pytest.mark.asyncio
async def test_ai_service_query_with_empty_prompt(ai_service):
    """Tests that querying with an empty prompt raises an HTTPException."""
    with pytest.raises(HTTPException) as exc_info:
        await ai_service.query("")
    
    assert exc_info.value.status_code == 400
    assert "Prompt cannot be empty" in exc_info.value.detail

@pytest.mark.asyncio
async def test_ai_service_handles_llm_exception(ai_service, mock_llm_client):
    """Tests that the service properly handles exceptions from the LLM client."""
    mock_llm_client.chat.side_effect = Exception("LLM provider is down")
    
    with pytest.raises(HTTPException) as exc_info:
        await ai_service.query("A prompt that will fail")

    assert exc_info.value.status_code == 503
    assert "AI service is currently unavailable" in exc_info.value.detail
