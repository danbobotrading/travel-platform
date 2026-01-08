from pydantic import Field, PostgresDsn, RedisDsn, SecretStr
from pydantic_settings import BaseSettings
from typing import Optional, List
import os


class Settings(BaseSettings):
    """Application settings."""
    
    # App
    APP_ENV: str = Field(default="development", description="Environment: development, staging, production")
    APP_NAME: str = Field(default="Travel Platform", description="Application name")
    DEBUG: bool = Field(default=False, description="Debug mode")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", description="Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL")
    LOG_FORMAT: str = Field(default="json", description="Log format: json, console")
    LOG_FILE: Optional[str] = Field(default=None, description="Path to log file")
    
    # Database
    DATABASE_URL: PostgresDsn = Field(
        default="postgresql://postgres:password@localhost:5432/travel_platform",
        description="PostgreSQL connection URL"
    )
    
    # Redis
    REDIS_URL: RedisDsn = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL"
    )
    
    # Telegram
    TELEGRAM_BOT_TOKEN: SecretStr = Field(
        ...,
        description="Telegram Bot Token",
        min_length=10
    )
    TELEGRAM_API_URL: str = Field(
        default="https://api.telegram.org/bot",
        description="Telegram API base URL"
    )
    TELEGRAM_ADMIN_IDS: List[int] = Field(
        default_factory=lambda: [123456789],
        description="List of admin Telegram IDs"
    )
    
    # Currency API (for Section 6)
    CURRENCY_API_KEY: Optional[str] = Field(default=None, description="Currency conversion API key")
    CURRENCY_API_URL: str = Field(
        default="https://api.exchangerate-api.com/v4/latest/ZAR",
        description="Currency API endpoint"
    )
    
    # Cache
    CACHE_TTL: int = Field(default=300, description="Default cache TTL in seconds")
    CACHE_PREFIX: str = Field(default="travel", description="Cache key prefix")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # This allows extra fields in .env


# Create settings instance
settings = Settings()
