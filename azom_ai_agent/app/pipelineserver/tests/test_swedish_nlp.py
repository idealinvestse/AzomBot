import pytest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from app.pipelineserver.pipeline_app.utils.swedish_nlp import SwedishNLP


@pytest.mark.asyncio
async def test_swedish_nlp_initialization():
    """Test SwedishNLP initialization."""
    nlp = SwedishNLP()
    assert nlp is not None


@pytest.mark.asyncio
async def test_extract_car_entities():
    """Test the extract_car_entities method."""
    nlp = SwedishNLP()

    # Test case where the entity is found
    text_with_volvo = "Jag kör en Volvo V90."
    entities = await nlp.extract_car_entities(text_with_volvo)
    assert entities == ["Volvo"]

    # Test case with different casing
    text_with_volvo_upper = "Min bil är en VOLVO."
    entities_upper = await nlp.extract_car_entities(text_with_volvo_upper)
    assert entities_upper == ["Volvo"]

    # Test case where the entity is not found
    text_without_volvo = "Jag har en Saab."
    no_entities = await nlp.extract_car_entities(text_without_volvo)
    assert no_entities == []
