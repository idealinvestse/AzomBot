import json
from pathlib import Path

import pytest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Adjust import path if project structure changes
from app.pipelineserver.pipeline_app.services.vector_store_service import (
    VectorStoreService,
)


def test_similarity_search_returns_relevant(tmp_path: Path) -> None:
    """Vector store should return at least one hit matching query text."""
    # Arrange – create small corpus
    docs = [
        {"description": "Installationsguide för AZOM Volvo modulen."},
        {"description": "Manual för Tesla Model 3"},
    ]
    data_file = tmp_path / "products.json"
    data_file.write_text(json.dumps(docs, ensure_ascii=False), encoding="utf-8")

    # Act
    store = VectorStoreService(data_dir=str(tmp_path))
    results = store.similarity_search("volvo", top_k=2)

    # Assert
    assert results, "Expected non-empty similarity results"
    assert "Volvo".lower() in results[0][0].lower()
