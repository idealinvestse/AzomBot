"""Middleware-modul för AZOM AI Agent.

Inkluderar alla middleware-komponenter som används i AZOM AI Agent:  
- RateLimitingMiddleware: begränsar antalet förfrågningar per tidsenhet  
- RequestLoggingMiddleware: loggar alla förfrågningar med korrelations-ID  

Exempel:  
    ```python
    from fastapi import FastAPI
    from app.middlewares import RateLimitingMiddleware, RequestLoggingMiddleware
    from app.config import Settings
    
    app = FastAPI()
    settings = Settings()
    
    # Lägg till middleware
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(RateLimitingMiddleware, settings=settings)
    ```
"""
from .rate_limiter import RateLimitingMiddleware
from .request_logging import RequestLoggingMiddleware

__all__ = ["RateLimitingMiddleware", "RequestLoggingMiddleware"]
