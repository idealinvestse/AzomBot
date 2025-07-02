import pytest

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from app.pipelineserver.pipeline_app.pipelines.azom_installation_pipeline import AZOMInstallationPipeline


def test_azom_installation_pipeline_initialization():
    """Test AZOMInstallationPipeline initialization."""
    pipeline = AZOMInstallationPipeline()
    assert pipeline is not None
