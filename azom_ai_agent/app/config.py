import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional

class Settings(BaseSettings):
    APP_NAME: str = "AZOM AI Agent"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8008
    OPENWEBUI_URL: str = "http://titanic.urem.org:3000"
    OPENWEBUI_API_TOKEN: str = "DUMMY"  # Default för tests/utv
    TARGET_MODEL: str = "azom-se-general"
    DATA_PATH: Path = Path("data")
    KNOWLEDGE_CACHE_TTL: int = 3600
    ENABLE_DYNAMIC_KNOWLEDGE: bool = True
    ENABLE_SCHEDULED_UPDATES: bool = True
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
