import sys
import os
import pytest
from unittest.mock import patch, MagicMock

# Add the project root to sys.path to resolve imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.append(project_root)

try:
    from app.services.llm_service import LLMService
    LLM_SERVICE_AVAILABLE = True
except ImportError:
    LLM_SERVICE_AVAILABLE = False

try:
    from app.services.ai_service import AIService
    AI_SERVICE_AVAILABLE = True
except ImportError:
    AI_SERVICE_AVAILABLE = False

try:
    from app.services.groq_service import GroqService
    GROQ_SERVICE_AVAILABLE = True
except ImportError:
    GROQ_SERVICE_AVAILABLE = False

try:
    from app.services.test_llm_service import TestLLMService
    TEST_LLM_SERVICE_AVAILABLE = True
except ImportError:
    TEST_LLM_SERVICE_AVAILABLE = False

@pytest.mark.skipif(not LLM_SERVICE_AVAILABLE, reason="LLMService class not available")
class TestLLMService:
    def setup_method(self):
        """Setup method to initialize common test fixtures."""
        self.service_openwebui = LLMService(backend="openwebui", openwebui_url="http://localhost:3000", api_token="test_token", model="test_model")
        if GROQ_SERVICE_AVAILABLE:
            self.service_groq = LLMService(backend="groq", groq_api_key="test_key")

    def test_initialization_openwebui(self):
        """Test that LLMService initializes correctly with OpenWebUI backend."""
        assert self.service_openwebui is not None
        assert self.service_openwebui.backend == "openwebui"
        if AI_SERVICE_AVAILABLE:
            assert isinstance(self.service_openwebui.client, AIService)

    @pytest.mark.skipif(not GROQ_SERVICE_AVAILABLE, reason="GroqService class not available")
    def test_initialization_groq(self):
        """Test that LLMService initializes correctly with Groq backend."""
        assert self.service_groq is not None
        assert self.service_groq.backend == "groq"
        assert isinstance(self.service_groq.client, GroqService)

    def test_initialization_unsupported_backend(self):
        """Test that LLMService raises ValueError for unsupported backend."""
        with pytest.raises(ValueError, match="Unsupported backend: invalid"):
            LLMService(backend="invalid")

    def test_chat_empty_messages(self):
        """Test chat method with an empty message list, expecting an exception."""
        with pytest.raises(ValueError, match="Messages cannot be empty"):
            self.service_openwebui.chat([])

    @pytest.mark.skipif(not AI_SERVICE_AVAILABLE, reason="AIService class not available")
    @patch('app.services.ai_service.AIService.query')
    def test_chat_openwebui_backend(self, mock_query):
        """Test chat method with OpenWebUI backend."""
        mock_response = "Hello from OpenWebUI"
        mock_query.return_value = mock_response
        messages = [{"role": "user", "content": "Hi!"}]
        result = self.service_openwebui.chat(messages)
        mock_query.assert_called_once_with("Hi!", context={"messages": []})
        assert result["choices"][0]["message"]["content"] == mock_response

    @pytest.mark.skipif(not AI_SERVICE_AVAILABLE, reason="AIService class not available")
    @patch('app.services.ai_service.AIService.query')
    def test_chat_openwebui_backend_error(self, mock_query):
        """Test chat method with OpenWebUI backend handling errors."""
        mock_query.side_effect = Exception("OpenWebUI error")
        messages = [{"role": "user", "content": "Hi!"}]
        with pytest.raises(Exception) as exc_info:
            self.service_openwebui.chat(messages)
        assert str(exc_info.value) == "OpenWebUI error"

    @pytest.mark.skipif(not GROQ_SERVICE_AVAILABLE, reason="GroqService class not available")
    @patch('app.services.groq_service.GroqService.chat')
    def test_chat_groq_backend(self, mock_chat):
        """Test chat method with Groq backend."""
        mock_response = {"choices": [{"message": {"role": "assistant", "content": "Hello from Groq"}}]}
        mock_chat.return_value = mock_response
        messages = [{"role": "user", "content": "Hi!"}]
        result = self.service_groq.chat(messages)
        mock_chat.assert_called_once_with(messages)
        assert result == mock_response

    @pytest.mark.skipif(not GROQ_SERVICE_AVAILABLE, reason="GroqService class not available")
    @patch('app.services.groq_service.GroqService.chat')
    def test_chat_groq_backend_error(self, mock_chat):
        """Test chat method with Groq backend handling errors."""
        mock_chat.side_effect = Exception("Groq error")
        messages = [{"role": "user", "content": "Hi!"}]
        with pytest.raises(Exception) as exc_info:
            self.service_groq.chat(messages)
        assert str(exc_info.value) == "Groq error"

    @pytest.mark.skipif(not AI_SERVICE_AVAILABLE, reason="AIService class not available")
    @patch('app.services.ai_service.AIService.query')
    def test_query_openwebui_backend(self, mock_query):
        """Test query method with OpenWebUI backend."""
        mock_response = "Response from OpenWebUI"
        mock_query.return_value = mock_response
        result = self.service_openwebui.query("Test query", context={"system": "Test context"})
        mock_query.assert_called_once_with("Test query", context={"system": "Test context"})
        assert result == mock_response

    @pytest.mark.skipif(not AI_SERVICE_AVAILABLE, reason="AIService class not available")
    @patch('app.services.ai_service.AIService.query')
    def test_query_openwebui_backend_no_context(self, mock_query):
        """Test query method with OpenWebUI backend without context."""
        mock_response = "Response from OpenWebUI"
        mock_query.return_value = mock_response
        result = self.service_openwebui.query("Test query", context=None)
        mock_query.assert_called_once_with("Test query", context=None)
        assert result == mock_response

    @pytest.mark.skipif(not GROQ_SERVICE_AVAILABLE, reason="GroqService class not available")
    @patch('app.services.groq_service.GroqService.chat')
    def test_query_groq_backend(self, mock_chat):
        """Test query method with Groq backend."""
        mock_response = {"choices": [{"message": {"role": "assistant", "content": "Response from Groq"}}]}
        mock_chat.return_value = mock_response
        result = self.service_groq.query("Test query", context={"system": "Test context"})
        mock_chat.assert_called_once_with([{"role": "system", "content": "Test context"}, {"role": "user", "content": "Test query"}])
        assert result == "Response from Groq"

    @pytest.mark.skipif(not GROQ_SERVICE_AVAILABLE, reason="GroqService class not available")
    @patch('app.services.groq_service.GroqService.chat')
    def test_query_groq_backend_no_context(self, mock_chat):
        """Test query method with Groq backend without context."""
        mock_response = {"choices": [{"message": {"role": "assistant", "content": "Response from Groq"}}]}
        mock_chat.return_value = mock_response
        result = self.service_groq.query("Test query", context=None)
        mock_chat.assert_called_once_with([{"role": "user", "content": "Test query"}])
        assert result == "Response from Groq"

    @pytest.mark.skipif(not GROQ_SERVICE_AVAILABLE, reason="GroqService class not available")
    @patch('app.services.groq_service.GroqService.chat')
    def test_query_groq_backend_error(self, mock_chat):
        """Test query method with Groq backend handling errors."""
        mock_chat.side_effect = Exception("Groq error")
        result = self.service_groq.query("Test query", context={"system": "Test context"})
        assert result == "Tyvärr kan vi inte svara just nu."

    @pytest.mark.skipif(not AI_SERVICE_AVAILABLE, reason="AIService class not available")
    @patch('app.services.ai_service.AIService.update_config')
    def test_update_config_openwebui(self, mock_update_config):
        """Test update_config method with OpenWebUI backend."""
        new_url = "http://localhost:4000"
        new_token = "new_token"
        new_model = "new_model"
        self.service_openwebui.update_config(openwebui_url=new_url, api_token=new_token, model=new_model)
        mock_update_config.assert_called_once_with(openwebui_url=new_url, api_token=new_token, model=new_model)

    @pytest.mark.skipif(not GROQ_SERVICE_AVAILABLE, reason="GroqService class not available")
    def test_update_config_groq(self):
        """Test update_config method with Groq backend (no-op)."""
        # Since GroqService does not have update_config, this should not raise an error but do nothing
        self.service_groq.update_config()
        # No assertion needed as it's a no-op
