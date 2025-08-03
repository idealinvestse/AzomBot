import pytest
import json
import os
from unittest.mock import MagicMock
from app.pipelineserver.pipeline_app.pipelines.troubleshooting_pipeline import TroubleshootingPipeline

@pytest.fixture(autouse=True)
def mock_orchestration_service(monkeypatch):
    """Automatically mock the AZOMOrchestrationService for all tests in this file."""
    mock_service = MagicMock()
    monkeypatch.setattr(
        'app.pipelineserver.pipeline_app.pipelines.troubleshooting_pipeline.AZOMOrchestrationService',
        lambda: mock_service
    )

@pytest.fixture
def mock_data_dir(tmp_path):
    """Creates a temporary data directory with mock troubleshooting files."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    return data_dir

def test_init_loads_troubleshooting_json(mock_data_dir, monkeypatch):
    """Test that the pipeline correctly loads the main troubleshooting.json."""
    troubleshooting_content = [{
        "model": "Test Model S",
        "issue_keywords": ["no power"],
        "steps": ["Check the main fuse."]
    }]
    (mock_data_dir / "troubleshooting.json").write_text(json.dumps(troubleshooting_content), encoding='utf-8')

    # Patch the os.path.dirname to point to our mock setup
    monkeypatch.setattr('app.pipelineserver.pipeline_app.pipelines.troubleshooting_pipeline.os.path.abspath', lambda _: str(mock_data_dir))

    pipeline = TroubleshootingPipeline()
    assert len(pipeline.troubleshooting_data) == 1
    assert pipeline.troubleshooting_data[0]["model"] == "Test Model S"

def test_init_loads_other_troubleshooting_files(mock_data_dir, monkeypatch):
    """Test that the pipeline loads other relevant troubleshooting files."""
    other_content = [{
        "model": "Test Model X",
        "issue_keywords": ["flickering"],
        "steps": ["Check the display cable."]
    }]
    (mock_data_dir / "other_troubleshooting_guide.json").write_text(json.dumps(other_content), encoding='utf-8')
    (mock_data_dir / "other_errors.json").write_text(json.dumps(other_content), encoding='utf-8')
    (mock_data_dir / "other_irrelevant.json").write_text("[]", encoding='utf-8') # Should not be loaded

    monkeypatch.setattr('app.pipelineserver.pipeline_app.pipelines.troubleshooting_pipeline.os.path.abspath', lambda _: str(mock_data_dir))

    pipeline = TroubleshootingPipeline()
    assert len(pipeline.troubleshooting_data) == 2

def test_init_handles_missing_files_gracefully(mock_data_dir, monkeypatch):
    """Test that the pipeline doesn't crash if no files are found."""
    monkeypatch.setattr('app.pipelineserver.pipeline_app.pipelines.troubleshooting_pipeline.os.path.abspath', lambda _: str(mock_data_dir))
    pipeline = TroubleshootingPipeline()
    assert len(pipeline.troubleshooting_data) == 0

def test_init_handles_malformed_json_gracefully(mock_data_dir, monkeypatch):
    """Test that the pipeline skips malformed JSON files."""
    (mock_data_dir / "troubleshooting.json").write_text("this is not json", encoding='utf-8')
    monkeypatch.setattr('app.pipelineserver.pipeline_app.pipelines.troubleshooting_pipeline.os.path.abspath', lambda _: str(mock_data_dir))
    pipeline = TroubleshootingPipeline()
    assert len(pipeline.troubleshooting_data) == 0

@pytest.mark.asyncio
async def test_run_troubleshooting_no_match_found():
    """Test the response when no troubleshooting guide matches the query."""
    pipeline = TroubleshootingPipeline()
    pipeline.troubleshooting_data = [] # Ensure no data
    result = await pipeline.run_troubleshooting("some random issue", "Some Car")
    assert result == {"steps": ["Ingen felsökningsguide hittades för din fråga. Kontrollera stavning eller kontakta support."]}

@pytest.mark.asyncio
async def test_run_troubleshooting_match_by_car_model():
    """Test finding a guide by matching the car model."""
    pipeline = TroubleshootingPipeline()
    pipeline.troubleshooting_data = [{
        "model": "Test CR-V",
        "issue_keywords": ["no power"],
        "steps": ["Step 1 for CR-V"]
    }]
    result = await pipeline.run_troubleshooting("it won't start", "Test CR-V")
    assert result == {"steps": ["Step 1 for CR-V"]}

@pytest.mark.asyncio
async def test_run_troubleshooting_match_by_keyword():
    """Test finding a guide by matching a keyword."""
    pipeline = TroubleshootingPipeline()
    pipeline.troubleshooting_data = [{
        "model": "Some Other Model",
        "issue_keywords": ["bluetooth"],
        "steps": ["Reset bluetooth module."]
    }]
    result = await pipeline.run_troubleshooting("my bluetooth is not working", "Test CR-V")
    assert result == {"steps": ["Reset bluetooth module."]}

@pytest.mark.asyncio
async def test_run_troubleshooting_deduplicates_steps():
    """Test that steps from multiple matching guides are merged and deduplicated."""
    pipeline = TroubleshootingPipeline()
    pipeline.troubleshooting_data = [
        {
            "model": "Test CR-V",
            "issue_keywords": ["power"],
            "steps": ["Check fuse", "Check battery"]
        },
        {
            "model": "Any",
            "issue_keywords": ["power"],
            "steps": ["Check battery", "Call support"]
        }
    ]
    result = await pipeline.run_troubleshooting("no power", "Test CR-V")
    # Order is preserved from the first appearance
    assert result == {"steps": ["Check fuse", "Check battery", "Call support"]}
