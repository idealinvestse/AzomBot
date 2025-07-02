import pytest
import sys
import os
from pathlib import Path
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import FastAPI

# Add the parent directory to the path so we can import the app
sys.path.append(str(Path(__file__).parent.parent))

# Test data
TEST_PRODUCT = {
    "name": "Test Product",
    "description": "A test product",
    "price": 999.99,
    "category": "test",
    "sku": "TEST-001",
    "stock_quantity": 10
}

TEST_FAQ = {
    "question": "Test question?",
    "answer": "Test answer.",
    "category": "general"
}

TEST_TROUBLESHOOTING_STEP = {
    "symptom": "Test symptom",
    "possible_cause": "Test cause",
    "solution": "Test solution",
    "car_model": "Test Model"
}

@pytest.fixture
def admin_client():
    from pipeline_app.main import app
    
    # Mock authentication
    app.dependency_overrides = {}
    
    # Mock the database session
    with patch('pipeline_app.database.SessionLocal') as mock_session:
        mock_db = MagicMock()
        mock_session.return_value = mock_db
        
        # Mock the token verification
        with patch('pipeline_app.admin.auth.verify_credentials') as mock_verify:
            mock_verify.return_value = "admin_user"
            with TestClient(app) as client:
                yield client

# Products endpoints
def test_create_product(admin_client):
    """Test creating a new product."""
    # Mock the database operations
    with patch('pipeline_app.admin.products_api.save_products') as mock_create:
        mock_create.return_value = {**TEST_PRODUCT, "id": 1}
        
        response = admin_client.post(
            "/admin/products",
            json=TEST_PRODUCT,
            headers={"Authorization": "Basic YWRtaW46YXpvbTEyMw=="}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == TEST_PRODUCT["name"]

def test_get_products(admin_client):
    """Test retrieving all products."""
    # Mock the database operations
    with patch('pipeline_app.admin.products_api.load_products') as mock_get:
        mock_get.return_value = [{**TEST_PRODUCT, "id": 1}]
        
        response = admin_client.get(
            "/admin/products",
            headers={"Authorization": "Basic YWRtaW46YXpvbTEyMw=="}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert data[0]["name"] == TEST_PRODUCT["name"]

# FAQ endpoints
def test_create_faq(admin_client):
    """Test creating a new FAQ."""
    # Mock the database operations
    with patch('pipeline_app.admin.faq_api.save_faq') as mock_create:
        mock_create.return_value = {**TEST_FAQ, "id": 1}
        
        response = admin_client.post(
            "/admin/faq",
            json=TEST_FAQ,
            headers={"Authorization": "Basic YWRtaW46YXpvbTEyMw=="}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["question"] == TEST_FAQ["question"]

def test_get_faqs(admin_client):
    """Test retrieving all FAQs."""
    # Mock the database operations
    with patch('pipeline_app.admin.faq_api.load_faq') as mock_get:
        mock_get.return_value = [{**TEST_FAQ, "id": 1}]
        
        response = admin_client.get(
            "/admin/faq",
            headers={"Authorization": "Basic YWRtaW46YXpvbTEyMw=="}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

# Troubleshooting endpoints
def test_add_troubleshooting_step(admin_client):
    """Test adding a new troubleshooting step."""
    # Mock the database operations
    with patch('pipeline_app.admin.troubleshooting_api.save_troubleshooting') as mock_create:
        mock_create.return_value = {**TEST_TROUBLESHOOTING_STEP, "id": 1}
        
        response = admin_client.post(
            "/admin/troubleshooting",
            json=TEST_TROUBLESHOOTING_STEP,
            headers={"Authorization": "Basic YWRtaW46YXpvbTEyMw=="}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["symptom"] == TEST_TROUBLESHOOTING_STEP["symptom"]

def test_get_troubleshooting_steps(admin_client):
    """Test retrieving troubleshooting steps."""
    # Mock the database operations
    with patch('pipeline_app.admin.troubleshooting_api.load_troubleshooting') as mock_get:
        mock_get.return_value = [{**TEST_TROUBLESHOOTING_STEP, "id": 1}]
        
        response = admin_client.get(
            "/admin/troubleshooting",
            headers={"Authorization": "Basic YWRtaW46YXpvbTEyMw=="}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

# Test authentication
def test_unauthenticated_access():
    """Test that unauthenticated access is denied."""
    from pipeline_app.main import app
    
    with TestClient(app) as client:
        response = client.get("/admin/products")
        assert response.status_code in [401, 403]  # Unauthorized or Forbidden
