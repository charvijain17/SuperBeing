"""Application configuration loaded from environment variables."""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "SuperBeing API"
    app_version: str = "0.1.0"
    environment: str = "development"
    app_api_key: str | None = None
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    google_api_key: str | None = None
    openai_model: str = "gpt-4o"
    anthropic_model: str = "claude-3-5-sonnet-latest"
    gemini_model: str = "gemini-2.0-flash"
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

@lru_cache
def get_settings() -> Settings:
    return Settings()
