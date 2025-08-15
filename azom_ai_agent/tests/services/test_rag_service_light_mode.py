import pytest

from app.pipelineserver.pipeline_app.services.rag_service import RAGService

@pytest.mark.asyncio
async def test_rag_service_does_not_init_vectors_when_disabled(monkeypatch):
    svc = RAGService()

    def fail_get_vector_store():
        raise AssertionError("_get_vector_store should not be called when use_vectors=False")

    monkeypatch.setattr(svc, "_get_vector_store", fail_get_vector_store, raising=True)

    # Should not raise and should return a list from keyword fallback (possibly empty)
    results = await svc.search("any query", top_k=3, use_vectors=False)
    assert isinstance(results, list)

@pytest.mark.asyncio
async def test_rag_service_calls_vectors_when_enabled(monkeypatch):
    svc = RAGService()
    called = {"n": 0}

    async def fake_similarity_search(query, top_k):
        return [("doc1", 0.9), ("doc2", 0.8)][:top_k]

    class DummyVS:
        async def similarity_search(self, query, top_k):
            return await fake_similarity_search(query, top_k)

    def get_vs():
        called["n"] += 1
        return DummyVS()

    monkeypatch.setattr(svc, "_get_vector_store", get_vs, raising=True)

    results = await svc.search("pump issue", top_k=2, use_vectors=True)
    assert called["n"] == 1
    assert isinstance(results, list)
    assert len(results) == 2
    assert all("content" in r and "similarity_score" in r for r in results)
