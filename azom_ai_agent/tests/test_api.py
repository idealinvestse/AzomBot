import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.main import app as main_app  # Rename to avoid conflict
from app.config import Settings, get_current_config


@pytest.fixture
def client() -> TestClient:
    """Fixture to create a TestClient with proper settings state."""
    app = FastAPI()
    
    settings = Settings()

    # Manually add middleware, mirroring main.py, to ensure a stable test environment.
    # This is necessary because dynamically iterating main_app.user_middleware proved unreliable.
    from starlette.middleware.cors import CORSMiddleware
    from app.middlewares.request_logging import RequestLoggingMiddleware
    from app.middlewares.rate_limiter import RateLimitingMiddleware

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(RateLimitingMiddleware)

    # Add routes from the main application
    app.include_router(main_app.router)

    # Attach settings to the app state, which is critical for the middleware
    app.state.settings = settings
    
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def reset_runtime_settings():
    """
    Fixture to ensure runtime settings are reset to their initial state
    before each test that might modify them. This prevents state leakage
    between tests.
    """
    initial_state = Settings().model_dump()
    from app import config
    config._current_settings = initial_state.copy()
    yield
    config._current_settings = initial_state.copy()


def test_ping(client: TestClient):
    r = client.get("/ping")
    assert r.status_code == 200
    assert "version" in r.json()

def test_health(client: TestClient):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "systemet är friskt"

def test_knowledge_status(client: TestClient):
    r = client.get("/knowledge/status")
    assert r.status_code == 200
    assert "status" in r.json()
    assert "categories" in r.json()

def test_knowledge_upload_wrong_format(client: TestClient):
    response = client.post(
        "/knowledge/upload",
        files={"files": ("feltyp.exe", b"data"),},
        data={"category": "testcat"}
    )
    assert response.status_code == 400
    assert "Filtyp inte stödd" in response.text

def test_knowledge_upload_too_large(client: TestClient, monkeypatch):
    class DummyUpload:
        filename = "too_big.md"
        async def read(self):
            return b'a' * (11 * 1024 * 1024)  # 11MB
    r = client.post(
        "/knowledge/upload",
        files={"files": ("dummy.md", b'a' * (11 * 1024 * 1024))},
        data={"category": "testcat"}
    )
    assert r.status_code == 400
    assert "för stor" in r.text

# --- Tests for Settings Endpoint ---

def test_update_settings_success(client: TestClient):
    """Test that the settings endpoint returns 204 No Content for a valid payload."""
    payload = {
        "llmBackend": "groq",
        "targetModel": "llama3-70b-8192",
        "groqApiKey": "gsk_test_12345",
        "theme": "light"
    }
    response = client.post("/api/v1/settings", json=payload)
    assert response.status_code == 204


def test_update_settings_and_verify_change(client: TestClient):
    """Test that the backend's runtime configuration is correctly updated after a valid request."""
    payload = {
        "llmBackend": "groq",
        "targetModel": "new-model-for-test",
        "groqApiKey": "a-new-key"
    }
    
    client.post("/api/v1/settings", json=payload)
    
    current_config = get_current_config()
    assert current_config["LLM_BACKEND"] == "groq"
    assert current_config["TARGET_MODEL"] == "new-model-for-test"
    assert current_config["GROQ_API_KEY"] == "a-new-key"


def test_update_settings_validation_error(client: TestClient):
    """Test that the endpoint returns 422 for a payload with invalid data (e.g., wrong type)."""
    payload = {
        "llmBackend": 12345,
        "targetModel": "some-model"
    }
    response = client.post("/api/v1/settings", json=payload)
    assert response.status_code == 422


def test_update_settings_missing_required_field(client: TestClient):
    """Test that the endpoint returns 422 for a payload missing a required field ('targetModel')."""
    payload = {
        "llmBackend": "openwebui"
    }
    response = client.post("/api/v1/settings", json=payload)
    assert response.status_code == 422
