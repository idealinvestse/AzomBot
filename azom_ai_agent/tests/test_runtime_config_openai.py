import pytest

from app.config import FrontendSettings, update_runtime_settings, get_current_config


def test_update_runtime_settings_maps_openai_keys_and_backend():
    # Build a FrontendSettings payload mimicking frontend runtime change
    fs = FrontendSettings(
        llmBackend="openai",
        openaiApiKey="sk-live-test",
        openaiBaseUrl="https://gateway.example.com/v1",
        targetModel="gpt-4o-mini",
        openwebuiUrl=None,
        openwebuiApiToken=None,
        groqApiKey=None,
    )

    # Snapshot current config to restore after test
    current_before = get_current_config().copy()
    try:
        update_runtime_settings(fs)
        cfg = get_current_config()
        assert cfg["LLM_BACKEND"] == "openai"
        assert cfg["OPENAI_API_KEY"] == "sk-live-test"
        assert cfg["OPENAI_BASE_URL"] == "https://gateway.example.com/v1"
        assert cfg["TARGET_MODEL"] == "gpt-4o-mini"
    finally:
        # restore keys we may have changed
        for k, v in current_before.items():
            get_current_config()[k] = v
