import os
import sys
import pytest
import json
from unittest.mock import patch, MagicMock, PropertyMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session as SessionBase

# Lägg till sökvägen till projektet i Python-sökvägen
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Hitta sökvägen till testdatakatalogen
TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'test_data')

# Sätt miljövariabel för testning
os.environ['TESTING'] = 'true'

@pytest.fixture(scope="session")
def db_engine():
    """Create a test database engine."""
    # Create an in-memory SQLite database for testing
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    
    # Import models to create tables
    from pipeline_app.models.database_models import Base
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    yield engine
    
    # Cleanup
    engine.dispose()

from sqlalchemy import text

@pytest.fixture(scope="function")
def db_session(db_engine):
    """Create a new database session for a test."""
    connection = db_engine.connect()
    transaction = connection.begin()
    
    # Create a session that's bound to the connection
    session_factory = sessionmaker(bind=connection)
    session = session_factory()
    
    # Begin a savepoint using text() for SQL expressions
    if connection.dialect.name == 'sqlite':
        session.execute(text('BEGIN IMMEDIATE'))
    
    # Start a transaction
    nested = connection.begin_nested()
    
    # If the application code calls commit, it will end the nested
    # transaction. We need to start a new one when that happens.
    @event.listens_for(session, 'after_transaction_end')
    def restart_savepoint(session, transaction):
        nonlocal nested
        if not nested.is_active and connection.in_transaction() and not connection.in_nested_transaction():
            nested = connection.begin_nested()
    
    try:
        yield session
    finally:
        # Cleanup
        session.close()
        transaction.rollback()
        connection.close()

@pytest.fixture(autouse=True)
def setup_test_environment(db_session, monkeypatch):
    """Set up test environment with mocks and patches."""
    # Mock the database session for the application
    def mock_get_db():
        try:
            yield db_session
        finally:
            pass
    
    # Apply the mock to the main module
    monkeypatch.setattr('pipeline_app.main.get_db', mock_get_db)
    
    # Load test products data
    test_products_path = os.path.join(TEST_DATA_DIR, 'test_products.json')
    with open(test_products_path, 'r', encoding='utf-8') as f:
        test_products = json.load(f)
    
    # Create a mock for AZOMKnowledgeService
    mock_knowledge_service = MagicMock()
    
    # Define the behavior for get_product_info
    async def mock_get_product_info(product_name=None, car_model=None):
        print(f"Mock get_product_info called with product_name={product_name}, car_model={car_model}")
        
        # Search by product name (case insensitive)
        if product_name:
            for product in test_products:
                if product['name'].lower() == product_name.lower():
                    return product
        
        # Search by car model (case insensitive)
        if car_model:
            car_model_lower = car_model.lower()
            for product in test_products:
                if 'compatible_models' in product and any(
                    model.lower() == car_model_lower 
                    for model in product['compatible_models']
                ):
                    return product
        
        # If not found, raise an error
        raise ValueError(f"Ingen produkt hittades för namn '{product_name}' eller bilmodell '{car_model}'")
    
    # Set the mock return value
    mock_knowledge_service.get_product_info.side_effect = mock_get_product_info
    
    # Mock the AZOMOrchestrationService
    mock_orchestration_service = MagicMock()
    
    # Define the behavior for orchestrate
    async def mock_orchestrate(user_input, car_model=None, user_experience=None):
        # Default product name is now AZOM DLR
        default_product_name = "AZOM DLR"
        
        # Try to get product info using the mocked service
        try:
            product_info = await mock_get_product_info(default_product_name, car_model)
        except ValueError:
            # If default product not found, try to find any compatible product
            if car_model:
                product_info = await mock_get_product_info(car_model=car_model)
            else:
                product_info = test_products[0]  # Fallback to first test product
        
        # Create a response with the product info
        return {
            "steps": ["Step 1", "Step 2"],
            "total_time": "2 hours",
            "difficulty": "Medium",
            "recommended_product": product_info,
            "experience_level": user_experience or "nybörjare"
        }
    
    # Set the mock return value
    mock_orchestration_service.orchestrate.side_effect = mock_orchestrate
    
    # Patch the services to use our mocks
    monkeypatch.setattr(
        'pipeline_app.services.azom_knowledge_service.AZOMKnowledgeService',
        lambda *args, **kwargs: mock_knowledge_service
    )
    
    monkeypatch.setattr(
        'pipeline_app.services.orchestration_service.AZOMOrchestrationService',
        lambda *args, **kwargs: mock_orchestration_service
    )
    
    # Create a mock for the installation pipeline
    mock_installation_pipeline = MagicMock()
    
    # Define the behavior for run_installation
    async def mock_run_installation(user_input, car_model=None, user_experience=None):
        # Use the mocked orchestration service to get the result
        result = await mock_orchestrate(user_input, car_model, user_experience)
        return {
            "steps": result["steps"],
            "total_time": result["total_time"],
            "difficulty": result["difficulty"],
            "recommended_product": result["recommended_product"],
            "experience_level": result["experience_level"]
        }
    
    # Set the mock return value
    mock_installation_pipeline.run_installation.side_effect = mock_run_installation
    
    # Patch the pipeline instances in main.py
    monkeypatch.setattr(
        'pipeline_app.main.pipeline',
        mock_installation_pipeline
    )
    
    # Also patch the support pipeline
    mock_support_pipeline = MagicMock()
    mock_support_pipeline.run_support.return_value = {"answer": "Test support answer"}
    monkeypatch.setattr(
        'pipeline_app.main.support_pipeline',
        mock_support_pipeline
    )
    
    yield

@pytest.fixture
def test_client(db_session):
    """Create a test client for the FastAPI app."""
    from fastapi.testclient import TestClient
    from pipeline_app.main import app
    from pipeline_app.database import get_db
    
    # Store the original dependency
    original_get_db = app.dependency_overrides.get(get_db)
    
    # Override the get_db dependency to use our test session
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    # Apply the override
    app.dependency_overrides[get_db] = override_get_db
    
    # Create test client with our app
    with TestClient(app) as client:
        yield client
    
    # Clean up overrides
    app.dependency_overrides.clear()
    
    # Restore original dependency if it existed
    if original_get_db is not None:
        app.dependency_overrides[get_db] = original_get_db
