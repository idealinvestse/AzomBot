import pytest
import asyncio
import sys
import os
import unittest
from unittest.mock import patch, MagicMock, AsyncMock

# Lägg till sökvägen till projektet i Python-sökvägen
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pipeline_app.pipelines.azom_installation_pipeline import AZOMInstallationPipeline
from pipeline_app.pipelines.troubleshooting_pipeline import TroubleshootingPipeline
from pipeline_app.services.memory_service import MemoryService
from pipeline_app.services.rag_service import RAGService
from pipeline_app.services.azom_knowledge_service import AZOMKnowledgeService

@pytest.mark.asyncio
async def test_installation_unknown_car():
    """Testa med en okänd bilmodell."""
    # Skapa en riktig instans med testdata
    knowledge_service = AZOMKnowledgeService()
    knowledge_service.products_path = os.path.join(
        os.path.dirname(__file__), 'test_data/test_products.json'
    )
    
    # Testa att en okänd bilmodell ger ett fel
    with pytest.raises(ValueError, match="Ingen produkt hittades"):
        await knowledge_service.get_product_info(car_model="Lada")

@pytest.mark.asyncio
async def test_troubleshooting_no_result():
    """Testa felsökning utan resultat."""
    # Skapa en instans med mockad filsystemstillgång
    with patch('builtins.open', unittest.mock.mock_open(read_data='[]')), \
         patch('os.path.exists', return_value=True), \
         patch('os.listdir', return_value=[]):
        
        pipeline = TroubleshootingPipeline()
        
        # Kör testet
        result = await pipeline.run_troubleshooting("okänt fel", car_model="Lada")
        
        # Verifiera resultatet
        assert "steps" in result
        assert len(result["steps"]) > 0
        assert "Ingen felsökningsguide" in result["steps"][0]

@pytest.mark.asyncio
async def test_memory_history():
    """Testa minneshantering."""
    # Skapa en riktig instans
    memory = MemoryService()
    
    # Använd ett unikt användar-ID för detta test
    test_user_id = "test_memory_history_user"
    
    # Spara lite testdata
    test_data = {
        "test": "data", 
        "action": "test_memory_history"
    }
    
    # Spara kontexten
    save_result = await memory.save_context(test_data, user_id=test_user_id)
    assert save_result["status"] == "context saved"
    
    # Hämta historik
    hist = await memory.get_history(user_id=test_user_id)
    
    # Verifiera att historiken är en lista och innehåller vår testdata
    assert isinstance(hist, list)
    assert len(hist) > 0
    
    # Kontrollera att vår testdata finns i historiken
    test_entry = next((item for item in hist if item.get("action") == "test_memory_history"), None)
    assert test_entry is not None
    assert test_entry["test"] == "data"

@pytest.mark.asyncio
async def test_installation_empty_input():
    """Testa med tom användarinput."""
    # Skapa en riktig instans
    pipeline = AZOMInstallationPipeline()
    
    # Testa med tom input
    with pytest.raises(ValueError, match="User input cannot be empty"):
        await pipeline.run_installation("", car_model="Volvo")
