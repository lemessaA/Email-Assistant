"""
Production Configuration Module

This module manages production configuration settings for the email assistant.
It provides secure configuration management with environment variables
and default values for production deployment.
"""

import os
from typing import Dict, Any, Optional
from pydantic import BaseSettings, Field
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class ProductionSettings(BaseSettings):
    """
    Production settings configuration using Pydantic for validation
    """
    
    # Email Configuration
    SMTP_SERVER: str = Field(default="smtp.gmail.com", description="SMTP server address")
    SMTP_PORT: int = Field(default=587, description="SMTP server port")
    SMTP_USERNAME: str = Field(..., description="SMTP username for email sending")
    SMTP_PASSWORD: str = Field(..., description="SMTP password for email sending")
    EMAIL_FROM: str = Field(default="noreply@yourcompany.com", description="Default sender email address")
    
    # IMAP Configuration
    IMAP_SERVER: str = Field(default="imap.gmail.com", description="IMAP server address")
    IMAP_USERNAME: str = Field(..., description="IMAP username for email retrieval")
    IMAP_PASSWORD: str = Field(..., description="IMAP password for email retrieval")
    
    # LLM Configuration
    PRIMARY_LLM: str = Field(default="ollama/llama2", description="Primary language model for processing")
    OLLAMA_BASE_URL: str = Field(default="http://localhost:11434", description="Ollama server URL")
    LLM_TEMPERATURE: float = Field(default=0.1, description="LLM temperature for response generation")
    LLM_MAX_TOKENS: int = Field(default=2048, description="Maximum tokens for LLM responses")
    
    # Search Configuration
    SEARCH_API_KEY: str = Field(default="", description="API key for web search services")
    SEARCH_ENGINE: str = Field(default="serper", description="Search engine to use (serper, google, bing)")
    SEARCH_MAX_RESULTS: int = Field(default=10, description="Maximum search results to return")
    
    # Calendar Configuration
    CALENDAR_API_KEY: str = Field(default="", description="API key for calendar services")
    CALENDAR_PROVIDER: str = Field(default="google", description="Calendar provider (google, outlook, apple)")
    CALENDAR_TIMEZONE: str = Field(default="UTC", description="Timezone for calendar operations")
    
    # Database Configuration
    DATABASE_URL: str = Field(default="sqlite:///./email_assistant.db", description="Database connection URL")
    DATABASE_POOL_SIZE: int = Field(default=5, description="Database connection pool size")
    
    # File Storage Configuration
    KNOWLEDGE_BASE_PATH: str = Field(default="./data/knowledge_base", description="Path to knowledge base files")
    DRAFTS_PATH: str = Field(default="./data/drafts", description="Path to save email drafts")
    ATTACHMENTS_PATH: str = Field(default="./data/attachments", description="Path to store email attachments")
    MAX_ATTACHMENT_SIZE: int = Field(default=25 * 1024 * 1024, description="Maximum attachment size in bytes (25MB)")
    
    # API Configuration
    API_HOST: str = Field(default="0.0.0.0", description="API server host")
    API_PORT: int = Field(default=8000, description="API server port")
    API_WORKERS: int = Field(default=4, description="Number of API worker processes")
    API_RELOAD: bool = Field(default=True, description="Enable auto-reload for development")
    
    # Security Configuration
    SECRET_KEY: str = Field(..., description="Secret key for API authentication")
    CORS_ORIGINS: str = Field(default="*", description="CORS allowed origins")
    ACCESS_LOG_EXPIRE: int = Field(default=3600, description="Access token expiration time in seconds")
    
    # Logging Configuration
    LOG_LEVEL: str = Field(default="INFO", description="Logging level (DEBUG, INFO, WARNING, ERROR)")
    LOG_FILE: str = Field(default="./logs/email_assistant.log", description="Log file path")
    LOG_MAX_SIZE: int = Field(default=10 * 1024 * 1024, description="Maximum log file size in bytes (10MB)")
    
    # Monitoring Configuration
    METRICS_ENABLED: bool = Field(default=True, description="Enable metrics collection")
    METRICS_PORT: int = Field(default=9090, description="Metrics server port")
    HEALTH_CHECK_INTERVAL: int = Field(default=30, description="Health check interval in seconds")
    
    # Performance Configuration
    CACHE_TTL: int = Field(default=3600, description="Cache time-to-live in seconds")
    RATE_LIMIT_REQUESTS: int = Field(default=100, description="Rate limit requests per minute")
    RATE_LIMIT_WINDOW: int = Field(default=60, description="Rate limit time window in seconds")
    
    class Config:
        env_file = ".env"  # Environment file to load settings from
        case_sensitive = False  # Allow case-insensitive environment variable names

def get_production_settings() -> ProductionSettings:
    """
    Get production settings instance
    
    Returns:
        ProductionSettings: Validated configuration object
    """
    return ProductionSettings()

def get_database_config() -> Dict[str, Any]:
    """
    Get database configuration dictionary
    
    Returns:
        Dictionary with database connection parameters
    """
    settings = get_production_settings()
    return {
        "url": settings.DATABASE_URL,
        "pool_size": settings.DATABASE_POOL_SIZE,
        "echo": False,  # Disable SQL echo in production
        "pool_pre_ping": True,  # Validate connections before use
        "pool_recycle": 300,  # Recycle connections every 5 minutes
    }

def get_email_config() -> Dict[str, Any]:
    """
    Get email configuration dictionary
    
    Returns:
        Dictionary with email server parameters
    """
    settings = get_production_settings()
    return {
        "smtp_server": settings.SMTP_SERVER,
        "smtp_port": settings.SMTP_PORT,
        "smtp_username": settings.SMTP_USERNAME,
        "smtp_password": settings.SMTP_PASSWORD,
        "from_email": settings.EMAIL_FROM,
        "imap_server": settings.IMAP_SERVER,
        "imap_username": settings.IMAP_USERNAME,
        "imap_password": settings.IMAP_PASSWORD,
        "use_tls": True,
        "use_ssl": True,
        "timeout": 30
    }

def get_llm_config() -> Dict[str, Any]:
    """
    Get LLM configuration dictionary
    
    Returns:
        Dictionary with LLM parameters
    """
    settings = get_production_settings()
    return {
        "primary_model": settings.PRIMARY_LLM,
        "base_url": settings.OLLAMA_BASE_URL,
        "temperature": settings.LLM_TEMPERATURE,
        "max_tokens": settings.LLM_MAX_TOKENS,
        "timeout": 60,
        "retry_attempts": 3,
        "fallback_to_mock": True
    }

def get_search_config() -> Dict[str, Any]:
    """
    Get search configuration dictionary
    
    Returns:
        Dictionary with search parameters
    """
    settings = get_production_settings()
    return {
        "api_key": settings.SEARCH_API_KEY,
        "engine": settings.SEARCH_ENGINE,
        "max_results": settings.SEARCH_MAX_RESULTS,
        "timeout": 10,
        "retry_attempts": 2
    }

def get_calendar_config() -> Dict[str, Any]:
    """
    Get calendar configuration dictionary
    
    Returns:
        Dictionary with calendar parameters
    """
    settings = get_production_settings()
    return {
        "api_key": settings.CALENDAR_API_KEY,
        "provider": settings.CALENDAR_PROVIDER,
        "timezone": settings.CALENDAR_TIMEZONE,
        "default_duration": 60,
        "buffer_minutes": 15,
        "max_attendees": 50
    }

def get_file_config() -> Dict[str, Any]:
    """
    Get file storage configuration dictionary
    
    Returns:
        Dictionary with file storage parameters
    """
    settings = get_production_settings()
    return {
        "knowledge_base_path": settings.KNOWLEDGE_BASE_PATH,
        "drafts_path": settings.DRAFTS_PATH,
        "attachments_path": settings.ATTACHMENTS_PATH,
        "max_attachment_size": settings.MAX_ATTACHMENT_SIZE,
        "allowed_extensions": [".pdf", ".docx", ".txt", ".md", ".csv", ".jpg", ".png"],
        "auto_cleanup": True,
        "retention_days": 30
    }

def get_api_config() -> Dict[str, Any]:
    """
    Get API configuration dictionary
    
    Returns:
        Dictionary with API parameters
    """
    settings = get_production_settings()
    return {
        "host": settings.API_HOST,
        "port": settings.API_PORT,
        "workers": settings.API_WORKERS,
        "reload": settings.API_RELOAD,
        "secret_key": settings.SECRET_KEY,
        "cors_origins": settings.CORS_ORIGINS,
        "access_token_expire": settings.ACCESS_LOG_EXPIRE,
        "rate_limit_requests": settings.RATE_LIMIT_REQUESTS,
        "rate_limit_window": settings.RATE_LIMIT_WINDOW
    }

def get_logging_config() -> Dict[str, Any]:
    """
    Get logging configuration dictionary
    
    Returns:
        Dictionary with logging parameters
    """
    settings = get_production_settings()
    return {
        "level": settings.LOG_LEVEL,
        "file": settings.LOG_FILE,
        "max_size": settings.LOG_MAX_SIZE,
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "date_format": "%Y-%m-%d %H:%M:%S",
        "enable_console": True,
        "enable_file": True,
        "rotate": True,
        "backup_count": 5
    }

def validate_production_environment() -> bool:
    """
    Validate that all required production environment variables are set
    
    Returns:
        bool: True if environment is properly configured
    """
    settings = get_production_settings()
    
    # Check required environment variables
    required_vars = {
        "SMTP_USERNAME": settings.SMTP_USERNAME,
        "SMTP_PASSWORD": settings.SMTP_PASSWORD,
        "IMAP_USERNAME": settings.IMAP_USERNAME,
        "IMAP_PASSWORD": settings.IMAP_PASSWORD,
        "SECRET_KEY": settings.SECRET_KEY
    }
    
    missing_vars = [var for var, value in required_vars.items() if not value]
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        return False
    
    print("✅ Production environment is properly configured")
    return True

# Create global settings instance
production_settings = get_production_settings()
