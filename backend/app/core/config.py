from pydantic import field_validator
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    APP_NAME: str = "SkillBridge"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    DATABASE_URL: str = "sqlite:///./skillbridge.db"
    REDIS_URL: str = "redis://localhost:6379/0"

    LLM_PROVIDER: str = "groq"
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.1-8b-instant"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "mistral"
    LLM_TIMEOUT_SECONDS: float = 30.0
    LLM_PARSE_TIMEOUT_SECONDS: float = 8.0
    FAST_PARSE_MIN_SKILLS: int = 3

    EMBEDDING_DIMENSIONS: int = 384
    SIMILARITY_THRESHOLD: float = 0.62
    SECRET_KEY: str = "dev-secret-key-change-in-production"

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def normalize_database_url(cls, value):
        if not value:
            return "sqlite:///./skillbridge.db"
        if isinstance(value, str) and value.startswith("postgres://"):
            return value.replace("postgres://", "postgresql://", 1)
        return value

    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug(cls, value):
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"true", "1", "yes", "y", "on"}:
                return True
            if normalized in {"false", "0", "no", "n", "off", "warn", "warning", "info", "error", "critical", "release", "prod", "production", ""}:
                return False
        return value

    class Config:
        env_file = ".env"
        extra = "ignore"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
