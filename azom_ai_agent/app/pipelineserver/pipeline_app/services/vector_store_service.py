"""Very small FAISS-backed vector store for RAG searches.
   Embeds Swedish text with sentence-transformers all-MiniLM-L6-v2.
"""
from __future__ import annotations

import json
import os
from typing import List, Tuple

import faiss
from sentence_transformers import SentenceTransformer

__all__ = ["VectorStoreService"]

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


class VectorStoreService:
    """Singleton-like vector store with lazy index build & simple similarity search."""

    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.model = SentenceTransformer(MODEL_NAME)
        self.index: faiss.IndexFlatIP | None = None
        self.texts: List[str] = []
        self._build_index()

    # ---------------------------------------------------------------------
    # Private helpers
    # ---------------------------------------------------------------------
    def _load_documents(self) -> List[str]:
        texts: List[str] = []
        for fname in os.listdir(self.data_dir):
            if fname.endswith(".json"):
                with open(os.path.join(self.data_dir, fname), encoding="utf-8") as f:
                    items = json.load(f)
                    for itm in items:
                        if isinstance(itm, dict):
                            # Try common content fields
                            txt = (
                                itm.get("description")
                                or itm.get("content")
                                or " ".join(itm.get("steps", []))
                                or itm.get("answer")
                            )
                            if txt:
                                texts.append(txt)
                        elif isinstance(itm, str):
                            texts.append(itm)
        return texts

    def _build_index(self) -> None:
        self.texts = self._load_documents()
        if not self.texts:
            raise RuntimeError("No documents found for vector store")
        embeddings = self.model.encode(self.texts, normalize_embeddings=True)
        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dim)
        self.index.add(embeddings)

    # ---------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------
    def similarity_search(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        if self.index is None:
            raise RuntimeError("Vector store has not been built")
        query_emb = self.model.encode([query], normalize_embeddings=True)
        scores, idxs = self.index.search(query_emb, top_k)
        return [(self.texts[i], float(scores[0][n])) for n, i in enumerate(idxs[0]) if i < len(self.texts)]
