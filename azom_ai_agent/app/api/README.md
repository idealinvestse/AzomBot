# API Module

Denna modul innehåller alla FastAPI-endpoints för AZOM AI Agent Core API. Modulen är organiserad enligt REST-principer och API-versioner.

## Struktur

```
api/
├── v1/              # API version 1
│   ├── diagnose.py    # Diagnostik-endpoints
│   ├── health.py      # Hälsokontroll-endpoints
│   └── knowledge_management.py  # Endpoints för kunskapshantering
├── __init__.py
└── README.md        # Denna fil
```

## Användning

API-routers definieras med FastAPI router och importeras i `app.main.py`. Alla routes ska ha komplett dokumentation med FastAPI annotations, Pydantic-modeller och OpenAPI-specification.

Exempel på hur en endpoint definieras:

```python
from fastapi import APIRouter, Depends
from pydantic import BaseModel

router = APIRouter(prefix="/diagnose", tags=["diagnose"])

class DiagnoseRequest(BaseModel):
    query: str
    car_model: str | None = None

@router.post("/problem")
async def diagnose_problem(request: DiagnoseRequest):
    """Diagnosticera ett problem baserat på användarens fråga."""
    # Implementation
    return {"result": "diagnosis"}
```

## Konventioner

1. Använd async/await för alla endpoints som utför I/O-operationer
2. Validera alla indata med Pydantic-modeller
3. Returnera JSON-kompatibla objekt
4. Dokumentera alla endpoints med docstrings
5. Använd tydliga status-koder och felhantering
