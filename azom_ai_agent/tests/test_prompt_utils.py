import pytest
from pathlib import Path
from app import prompt_utils

@pytest.fixture
def mock_prompt_dir(tmp_path, monkeypatch):
    """Creates a temporary prompt directory and patches prompt_utils.Path."""
    base_dir = tmp_path / "data" / "prompts"
    base_dir.mkdir(parents=True)

    original_path_class = prompt_utils.Path
    def patched_path_constructor(path_str):
        # Intercepts the Path('data/prompts') call and returns an absolute path
        # to our temporary directory structure.
        return tmp_path / original_path_class(path_str)

    monkeypatch.setattr(prompt_utils, 'Path', patched_path_constructor)
    return base_dir

@pytest.mark.asyncio
async def test_inject_prompt_vars():
    prompt = "Hello {{NAME}}, the date is {{CURRENT_DATE}}."
    context = {"NAME": "World"}
    result = await prompt_utils.inject_prompt_vars(prompt, context)
    assert "Hello World" in result
    assert "{{CURRENT_DATE}}" not in result
    assert "{{UNKNOWN}}" in await prompt_utils.inject_prompt_vars("{{UNKNOWN}}", {})

@pytest.mark.asyncio
async def test_select_prompts(mock_prompt_dir):
    # Default
    selected = await prompt_utils.select_prompts({})
    assert len(selected) == 1
    assert "azom_iexpertpro_v3.md" in str(selected[0])

    # With safety flag
    selected = await prompt_utils.select_prompts({'safety_flag': True})
    assert len(selected) == 2
    assert any("azom_safetyfilter_v1.md" in str(p) for p in selected)

    # With session memory
    selected = await prompt_utils.select_prompts({'session_memory': 'some memory'})
    assert len(selected) == 2
    assert any("azom_memoryinject_v1.md" in str(p) for p in selected)

@pytest.mark.asyncio
async def test_compose_full_prompt_success(mock_prompt_dir):
    (mock_prompt_dir / "azom_iexpertpro_v3.md").write_text("System: You are {{ROLE}}.", encoding='utf-8')
    context = {"ROLE": "a bot"}
    user_prompt = "User query"
    
    result = await prompt_utils.compose_full_prompt(user_prompt, context)
    
    assert "System: You are a bot." in result
    assert "User query" in result

@pytest.mark.asyncio
async def test_compose_full_prompt_missing_file_triggers_safety_fallback(mock_prompt_dir):
    # The main prompt is missing, but the safety prompt exists.
    (mock_prompt_dir / "azom_safetyfilter_v1.md").write_text("Safety prompt.", encoding='utf-8')
    context = {'safety_flag': True}
    user_prompt = "User query"
    
    result = await prompt_utils.compose_full_prompt(user_prompt, context)
    
    assert "Safety prompt." in result
    # The specific safety fallback is also triggered because the loaded prompt lacks the keywords.
    assert "Säkerhetsfilter: Var restriktiv och fokusera på säkerhet." in result
    # The main fallback is NOT triggered because at least one file was loaded.
    assert "AZOM Systemprompt" not in result

@pytest.mark.asyncio
async def test_compose_full_prompt_no_files_found_triggers_main_fallback(mock_prompt_dir):
    result = await prompt_utils.compose_full_prompt("User query", {})
    assert "AZOM Systemprompt: Du är en hjälpsam AI-assistent från AZOM." in result
    assert "User query" in result

@pytest.mark.asyncio
async def test_compose_full_prompt_no_files_found_with_safety_flag(mock_prompt_dir):
    context = {'safety_flag': True}
    result = await prompt_utils.compose_full_prompt("User query", context)
    assert "AZOM Systemprompt" in result
    assert "Säkerhetsfilter: Var restriktiv och fokusera på säkerhet." in result
