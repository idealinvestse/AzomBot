from __future__ import annotations

from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.modes import Mode


class ModeMiddleware(BaseHTTPMiddleware):
    """Middleware that resolves and propagates runtime mode.

    Reads mode from header `X-AZOM-Mode` or query param `mode`.
    Defaults to FULL and echoes selected mode in `X-AZOM-Mode` response header.
    """

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable[[Request], Response]) -> Response:
        # Resolve from header or query param
        hdr = request.headers.get("X-AZOM-Mode")
        q = request.query_params.get("mode")
        mode = Mode.from_str(hdr or q, default=Mode.FULL)

        # Attach to request state for downstream handlers
        request.state.mode = mode

        # Continue pipeline
        response = await call_next(request)

        # Echo for clients/observability
        response.headers["X-AZOM-Mode"] = mode.value.upper()
        return response


def get_request_mode(request: Request) -> Mode:
    """FastAPI dependency/helper to access current request mode."""
    mode = getattr(request.state, "mode", None)
    if isinstance(mode, Mode):
        return mode
    return Mode.FULL
