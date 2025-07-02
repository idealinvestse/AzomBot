"""
Test suite för RequestLoggingMiddleware.

Detta testmodul testar funktionaliteten för loggnings-middleware
med fokus på korrelations-ID och korrekt loggning av begäran.
"""
import asyncio
import logging
import re
import uuid
from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from starlette.middleware.base import BaseHTTPMiddleware

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
    return TestClient(app)


@pytest.mark.asyncio
async def test_request_logging_adds_correlation_id(client):
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


@pytest.mark.asyncio
async def test_request_logging_adds_process_time_in_debug(client):
    """Test att middleware lägger till processeringstid i svaret i debug-läge."""
    response = client.get("/test")
    assert response.status_code == 200
    assert "X-Process-Time" in response.headers
    
    # Verifiera att processeringstiden är ett flyttal följt av 'ms'
    process_time = response.headers["X-Process-Time"]
    assert re.match(r"^\d+\.\d+ms$", process_time)


@pytest.mark.asyncio
async def test_request_logging_logs_info(client, caplog):
    """Test att middleware loggar information på INFO-nivå."""
    with caplog.at_level(logging.INFO):
        response = client.get("/test")
    
    # Verifiera att vi har loggat både inkommande förfrågan och svar
    assert any("Inkommande förfrågan" in record.message for record in caplog.records)
    assert any("Förfrågan hanterad" in record.message for record in caplog.records)
    
    # Verifiera att metodinformation loggas korrekt
    method_logs = [r for r in caplog.records if hasattr(r, "method")]
    assert any(r.method == "GET" for r in method_logs)
    
    # Verifiera att sökväg loggas korrekt
    path_logs = [r for r in caplog.records if hasattr(r, "path")]
    assert any(r.path == "/test" for r in path_logs)


@pytest.mark.asyncio
async def test_request_logging_logs_exceptions(client, caplog):
    """Test att middleware loggar undantag på ERROR-nivå."""
    with caplog.at_level(logging.ERROR):
        # Anropa endpoint som kastar undantag
        with pytest.raises(ValueError):
            client.get("/error")
    
    # Verifiera att undantag loggas
    assert any("Ohanterat undantag" in record.message for record in caplog.records)
    
    # Verifiera att undantagsinformation finns med
    exception_logs = [r for r in caplog.records if "Testfel" in str(r.message)]
    assert len(exception_logs) > 0


@pytest.mark.asyncio
async def test_request_logging_warns_on_error_status(app):
    """Test att middleware loggar varningar för felstatuskoder."""
    # Skapa en modifierad app med en endpoint som returnerar 404
    app = FastAPI()
    mock_logger = MagicMock()
    
    # Patcha get_logger för att returnera vår mock
    with patch("app.middlewares.request_logging.get_logger", return_value=mock_logger):
        app.add_middleware(RequestLoggingMiddleware)
        
        @app.get("/not_found")
        async def not_found():
            return JSONResponse(status_code=404, content={"error": "Not found"})
        
        client = TestClient(app)
        response = client.get("/not_found")
        
        # Verifiera att warning-metoden anropades för 404
        mock_logger.warning.assert_called_once()
        

@pytest.mark.asyncio
async def test_middleware_with_complex_request():
    """Test middleware med en komplex manuellt skapad request."""
    # Skapa en manuell request med specifika headers
    scope = {
        "type": "http", 
        "method": "POST",
        "path": "/api/test",
        "headers": [
            (b"user-agent", b"test-agent"),
            (b"content-type", b"application/json"),
            (b"x-custom-header", b"test-value")
        ],
        "client": ("192.168.1.1", 12345)
    }
    
    # Skapa en mock för call_next
    async def mock_call_next(request):
        return Response(content=b'{"status":"ok"}', media_type="application/json")
    
    request = Request(scope)
    middleware = RequestLoggingMiddleware(lambda: None)
    
    # Anropa dispatch direkt
    with patch("app.middlewares.request_logging.get_logger") as mock_get_logger:
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        response = await middleware.dispatch(request, mock_call_next)
        
        # Verifiera att middleware fungerar som förväntat
        assert isinstance(response, Response)
        assert "X-Correlation-ID" in response.headers
        
        # Verifiera loggning
        mock_logger.info.assert_called()
        # Kontrollera att användar-agent och IP loggades
        call_args = mock_logger.info.call_args_list[0][1]["extra"]
        assert call_args["client_ip"] == "192.168.1.1"
        assert call_args["user_agent"] == "test-agent"
