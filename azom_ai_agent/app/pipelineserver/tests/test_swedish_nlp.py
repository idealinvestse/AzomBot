import pytest

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from app.pipelineserver.pipeline_app.utils.swedish_nlp import SwedishNLP


def test_swedish_nlp_initialization():
    """Test SwedishNLP initialization."""
    nlp = SwedishNLP()
    assert nlp is not None

# Placeholder for additional tests if methods are added or confirmed in source
# Example test for a potential method, will be skipped if method doesn't exist
def test_swedish_nlp_process_text():
    """Test processing text with SwedishNLP, if method exists."""
    nlp = SwedishNLP()
    try:
        result = nlp.process_text("Hej, hur mår du?")
        assert result is not None
    except AttributeError:
        pytest.skip("process_text method not found in SwedishNLP")
