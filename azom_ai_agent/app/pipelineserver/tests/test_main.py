import pytest
from fastapi.testclient import TestClient
import sys
import os
import json
from unittest.mock import patch, MagicMock

# Importera appen efter att ha konfigurerat sökvägarna
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pipeline_app.main import app

# Läs in testdata
TEST_PRODUCTS_PATH = os.path.join(os.path.dirname(__file__), 'test_data/test_products.json')
with open(TEST_PRODUCTS_PATH, 'r', encoding='utf-8') as f:
    TEST_PRODUCTS = json.load(f)

def test_health_check(test_client):
    """Testa hälsokontrollen."""
    # Test the health check endpoint directly
    response = test_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_pipeline_install_dummy(test_client):
    """Testa en lyckad installation."""
    # Testdata - använd en produkt som faktiskt finns i databasen
    payload = {
        "user_input": "Jag vill installera AZOM på min bil",
        "car_model": "Honda CR-V",
        "user_experience": "nybörjare"
    }
    
    # Gör anropet
    response = test_client.post("/pipeline/install", json=payload)
    
    # Skriv ut felmeddelande om status inte är 200
    if response.status_code != 200:
        print(f"Fel vid anrop till /pipeline/install: {response.status_code}")
        print(f"Svar: {response.text}")
    
    # Verifiera resultatet
    assert response.status_code == 200, f"Fick oväntat statuskod {response.status_code}: {response.text}"
    response_data = response.json()
    assert "result" in response_data, f"Saknar 'result' i svaret: {response_data}"
    assert "recommended_product" in response_data["result"], f"Saknar 'recommended_product' i resultatet: {response_data}"
    assert "steps" in response_data["result"], f"Saknar 'steps' i resultatet: {response_data}"
    assert isinstance(response_data["result"]["steps"], list), "steps är inte en lista"
    assert len(response_data["result"]["steps"]) > 0, "Inga installationssteg returnerades"
    # Expecting "AZOM DLR" as that's what the orchestration service is hardcoded to return for Honda CR-V
    assert "AZOM DLR" in response_data["result"]["recommended_product"]["name"], \
        f"Fick fel produkt: {response_data['result']['recommended_product']['name']}. Förväntade mig en produkt med 'AZOM DLR' i namnet."

def test_pipeline_missing_input(test_client):
    """Testa med saknad användarinput."""
    response = test_client.post(
        "/pipeline/install", 
        json={"user_input": "", "car_model": "Volvo"}
    )
    assert response.status_code == 400
    assert "Ange en beskrivning" in response.json()["detail"]

def test_pipeline_missing_car_model(test_client):
    """Testa med saknad bilmodell."""
    response = test_client.post(
        "/pipeline/install", 
        json={"user_input": "Jag vill installera AZOM", "car_model": ""}
    )
    assert response.status_code == 400
    assert "Ange bilmodell" in response.json()["detail"]

def test_pipeline_default_experience_level(test_client):
    """Testa med standardvärde för användarupplevelse."""
    # Gör anropet utan user_experience
    response = test_client.post(
        "/pipeline/install",
        json={
            "user_input": "Installation",
            "car_model": "Honda CR-V"
        }
    )

    # Skriv ut felmeddelande om status inte är 200
    if response.status_code != 200:
        print(f"Fel vid anrop till /pipeline/install: {response.status_code}")
        print(f"Svar: {response.text}")
    
    # Verifiera resultatet
    assert response.status_code == 200, f"Fick oväntat statuskod {response.status_code}: {response.text}"
    result = response.json()
    assert "result" in result, f"Saknar 'result' i svaret: {result}"
    assert "recommended_product" in result["result"], f"Saknar 'recommended_product' i resultatet: {result}"
    assert "experience_level" in result["result"], f"Saknar 'experience_level' i resultatet: {result}"
    
    # Check that we got the expected product (should be AZOM DLR for Honda CR-V)
    assert "AZOM DLR" in result["result"]["recommended_product"]["name"], \
        f"Fick fel produkt: {result['result']['recommended_product']['name']}. Förväntade mig en produkt med 'AZOM DLR' i namnet."
    
    # Check default experience level
    assert result["result"]["experience_level"] == "nybörjare", \
        f"Fick fel experience_level: {result['result']['experience_level']}"
