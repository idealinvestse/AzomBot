import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from starlette.responses import JSONResponse

from app.middlewares.rate_limiter import RateLimitingMiddleware
from app.config import Settings

# --- Fixtures ---

@pytest.fixture
def mock_settings_enabled():
    """Provides settings with rate limiting enabled."""
    settings = Settings()
    settings.RATE_LIMIT_ENABLED = True
    settings.RATE_LIMIT_REQUESTS = 5
    settings.RATE_LIMIT_WINDOW_SECONDS = 10
    return settings

@pytest.fixture
def app(mock_settings_enabled):
    """Creates a FastAPI app instance with the rate limiting middleware."""
    test_app = FastAPI()
    test_app.state.settings = mock_settings_enabled
    test_app.add_middleware(RateLimitingMiddleware)

    @test_app.get("/test")
    async def test_endpoint(request: Request):
        client_ip = request.client.host if request.client else "testclient"
        return JSONResponse({"message": "success", "client_ip": client_ip})

    return test_app

@pytest.fixture
def client(app):
    """Provides a TestClient for making requests to the app."""
    with TestClient(app, base_url="http://testserver") as test_client:
        yield test_client

# --- Middleware Integration Tests (Refactored) ---

def test_middleware_allows_requests_under_limit(client):
    """The middleware should allow requests that are under the limit."""
    headers = {"X-Forwarded-For": "1.1.1.1"}
    for i in range(5):
        response = client.get("/test", headers=headers)
        assert response.status_code == 200, f"Request {i+1} failed"

def test_middleware_blocks_requests_over_limit(client):
    """The middleware should block requests that exceed the limit and add Retry-After header."""
    headers = {"X-Forwarded-For": "2.2.2.2"}
    # Exhaust the limit
    for _ in range(5):
        response = client.get("/test", headers=headers)
        assert response.status_code == 200

    # The 6th request should be blocked
    response = client.get("/test", headers=headers)
    assert response.status_code == 429
    assert "Retry-After" in response.headers
    assert int(response.headers["Retry-After"]) <= 10

def test_middleware_handles_different_ips_independently(client):
    """The middleware should track limits for different IPs separately."""
    headers_ip1 = {"X-Forwarded-For": "3.3.3.3"}
    headers_ip2 = {"X-Forwarded-For": "4.4.4.4"}

    # Exhaust limit for IP 1
    for _ in range(5):
        assert client.get("/test", headers=headers_ip1).status_code == 200
    assert client.get("/test", headers=headers_ip1).status_code == 429

    # IP 2 should still be allowed
    assert client.get("/test", headers=headers_ip2).status_code == 200

def test_middleware_is_disabled_via_settings():
    """The middleware should not block requests if disabled in settings."""
    disabled_settings = Settings()
    disabled_settings.RATE_LIMIT_ENABLED = False
    disabled_settings.RATE_LIMIT_REQUESTS = 1  # Set a low limit to confirm it's ignored
    disabled_settings.RATE_LIMIT_WINDOW_SECONDS = 10
    app_disabled = FastAPI()
    app_disabled.state.settings = disabled_settings
    app_disabled.add_middleware(RateLimitingMiddleware)

    @app_disabled.get("/test")
    async def test_endpoint(request: Request):
        return JSONResponse({"message": "success"})

    with TestClient(app_disabled) as client_disabled:
        # Make more requests than the limit, should not be blocked
        for _ in range(5):
            response = client_disabled.get("/test")
            assert response.status_code == 200
