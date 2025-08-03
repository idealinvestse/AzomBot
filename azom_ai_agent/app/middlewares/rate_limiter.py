"""Rate-limiting middleware för AZOM AI Agent.

Implementerar rate-limiting per IP-adress enligt konfigurationen.
"""
from __future__ import annotations

import time
from typing import Dict, Tuple
from fastapi import Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp

from ..config import Settings
from ..logger import get_logger

class RateLimiter:
    """Klass för att spåra och begränsa requests per IP."""
    
    def __init__(self, limit: int, window: int = 3600):
        """
        Initialisera rate limiter.
        
        Args:
            limit: Maximalt antal requests per tidsfönster
            window: Tidsfönster i sekunder (standard: 1 timme)
        """
        self.limit = limit
        self.window = window
        self._requests: Dict[str, Tuple[int, float]] = {}  # IP -> (count, start_time)
        self._logger = get_logger("RateLimiter")

    async def is_allowed(self, ip: str) -> Tuple[bool, int, int]:
        """
        Kontrollera om en IP har överskridit sin rate-limit.
        
        Args:
            ip: IP-adress att kontrollera
            
        Returns:
            Tuple med (tillåten, återstående requests, sekunder till reset)
        """
        now = time.time()
        
        # Om vi inte har sett denna IP innan eller om fönstret har passerat
        if ip not in self._requests or (now - self._requests[ip][1]) > self.window:
            self._requests[ip] = (1, now)
            return True, self.limit - 1, self.window
            
        # Uppdatera och kontrollera count
        count, start_time = self._requests[ip]
        time_passed = now - start_time
        time_left = max(0, self.window - time_passed)
        
        # Om vi fortfarande är inom fönstret
        if count < self.limit:
            self._requests[ip] = (count + 1, start_time)
            return True, self.limit - count - 1, int(time_left)
            
        return False, 0, int(time_left)

    async def cleanup(self) -> int:
        """
        Rensa bort gamla poster från rate-limiting-cachen.
        
        Returns:
            Antal borttagna poster
        """
        now = time.time()
        expired = [ip for ip, (_, start_time) in self._requests.items() 
                  if (now - start_time) > self.window]
                  
        for ip in expired:
            del self._requests[ip]
            
        return len(expired)


class RateLimitingMiddleware(BaseHTTPMiddleware):
    """Middleware som tillämpar rate-limiting per IP."""
    
    def __init__(self, app: ASGIApp):
        """
        Initialisera middleware.
        
        Args:
            app: ASGI-applikation
        """
        super().__init__(app)
        self.rate_limiter: Optional[RateLimiter] = None
        self.settings: Optional[Settings] = None
        self.logger = get_logger("RateLimiterMiddleware")

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """
        Hantera inkommande request med rate-limiting.
        
        Args:
            request: Inkommande HTTP-request
            call_next: Nästa middleware i kedjan
            
        Returns:
            HTTP-response
        """
        if self.settings is None:
            self.settings = request.app.state.settings

        if not self.settings.RATE_LIMIT_ENABLED:
            return await call_next(request)

        if self.rate_limiter is None:
            self.rate_limiter = RateLimiter(
                limit=self.settings.RATE_LIMIT_REQUESTS,
                window=self.settings.RATE_LIMIT_WINDOW_SECONDS
            )

        # Hämta klient-IP, med stöd för proxy headers
        client_ip = request.headers.get("x-forwarded-for", request.client.host if request.client else "testclient").split(',')[0].strip()
        
        if not client_ip:
            client_ip = "unknown"

        allowed, remaining, reset_in = await self.rate_limiter.is_allowed(client_ip)
        
        if not allowed:
            self.logger.warning(f"Rate limit överskriden för IP: {client_ip}")
            return Response(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content='{"error": "Too many requests"}',
                headers={
                    "Retry-After": str(reset_in),
                    "Content-Type": "application/json"
                }
            )
            
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.rate_limiter.limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_in)
        
        return response
