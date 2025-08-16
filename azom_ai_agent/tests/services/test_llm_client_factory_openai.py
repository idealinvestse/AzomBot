import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
import pytest
from starlette.requests import Request

from app.core.modes import Mode
from app.pipelineserver.pipeline_app.services.llm_client import (
    get_llm_client,
    LLMClient,
    OpenAIClient,
    _clients,
)


@pytest.mark.asyncio
async def test_factory_forces_openwebui_in_light_mode_when_openai_configured():
    _clients.clear()

    scope = {"type": "http", "headers": []}
    req = Request(scope)
    req.state.mode = Mode.LIGHT

    config = {
        "LLM_BACKEND": "openai",
        "OPENAI_API_KEY": "sk-test",
        "OPENAI_BASE_URL": "https://api.openai.com/v1",
        "OPENWEBUI_URL": "http://localhost:3000",
    }

    client = await get_llm_client(req, config=config)
    assert isinstance(client, LLMClient), "Light mode must force OpenWebUI even if OpenAI is configured"


@pytest.mark.asyncio
async def test_factory_uses_openai_in_full_mode_when_configured():
    _clients.clear()

    scope = {"type": "http", "headers": []}
    req = Request(scope)
    req.state.mode = Mode.FULL

    config = {
        "LLM_BACKEND": "openai",
        "OPENAI_API_KEY": "sk-test",
        "OPENAI_BASE_URL": "https://api.openai.com/v1",
        "TARGET_MODEL": "gpt-4o-mini",
    }

    client = await get_llm_client(req, config=config)
    assert isinstance(client, OpenAIClient), "Full mode should honor configured OpenAI backend"
