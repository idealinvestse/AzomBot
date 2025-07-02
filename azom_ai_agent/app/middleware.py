from __future__ import annotations

import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from .logger import get_logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware that logs each request and response with a correlation ID."""

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)
        self.logger = get_logger("RequestLogger")

    async def dispatch(self, request: Request, call_next: Callable[[Request], Response]):
        correlation_id: str = str(uuid.uuid4())
        request.state.correlation_id = correlation_id
        start_time = time.perf_counter()

        self.logger.info(
            "Incoming request",
            extra={
                "method": request.method,
                "path": request.url.path,
                "correlation_id": correlation_id,
            },
        )

        try:
            response = await call_next(request)
        except Exception as exc:  # ensure we log unhandled exceptions
            process_time = (time.perf_counter() - start_time) * 1000
            self.logger.exception(
                "Unhandled exception",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "correlation_id": correlation_id,
                    "duration_ms": process_time,
                },
            )
            raise

        process_time = (time.perf_counter() - start_time) * 1000
        self.logger.info(
            "Request handled",
            extra={
                "method": request.method,
                "path": request.url.path,
                "correlation_id": correlation_id,
                "status_code": response.status_code,
                "duration_ms": f"{process_time:.2f}",
            },
        )
        # Add correlation id to response headers for client reference
        response.headers["X-Correlation-ID"] = correlation_id
        return response
