"""Configuration for AZOM Pipeline Server.
Values can be overridden via environment variables or a local .env file.
"""

import json
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, AliasChoices, field_validator
from typing import Optional, List, Any

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
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_BASE_URL: Optional[str] = None
    LLM_BACKEND: Optional[str] = "openwebui"

    # CORS (accepts env PIPELINE_CORS_ORIGINS or CORS_ORIGINS)
    CORS_ORIGINS: List[str] = Field(
        default_factory=lambda: ["*"],
        validation_alias=AliasChoices("PIPELINE_CORS_ORIGINS", "CORS_ORIGINS"),
    )

    # Normalize CORS_ORIGINS from env (supports JSON list string or comma-separated)
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def _parse_cors_origins(cls, v: Any) -> Any:
        if v is None or v == "":
            return v
        if isinstance(v, str):
            s = v.strip()
            # Try JSON first
            try:
                parsed = json.loads(s)
                if isinstance(parsed, list):
                    return [str(x) for x in parsed]
            except Exception:
                pass
            # Fallback to comma-separated
            return [part.strip() for part in s.split(",") if part.strip()]
        return v

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
