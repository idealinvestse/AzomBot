# Models Module

Denna modul innehåller Pydantic-modeller för datavalidering och serialisering i AZOM AI Agent.

## Struktur

```
models/
├── __init__.py
├── ai_models.py     # Modeller för AI-tjänster och requests
├── knowledge.py     # Modeller för kunskapshantering
└── README.md        # Denna fil
```

## Användning

Pydantic-modellerna används för:
1. Validering av indata från API-anrop
2. Serialisering/deserialisering av data för persistens
3. OpenAPI-dokumentation
4. Typvalidering med mypy

Exempel:

```python
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class KnowledgeItem(BaseModel):
    id: str = Field(..., description="Unik identifierare")
    title: str = Field(..., description="Rubrik på kunskapsobjekt") 
    content: str = Field(..., description="Innehåll")
    tags: List[str] = Field(default_factory=list, description="Taggningskategorier")
    updated_at: Optional[datetime] = Field(None, description="Senast uppdaterad")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "kb-001",
                "title": "Installation av AZOM-antenn",
                "content": "Monteringsanvisning för AZOM V2 på Volvo...",
                "tags": ["installation", "volvo", "antenn"],
                "updated_at": "2025-06-30T12:00:00Z"
            }
        }
    }
```

## Kodkonventioner

1. Använd Python 3.12+ typannotationer med Pydantic v2-syntax
2. Alla modeller ska ha docstrings och Field-beskrivningar för OpenAPI
3. Inkludera exempel på giltiga värden i `model_config`
4. Använd strikt validering där möjligt
5. Deklarera explicita standardvärden för alla optionella fält
