import pytest
import os
import importlib
from sqlalchemy.orm import Session
from unittest.mock import MagicMock

# We need to adjust the path to import the module under test
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Now we can import the database module
from app.pipelineserver.pipeline_app import database

def test_get_db_dependency():
    """Test the get_db dependency generator ensures the session is closed."""
    db_generator = database.get_db()
    db_session = next(db_generator)

    # Mock the close method on this specific session instance
    db_session.close = MagicMock()

    # Check that we got a session
    assert db_session is not None
    assert isinstance(db_session, Session)

    # Exhaust the generator to trigger the finally block
    with pytest.raises(StopIteration):
        next(db_generator)
    
    # Assert that the mocked close method was called
    db_session.close.assert_called_once()

def test_database_url_for_production(monkeypatch):
    """Test that the correct database URL is used when not in testing mode."""
    # Set TESTING environment variable to 'false'
    monkeypatch.setenv('TESTING', 'false')

    # Reload the database module to apply the environment variable change
    importlib.reload(database)

    # Check that the engine URL is for the file-based database
    assert 'sqlite:///./azom_pipelines.db' in str(database.engine.url)

    # Clean up by resetting to testing mode for other tests
    monkeypatch.setenv('TESTING', 'true')
    importlib.reload(database)
    assert 'sqlite:///:memory:' in str(database.engine.url)
