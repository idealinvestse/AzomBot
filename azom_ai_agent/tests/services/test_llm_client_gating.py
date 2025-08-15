import asyncio
import pytest
from starlette.requests import Request

from app.core.modes import Mode
from app.pipelineserver.pipeline_app.services.llm_client import (
    get_llm_client,
    LLMClient,
    GroqClient,
    _clients,
)

@pytest.mark.asyncio
async def test_get_llm_client_forces_openwebui_in_light_mode():
    # Ensure clean client cache
    _clients.clear()

    # Fake request with Light mode in state
    scope = {"type": "http", "headers": []}
    req = Request(scope)
    req.state.mode = Mode.LIGHT

    # Config intentionally asks for Groq
    config = {
        "LLM_BACKEND": "groq",
        "GROQ_API_KEY": "test-key",
        "OPENWEBUI_URL": "http://localhost:3000",
    }

    client = await get_llm_client(req, config=config)
    assert isinstance(client, LLMClient), "Light mode must force OpenWebUI backend"

@pytest.mark.asyncio
async def test_get_llm_client_uses_config_backend_in_full_mode():
    _clients.clear()

    scope = {"type": "http", "headers": []}
    req = Request(scope)
    req.state.mode = Mode.FULL

    config = {
        "LLM_BACKEND": "groq",
        "GROQ_API_KEY": "test-key",
        "OPENWEBUI_URL": "http://localhost:3000",
    }

    client = await get_llm_client(req, config=config)
    assert isinstance(client, GroqClient), "Full mode should honor configured Groq backend"
