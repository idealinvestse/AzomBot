"""Minimal OpenWebUI/Ollama (OpenAI-compatible) async client.

This small helper wraps an async HTTP call to a locally running OpenWebUI
instance (or any service that exposes the `/api/chat/completions` route with
OpenAI-compatible JSON).

Environment variables:
    OPENWEBUI_API_URL  – Base URL to the API (default http://localhost:3000/api)
    OPENWEBUI_API_KEY  – Bearer token if the instance is secured.
"""
from __future__ import annotations

import os
from typing import List, Dict, Any, Optional

import httpx
from functools import lru_cache

__all__ = ["LLMClient"]


class LLMClient:
    """Very small async client for chat completion requests."""

    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None, timeout: int = 30):
        self.base_url = (base_url or os.getenv("OPENWEBUI_API_URL", "http://localhost:3000/api")).rstrip("/")
        self.api_key = api_key or os.getenv("OPENWEBUI_API_KEY")
        self._timeout = timeout
        # Reuse a single AsyncClient with keep-alive
        self._client: httpx.AsyncClient | None = None

    async def chat(self, messages: List[Dict[str, str]], model: Optional[str] = None, stream: bool = False) -> str:
        """Send an OpenAI-style chat completion request and return the assistant message string.

        Args:
            messages: list with dictionaries – at minimum: {"role":"user","content":".."}
            model: optional model override (OpenWebUI supports this field and will pick
                   whatever is configured in its backend if omitted).
            stream: if True, a streaming response is requested. Only non-streaming is returned
                    to the caller; this flag is mainly for future extension.
        """
        payload: Dict[str, Any] = {"messages": messages, "stream": stream}
        if model:
            payload["model"] = model

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        if self._client is None or self._client.is_closed:
            # create lazily, reuse thereafter
            self._client = httpx.AsyncClient(timeout=self._timeout)

        resp = await self._client.post(f"{self.base_url}/chat/completions", json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()

        # OpenAI-style return shape
        return data["choices"][0]["message"]["content"].strip()

    async def aclose(self) -> None:
        """Close underlying httpx client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
