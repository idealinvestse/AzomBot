from typing import Dict, Any
from app.prompt_utils import compose_full_prompt
from app.services.protocols import LLMClientProtocol
from fastapi import Depends, HTTPException, status

class AIService:
    """Service layer for handling AI-related business logic."""

    def __init__(self, llm_client: LLMClientProtocol):
        self.llm_client = llm_client

    def update_config(self, **kwargs: Any) -> None:
        """Placeholder for dynamic configuration updates."""
        # This service is a facade, so config is handled by the underlying client.
        if hasattr(self.llm_client, 'update_config') and callable(getattr(self.llm_client, 'update_config')):
            self.llm_client.update_config(**kwargs)



    async def query(self, user_prompt: str, context: Dict[str, Any] | None = None) -> str:
        """Processes a user query by composing a full prompt and querying the LLM."""
        if not user_prompt:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Prompt cannot be empty"
            )
        
        context = context or {}
        # The system prompt is now managed by the llm_client/prompt_utils, 
        # so we only need to send the user message.
        messages = [
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            # The model is now selected based on the backend configuration
            response = await self.llm_client.chat(messages=messages)
            return response
        except Exception as e:
            # Log the exception properly in a real app
            print(f"Error querying LLM: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="The AI service is currently unavailable. Please try again later."
            )
