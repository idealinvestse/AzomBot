import sys
import os
import pytest

# Add the project root to sys.path to resolve imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.append(project_root)

try:
    from app.services.test_llm_service import TestLLMService
    TEST_LLM_SERVICE_AVAILABLE = True
except ImportError:
    TEST_LLM_SERVICE_AVAILABLE = False

@pytest.mark.skipif(not TEST_LLM_SERVICE_AVAILABLE, reason="TestLLMService class not available")
class TestTestLLMService:
    def setup_method(self):
        """Setup method to initialize common test fixtures."""
        self.service = TestLLMService()

    def test_initialization(self):
        """Test that the TestLLMService initializes correctly."""
        assert self.service is not None
        assert hasattr(self.service, 'generate_response')
        assert hasattr(self.service, 'chat')
        assert hasattr(self.service, 'query')

    def test_generate_response_basic(self):
        """Test generate_response with a basic input."""
        response = self.service.generate_response("Hello")
        assert isinstance(response, str)
        assert len(response) > 0

    def test_generate_response_empty_input(self):
        """Test generate_response with an empty input string."""
        response = self.service.generate_response("")
        assert isinstance(response, str)
        assert "default response" in response.lower() or "empty input" in response.lower() or len(response) > 0

    def test_generate_response_long_input(self):
        """Test generate_response with a long input string."""
        long_input = "a" * 1000
        response = self.service.generate_response(long_input)
        assert isinstance(response, str)
        assert len(response) > 0

    def test_generate_response_special_characters(self):
        """Test generate_response with special characters in input."""
        special_input = "Hello!@#$%^&*()"
        response = self.service.generate_response(special_input)
        assert isinstance(response, str)
        assert len(response) > 0

    def test_generate_response_multiple_calls(self):
        """Test generate_response with multiple consecutive calls."""
        for i in range(3):
            response = self.service.generate_response(f"Test call {i}")
            assert isinstance(response, str)
            assert len(response) > 0

    def test_chat_method(self):
        """Test chat method with a list of messages."""
        messages = [
            {"role": "user", "content": "Hello"}
        ]
        response = self.service.chat(messages)
        assert isinstance(response, dict)
        assert "choices" in response
        assert len(response["choices"]) > 0
        assert "message" in response["choices"][0]
        assert "content" in response["choices"][0]["message"]
        assert isinstance(response["choices"][0]["message"]["content"], str)

    def test_chat_empty_messages(self):
        """Test chat method with empty messages list."""
        with pytest.raises(ValueError, match="Messages cannot be empty"):
            self.service.chat([])

    def test_query_method_basic(self):
        """Test query method with a basic input."""
        response = self.service.query("Hello")
        assert isinstance(response, str)
        assert len(response) > 0

    def test_query_method_with_context(self):
        """Test query method with context."""
        context = {"system": "You are a helpful assistant."}
        response = self.service.query("Hello", context=context)
        assert isinstance(response, str)
        assert len(response) > 0

    def test_query_method_empty_input(self):
        """Test query method with empty input."""
        response = self.service.query("")
        assert isinstance(response, str)
        assert len(response) > 0 or "empty input" in response.lower()
