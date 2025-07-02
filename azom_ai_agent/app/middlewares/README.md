# Middlewares Module

Denna modul innehåller FastAPI middleware-komponenter för AZOM AI Agent. Middleware-komponenter appliceras på alla inkommande requests och utgående responses.

## Struktur

```
middlewares/
├── __init__.py
├── rate_limiter.py     # Rate limiting middleware
├── request_logging.py  # Request logging middleware
└── README.md           # Denna fil
```

## Komponenter

| Middleware | Beskrivning |
|------------|-------------|
| `RateLimitingMiddleware` | Begränsar antalet requests per IP-adress per tidsenhet |
| `RequestLoggingMiddleware` | Loggar inkommande requests och deras svarstider |

## Användning

Middleware registreras i `app.main.py` med FastAPI's add_middleware-metod:

```python
from app.middlewares import RequestLoggingMiddleware, RateLimitingMiddleware
from app.config import Settings

settings = Settings()
app = FastAPI()

app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RateLimitingMiddleware, settings=settings)
```

Ordningen är viktig - middlewares körs i omvänd ordning mot hur de registreras (sista middleware körs först).

## Implementation

Alla middlewares implementeras enligt Starlette's BaseHTTPMiddleware-pattern:

```python
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from fastapi import Request, Response

class CustomMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Före-behandling
        response = await call_next(request)
        # Efter-behandling
        return response
```

## Kodkonventioner

1. Använd asynkrona funktioner för all I/O
2. Fånga och logga alla fel i middleware
3. Påverka inte request/response-innehåll om det inte är nödvändigt
4. Dokumentera eventuella headers som läggs till eller modifieras
