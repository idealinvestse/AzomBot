import os
import json
import requests

class GroqService:
    def __init__(self, api_key: str = None, api_url: str = None, model: str = None):
        if not api_key:
            raise ValueError("API key cannot be empty")
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.api_url = api_url or os.getenv("GROQ_API_URL", "https://api.groq.com/openai/v1/chat/completions")

        # Förval: env-variabel eller parameter
        self.model = model or os.getenv("GROQ_MODEL", "llama3-70b-8192")

        # Dynamic override via llm_settings.json om den finns
        settings_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../pipelineserver/pipeline_app/data/llm_settings.json'))
        if os.path.exists(settings_path):
            try:
                with open(settings_path, encoding='utf-8') as f:
                    data = json.load(f)
                    self.model = data.get('model_id', self.model)
            except Exception:
                # Ignorera fel och använd tidigare modell
                pass

    def chat(self, messages: list, temperature: float = 0.3, max_tokens: int = 1024, model: str | None = None):
        if not messages:
            raise ValueError("Messages cannot be empty")
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model or self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        response = requests.post(self.api_url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()

# Example usage:
# groq = GroqService()
# result = groq.chat([
#     {"role": "user", "content": "Hello, who are you?"}
# ])
# print(result)
