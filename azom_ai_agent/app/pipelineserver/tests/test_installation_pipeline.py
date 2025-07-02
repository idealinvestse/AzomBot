import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from pipeline_app.pipelines.azom_installation_pipeline import AZOMInstallationPipeline
from pipeline_app.services.orchestration_service import AZOMOrchestrationService

# Test data
TEST_INPUT = {
    "user_input": "I want to install AZOM on my car",
    "car_model": "Volvo XC90",
    "user_experience": "beginner"
}

# Mock response data
MOCK_ORCHESTRATION_RESULT = {
    "result": {
        "recommended_product": {
            "name": "AZOM Volvo Special",
            "description": "Specialanpassad för Volvo",
            "price_sek": 8995,
            "vendor": "AZOM",
            "tags": ["premium"],
            "product_type": "Bilalarm",
            "sku": "AZOM-VOLVO-001",
            "barcode": "123456789012"
        },
        "installation_steps": ["Steg 1: Koppla loss batteriet"],
        "safety_warnings": ["Alltid koppla ur batteriet först"],
        "experience_level": "beginner"
    }
}

# Patch the orchestration service at the module level for all tests
@pytest.fixture(autouse=True)
def mock_orchestration_service():
    with patch('pipeline_app.pipelines.azom_installation_pipeline.AZOMOrchestrationService') as mock_service:
        # Setup mock for the orchestrate method
        mock_instance = AsyncMock()
        mock_instance.orchestrate.return_value = MOCK_ORCHESTRATION_RESULT
        mock_service.return_value = mock_instance
        yield mock_instance

# Test the installation pipeline directly
@pytest.mark.asyncio
async def test_installation_pipeline_happy_path(mock_orchestration_service):
    """Test the installation pipeline with valid input."""
    # Setup mock return value for this test
    mock_orchestration_service.orchestrate.return_value = MOCK_ORCHESTRATION_RESULT
    
    # Create pipeline instance
    pipeline = AZOMInstallationPipeline()
    
    # Test with valid input
    result = await pipeline.run_installation(
        user_input=TEST_INPUT["user_input"],
        car_model=TEST_INPUT["car_model"],
        user_experience=TEST_INPUT["user_experience"]
    )
    
    # Verify results
    assert result == MOCK_ORCHESTRATION_RESULT  # Should return exactly what the service returns
    
    # Verify service was called with correct parameters
    mock_orchestration_service.orchestrate.assert_called_once_with(
        TEST_INPUT["user_input"],
        TEST_INPUT["car_model"],
        TEST_INPUT["user_experience"]
    )

# Test validation in the installation pipeline
@pytest.mark.asyncio
async def test_installation_pipeline_validation():
    """Test input validation in the installation pipeline."""
    # Create pipeline instance
    pipeline = AZOMInstallationPipeline()
    
    # Test with empty user input
    with pytest.raises(ValueError, match="User input cannot be empty"):
        await pipeline.run_installation("", "Volvo XC90", "beginner")
    
    # Test with empty car model
    with pytest.raises(ValueError, match="Car model is required"):
        await pipeline.run_installation("I need help", "", "beginner")

# Test error handling in the installation pipeline
@pytest.mark.asyncio
async def test_installation_pipeline_error(mock_orchestration_service):
    """Test error handling in the installation pipeline."""
    # Setup mock to raise exception
    mock_orchestration_service.orchestrate.side_effect = Exception("Test error")
    
    # Create pipeline instance
    pipeline = AZOMInstallationPipeline()
    
    # Test with error - the error should be propagated
    with pytest.raises(Exception, match="Test error"):
        await pipeline.run_installation(
            user_input=TEST_INPUT["user_input"],
            car_model=TEST_INPUT["car_model"],
            user_experience=TEST_INPUT["user_experience"]
        )
    
    # Verify service was called
    mock_orchestration_service.orchestrate.assert_called_once()
