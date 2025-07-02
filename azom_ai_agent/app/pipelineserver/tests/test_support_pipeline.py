import pytest
import os
import json
from unittest.mock import patch, mock_open, AsyncMock
from fastapi.testclient import TestClient

# Import the app after patching the environment
from pipeline_app.main import app as fastapi_app
from pipeline_app.pipelines.support_pipeline import SupportPipeline

# Test data
TEST_FAQ = [
    {"question": "Hur lång är garantin?", "answer": "Garantin är 3 år."},
    {"question": "Hur lång är returrätten?", "answer": "Du har 14 dagars öppet köp."},
    {"question": "Hur länge tar leveransen?", "answer": "Leveranstiden är 1-3 arbetsdagar."}
]

@pytest.fixture
def mock_faq_file(tmp_path):
    """Create a temporary FAQ JSON file for testing."""
    faq_data = [
        {"question": "Hur lång är garantin?", "answer": "Garantin är 3 år."},
        {"question": "Hur lång är returrätten?", "answer": "Returrätten är 14 dagar."},
        {"question": "Hur länge tar leveransen?", "answer": "Leveranstiden är 2-5 arbetsdagar."}
    ]
    faq_file = tmp_path / "test_faq.json"
    with open(faq_file, 'w', encoding='utf-8') as f:
        json.dump(faq_data, f, ensure_ascii=False)
    return str(faq_file)

@pytest.fixture
def support_pipeline(mock_faq_file):
    """Create a SupportPipeline instance with test data."""
    return SupportPipeline(faq_path=mock_faq_file)

# Using the test_client fixture from conftest.py

@pytest.mark.asyncio
async def test_get_faq(support_pipeline):
    """Test getting the FAQ list."""
    faq = await support_pipeline.get_all_faq()
    assert isinstance(faq, list)
    assert len(faq) == 3
    assert "question" in faq[0]
    assert "answer" in faq[0]

@pytest.mark.asyncio
async def test_run_support_exact_match(support_pipeline):
    """Test getting a support answer with an exact match."""
    result = await support_pipeline.run_support("Hur lång är garantin?")
    assert result == {"answer": "Garantin är 3 år."}

@pytest.mark.asyncio
async def test_run_support_partial_match(support_pipeline):
    """Test getting a support answer with a partial match."""
    result = await support_pipeline.run_support("Jag undrar om garantin")
    assert "garantin" in result["answer"].lower()

@pytest.mark.asyncio
async def test_run_support_no_match(support_pipeline):
    """Test getting a support answer with no match."""
    result = await support_pipeline.run_support("Något helt annat")
    assert result == {"answer": "Din fråga matchade ingen FAQ. Kontakta support@azom.se."}

@pytest.mark.asyncio
async def test_support_pipeline_basic(support_pipeline):
    """Test the SupportPipeline with a basic question."""
    # Test exact match
    result = await support_pipeline.run_support("Hur lång är garantin?")
    assert result == {"answer": "Garantin är 3 år."}

    # Test exact match for return policy
    result = await support_pipeline.run_support("Hur lång är returrätten?")
    assert result == {"answer": "Returrätten är 14 dagar."}

    # Test no match
    result = await support_pipeline.run_support("Något helt annat")
    assert "ingen FAQ" in result["answer"] or "support@azom.se" in result["answer"]

@pytest.mark.asyncio
async def test_support_endpoint(test_client, support_pipeline):
    """Test the support endpoint with a valid question."""
    # Patch the support_pipeline to return a mock response
    with patch('pipeline_app.main.support_pipeline', support_pipeline):
        # Test with a question that should match the test FAQ data
        response = test_client.post(
            "/api/v1/support",
            json={"question": "Hur lång är garantin?"},
        )
        assert response.status_code == 200
        assert "answer" in response.json()
        assert "garantin" in response.json()["answer"].lower()

@pytest.mark.asyncio
async def test_support_endpoint_empty_input(test_client):
    """Test the support endpoint with empty input."""
    response = test_client.post(
        "/api/v1/support",
        json={"question": ""},
    )
    assert response.status_code == 422  # Validation error
    assert "detail" in response.json()
    assert "Question is required" in response.json()["detail"]

@pytest.mark.asyncio
async def test_support_endpoint_missing_question(test_client):
    """Test the support endpoint with missing question field."""
    response = test_client.post(
        "/api/v1/support",
        json={},
    )
    assert response.status_code == 422  # Validation error
    assert "detail" in response.json()

# Test get_all_faq method
@pytest.mark.asyncio
async def test_get_all_faq(mock_faq_file):
    """Test getting all FAQs."""
    # Create pipeline instance with the test FAQ file
    pipeline = SupportPipeline(faq_path=mock_faq_file)
    
    # Test get_all_faq
    result = await pipeline.get_all_faq()
    assert isinstance(result, list)
    assert len(result) == 3  # We have 3 test FAQ items
    assert "question" in result[0]
    assert "answer" in result[0]

# Rest of the code remains the same
