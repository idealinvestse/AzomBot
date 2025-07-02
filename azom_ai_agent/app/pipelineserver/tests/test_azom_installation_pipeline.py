import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from app.pipelineserver.pipeline_app.pipelines.azom_installation_pipeline import AZOMInstallationPipeline


def test_azom_installation_pipeline_initialization():
    """Test AZOMInstallationPipeline initialization."""
    pipeline = AZOMInstallationPipeline()
    assert pipeline is not None
    assert pipeline.orchestration_service is not None


@pytest.mark.asyncio
async def test_azom_installation_pipeline_validation():
    """Test validering av indata."""
    pipeline = AZOMInstallationPipeline()
    
    # Testa att tom användarinput ger ValueError
    with pytest.raises(ValueError, match="User input cannot be empty"):
        await pipeline.run_installation("", "Volvo V70", "nybörjare")
    
    # Testa att saknad bilmodell ger ValueError
    with pytest.raises(ValueError, match="Car model is required"):
        await pipeline.run_installation("Hur installerar jag", "", "nybörjare")


@pytest.mark.asyncio
async def test_azom_installation_pipeline_successful_run():
    """Test lyckad körning av installationspipeline."""
    mock_result = {
        "recommended_product": {"name": "AZOM DLR Test", "price_sek": 5000},
        "installation_steps": ["Steg 1", "Steg 2"],
        "safety_warnings": ["Varning 1"]
    }
    
    # Skapa en mock av orchestration service
    with patch('app.pipelineserver.pipeline_app.pipelines.azom_installation_pipeline.AZOMOrchestrationService') as mock_service:
        # Konfigurera mock för att returnera önskat resultat
        instance = mock_service.return_value
        instance.orchestrate = AsyncMock(return_value=mock_result)
        
        # Skapa pipeline med mockad service
        pipeline = AZOMInstallationPipeline()
        pipeline.orchestration_service = instance
        
        # Kör installation
        result = await pipeline.run_installation("Hur installerar jag AZOM?", "Volvo V70", "nybörjare")
        
        # Verifiera att orchestration_service.orchestrate anropades med rätt parametrar
        instance.orchestrate.assert_called_once_with("Hur installerar jag AZOM?", "Volvo V70", "nybörjare")
        
        # Verifiera att resultatet är korrekt
        assert result == mock_result
        assert result["recommended_product"]["name"] == "AZOM DLR Test"


@pytest.mark.asyncio
async def test_azom_installation_pipeline_exception_handling():
    """Test att fel från orchestration service hanteras korrekt."""
    # Skapa en mock av orchestration service som kastar ett exception
    with patch('app.pipelineserver.pipeline_app.pipelines.azom_installation_pipeline.AZOMOrchestrationService') as mock_service:
        # Konfigurera mock för att kasta exception
        instance = mock_service.return_value
        instance.orchestrate = AsyncMock(side_effect=Exception("Test exception"))
        
        # Skapa pipeline med mockad service
        pipeline = AZOMInstallationPipeline()
        pipeline.orchestration_service = instance
        
        # Verifiera att exception vidarebefordras
        with pytest.raises(Exception, match="Test exception"):
            await pipeline.run_installation("Hur installerar jag AZOM?", "Volvo V70", "nybörjare")
