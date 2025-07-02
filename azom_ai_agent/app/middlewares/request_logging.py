"""
Loggnings-middleware för AZOM AI Agent.

Denna middleware loggar alla inkommande förfrågningar och utgående svar
med korrelations-ID för att möjliggöra spårbarhet genom hela systemet.
"""
from __future__ import annotations

import time
import uuid
from typing import Callable, Any

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.logger import get_logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware som loggar varje förfrågan och svar med ett korrelations-ID.
    
    Denna middleware lägger till ett unikt UUID till varje förfrågan och
    loggar tidsstämplar, varaktighet och statuskoder för att underlätta
    felsökning och prestandaövervakning.
    """

    def __init__(self, app: ASGIApp) -> None:
        """
        Initialiserar middleware med en FastAPI-applikation.
        
        Args:
            app: FastAPI-applikationen som middleware ska tillämpas på
        """
        super().__init__(app)
        self.logger = get_logger("RequestLogger")

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Response]
    ) -> Response:
        """
        Hanterar förfrågan och loggar information om den.
        
        Args:
            request: Den inkommande HTTP-förfrågan
            call_next: Callback till nästa hanterare i middleware-kedjan
            
        Returns:
            Response-objektet från applikationen eller nästa middleware
            
        Raises:
            Exception: Vidarebefordrar alla undantag efter att ha loggat dem
        """
        # Skapa ett unikt korrelations-ID för denna förfrågan
        correlation_id: str = str(uuid.uuid4())
        request.state.correlation_id = correlation_id
        start_time = time.perf_counter()

        # Logga information om den inkommande förfrågan
        self.logger.info(
            "Inkommande förfrågan",
            extra={
                "method": request.method,
                "path": request.url.path,
                "correlation_id": correlation_id,
                "client_ip": request.client.host if request.client else "unknown",
                "user_agent": request.headers.get("user-agent", "unknown"),
            },
        )

        try:
            # Fortsätt till nästa middleware eller till routen
            response = await call_next(request)
        except Exception as exc:
            # Logga ohanterade undantag
            process_time = (time.perf_counter() - start_time) * 1000
            self.logger.exception(
                "Ohanterat undantag",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "correlation_id": correlation_id,
                    "duration_ms": f"{process_time:.2f}",
                    "exception": str(exc),
                },
            )
            # Återkasta undantaget för att global exception handler ska ta över
            raise

        # Beräkna hanteringstid och logga svaret
        process_time = (time.perf_counter() - start_time) * 1000
        log_method = (
            self.logger.warning if response.status_code >= 400 else self.logger.info
        )
        
        log_method(
            "Förfrågan hanterad",
            extra={
                "method": request.method,
                "path": request.url.path,
                "correlation_id": correlation_id,
                "status_code": response.status_code,
                "duration_ms": f"{process_time:.2f}",
            },
        )
        
        # Lägg till korrelations-ID i svarshuvuden för klientreferens
        response.headers["X-Correlation-ID"] = correlation_id
        
        # Lägg till laddningstid i svarshuvuden för prestandaövervakning i utvecklingsläge
        if hasattr(request.app, "debug") and request.app.debug:
            response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
            
        return response
