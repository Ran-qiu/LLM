from typing import List, Optional, Union, Annotated
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BeforeValidator


def parse_cors_origins(v: Union[str, List[str]]) -> List[str]:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list):
        return v
    return v


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_parse_none_str='null'
    )

    # Project
    PROJECT_NAME: str = "LLM Manager"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Security
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ENCRYPTION_KEY: str = "your-encryption-key-32-bytes-long"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Database
    DATABASE_URL: str = "sqlite:///./data/llm.db"

    # CORS
    BACKEND_CORS_ORIGINS: Annotated[
        List[str],
        BeforeValidator(parse_cors_origins)
    ] = ["http://localhost:5173", "http://localhost:80"]

    # Ollama
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    # LLM Providers
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None


settings = Settings()
