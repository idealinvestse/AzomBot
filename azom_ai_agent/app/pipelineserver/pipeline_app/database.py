"""Database configuration and models for the pipeline server."""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .models.database_models import Base

# Create SQLAlchemy engine and session
# Use in-memory SQLite for tests, file-based for development
TESTING = os.environ.get('TESTING', 'false').lower() == 'true'

if TESTING:
    SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
else:
    SQLALCHEMY_DATABASE_URL = "sqlite:///./azom_pipelines.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
def init_db():
    """Initialize the database by creating all tables."""
    Base.metadata.create_all(bind=engine)

# Initialize the database
init_db()

def get_db():
    """Dependency for getting database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
