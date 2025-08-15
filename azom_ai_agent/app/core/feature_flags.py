from __future__ import annotations

from app.core.modes import Mode

# Centralized, mode-based feature flags and limits.
# In future, these can read from environment or settings for more flexibility.


def allow_external_llm(mode: Mode | None) -> bool:
    """Whether external LLM providers (e.g., Groq) are allowed for current mode."""
    m = mode or Mode.FULL
    return m == Mode.FULL


def allow_embeddings(mode: Mode | None) -> bool:
    """Whether embeddings/vector operations are allowed for current mode."""
    m = mode or Mode.FULL
    return m == Mode.FULL


def rag_enabled(mode: Mode | None) -> bool:
    """Whether RAG/vector retrieval should be used for current mode."""
    return allow_embeddings(mode)


def llm_timeout_seconds(mode: Mode | None) -> int:
    """Timeout to use for LLM HTTP calls, per mode (stricter in Light)."""
    m = mode or Mode.FULL
    return 10 if m == Mode.LIGHT else 30


def payload_cap_bytes(mode: Mode | None) -> int:
    """Optional payload cap for requests; not yet enforced in endpoints."""
    m = mode or Mode.FULL
    return 8_000 if m == Mode.LIGHT else 32_000
