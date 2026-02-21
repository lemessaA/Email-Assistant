import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, List
from enum import Enum

# Resolve .env path from project root (parent of src/)
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_ENV_FILE = os.path.join(_ROOT, ".env")


class Environment(str, Enum):
    LOCAL = "local"
    STAGING = "staging"
    PRODUCTION = "production"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        extra="ignore",
        env_file=_ENV_FILE,
        env_file_encoding="utf-8",
    )
    
    # App
    APP_NAME: str = "Email Assistant AI"
    ENVIRONMENT: Environment = Environment.LOCAL
    DEBUG: bool = False
    
    # LLM
    OPENAI_API_KEY : Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    
    # Model Selection
    PRIMARY_LLM: str = "ollama/kimi-k2.5:cloud"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    embedding_model: str = "text-embedding-3-small"
    
    # Ollama Configuration
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    
    # Email
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    
    # Database
    database_url: str = "sqlite:///./email_assistant.db"
    redis_url: str = "redis://localhost:6379/0"
    
    # Vector Store
    chroma_persist_path: str = "./chroma_db"
    
    # Security
    secret_key: str = "your-secret-key-here"
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8501"]
    
    # Rate Limiting
    rate_limit_per_minute: int = 60

settings = Settings()
