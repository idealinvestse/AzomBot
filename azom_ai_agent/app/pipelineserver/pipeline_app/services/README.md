# Pipeline Services Module

Denna modul innehåller kärntjänsterna för AZOM pipeline-applikationen, organiserade enligt hexagonal arkitektur för att separera domänlogik från externa beroenden.

## Struktur

```
services/
├── __init__.py
├── llm_client.py           # Integration med LLM-tjänster (OpenWebUI/Ollama/Groq)
├── memory_service.py       # Hantering av konversationsminne och kontext
├── orchestration_service.py # Dirigering av installationspipelines
├── rag_service.py          # Retrieval-Augmented Generation tjänst
├── safety_service.py       # Validering av innehåll och säkerhetskontroller
├── vector_store_service.py # FAISS vektorlager för semantisk sökning
└── README.md               # Denna fil
```

## Komponenter

| Service | Beskrivning | Beroenden |
|---------|-------------|-----------|
| `LLMClient` | Asynkron klient för OpenWebUI/Ollama och Groq | `httpx`, `config` |
| `MemoryService` | Sessionshantering och konversationshistorik | `sqlite`/`postgresql` |
| `OrchestrationService` | Koordinering av pipeline-steg | `llm_client`, `rag_service` |
| `RAGService` | Semantisk sökning och kunskapsutvinning | `vector_store_service` |
| `SafetyService` | Innehållsvalidering och säkerhetskontroller | `llm_client` |
| `VectorStoreService` | FAISS/MiniLM-baserad vektorindex | `sentence_transformers`, `faiss` |

## Användning

Dessa tjänster följer dependency injection-mönstret och är designade för att vara asynkrona:

```python
from app.pipelineserver.pipeline_app.services.rag_service import RAGService
from app.pipelineserver.pipeline_app.services.llm_client import LLMClient

# Instantiera tjänster
rag_service = RAGService()
llm_client = LLMClient()

# Använd tjänsterna asynkront
async def process_query(query: str) -> dict:
    # Hämta relevant kontext från kunskapsbas
    context = await rag_service.search(query, top_k=3)
    
    # Kombinera kontext med användarfråga
    messages = [
        {"role": "system", "content": f"Kontext: {context}"},
        {"role": "user", "content": query}
    ]
    
    # Anropa LLM-tjänst
    response = await llm_client.chat(messages)
    return {"answer": response, "context": context}
```

## Kodkonventioner

1. Alla externa anrop (databas, API, filsystem) implementeras som `async def`
2. Använd explicit typannotering för alla funktioner och klasser
3. Implementera felhantering och resilience för externa tjänster
4. Tester ska täcka minst 80% av koden med mocks för externa tjänster
5. Dokumentera publika metoder med docstrings enligt PEP 257
