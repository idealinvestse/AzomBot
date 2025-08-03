import pytest
import time
from pathlib import Path

from app.services.knowledge_service import KnowledgeService

# --- Fixtures ---

@pytest.fixture
def knowledge_base_dir(tmp_path: Path) -> Path:
    """Creates a temporary knowledge base directory with sample files."""
    kb_path = tmp_path / "knowledge_base"
    
    # Category 1: Manuals
    manuals_path = kb_path / "manuals"
    manuals_path.mkdir(parents=True)
    (manuals_path / "volvo_install.md").write_text("Installation guide for Volvo.")
    (manuals_path / "tesla_guide.md").write_text("Guide for Tesla Model 3.")

    # Category 2: Products
    products_path = kb_path / "products"
    products_path.mkdir()
    (products_path / "parts.csv").write_text("part_id,name\n1,Wheel\n2,Brake Pad")
    
    # Category 3: FAQs
    faqs_path = kb_path / "faqs"
    faqs_path.mkdir()
    (faqs_path / "common_issues.json").write_text('{"q1": "How to reset?", "a1": "Press the reset button."}')

    return tmp_path

@pytest.fixture
def knowledge_service(knowledge_base_dir: Path) -> KnowledgeService:
    """Provides a KnowledgeService instance with a temporary data path."""
    return KnowledgeService(data_path=knowledge_base_dir, ttl=3600)

# --- KnowledgeService Tests ---

def test_knowledge_service_initialization(knowledge_service, knowledge_base_dir):
    """Tests that the KnowledgeService initializes correctly."""
    assert knowledge_service.data_path == knowledge_base_dir / "knowledge_base"
    assert knowledge_service.ttl == 3600
    assert not knowledge_service.cache  # Cache should be empty initially

def test_load_knowledge_populates_cache(knowledge_service):
    """Tests that load_knowledge correctly populates the cache from files."""
    knowledge_service.load_knowledge()
    
    assert "manuals" in knowledge_service.cache
    assert "products" in knowledge_service.cache
    assert "faqs" in knowledge_service.cache
    
    # Check if specific files were loaded
    assert "volvo_install.md" in knowledge_service.cache["manuals"]
    assert "parts.csv" in knowledge_service.cache["products"]
    assert "common_issues.json" in knowledge_service.cache["faqs"]

    # Check content types
    assert knowledge_service.cache["manuals"]["volvo_install.md"]["type"] == "md"
    assert knowledge_service.cache["products"]["parts.csv"]["type"] == "csv"
    assert knowledge_service.cache["faqs"]["common_issues.json"]["type"] == "json"

def test_get_knowledge_triggers_load(knowledge_service):
    """Tests that get_knowledge triggers a load if the cache is empty."""
    assert not knowledge_service.cache
    knowledge = knowledge_service.get_knowledge()
    assert knowledge  # Cache should now be populated
    assert "manuals" in knowledge

def test_get_knowledge_returns_cached_data(knowledge_service):
    """Tests that get_knowledge returns data from cache if available."""
    knowledge_service.load_knowledge() # Pre-populate cache
    first_call_timestamp = knowledge_service.cache_timestamp
    
    time.sleep(0.1) # Ensure time passes but not enough to expire cache
    
    knowledge = knowledge_service.get_knowledge()
    second_call_timestamp = knowledge_service.cache_timestamp

    assert knowledge
    assert first_call_timestamp == second_call_timestamp # Timestamp should not change

def test_get_knowledge_reloads_after_ttl(knowledge_service):
    """Tests that get_knowledge reloads data after the TTL expires."""
    knowledge_service.ttl = 1 # Set a short TTL
    knowledge_service.load_knowledge()
    first_call_timestamp = knowledge_service.cache_timestamp

    time.sleep(1.1) # Wait for TTL to expire

    knowledge = knowledge_service.get_knowledge()
    second_call_timestamp = knowledge_service.cache_timestamp

    assert knowledge
    assert second_call_timestamp > first_call_timestamp # Timestamp should be updated

def test_get_knowledge_with_category_filter(knowledge_service):
    """Tests that get_knowledge can filter results by category."""
    # The method returns the dictionary for the specified category
    manuals_knowledge = knowledge_service.get_knowledge(category="manuals")
    
    # The result should be a non-empty dictionary containing the manuals
    assert isinstance(manuals_knowledge, dict)
    assert len(manuals_knowledge) == 2  # Two manuals were created
    assert "volvo_install.md" in manuals_knowledge
    assert "tesla_guide.md" in manuals_knowledge

    # Also test that a non-existent category returns an empty dict
    non_existent_knowledge = knowledge_service.get_knowledge(category="non_existent")
    assert isinstance(non_existent_knowledge, dict)
    assert not non_existent_knowledge
