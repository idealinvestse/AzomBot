from typing import Protocol, runtime_checkable, Any, Dict, List, Tuple, Union

@runtime_checkable
class LLMClientProtocol(Protocol):
    """
    Protocol for a generic LLM client, ensuring a consistent API for different backends.
    This helps in decoupling services from concrete client implementations.
    """
    async def query(self, prompt: str, context: Dict[str, Any] | None = None) -> Union[str, Tuple[str, List[str]]]:
        """Sends a query and returns a response."""
        ...

    async def chat(self, messages: List[Dict[str, str]], **kwargs: Any) -> Dict[str, Any]:
        """Sends a list of messages for a chat-based interaction."""
        ...

    def update_config(self, **kwargs: Any) -> None:
        """Updates the client's configuration dynamically."""
        ...
