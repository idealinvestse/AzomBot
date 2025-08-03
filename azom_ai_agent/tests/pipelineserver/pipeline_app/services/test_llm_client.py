import pytest
import httpx
from unittest.mock import patch
from app.pipelineserver.pipeline_app.services.llm_client import LLMClient, GroqClient, get_llm_client

# Fixture to reset the client cache before each test
@pytest.fixture(autouse=True)
def clear_client_cache():
    from app.pipelineserver.pipeline_app.services import llm_client
    llm_client._clients.clear()
    yield

@pytest.mark.asyncio
async def test_get_llm_client_returns_llmclient_by_default():
    """Test that the factory returns an LLMClient when backend is 'openwebui' or default."""
    config = {"LLM_BACKEND": "openwebui"}
    client = await get_llm_client(config)
    assert isinstance(client, LLMClient)

@pytest.mark.asyncio
async def test_get_llm_client_returns_groqclient():
    """Test that the factory returns a GroqClient when backend is 'groq'."""
    config = {"LLM_BACKEND": "groq", "GROQ_API_KEY": "test-key"}
    client = await get_llm_client(config)
    assert isinstance(client, GroqClient)

@pytest.mark.asyncio
async def test_get_llm_client_raises_error_for_unsupported_backend():
    """Test that a ValueError is raised for an unsupported backend."""
    config = {"LLM_BACKEND": "unsupported_backend"}
    with pytest.raises(ValueError, match="Unsupported LLM backend: unsupported_backend"):
        await get_llm_client(config)

@pytest.mark.asyncio
async def test_get_llm_client_caches_instances():
    """Test that the factory caches and reuses client instances."""
    config = {"LLM_BACKEND": "openwebui"}
    client1 = await get_llm_client(config)
    client2 = await get_llm_client(config)
    assert client1 is client2

@pytest.mark.asyncio
async def test_llmclient_successful_chat(httpx_mock):
    """Test a successful chat call with LLMClient."""
    httpx_mock.add_response(
        url="http://localhost:3000/api/chat/completions",
        json={"choices": [{"message": {"content": "  Hello there!  "}}]}
    )
    config = {"OPENWEBUI_URL": "http://localhost:3000"}
    client = LLMClient(config)
    response = await client.chat(messages=[{"role": "user", "content": "Hi"}])
    assert response == "Hello there!"
    await client.aclose()

@pytest.mark.asyncio
async def test_groqclient_raises_error_if_no_key():
    """Test that GroqClient raises a ValueError if the API key is missing."""
    with pytest.raises(ValueError, match="Groq API key is required."):
        GroqClient(config={})

@pytest.mark.asyncio
async def test_groqclient_successful_chat(httpx_mock):
    """Test a successful chat call with GroqClient."""
    httpx_mock.add_response(
        url="https://api.groq.com/openai/v1/chat/completions",
        json={"choices": [{"message": {"content": "Response from Groq."}}]}
    )
    config = {"GROQ_API_KEY": "test-key"}
    client = GroqClient(config)
    response = await client.chat(messages=[{"role": "user", "content": "Hi"}])
    assert response == "Response from Groq."
    request = httpx_mock.get_request()
    assert request.headers["authorization"] == "Bearer test-key"
    await client.aclose()

@pytest.mark.asyncio
async def test_client_handles_http_error(httpx_mock):
    """Test that the client properly handles HTTP errors by calling raise_for_status."""
    httpx_mock.add_response(status_code=500)
    config = {"OPENWEBUI_URL": "http://localhost:3000"}
    client = LLMClient(config)
    with pytest.raises(httpx.HTTPStatusError):
        await client.chat(messages=[{"role": "user", "content": "Hi"}])
    await client.aclose()
