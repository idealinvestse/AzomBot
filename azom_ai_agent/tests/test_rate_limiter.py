"""
Test suite för RateLimitingMiddleware.

Detta testmodulen testar funktionaliteten för rate-limiting middleware
med fokus på olika tidsfönster, IP-baserad begränsning och felhantering.
"""
import asyncio
import time
from datetime import datetime
import pytest
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import BaseModel

from app.middlewares.rate_limiter import RateLimitingMiddleware, RateLimiter
from app.config import Settings


class MockSettings(BaseModel):
    """Mock-inställningar för tester."""
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS_PER_WINDOW: int = 5
    RATE_LIMIT_WINDOW_SECONDS: int = 10
    DEBUG: bool = True


@pytest.fixture
def settings():
    """Fixture för att skapa mock-inställningar."""
    return MockSettings()


@pytest.fixture
def rate_limiter():
    """Fixture för att skapa en isolerad RateLimiter för testning."""
    return RateLimiter(max_requests=5, window_seconds=10)


@pytest.fixture
def app(settings):
    """Fixture för att skapa en testapp med rate-limiter middleware."""
    app = FastAPI()
    app.add_middleware(RateLimitingMiddleware, settings=settings)

    @app.get("/test")
    async def test_endpoint():
        return {"message": "success"}

    @app.get("/unlimited")
    async def unlimited_endpoint():
        # Den här funktionen kommer att användas för att testa undantag
        return {"message": "unlimited access"}

    return app


@pytest.fixture
def client(app):
    """Fixture för att skapa en TestClient för FastAPI."""
    return TestClient(app)


def test_rate_limiter_init(rate_limiter):
    """Test att RateLimiter initieras korrekt."""
    assert rate_limiter.max_requests == 5
    assert rate_limiter.window_seconds == 10
    assert isinstance(rate_limiter.request_counts, dict)


def test_rate_limiter_add_request(rate_limiter):
    """Test att add_request ökar räknare för en specifik IP."""
    ip = "127.0.0.1"
    
    # Första begäran ska lyckas
    assert rate_limiter.add_request(ip) is True
    
    # Verifiera att begäran registrerats
    assert ip in rate_limiter.request_counts
    assert len(rate_limiter.request_counts[ip]) == 1
    
    # Lägg till flera begäran under gränsen
    for _ in range(3):
        assert rate_limiter.add_request(ip) is True
    
    # Verifiera att alla begäran registrerats
    assert len(rate_limiter.request_counts[ip]) == 4
    
    # Lägg till sista begäran inom gränsen
    assert rate_limiter.add_request(ip) is True
    
    # Nästa begäran ska överskrida gränsen
    assert rate_limiter.add_request(ip) is False


def test_rate_limiter_cleanup(rate_limiter):
    """Test att cleanup tar bort gamla begäran."""
    ip = "192.168.1.1"
    
    # Lägg till några begäran med gamla timestamps
    current_time = time.time()
    rate_limiter.request_counts[ip] = [
        current_time - 15,  # 15 sekunder gammal (över fönstret)
        current_time - 5,   # 5 sekunder gammal (inom fönstret)
        current_time        # Ny begäran
    ]
    
    # Kör cleanup
    rate_limiter.cleanup(ip)
    
    # Ska bara ha kvar de två nyaste begäran
    assert len(rate_limiter.request_counts[ip]) == 2


@pytest.mark.asyncio
async def test_middleware_allows_requests_under_limit(client):
    """Test att middleware tillåter begäran under gränsen."""
    # Gör begäran under gränsen (5)
    for i in range(5):
        response = client.get("/test", headers={"X-Forwarded-For": "127.0.0.1"})
        assert response.status_code == 200
        assert response.json() == {"message": "success"}


@pytest.mark.asyncio
async def test_middleware_blocks_requests_over_limit(client):
    """Test att middleware blockerar begäran över gränsen."""
    # Gör begäran upp till gränsen
    for i in range(5):
        response = client.get("/test", headers={"X-Forwarded-For": "127.0.0.2"})
        assert response.status_code == 200
    
    # Nästa begäran ska blockeras
    response = client.get("/test", headers={"X-Forwarded-For": "127.0.0.2"})
    assert response.status_code == 429
    assert "Too many requests" in response.text


@pytest.mark.asyncio
async def test_rate_limiter_different_ips(client):
    """Test att rate-limiter hanterar olika IP-adresser separat."""
    # Gör max antal begäran från en IP
    for i in range(5):
        client.get("/test", headers={"X-Forwarded-For": "10.0.0.1"})
    
    # Denna begäran ska blockeras
    response = client.get("/test", headers={"X-Forwarded-For": "10.0.0.1"})
    assert response.status_code == 429
    
    # Men en annan IP ska fortfarande kunna göra begäran
    response = client.get("/test", headers={"X-Forwarded-For": "10.0.0.2"})
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_middleware_disabled_setting(app):
    """Test att middleware inte begränsar när inställningen är avstängd."""
    # Skapa en ny app med inaktiverad rate-limiting
    disabled_settings = MockSettings(RATE_LIMIT_ENABLED=False)
    app.add_middleware(RateLimitingMiddleware, settings=disabled_settings)
    
    client = TestClient(app)
    
    # Gör fler begäran än gränsen
    for i in range(10):  # Dubbla gränsen
        response = client.get("/test", headers={"X-Forwarded-For": "127.0.0.3"})
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_client_ip():
    """Test att extrahera klient-IP från olika headers."""
    from app.middlewares.rate_limiter import get_client_ip
    
    # Test med X-Forwarded-For
    request = Request({"type": "http", "headers": [(b"x-forwarded-for", b"192.168.1.1")]})
    assert await get_client_ip(request) == "192.168.1.1"
    
    # Test med X-Real-IP
    request = Request({"type": "http", "headers": [(b"x-real-ip", b"10.0.0.1")]})
    assert await get_client_ip(request) == "10.0.0.1"
    
    # Test med client.host
    request = Request({"type": "http", "client": ("127.0.0.1", 8000), "headers": []})
    assert await get_client_ip(request) == "127.0.0.1"
    
    # Test med flera IP-adresser i X-Forwarded-For
    request = Request({"type": "http", "headers": [(b"x-forwarded-for", b"192.168.1.1, 10.0.0.1")]})
    assert await get_client_ip(request) == "192.168.1.1"


@pytest.mark.asyncio
async def test_window_expiration(rate_limiter):
    """Test att begäran går igenom efter att tidsfönstret har gått ut."""
    ip = "127.0.0.5"
    
    # Fyll upp med begäran
    for _ in range(5):
        assert rate_limiter.add_request(ip) is True
    
    # Nästa begäran ska blockeras
    assert rate_limiter.add_request(ip) is False
    
    # Simulera att tidsfönstret går ut genom att ändra timestamp på begäran
    current_time = time.time()
    rate_limiter.request_counts[ip] = [current_time - 11]  # 11 sekunder gammal (utanför fönstret)
    
    # Nu ska en ny begäran tillåtas
    assert rate_limiter.add_request(ip) is True
