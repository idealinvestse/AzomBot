import pytest

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from app.pipelineserver.pipeline_app.models.azom_models import (
    AZOMProduct,
    InstallationRecommendation,
    PipelineInstallRequest,
    PipelineInstallResponse
)


def test_azom_product_model():
    """Test AZOMProduct model initialization and attributes."""
    product = AZOMProduct(
        name="AZOM Sensor",
        price_sek=1999,
        success_rate=95,
        installation_time="30 minutes",
        canbus_required=False
    )
    
    assert product.name == "AZOM Sensor"
    assert product.price_sek == 1999
    assert product.success_rate == 95
    assert product.installation_time == "30 minutes"
    assert product.canbus_required == False


def test_installation_recommendation_model():
    """Test InstallationRecommendation model initialization and attributes."""
    product = AZOMProduct(
        name="AZOM Sensor",
        price_sek=1999,
        success_rate=95,
        installation_time="30 minutes",
        canbus_required=False
    )
    recommendation = InstallationRecommendation(
        recommended_product=product,
        alternative_products=[product],
        installation_steps=["Step 1", "Step 2"],
        safety_warnings=["Warning 1"]
    )
    
    assert recommendation.recommended_product == product
    assert len(recommendation.alternative_products) == 1
    assert len(recommendation.installation_steps) == 2
    assert len(recommendation.safety_warnings) == 1


def test_pipeline_install_request_model():
    """Test PipelineInstallRequest model initialization and attributes."""
    request = PipelineInstallRequest(
        user_input="Install AZOM on Volvo",
        car_model="Volvo XC60",
        user_experience="beginner"
    )
    
    assert request.user_input == "Install AZOM on Volvo"
    assert request.car_model == "Volvo XC60"
    assert request.user_experience == "beginner"


def test_pipeline_install_response_model():
    """Test PipelineInstallResponse model initialization and attributes."""
    product = AZOMProduct(
        name="AZOM Sensor",
        price_sek=1999,
        success_rate=95,
        installation_time="30 minutes",
        canbus_required=False
    )
    recommendation = InstallationRecommendation(
        recommended_product=product
    )
    response = PipelineInstallResponse(
        result=recommendation
    )
    
    assert response.result == recommendation
