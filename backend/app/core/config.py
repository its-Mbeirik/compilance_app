"""Application configuration."""

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings from environment variables."""

    # FastAPI
    debug: bool = True
    environment: str = "development"

    # LLM Configuration
    openai_api_key: str
    openai_model: str = "gpt-4-turbo-preview"

    # Database
    database_url: str
    pgvector_enabled: bool = True

    # Embeddings
    embedding_model: str = "intfloat/multilingual-e5-large-instruct"
    embedding_dim: int = 1024

    # Application
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    cors_origins: list = ["http://localhost:3000", "http://localhost:5173"]

    # File Upload
    max_upload_size_mb: int = 50
    upload_dir: str = "./data/uploads"

    # Logging
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
