import json
from pathlib import Path
import pytest

from azom_ai_agent.app.pipelineserver.pipeline_app.services.rag_service import RAGService


@pytest.mark.asyncio
async def test_keyword_search_returns_match(tmp_path: Path) -> None:
    """Fallback keyword search should return match when product name exists."""
    # Arrange – sample product data
    products = [
        {
            "name": "AZOM Test Module",
            "description": "Installationsguide för testmodul",
            "compatible_models": ["Volvo"],
        }
    ]
    products_file = tmp_path / "products.json"
    products_file.write_text(json.dumps(products, ensure_ascii=False), encoding="utf-8")

    # Instantiate service and monkeypatch paths
    rag = RAGService()
    rag.vector_store = None  # force keyword fallback
    rag.products_path = str(products_file)
    rag.troubleshooting_path = str(tmp_path / "troubleshooting.json")  # empty

    # Act
    results = await rag.search("AZOM Test Module", top_k=5)

    # Assert
    assert results, "Expected at least one result from keyword search"
    assert any("AZOM" in r["title"] or "AZOM" in r["content"] for r in results)
