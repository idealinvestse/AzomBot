import pytest

from app.services.ai_service import AIService

class DummyLLM:
    def __init__(self):
        self.last_messages = None
    async def chat(self, messages, model=None, stream: bool = False):
        self.last_messages = messages
        return "ok"
    async def aclose(self):
        return None

@pytest.mark.asyncio
async def test_ai_service_light_mode_uses_system_and_user(monkeypatch):
    # Stub compose_full_prompt to a deterministic output
    async def fake_compose_full_prompt(user_prompt: str, context: dict) -> str:
        return f"SYS-PROMPT\n\n{user_prompt}"
    monkeypatch.setattr(
        'app.services.ai_service.compose_full_prompt',
        fake_compose_full_prompt,
        raising=True,
    )

    dummy = DummyLLM()
    svc = AIService(llm_client=dummy)

    resp = await svc.query("hello", context={"azom_mode": "light"})
    assert resp == "ok"
    assert dummy.last_messages is not None
    assert len(dummy.last_messages) == 2
    assert dummy.last_messages[0]["role"] == "system"
    # System content should not include the user prompt in Light mode
    assert "SYS-PROMPT" in dummy.last_messages[0]["content"]
    assert "hello" not in dummy.last_messages[0]["content"]
    assert dummy.last_messages[1] == {"role": "user", "content": "hello"}

@pytest.mark.asyncio
async def test_ai_service_full_mode_user_only(monkeypatch):
    # Ensure compose_full_prompt is not required in full mode
    dummy = DummyLLM()
    svc = AIService(llm_client=dummy)

    resp = await svc.query("hej", context={"azom_mode": "full"})
    assert resp == "ok"
    assert dummy.last_messages is not None
    assert len(dummy.last_messages) == 1
    assert dummy.last_messages[0] == {"role": "user", "content": "hej"}
