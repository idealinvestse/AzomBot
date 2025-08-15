# Retrieval-Augmented Generation (RAG) service

import json
import os

from functools import lru_cache

# Make VectorStoreService patchable from tests by exposing a module attribute
VectorStoreService = None  # type: ignore

class RAGService:
    """Retrieval-Augmented Generation service för AZOM kunskapsbas."""
    def __init__(self):
        data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data'))
        # Vector store initialiseras lazy för att undvika tunga beroenden vid import
        self._vector_store = None
        self._data_dir = data_dir
        data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data'))
        self.products_path = os.path.join(data_dir, 'products.json')
        self.troubleshooting_path = os.path.join(data_dir, 'troubleshooting.json')
        # Ladda in alla relevanta other_*.json (support, felsökning, guider)
        self.other_data = []
        for fname in os.listdir(data_dir):
            if fname.startswith('other_') and fname.endswith('.json'):
                try:
                    with open(os.path.join(data_dir, fname), encoding='utf-8') as f:
                        self.other_data += json.load(f)
                except Exception:
                    pass

    def _get_vector_store(self):
        """Lazy-ladda VectorStoreService först när det behövs."""
        if self._vector_store is not None:
            return self._vector_store
        try:
            # Lokal import för att undvika att ladda faiss/sentence-transformers i onödan
            global VectorStoreService  # type: ignore
            if VectorStoreService is None:
                from .vector_store_service import VectorStoreService as _VSS  # type: ignore
                VectorStoreService = _VSS
            self._vector_store = VectorStoreService(self._data_dir) if VectorStoreService else None  # type: ignore
        except Exception:
            self._vector_store = None
        return self._vector_store

    @property
    def vector_store(self):
        """Backwards-compatible accessor that lazily initializes and returns the vector store."""
        if self._vector_store is None:
            return self._get_vector_store()
        return self._vector_store

    async def search(self, query: str, top_k: int = 5, use_vectors: bool = True):
        """
        Söker efter relevanta dokument baserat på frågan.
        
        Args:
            query: Sökfrågan som text
            top_k: Maximalt antal resultat att returnera
            use_vectors: Om True används vektorindex om tillgängligt, annars endast keyword-sökning
            
        Returns:
            Lista med matchande dokument
        """
        # 1. Prova vektorindex om tillåtet och tillgängligt
        if use_vectors:
            vector_store = self._get_vector_store()
            if vector_store:
                docs = await vector_store.similarity_search(query, top_k)
                return [{
                    "title": f"Match {i+1}", 
                    "content": txt,
                    "similarity_score": score
                } for i, (txt, score) in enumerate(docs)]

        # Fallback keyword search
        results = []
        query_lower = query.lower()
        # 1. Sök i produkter (installation)
        try:
            with open(self.products_path, encoding='utf-8') as f:
                products = json.load(f)
            for p in products:
                if any(word in query_lower for word in [p.get('name','').lower()] + [m.lower() for m in p.get('compatible_models',[])]):
                    results.append({"title": f"Installationsguide för {p.get('name','')}", "content": p.get("description", "Se manual.")})
        except Exception:
            pass
        # 2. Sök i troubleshooting
        try:
            with open(self.troubleshooting_path, encoding='utf-8') as f:
                guides = json.load(f)
            for g in guides:
                if any(word in query_lower for word in [str(g.get('model','')).lower()] + g.get('issue_keywords',[])):
                    results.append({"title": f"Felsökning för {g.get('model','')}", "content": " ".join(g.get('steps',[]))})
        except Exception:
            pass
        # 3. Sök i other_*.json (support, felsökning, guider)
        for item in self.other_data:
            # Support/FAQ
            if 'question' in item and 'answer' in item:
                if item['question'] and query_lower in item['question'].lower():
                    results.append({"title": f"FAQ: {item['question']}", "content": item['answer']})
            # Felsökning/guider
            elif 'steps' in item:
                model = str(item.get('model','')).lower()
                keywords = [k.lower() for k in item.get('issue_keywords',[])]
                if (model and model in query_lower) or any(k in query_lower for k in keywords):
                    results.append({"title": f"Guide för {model}", "content": " ".join(item.get('steps',[]))})
        return results[:top_k]
