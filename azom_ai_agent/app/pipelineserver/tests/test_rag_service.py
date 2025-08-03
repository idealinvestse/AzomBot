import pytest
from unittest.mock import patch, MagicMock, mock_open, AsyncMock
import json
from pathlib import Path

from app.pipelineserver.pipeline_app.services.rag_service import RAGService

# --- Test Data ---
MOCK_PRODUCT_DATA = json.dumps([{"name": "AZOM-123", "compatible_models": ["C-Class"], "description": "Install guide for AZOM-123"}])
MOCK_TROUBLESHOOTING_DATA = json.dumps([{"model": "E-Class", "issue_keywords": ["bluetooth"], "steps": ["Restart system"]}])
MOCK_FAQ_DATA = json.dumps([{"question": "Warranty info", "answer": "2 years warranty"}])
MOCK_GUIDE_DATA = json.dumps([{"model": "S-Class", "issue_keywords": ["navigation"], "steps": ["Update maps"]}])


@pytest.fixture
def rag_dependencies_factory():
    """
    A factory fixture to create a flexible mocking environment for RAGService tests.
    Allows simulating file system errors and different data structures.
    """
    def _factory(file_map=None, listdir_return=None, fail_on_open=None):
        if file_map is None:
            file_map = {}
        if listdir_return is None:
            listdir_return = list(file_map.keys())
        if fail_on_open is None:
            fail_on_open = []

        def mock_open_logic(path, *args, **kwargs):
            filename = Path(path).name
            if filename in fail_on_open:
                raise IOError(f"Failed to open {filename}")
            
            m_open = mock_open(read_data=file_map.get(filename, '[]'))
            return m_open()

        vss_patcher = patch('app.pipelineserver.pipeline_app.services.rag_service.VectorStoreService')
        open_patcher = patch('builtins.open', mock_open_logic)
        listdir_patcher = patch('os.listdir', MagicMock(return_value=listdir_return))
        
        return vss_patcher, open_patcher, listdir_patcher

    return _factory


@pytest.mark.asyncio
async def test_rag_search_with_vector_store(rag_dependencies_factory):
    """Test that search uses VectorStoreService when available."""
    vss_patcher, open_patcher, listdir_patcher = rag_dependencies_factory()
    with vss_patcher as mock_vss_class, open_patcher, listdir_patcher:
        mock_instance = mock_vss_class.return_value
        mock_instance.similarity_search = AsyncMock(return_value=[("Vector result content", 0.95)])
        
        rag_service = RAGService()
        assert rag_service.vector_store is not None

        results = await rag_service.search("some query")

        rag_service.vector_store.similarity_search.assert_awaited_once_with("some query", 5)
        assert len(results) == 1
        assert results[0]['content'] == "Vector result content"


@pytest.mark.asyncio
async def test_rag_search_with_keyword_fallback(rag_dependencies_factory):
    """Test keyword search fallback when VectorStoreService fails to initialize."""
    file_map = {
        'products.json': MOCK_PRODUCT_DATA,
        'troubleshooting.json': MOCK_TROUBLESHOOTING_DATA,
        'other_faq.json': MOCK_FAQ_DATA
    }
    vss_patcher, open_patcher, listdir_patcher = rag_dependencies_factory(file_map=file_map)
    with vss_patcher as mock_vss_class, open_patcher, listdir_patcher:
        mock_vss_class.side_effect = Exception("Failed to load model")

        rag_service = RAGService()
        assert rag_service.vector_store is None

        # Test product, troubleshooting, and FAQ search
        assert len(await rag_service.search("AZOM-123")) == 1
        assert len(await rag_service.search("bluetooth")) == 1
        assert len(await rag_service.search("warranty")) == 1


@pytest.mark.asyncio
async def test_rag_search_no_results(rag_dependencies_factory):
    """Test that search returns an empty list when no keywords match."""
    vss_patcher, open_patcher, listdir_patcher = rag_dependencies_factory()
    with vss_patcher as mock_vss_class, open_patcher, listdir_patcher:
        mock_vss_class.side_effect = Exception("Vector store disabled")
        rag_service = RAGService()
        results = await rag_service.search("nonexistent query")
        assert len(results) == 0


@pytest.mark.asyncio
async def test_rag_init_and_search_with_file_errors(rag_dependencies_factory):
    """Test RAGService handles file read errors gracefully during init and search."""
    # Simulate error during __init__
    vss_patcher, open_patcher, listdir_patcher = rag_dependencies_factory(
        listdir_return=['other_guide.json'], fail_on_open=['other_guide.json']
    )
    with vss_patcher as mock_vss_class, open_patcher, listdir_patcher:
        mock_vss_class.side_effect = Exception("Vector store disabled")
        rag_service = RAGService()
        assert len(rag_service.other_data) == 0

    # Simulate errors during search
    vss_patcher, open_patcher, listdir_patcher = rag_dependencies_factory(
        fail_on_open=['products.json', 'troubleshooting.json']
    )
    with vss_patcher as mock_vss_class, open_patcher, listdir_patcher:
        mock_vss_class.side_effect = Exception("Vector store disabled")
        rag_service = RAGService()
        results = await rag_service.search("any query")
        assert results == []


@pytest.mark.asyncio
async def test_rag_search_with_guide_data_type(rag_dependencies_factory):
    """Test keyword search finds results in 'other' data files with guide format."""
    file_map = {'other_guide.json': MOCK_GUIDE_DATA}
    vss_patcher, open_patcher, listdir_patcher = rag_dependencies_factory(file_map=file_map)
    with vss_patcher as mock_vss_class, open_patcher, listdir_patcher:
        mock_vss_class.side_effect = Exception("Vector store disabled")
        rag_service = RAGService()

        results = await rag_service.search("navigation issue")
        assert len(results) == 1
        assert results[0]['title'] == "Guide för s-class"
