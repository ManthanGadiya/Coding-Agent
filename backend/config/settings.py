from pydantic_settings import BaseSettings
from typing import Optional, List
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "CAMera"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    HOST: str = "0.0.0.0"
    PORT: int = 8000
    FRONTEND_URL: str = "http://localhost:3000"

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

    AGENT_MEMORY_MCP_URL: str = "http://localhost:8001"
    FIRECRAWL_MCP_URL: str = "http://localhost:8002"
    GITHUB_MCP_URL: str = "http://localhost:8003"
    MARKITDOWN_MCP_URL: str = "http://localhost:8004"
    COMPOSIO_MCP_URL: str = "http://localhost:8005"
    HERMES_MCP_URL: str = "http://localhost:8006"
    RUFLO_MCP_URL: str = "http://localhost:8007"

    GITHUB_TOKEN: Optional[str] = None
    GITHUB_OWNER: Optional[str] = None
    GITHUB_REPO: Optional[str] = None

    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]

    DEFAULT_AUTONOMY_MODE: str = "plan"
    REQUIRE_APPROVAL_FOR_PUSH: bool = True
    REQUIRE_APPROVAL_FOR_DEPLOY: bool = True

    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    MEMORY_RETENTION_DAYS: int = 365
    MAX_MEMORY_ENTRIES: int = 10000

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
