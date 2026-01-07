from typing import List, Optional
from pydantic import Field, PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App
    APP_NAME: str = "Travel Platform"
    APP_ENV: str = "development"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: PostgresDsn = "postgresql+asyncpg://travel_user:travel_password@localhost:5432/travel_platform"
    
    # Redis
    REDIS_URL: RedisDsn = "redis://localhost:6379/0"
    
    # Allow extra fields from .env
    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields instead of raising error

settings = Settings()
