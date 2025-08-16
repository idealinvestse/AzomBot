import pytest
from types import SimpleNamespace

import httpx

from app.pipelineserver.pipeline_app.services.llm_client import OpenAIClient


class FakeResponse:
    def __init__(self, json_data, raise_exc: Exception | None = None):
        self._json = json_data
        self._raise = raise_exc

    def json(self):
        return self._json

    def raise_for_status(self):
        if self._raise:
            raise self._raise


class FakeAsyncClient:
    def __init__(self, timeout=None):
        self.timeout = timeout
        self.is_closed = False
        self.calls = []
        self.next_response: FakeResponse | None = None

    async def post(self, url, json=None, headers=None):
        self.calls.append({"url": url, "json": json, "headers": headers})
        return self.next_response or FakeResponse({
            "choices": [{"message": {"role": "assistant", "content": "ok"}}]
        })

    async def aclose(self):
        self.is_closed = True


@pytest.mark.asyncio
async def test_openai_client_requires_api_key():
    with pytest.raises(ValueError, match="OpenAI API key is required"):
        OpenAIClient(config={}, timeout=5)


@pytest.mark.asyncio
async def test_openai_client_chat_success_default_model(monkeypatch):
    fake = FakeAsyncClient(timeout=5)
    monkeypatch.setattr(httpx, "AsyncClient", lambda timeout=None: fake)

    cfg = {
        "OPENAI_API_KEY": "sk-test",
        "OPENAI_BASE_URL": "https://api.openai.com/v1",
        "TARGET_MODEL": "gpt-4o-mini",
    }
    client = OpenAIClient(config=cfg, timeout=5)
    text = await client.chat([
        {"role": "user", "content": "Hello"}
    ])
    assert text == "ok"

    # Verify request shape
    assert len(fake.calls) == 1
    call = fake.calls[0]
    assert call["url"].endswith("/chat/completions")
    assert call["json"]["model"] == "gpt-4o-mini"
    assert call["json"]["messages"][0]["content"] == "Hello"
    assert call["headers"]["Authorization"].startswith("Bearer ")


@pytest.mark.asyncio
async def test_openai_client_chat_success_override_model_and_stream(monkeypatch):
    fake = FakeAsyncClient(timeout=10)
    monkeypatch.setattr(httpx, "AsyncClient", lambda timeout=None: fake)

    cfg = {
        "OPENAI_API_KEY": "sk-test",
        "OPENAI_BASE_URL": "https://gateway.example.com/v1",
        "TARGET_MODEL": "gpt-4o-mini",
    }
    client = OpenAIClient(config=cfg, timeout=10)
    text = await client.chat([
        {"role": "user", "content": "Hi"}
    ], model="gpt-4o", stream=True)
    assert text == "ok"

    call = fake.calls[0]
    assert call["url"] == "https://gateway.example.com/v1/chat/completions"
    assert call["json"]["model"] == "gpt-4o"
    assert call["json"]["stream"] is True


@pytest.mark.asyncio
async def test_openai_client_propagates_http_errors(monkeypatch):
    fake = FakeAsyncClient(timeout=5)
    fake.next_response = FakeResponse({}, raise_exc=httpx.HTTPStatusError(
        "Bad Request", request=SimpleNamespace(url="u"), response=SimpleNamespace(status_code=400)
    ))
    monkeypatch.setattr(httpx, "AsyncClient", lambda timeout=None: fake)

    cfg = {
        "OPENAI_API_KEY": "sk-test",
        "OPENAI_BASE_URL": "https://api.openai.com/v1",
    }
    client = OpenAIClient(config=cfg, timeout=5)

    with pytest.raises(httpx.HTTPStatusError):
        await client.chat([{"role": "user", "content": "Hello"}])

    await client.aclose()
    assert fake.is_closed is True
