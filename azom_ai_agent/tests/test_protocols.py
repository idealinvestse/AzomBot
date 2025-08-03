import pytest
from typing import Any, Dict, List, Tuple, Union

# Adjust path to import the protocol
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.protocols import LLMClientProtocol

# A class that correctly implements the protocol
class ValidLLMClient:
    async def query(self, prompt: str, context: Dict[str, Any] | None = None) -> Union[str, Tuple[str, List[str]]]:
        return "valid query response"

    async def chat(self, messages: List[Dict[str, str]], **kwargs: Any) -> Dict[str, Any]:
        return {"response": "valid chat response"}

    def update_config(self, **kwargs: Any) -> None:
        pass

# A class that is missing one of the required methods
class IncompleteLLMClient:
    async def query(self, prompt: str, context: Dict[str, Any] | None = None) -> Union[str, Tuple[str, List[str]]]:
        return "incomplete query response"

    async def chat(self, messages: List[Dict[str, str]], **kwargs: Any) -> Dict[str, Any]:
        return {"response": "incomplete chat response"}


def test_llm_client_protocol_runtime_check():
    """
    Tests the LLMClientProtocol's runtime checkability.
    Verifies that a class that correctly implements the protocol passes the
    isinstance check, while a class that does not is correctly identified.
    """
    valid_client = ValidLLMClient()
    incomplete_client = IncompleteLLMClient()

    assert isinstance(valid_client, LLMClientProtocol)
    assert not isinstance(incomplete_client, LLMClientProtocol)
