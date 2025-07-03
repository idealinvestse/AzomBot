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
from typing import List, Dict, Any, Optional, Protocol, runtime_checkable
import httpx
from app.config import get_current_config
from fastapi import Depends

__all__ = ["LLMClient", "GroqClient", "get_llm_client", "LLMServiceProtocol"]

@runtime_checkable
class LLMServiceProtocol(Protocol):
    """Protocol for a unified LLM client interface."""
    async def chat(self, messages: List[Dict[str, str]], model: Optional[str] = None, stream: bool = False) -> str:
        ...

    async def aclose(self) -> None:
        ...



class LLMClient:
    """Very small async client for OpenWebUI chat completion requests."""
    """Very small async client for chat completion requests."""

    def __init__(self, config: Dict[str, Any], timeout: int = 30):
        self.base_url = (config.get("OPENWEBUI_URL") or "http://localhost:3000").rstrip("/")
        self.api_key = config.get("OPENWEBUI_API_TOKEN")
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

        # Ensure the URL is correct for OpenWebUI
        url = f"{self.base_url}/api/chat/completions" if not self.base_url.endswith('/api') else f"{self.base_url}/chat/completions"
        resp = await self._client.post(url, json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()

        # OpenAI-style return shape
        return data["choices"][0]["message"]["content"].strip()

    async def aclose(self) -> None:
        """Close underlying httpx client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()

class GroqClient:
    """Client for Groq Cloud API."""
    
    def __init__(self, config: Dict[str, Any], timeout: int = 30):
        self.api_key = config.get("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("Groq API key is required.")
        self.base_url = "https://api.groq.com/openai/v1"
        self._timeout = timeout
        self._client: httpx.AsyncClient | None = None

    async def chat(self, messages: List[Dict[str, str]], model: Optional[str] = None, stream: bool = False) -> str:
        payload: Dict[str, Any] = {
            "messages": messages, 
            "model": model or "llama3-8b-8192", # Default Groq model
            "stream": stream
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=self._timeout)

        resp = await self._client.post(f"{self.base_url}/chat/completions", json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()

    async def aclose(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()


# --- Client Factory ---

_clients: Dict[str, LLMServiceProtocol] = {}

async def get_llm_client(config: Dict[str, Any] = Depends(get_current_config)) -> LLMServiceProtocol:
    """Factory dependency that provides the correct LLM client based on runtime settings."""
    backend = config.get("LLM_BACKEND", "openwebui").lower()
    
    # Use a simple cache to avoid re-creating clients on every request
    if backend in _clients:
        return _clients[backend]

    if backend == 'groq':
        client = GroqClient(config)
    elif backend == 'openwebui':
        client = LLMClient(config)
    else:
        raise ValueError(f"Unsupported LLM backend: {backend}")
    
    _clients[backend] = client
    return client
