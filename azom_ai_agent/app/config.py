"""Konfigurationsmodul för AZOM AI Agent.

Denna modul hanterar konfigurationsinställningar för hela applikationen med stöd för
miljövariabler, .env-filer och standardvärden.
"""
from __future__ import annotations

import os
from enum import Enum
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union


class LogLevel(str, Enum):
    """Giltiga loggningsnivåer."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class FrontendSettings(BaseModel):
    """Defines the structure of settings coming from the frontend."""
    llm_backend: str = Field(alias='llmBackend')
    openwebui_url: Optional[str] = Field(None, alias='openwebuiUrl')
    openwebui_api_token: Optional[str] = Field(None, alias='openwebuiApiToken')
    groq_api_key: Optional[str] = Field(None, alias='groqApiKey')
    openai_api_key: Optional[str] = Field(None, alias='openaiApiKey')
    openai_base_url: Optional[str] = Field(None, alias='openaiBaseUrl')
    target_model: str = Field(alias='targetModel')

    model_config = SettingsConfigDict(
        populate_by_name=True,  # Allows using alias for population
        extra="ignore"
    )

class Settings(BaseSettings):
    """Huvudkonfiguration för AZOM AI Agent.
    
    Attribut:
        APP_NAME: Applikationens namn som visas i API dokumentation
        APP_VERSION: Aktuell versionsstring
        DEBUG: Aktiverar debug-läge om True
        HOST: Värdadress som API:t binder till
        PORT: Port som API:t lyssnar på
        OPENWEBUI_URL: URL till OpenWebUI-backend
        OPENWEBUI_API_TOKEN: API-token för OpenWebUI
        TARGET_MODEL: Modellnamn att använda i OpenWebUI
        DATA_PATH: Sökväg till datakatalog
        KNOWLEDGE_CACHE_TTL: Time-to-live för kunskapscache i sekunder
        ENABLE_DYNAMIC_KNOWLEDGE: Aktivera dynamisk inläsning av kunskapsdata
        ENABLE_SCHEDULED_UPDATES: Aktivera schemalagda uppdateringar
        LOG_LEVEL: Loggningsnivå
        LOG_FORMAT: Format för loggmeddelanden
        MAX_REQUEST_SIZE_MB: Maximal storlek på HTTP-requests i MB
        RATE_LIMIT_REQUESTS: Antal requests tillåtna per timme per IP
        CORS_ORIGINS: Lista med tillåtna CORS origins
    """
    APP_NAME: str = "AZOM AI Agent"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8008
    OPENWEBUI_URL: str = "http://192.168.50.164:3000"
    OPENWEBUI_API_TOKEN: Optional[str] = "sk-34c40884f61b46fd824629f88cfbf1f0"  # Default för tests/utv
    GROQ_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_BASE_URL: Optional[str] = None
    LLM_BACKEND: str = "openwebui"
    TARGET_MODEL: str = "azom-se-general"
    DATA_PATH: Path = Path("data")
    KNOWLEDGE_CACHE_TTL: int = 3600
    ENABLE_DYNAMIC_KNOWLEDGE: bool = True
    ENABLE_SCHEDULED_UPDATES: bool = True
    LOG_LEVEL: LogLevel = LogLevel.INFO
    LOG_FORMAT: str = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    MAX_REQUEST_SIZE_MB: int = 10
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW_SECONDS: int = 3600  # 1 hour
    CORS_ORIGINS: List[str] = ["*"]
    
    # Pydantic-konfiguration
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        extra="ignore",
        validate_default=True
    )
    
    def get_data_path(self, *paths: str) -> Path:
        """Returnerar en komplett sökväg relativ till DATA_PATH.
        
        Args:
            *paths: Ytterligare sökvägskomponenter att lägga till
            
        Returns:
            En Path-instans med den kompletta sökvägen
        """
        return self.DATA_PATH.joinpath(*paths)
    
    def to_dict(self) -> Dict[str, Any]:
        """Konverterar inställningar till ett dictionary.
        
        Returns:
            Dictionary med alla konfigurationsvärden
        """
        return self.model_dump()

# --- Dynamic Settings Management ---

# Initialize settings from file/env
_initial_settings = Settings()
# Create a mutable dictionary for runtime settings
_current_settings: Dict[str, Any] = _initial_settings.model_dump()

def update_runtime_settings(new_settings: FrontendSettings):
    """Updates the runtime configuration from frontend settings."""
    global _current_settings
    
    update_data = new_settings.model_dump(by_alias=False)  # get snake_case keys
    
    mapping = {
        'llm_backend': 'LLM_BACKEND',
        'openwebui_url': 'OPENWEBUI_URL',
        'openwebui_api_token': 'OPENWEBUI_API_TOKEN',
        'groq_api_key': 'GROQ_API_KEY',
        'openai_api_key': 'OPENAI_API_KEY',
        'openai_base_url': 'OPENAI_BASE_URL',
        'target_model': 'TARGET_MODEL',
    }
    
    updates_applied = {}
    for frontend_key, backend_key in mapping.items():
        if frontend_key in update_data and update_data[frontend_key] is not None:
            _current_settings[backend_key] = update_data[frontend_key]
            updates_applied[backend_key] = update_data[frontend_key]

    if updates_applied:
        print(f"Runtime settings updated: {updates_applied}")

def get_current_config() -> Dict[str, Any]:
    """FastAPI dependency to get the current runtime configuration."""
    return _current_settings
