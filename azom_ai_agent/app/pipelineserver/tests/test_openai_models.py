import pytest

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from app.pipelineserver.pipeline_app.models.openai_models import OpenAIModel


def test_openai_model_initialization():
    """Test OpenAIModel initialization."""
    model = OpenAIModel()
    assert model is not None
