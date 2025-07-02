from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette import status
from .logger import get_logger

logger = get_logger(__name__)


class AppException(Exception):
    """Base class for custom application errors."""

    def __init__(self, message: str, code: int = status.HTTP_400_BAD_REQUEST):
        self.message = message
        self.code = code
        super().__init__(message)


class NotFoundException(AppException):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class UnauthorizedException(AppException):
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)


def add_exception_handlers(app: FastAPI):
    """Register global exception handlers for the FastAPI app."""

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):  # type: ignore[override]
        correlation_id = getattr(request.state, "correlation_id", None)
        payload = {"error": exc.message}
        if correlation_id:
            payload["correlation_id"] = correlation_id
        return JSONResponse(content=payload, status_code=exc.code)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):  # type: ignore[override]
        correlation_id = getattr(request.state, "correlation_id", None)
        payload = {"error": "Validation failed", "detail": exc.errors(), "details": exc.errors()}
        if correlation_id:
            payload["correlation_id"] = correlation_id
        return JSONResponse(content=payload, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):  # type: ignore[override]
        # Log the error with traceback
        logger.exception("Unhandled exception", exc_info=exc)
        correlation_id = getattr(request.state, "correlation_id", None)
        payload = {"error": "Internal server error", "detail": "Internal server error"}
        if correlation_id:
            payload["correlation_id"] = correlation_id
        return JSONResponse(content=payload, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
