import sys
import os
import pytest
from unittest.mock import patch, AsyncMock
from fastapi import HTTPException

# Add the project root to sys.path to resolve imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.append(project_root)

from app.services.llm_service import LLMService
from app.services.ai_service import AIService
from app.services.groq_service import GroqService

class TestLLMService:
    def setup_method(self):
        """Setup method to initialize common test fixtures."""
        self.service_openwebui = LLMService(backend="openwebui", openwebui_url="http://localhost:3000", api_token="test_token", model="test_model")
        self.service_groq = LLMService(backend="groq", groq_api_key="test_key")

    def test_initialization_openwebui(self):
        assert self.service_openwebui is not None
        assert self.service_openwebui.backend == "openwebui"
        assert isinstance(self.service_openwebui.client, AIService)

    def test_initialization_groq(self):
        assert self.service_groq is not None
        assert self.service_groq.backend == "groq"
        assert isinstance(self.service_groq.client, GroqService)

    def test_initialization_unsupported_backend(self):
        with pytest.raises(ValueError, match="Unsupported backend: invalid"):
            LLMService(backend="invalid")

    @pytest.mark.asyncio
    async def test_chat_empty_messages(self):
        with pytest.raises(ValueError, match="Messages cannot be empty"):
            await self.service_openwebui.chat([])

    @pytest.mark.asyncio
    @patch('app.services.ai_service.AIService.query', new_callable=AsyncMock)
    async def test_chat_openwebui_backend(self, mock_query):
        mock_response = "Hello from OpenWebUI"
        mock_query.return_value = mock_response
        messages = [{"role": "user", "content": "Hi!"}]
        result = await self.service_openwebui.chat(messages)
        mock_query.assert_called_once_with("Hi!", context={"messages": []})
        assert result["choices"][0]["message"]["content"] == mock_response

    @pytest.mark.asyncio
    @patch('app.services.ai_service.AIService.query', new_callable=AsyncMock)
    async def test_chat_openwebui_backend_error(self, mock_query):
        mock_query.side_effect = HTTPException(status_code=500, detail="OpenWebUI error")
        messages = [{"role": "user", "content": "Hi!"}]
        with pytest.raises(HTTPException) as exc_info:
            await self.service_openwebui.chat(messages)
        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == "OpenWebUI error"

    @pytest.mark.asyncio
    @patch('app.services.groq_service.GroqService.chat', new_callable=AsyncMock)
    async def test_chat_groq_backend(self, mock_chat):
        mock_response = {"choices": [{"message": {"role": "assistant", "content": "Hello from Groq"}}]}
        mock_chat.return_value = mock_response
        messages = [{"role": "user", "content": "Hi!"}]
        result = await self.service_groq.chat(messages)
        mock_chat.assert_called_once_with(messages)
        assert result == mock_response

    @pytest.mark.asyncio
    @patch('app.services.groq_service.GroqService.chat', new_callable=AsyncMock)
    async def test_chat_groq_backend_error(self, mock_chat):
        mock_chat.side_effect = Exception("Groq error")
        messages = [{"role": "user", "content": "Hi!"}]
        with pytest.raises(Exception, match="Groq error"):
            await self.service_groq.chat(messages)

    @pytest.mark.asyncio
    @patch('app.services.ai_service.AIService.query', new_callable=AsyncMock)
    async def test_query_openwebui_backend(self, mock_query):
        mock_response = "Response from OpenWebUI"
        mock_query.return_value = mock_response
        result = await self.service_openwebui.query("Test query", context={"system": "Test context"})
        mock_query.assert_called_once_with("Test query", context={"system": "Test context"})
        assert result == mock_response

    @pytest.mark.asyncio
    @patch('app.services.ai_service.AIService.query', new_callable=AsyncMock)
    async def test_query_openwebui_backend_no_context(self, mock_query):
        mock_response = "Response from OpenWebUI"
        mock_query.return_value = mock_response
        result = await self.service_openwebui.query("Test query", context=None)
        mock_query.assert_called_once_with("Test query", context=None)
        assert result == mock_response

    @pytest.mark.asyncio
    @patch('app.services.groq_service.GroqService.chat', new_callable=AsyncMock)
    async def test_query_groq_backend(self, mock_chat):
        mock_response = {"choices": [{"message": {"role": "assistant", "content": "Response from Groq"}}]}
        mock_chat.return_value = mock_response
        result = await self.service_groq.query("Test query", context={"system": "Test context"})
        mock_chat.assert_called_once_with([{"role": "system", "content": "Test context"}, {"role": "user", "content": "Test query"}])
        assert result == "Response from Groq"

    @pytest.mark.asyncio
    @patch('app.services.groq_service.GroqService.chat', new_callable=AsyncMock)
    async def test_query_groq_backend_no_context(self, mock_chat):
        mock_response = {"choices": [{"message": {"role": "assistant", "content": "Response from Groq"}}]}
        mock_chat.return_value = mock_response
        result = await self.service_groq.query("Test query", context=None)
        mock_chat.assert_called_once_with([{"role": "user", "content": "Test query"}])
        assert result == "Response from Groq"

    @pytest.mark.asyncio
    @patch('app.services.groq_service.GroqService.chat', new_callable=AsyncMock)
    async def test_query_groq_backend_error(self, mock_chat):
        mock_chat.side_effect = Exception("Groq error")
        result = await self.service_groq.query("Test query", context={"system": "Test context"})
        assert result == "Tyvärr kan vi inte svara just nu."

    def test_update_config_groq_noop(self):
        """Tests that update_config is a no-op for Groq backend and doesn't raise an error."""
        try:
            self.service_groq.update_config(model="new-model")
        except Exception as e:
            pytest.fail(f"update_config with groq backend should be a no-op but raised {e}")

    @patch.object(AIService, 'update_config')
    def test_update_config_openwebui(self, mock_update):
        """Tests update_config for the OpenWebUI backend."""
        self.service_openwebui.update_config(model="new-model")
        mock_update.assert_called_once_with(model="new-model")


