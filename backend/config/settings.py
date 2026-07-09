from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, List
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "CAMera"
    APP_VERSION: str = "1.0.0"

    DATABASE_URL: str = "sqlite:///./camera.db"
    DATABASE_ECHO: bool = False

    DEFAULT_LOCAL_MODEL: str = "qwen2.5-coder:7b"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None

    OPENAI_COMPATIBLE_BASE_URL: Optional[str] = None
    OPENAI_COMPATIBLE_API_KEY: Optional[str] = None
    OPENAI_COMPATIBLE_MODEL: str = "gpt-4o"

    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]

    LOG_LEVEL: str = "INFO"

    


@lru_cache()
def get_settings() -> Settings:
    return Settings()
