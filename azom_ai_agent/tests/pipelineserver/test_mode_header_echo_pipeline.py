import sys
import os
from fastapi.testclient import TestClient
import pytest

# Ensure project root on path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from app.pipelineserver.pipeline_app.main import app  # noqa: E402


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.mark.parametrize("mode", ["LIGHT", "FULL"]) 
def test_pipeline_echoes_mode_header_from_header(client, mode):
    resp = client.post(
        "/chat/azom",
        json={"message": "Hej"},
        headers={"X-AZOM-Mode": mode},
    )
    assert resp.status_code in (200, 413)  # payload may trigger caps; we only assert header echo
    assert resp.headers.get("X-AZOM-Mode") == mode


@pytest.mark.parametrize("mode", ["light", "full"]) 
def test_pipeline_echoes_mode_header_from_query(client, mode):
    resp = client.post(
        f"/chat/azom?mode={mode}",
        json={"message": "Hej"},
    )
    assert resp.status_code in (200, 413)
    assert resp.headers.get("X-AZOM-Mode") == mode
