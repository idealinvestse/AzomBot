import requests
from app.prompt_utils import compose_full_prompt

class AIService:
    def __init__(self, openwebui_url: str, api_token: str, model: str):
        self.url = openwebui_url
        self.token = api_token
        self.model = model

    def update_config(self, *, openwebui_url: str | None = None, api_token: str | None = None, model: str | None = None):
        """Update runtime configuration without recreating instance."""
        if openwebui_url is not None:
            self.url = openwebui_url
        if api_token is not None:
            self.token = api_token
        if model is not None:
            self.model = model

    def query(self, user_prompt: str, context=None) -> str:
        if not user_prompt:
            raise ValueError("Prompt cannot be empty")
        context = context or {}  # t.ex. {"USER_NAME": ..., "safety_flag": ..., "session_memory": ..., ...}
        full_prompt = compose_full_prompt(user_prompt, context)
        headers = {"Authorization": f"Bearer {self.token}"}
        payload = {"model": self.model, "prompt": full_prompt}
        try:
            res = requests.post(f"{self.url}/api/chat", json=payload, headers=headers, timeout=10)
            res.raise_for_status()
            return res.json().get('response', 'Inget svar.')
        except Exception:
            return "Tyvärr kan vi inte svara automatiskt just nu. Vänligen kontakta support eller prova igen senare."
