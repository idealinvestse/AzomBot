# Services Module

Denna modul innehåller de centrala tjänsterna för AZOM AI Agent. Tjänsterna utgör applikationens domänlager enligt Clean Architecture-principerna.

## Struktur

```
services/
├── ai_service.py        # AI-tjänster och integration mot LLM
├── knowledge_service.py # Kunskapshanteringstjänster
├── tests/               # Testfiler för tjänsterna
│   └── test_ai_service.py
├── __init__.py
└── README.md            # Denna fil
```

## Tjänster

| Tjänst | Beskrivning | Beroenden |
|--------|-------------|-----------|
| `AIService` | Integration mot LLM backends (OpenWebUI, Groq) | `config`, `logger` |
| `KnowledgeService` | Hantering av kunskapsbas och metadata | `config`, `logger` |

## Användning

Tjänsterna följer Single Responsibility-principen och ska ha tydliga, väldefinierade gränssnitt. De ska vara lätta att mocka för testning och ha minimal koppling till externa system.

Exempel:

```python
from app.services.ai_service import AIService
from app.config import Settings

settings = Settings()
ai_service = AIService(settings)

async def get_response(prompt: str) -> str:
    return await ai_service.get_completion(prompt)
```

## Kodkonventioner

1. Implementera alla I/O-operationer som `async def`
2. Använd type hints för alla funktioner och klasser
3. Dokumentera publika funktioner med docstrings
4. Föredra dependency injection framför globala variabler
5. Använd enhetliga fel och undantag
