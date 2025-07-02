import re

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.middleware import RequestLoggingMiddleware
from app.exceptions import add_exception_handlers, NotFoundException

UUID_REGEX = re.compile(r"^[a-f0-9]{8}-[a-f0-9]{4}-[1-5][a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$", re.I)


def _create_test_app() -> FastAPI:
    """Helper that returns a fresh FastAPI app instrumented with our middleware/handlers."""

    test_app = FastAPI()
    test_app.add_middleware(RequestLoggingMiddleware)
    add_exception_handlers(test_app)

    @test_app.get("/ok")
    async def ok():  # pragma: no cover
        return {"status": "ok"}

    @test_app.get("/raise-app")
    async def raise_app():  # pragma: no cover
        raise NotFoundException("Inte hittad")

    @test_app.get("/raise-unhandled")
    async def raise_unhandled():  # pragma: no cover
        raise ValueError("Boom")

    return test_app


def test_correlation_id_header_and_format():
    client = TestClient(_create_test_app(), raise_server_exceptions=False)
    resp = client.get("/ok")
    assert resp.status_code == 200
    correlation_id = resp.headers.get("X-Correlation-ID")
    assert correlation_id, "Header saknas"
    assert UUID_REGEX.match(correlation_id), "Headern är inte giltig UUID"


def test_app_exception_returns_json_and_status():
    client = TestClient(_create_test_app(), raise_server_exceptions=False)
    resp = client.get("/raise-app")
    assert resp.status_code == 404  # mapped via NotFoundException
    body = resp.json()
    assert body["error"] == "Inte hittad"
    assert "correlation_id" in body
    # Correlation id should be valid UUID as well
    assert UUID_REGEX.match(body["correlation_id"])


def test_unhandled_exception_translated_to_500():
    client = TestClient(_create_test_app(), raise_server_exceptions=False)
    resp = client.get("/raise-unhandled")
    assert resp.status_code == 500
    body = resp.json()
    assert body["error"] == "Internal server error"
    assert "correlation_id" in body
