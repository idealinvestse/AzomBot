"""Configuration for AZOM Pipeline Server.
Values can be overridden via environment variables or a local .env file.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables.
    Any attribute can be overridden by defining it in a `.env` file at the project root
    or by exporting an environment variable with the same name.
    """

    PROJECT_NAME: str = "AZOM Pipeline Server"
    VERSION: str = "0.1.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8001

    # Example pipeline-specific tuning parameters
    DEFAULT_USER_EXPERIENCE: str = "nybörjare"  # default experience level if not supplied
    CACHE_TTL_SECONDS: int = 3600  # generic TTL for in-memory caches

    # Admin credentials
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "azom123"

    # LLM and integration fields
    OPENWEBUI_URL: Optional[str] = None
    OPENWEBUI_API_TOKEN: Optional[str] = None
    TARGET_MODEL: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    GROQ_API_URL: Optional[str] = None
    GROQ_MODEL: Optional[str] = None
    LLM_BACKEND: Optional[str] = "openwebui"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
