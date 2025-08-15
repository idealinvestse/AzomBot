import pytest

from app.core.modes import Mode
from app.core.feature_flags import (
    allow_external_llm,
    allow_embeddings,
    rag_enabled,
    llm_timeout_seconds,
    payload_cap_bytes,
)


def test_allow_external_llm():
    assert allow_external_llm(Mode.FULL) is True
    assert allow_external_llm(Mode.LIGHT) is False
    # None defaults to FULL behavior
    assert allow_external_llm(None) is True


def test_allow_embeddings_and_rag_enabled():
    assert allow_embeddings(Mode.FULL) is True
    assert allow_embeddings(Mode.LIGHT) is False
    assert rag_enabled(Mode.FULL) is True
    assert rag_enabled(Mode.LIGHT) is False


def test_llm_timeout_seconds():
    assert llm_timeout_seconds(Mode.LIGHT) == 10
    assert llm_timeout_seconds(Mode.FULL) == 30
    assert llm_timeout_seconds(None) == 30


def test_payload_cap_bytes():
    assert payload_cap_bytes(Mode.LIGHT) == 8000
    assert payload_cap_bytes(Mode.FULL) == 32000
    assert payload_cap_bytes(None) == 32000
