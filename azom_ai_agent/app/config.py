"""Konfigurationsmodul för AZOM AI Agent.

Denna modul hanterar konfigurationsinställningar för hela applikationen med stöd för
miljövariabler, .env-filer och standardvärden.
"""
from __future__ import annotations

import os
from enum import Enum
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional, Dict, Any, Union


class LogLevel(str, Enum):
    """Giltiga loggningsnivåer."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


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
    OPENWEBUI_API_TOKEN: str = "sk-34c40884f61b46fd824629f88cfbf1f0"  # Default för tests/utv
    TARGET_MODEL: str = "azom-se-general"
    DATA_PATH: Path = Path("data")
    KNOWLEDGE_CACHE_TTL: int = 3600
    ENABLE_DYNAMIC_KNOWLEDGE: bool = True
    ENABLE_SCHEDULED_UPDATES: bool = True
    LOG_LEVEL: LogLevel = LogLevel.INFO
    LOG_FORMAT: str = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    MAX_REQUEST_SIZE_MB: int = 10
    RATE_LIMIT_REQUESTS: int = 100  # Per timme per IP
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
        return {k: v for k, v in self.__dict__.items() 
                if not k.startswith('_') and k != 'model_config'}
