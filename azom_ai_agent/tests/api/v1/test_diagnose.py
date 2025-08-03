import pytest
from fastapi.testclient import TestClient


def test_diagnose_endpoint(client):
    """
    Tests the /api/v1/diagnose endpoint to ensure it's active and returns the correct message.
    """
    response = client.get("/diagnose")
    assert response.status_code == 200
    assert response.json() == {"diagnose": "Tjänsten är igång. Beskriv felkod eller bilmodell för felsökning."}
