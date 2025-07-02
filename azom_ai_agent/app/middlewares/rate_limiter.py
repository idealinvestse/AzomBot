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
    
    def __init__(self, app: ASGIApp, settings: Settings):
        """
        Initialisera middleware.
        
        Args:
            app: ASGI-applikation
            settings: Konfiguration med rate-limit-inställningar
        """
        super().__init__(app)
        self.rate_limiter = RateLimiter(limit=settings.RATE_LIMIT_REQUESTS)
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
        # Hämta klient-IP, med stöd för proxy headers
        client_ip = request.client.host
        forwarded_for = request.headers.get("X-Forwarded-For")
        
        if forwarded_for:
            # Använd den första IP:n i X-Forwarded-For
            client_ip = forwarded_for.split(",")[0].strip()

        # Skippa rate-limiting för vissa kritiska endpoints
        if request.url.path in ["/health", "/ping", "/metrics"]:
            return await call_next(request)

        # Kontrollera om requesten är tillåten
        allowed, remaining, reset_in = await self.rate_limiter.is_allowed(client_ip)
        
        # Lägg till rate-limit-headers
        response_headers = {
            "X-RateLimit-Limit": str(self.rate_limiter.limit),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(reset_in),
        }
        
        if not allowed:
            self.logger.warning(
                f"Rate limit exceeded for IP: {client_ip}",
                extra={"client_ip": client_ip, "path": request.url.path}
            )
            
            # Skapa ett 429 Too Many Requests-svar
            return Response(
                content='{"error": "Too many requests. Try again later."}',
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                headers={**response_headers, "Content-Type": "application/json"},
            )
            
        # Om tillåten, fortsätt till nästa middleware
        response = await call_next(request)
        
        # Lägg till rate-limit-headers till svaret
        for key, value in response_headers.items():
            response.headers[key] = value
            
        return response
