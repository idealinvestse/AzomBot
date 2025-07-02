import os
from .ai_service import AIService
from .groq_service import GroqService

class LLMService:
    def __init__(self, backend="openwebui", openwebui_url=None, api_token=None, model=None, groq_api_key=None):
        self.backend = backend
        if backend == "openwebui":
            self.client = AIService(openwebui_url, api_token, model)
        elif backend == "groq":
            self.client = GroqService(groq_api_key)
        else:
            raise ValueError(f"Unsupported backend: {backend}")

    def chat(self, messages, **kwargs):
        if not messages:
            raise ValueError("Messages cannot be empty")
        if self.backend == "groq":
            response = self.client.chat(messages, **kwargs)
            return response
        else:
            # OpenWebUI
            content = self.client.query(messages[-1]["content"], context={"messages": messages[:-1]})
            return {"choices": [{"message": {"role": "assistant", "content": content}}]}

    def query(self, user_prompt: str, context: dict | None = None):
        """Unified helper used by legacy code expecting .query."""
        if self.backend == "groq":
            # Map to OpenAI-style chat and extract text content
            messages = []
            if context:
                # Provide system context if available
                messages.append({"role": "system", "content": context.get("system", "Du är en hjälpsam assistent.")})
            messages.append({"role": "user", "content": user_prompt})
            try:
                res = self.client.chat(messages)
                return res["choices"][0]["message"]["content"]
            except Exception:
                return "Tyvärr kan vi inte svara just nu."
        else:
            return self.client.query(user_prompt, context=context)

    def update_config(self, **kwargs):
        """Runtime update of underlying client without recreation."""
        backend = kwargs.get("backend")
        if backend and backend.lower() != self.backend:
            # Recreate with new backend
            self.__init__({"backend": backend})

        if self.backend == "groq":
            model = kwargs.get("groq_model") or kwargs.get("model")
            if model:
                setattr(self.client, "model", model)
            api_key = kwargs.get("groq_api_key")
            if api_key:
                setattr(self.client, "api_key", api_key)
        else:
            # OpenWebUI params
            self.client.update_config(
                openwebui_url=kwargs.get("openwebui_url"),
                api_token=kwargs.get("api_token"),
                model=kwargs.get("model"),
            )
