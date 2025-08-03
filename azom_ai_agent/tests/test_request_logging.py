"""
Test suite för RequestLoggingMiddleware.

Detta testmodul testar funktionaliteten för loggnings-middleware
med fokus på korrelations-ID och korrekt loggning av begäran.
"""
import logging
import re
from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

from app.middlewares.request_logging import RequestLoggingMiddleware


@pytest.fixture
def app():
    """Fixture för att skapa en testapp med loggnings-middleware."""
    app = FastAPI(debug=True)
    app.add_middleware(RequestLoggingMiddleware)

    @app.get("/test")
    async def test_endpoint():
        return {"message": "success"}

    @app.get("/error")
    async def error_endpoint():
        raise ValueError("Testfel")

    return app


@pytest.fixture
def client(app):
    """Fixture för att skapa en TestClient för FastAPI."""
    with TestClient(app) as test_client:
        yield test_client


def test_request_logging_adds_correlation_id(client):
    """Test att middleware lägger till ett korrelations-ID i svaret."""
    response = client.get("/test")
    assert response.status_code == 200
    assert "X-Correlation-ID" in response.headers
    
    # Verifiera att korrelations-ID är ett giltigt UUID
    correlation_id = response.headers["X-Correlation-ID"]
    assert re.match(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
        correlation_id,
        re.I
    )


def test_request_logging_adds_process_time_in_debug(client):
    """Test att middleware lägger till processeringstid i svaret i debug-läge."""
    response = client.get("/test")
    assert response.status_code == 200
    assert "X-Process-Time" in response.headers
    
    # Verifiera att processeringstiden är ett flyttal följt av 'ms'
    process_time = response.headers["X-Process-Time"]
    assert re.match(r"^\d+\.\d+ms$", process_time)


def test_request_logging_logs_info(client, caplog):
    """Test att middleware loggar information på INFO-nivå."""
    with caplog.at_level(logging.INFO):
        client.get("/test")
    
    # Verifiera att vi har loggat både inkommande förfrågan och svar
    assert any("Inkommande förfrågan" in record.message for record in caplog.records)
    assert any("Förfrågan hanterad" in record.message for record in caplog.records)
    
    # Verifiera att metodinformation loggas korrekt
    request_log = next(r for r in caplog.records if r.message == "Inkommande förfrågan")
    assert request_log.method == "GET"
    assert request_log.path == "/test"


def test_request_logging_logs_exceptions(client, caplog):
    """Test att middleware loggar undantag på ERROR-nivå."""
    with caplog.at_level(logging.ERROR):
        with pytest.raises(ValueError):
            client.get("/error")

    # Verifiera att ett undantag har loggats
    error_logs = [r for r in caplog.records if r.levelname == "ERROR"]
    assert len(error_logs) == 1
    
    log_record = error_logs[0]
    assert "Ohanterat undantag" in log_record.message
    assert log_record.exc_info is not None
    # Verifiera att traceback innehåller rätt undantagstyp och meddelande
    formatted_exception = "".join(logging.Formatter().formatException(log_record.exc_info))
    assert "ValueError: Testfel" in formatted_exception


def test_request_logging_warns_on_error_status():
    """Test att middleware loggar varningar för felstatuskoder."""
    app = FastAPI()
    mock_logger = MagicMock()
    
    with patch("app.middlewares.request_logging.get_logger", return_value=mock_logger):
        app.add_middleware(RequestLoggingMiddleware)
        
        @app.get("/not_found")
        async def not_found():
            return JSONResponse(status_code=404, content={"error": "Not found"})
        
        with TestClient(app) as client:
            client.get("/not_found")
        
        # Verifiera att warning-metoden anropades för 404
        mock_logger.warning.assert_called_once()
        warning_call_args = mock_logger.warning.call_args
        assert warning_call_args.args[0] == "Förfrågan hanterad"
        assert warning_call_args.kwargs["extra"]["status_code"] == 404


@pytest.mark.asyncio
async def test_middleware_with_complex_request(caplog):
    """Testar middleware med en manuellt skapad, mer komplex request."""
    scope = {
        "type": "http",
        "method": "POST",
        "path": "/api/test",
        "headers": [
            (b"user-agent", b"test-agent-complex"),
            (b"content-type", b"application/json"),
        ],
        "client": ("192.168.1.100", 54321),
        "state": {},  # Viktigt för att middleware ska kunna fästa correlation_id
    }
    
    async def mock_call_next(request: Request) -> Response:
        return Response(status_code=201, content=b'{"status":"created"}')

    request = Request(scope)
    middleware = RequestLoggingMiddleware(app=FastAPI())

    with caplog.at_level(logging.INFO):
        response = await middleware.dispatch(request, mock_call_next)

    assert response.status_code == 201
    assert "X-Correlation-ID" in response.headers
    assert "X-Process-Time" in response.headers

    # Verifiera loggarna
    request_log = next(r for r in caplog.records if r.message == "Inkommande förfrågan")
    response_log = next(r for r in caplog.records if r.message == "Förfrågan hanterad")

    assert request_log.method == "POST"
    assert request_log.path == "/api/test"
    assert request_log.client_ip == "192.168.1.100"
    assert request_log.user_agent == "test-agent-complex"
    assert response_log.status_code == 201

