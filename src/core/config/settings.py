"""
Settings management for Travel Platform.

This module defines all application settings using Pydantic BaseSettings
with environment variable loading, validation, and type conversion.
"""

import os
import secrets
from typing import Any, Dict, List, Optional, Union
from functools import lru_cache

from pydantic import (
    BaseSettings,
    Field,
    PostgresDsn,
    RedisDsn,
    HttpUrl,
    EmailStr,
    validator,
    root_validator,
)
from pydantic.networks import AnyUrl
from pydantic.types import SecretStr

from src.core.config.constants import (
    AppConstants,
    DatabaseConstants,
    SecurityConstants,
    ApiConstants,
    CacheConstants,
)
from src.core.config.validators import (
    validate_email,
    validate_phone,
    validate_url,
    validate_currency,
    validate_language,
)


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    All sensitive values are stored as SecretStr and decrypted only when needed.
    """
    
    # ============ APPLICATION ============
    APP_NAME: str = Field(
        default="Travel Platform",
        description="Application name"
    )
    APP_ENV: str = Field(
        default="development",
        description="Application environment: development, staging, production",
        regex="^(development|staging|production|test)$"
    )
    APP_DEBUG: bool = Field(
        default=False,
        description="Debug mode"
    )
    APP_VERSION: str = Field(
        default="1.0.0",
        description="Application version"
    )
    APP_DESCRIPTION: str = Field(
        default="Enterprise Telegram travel search & booking bot for African users",
        description="Application description"
    )
    APP_URL: HttpUrl = Field(
        default="http://localhost:8000",
        description="Base URL of the application"
    )
    APP_HOST: str = Field(
        default="0.0.0.0",
        description="Host to bind the application to"
    )
    APP_PORT: int = Field(
        default=8000,
        description="Port to bind the application to",
        ge=1,
        le=65535
    )
    APP_SECRET_KEY: SecretStr = Field(
        default=...,
        description="Secret key for encryption and signing"
    )
    API_PREFIX: str = Field(
        default="/api",
        description="API URL prefix"
    )
    API_VERSION: str = Field(
        default="v1",
        description="API version"
    )
    
    # ============ DATABASE ============
    DATABASE_URL: PostgresDsn = Field(
        default=...,
        description="PostgreSQL database connection URL"
    )
    DATABASE_TEST_URL: Optional[PostgresDsn] = Field(
        default=None,
        description="Test database connection URL"
    )
    DATABASE_POOL_SIZE: int = Field(
        default=20,
        description="Database connection pool size",
        ge=1,
        le=100
    )
    DATABASE_MAX_OVERFLOW: int = Field(
        default=40,
        description="Maximum overflow connections",
        ge=0,
        le=100
    )
    DATABASE_POOL_TIMEOUT: int = Field(
        default=30,
        description="Connection pool timeout in seconds",
        ge=1
    )
    DATABASE_ECHO: bool = Field(
        default=False,
        description="Echo SQL queries (for debugging)"
    )
    
    # ============ REDIS ============
    REDIS_URL: RedisDsn = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL"
    )
    REDIS_CACHE_TTL: int = Field(
        default=3600,
        description="Redis cache TTL in seconds",
        ge=1
    )
    REDIS_SESSION_TTL: int = Field(
        default=86400,
        description="Redis session TTL in seconds",
        ge=1
    )
    REDIS_MAX_CONNECTIONS: int = Field(
        default=50,
        description="Maximum Redis connections",
        ge=1
    )
    
    # ============ TELEGRAM ============
    TELEGRAM_BOT_TOKEN: SecretStr = Field(
        default=...,
        description="Telegram Bot API token"
    )
    TELEGRAM_API_URL: HttpUrl = Field(
        default="https://api.telegram.org/bot",
        description="Telegram Bot API base URL"
    )
    TELEGRAM_WEBHOOK_URL: Optional[HttpUrl] = Field(
        default=None,
        description="Telegram webhook URL"
    )
    TELEGRAM_WEBHOOK_SECRET: Optional[SecretStr] = Field(
        default=None,
        description="Webhook secret token for verification"
    )
    TELEGRAM_ADMIN_IDS: List[int] = Field(
        default_factory=list,
        description="Telegram admin user IDs"
    )
    
    # ============ THIRD-PARTY APIs ============
    AMADEUS_API_KEY: Optional[SecretStr] = Field(
        default=None,
        description="Amadeus API key"
    )
    AMADEUS_API_SECRET: Optional[SecretStr] = Field(
        default=None,
        description="Amadeus API secret"
    )
    AMADEUS_API_URL: HttpUrl = Field(
        default="https://test.api.amadeus.com",
        description="Amadeus API URL"
    )
    
    BOOKING_API_KEY: Optional[SecretStr] = Field(
        default=None,
        description="Booking.com API key"
    )
    BOOKING_API_URL: HttpUrl = Field(
        default="https://distribution-xml.booking.com/json",
        description="Booking.com API URL"
    )
    
    PAYSTACK_SECRET_KEY: Optional[SecretStr] = Field(
        default=None,
        description="Paystack secret key"
    )
    PAYSTACK_PUBLIC_KEY: Optional[SecretStr] = Field(
        default=None,
        description="Paystack public key"
    )
    PAYSTACK_API_URL: HttpUrl = Field(
        default="https://api.paystack.co",
        description="Paystack API URL"
    )
    
    EXCHANGERATE_API_KEY: Optional[SecretStr] = Field(
        default=None,
        description="Exchange rate API key"
    )
    EXCHANGERATE_API_URL: HttpUrl = Field(
        default="https://api.exchangerate-api.com/v4",
        description="Exchange rate API URL"
    )
    
    # ============ SECURITY ============
    ENCRYPTION_KEY: SecretStr = Field(
        default=...,
        description="32-character encryption key for sensitive data"
    )
    JWT_SECRET_KEY: SecretStr = Field(
        default=...,
        description="JWT secret key"
    )
    JWT_ALGORITHM: str = Field(
        default="HS256",
        description="JWT algorithm",
        regex="^(HS256|HS384|HS512|RS256|RS384|RS512|ES256|ES384|ES512)$"
    )
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        description="JWT access token expiration in minutes",
        ge=1
    )
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default=7,
        description="JWT refresh token expiration in days",
        ge=1
    )
    
    # CORS settings
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="Allowed CORS origins"
    )
    CORS_ALLOW_CREDENTIALS: bool = Field(
        default=True,
        description="Allow credentials in CORS"
    )
    
    # Rate limiting
    RATE_LIMIT_REQUESTS: int = Field(
        default=100,
        description="Number of requests allowed per period",
        ge=1
    )
    RATE_LIMIT_PERIOD: int = Field(
        default=60,
        description="Rate limit period in seconds",
        ge=1
    )
    
    # ============ LOGGING ============
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Logging level",
        regex="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$"
    )
    LOG_FILE: Optional[str] = Field(
        default="logs/travel_platform.log",
        description="Log file path"
    )
    LOG_FORMAT: str = Field(
        default="json",
        description="Log format: json or text",
        regex="^(json|text)$"
    )
    SENTRY_DSN: Optional[HttpUrl] = Field(
        default=None,
        description="Sentry DSN for error tracking"
    )
    
    # ============ EMAIL ============
    SMTP_HOST: Optional[str] = Field(
        default=None,
        description="SMTP server host"
    )
    SMTP_PORT: Optional[int] = Field(
        default=None,
        description="SMTP server port",
        ge=1,
        le=65535
    )
    SMTP_USER: Optional[str] = Field(
        default=None,
        description="SMTP username"
    )
    SMTP_PASSWORD: Optional[SecretStr] = Field(
        default=None,
        description="SMTP password"
    )
    SMTP_FROM: Optional[EmailStr] = Field(
        default=None,
        description="Default sender email address"
    )
    SMTP_USE_TLS: bool = Field(
        default=True,
        description="Use TLS for SMTP"
    )
    
    # ============ CACHE ============
    CACHE_TYPE: str = Field(
        default="redis",
        description="Cache type: redis, memory",
        regex="^(redis|memory)$"
    )
    CACHE_DEFAULT_TIMEOUT: int = Field(
        default=300,
        description="Default cache timeout in seconds",
        ge=1
    )
    CACHE_KEY_PREFIX: str = Field(
        default="travel_platform",
        description="Cache key prefix"
    )
    
    # ============ MONITORING ============
    PROMETHEUS_PORT: int = Field(
        default=9090,
        description="Prometheus metrics port",
        ge=1,
        le=65535
    )
    METRICS_ENABLED: bool = Field(
        default=True,
        description="Enable metrics collection"
    )
    HEALTH_CHECK_ENABLED: bool = Field(
        default=True,
        description="Enable health check endpoints"
    )
    
    # ============ QUEUE ============
    QUEUE_BACKEND: str = Field(
        default="redis",
        description="Queue backend: redis, database, memory",
        regex="^(redis|database|memory)$"
    )
    QUEUE_NAME: str = Field(
        default="travel_platform_jobs",
        description="Queue name"
    )
    WORKER_COUNT: int = Field(
        default=4,
        description="Number of worker processes",
        ge=1
    )
    
    # ============ FILE STORAGE ============
    STORAGE_TYPE: str = Field(
        default="local",
        description="Storage type: local, s3, azure",
        regex="^(local|s3|azure)$"
    )
    STORAGE_PATH: str = Field(
        default="./uploads",
        description="Local storage path"
    )
    AWS_ACCESS_KEY_ID: Optional[SecretStr] = Field(
        default=None,
        description="AWS access key ID"
    )
    AWS_SECRET_ACCESS_KEY: Optional[SecretStr] = Field(
        default=None,
        description="AWS secret access key"
    )
    AWS_S3_BUCKET: Optional[str] = Field(
        default=None,
        description="AWS S3 bucket name"
    )
    AWS_REGION: Optional[str] = Field(
        default="af-south-1",
        description="AWS region"
    )
    
    # ============ GEOCODING ============
    MAPBOX_API_KEY: Optional[SecretStr] = Field(
        default=None,
        description="Mapbox API key"
    )
    GOOGLE_MAPS_API_KEY: Optional[SecretStr] = Field(
        default=None,
        description="Google Maps API key"
    )
    
    # ============ TESTING ============
    TEST_DATABASE_URL: Optional[PostgresDsn] = Field(
        default=None,
        description="Test database URL"
    )
    TEST_REDIS_URL: Optional[RedisDsn] = Field(
        default=None,
        description="Test Redis URL"
    )
    TEST_TELEGRAM_TOKEN: Optional[SecretStr] = Field(
        default=None,
        description="Test Telegram bot token"
    )
    TEST_MODE: bool = Field(
        default=False,
        description="Test mode flag"
    )
    
    # ============ DEVELOPMENT ============
    DEVELOPMENT_MODE: bool = Field(
        default=False,
        description="Development mode flag"
    )
    AUTO_RELOAD: bool = Field(
        default=True,
        description="Auto reload on code changes"
    )
    DEBUG_TOOLBAR: bool = Field(
        default=False,
        description="Enable debug toolbar"
    )
    SQL_LOGGING: bool = Field(
        default=False,
        description="Log SQL queries"
    )
    
    # ============ DEPLOYMENT ============
    DOCKER_REGISTRY: Optional[str] = Field(
        default=None,
        description="Docker registry URL"
    )
    DEPLOYMENT_ENV: str = Field(
        default="production",
        description="Deployment environment"
    )
    BACKUP_ENABLED: bool = Field(
        default=True,
        description="Enable automatic backups"
    )
    BACKUP_SCHEDULE: str = Field(
        default="0 2 * * *",
        description="Backup schedule (cron format)"
    )
    
    # Validators
    @validator("APP_SECRET_KEY", pre=True)
    def validate_app_secret_key(cls, v: Optional[str]) -> str:
        """Validate and generate APP_SECRET_KEY if not provided."""
        if v is None or v == "":
            if os.getenv("APP_ENV") == "production":
                raise ValueError("APP_SECRET_KEY must be set in production")
            # Generate a random secret for development
            return secrets.token_urlsafe(32)
        return v
    
    @validator("ENCRYPTION_KEY", pre=True)
    def validate_encryption_key(cls, v: Optional[str]) -> str:
        """Validate encryption key length."""
        if v is None or v == "":
            if os.getenv("APP_ENV") == "production":
                raise ValueError("ENCRYPTION_KEY must be set in production")
            # Generate a 32-character key for development
            return secrets.token_urlsafe(32)
        
        if len(v) != 32:
            raise ValueError("ENCRYPTION_KEY must be exactly 32 characters")
        return v
    
    @validator("TELEGRAM_ADMIN_IDS", pre=True)
    def validate_telegram_admin_ids(cls, v: Union[str, List[int]]) -> List[int]:
        """Parse comma-separated Telegram admin IDs."""
        if isinstance(v, str):
            if v.strip() == "":
                return []
            try:
                return [int(id.strip()) for id in v.split(",")]
            except ValueError:
                raise ValueError("TELEGRAM_ADMIN_IDS must be comma-separated integers")
        return v
    
    @validator("CORS_ORIGINS", pre=True)
    def validate_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse comma-separated CORS origins."""
        if isinstance(v, str):
            if v.strip() == "":
                return []
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("LOG_LEVEL", pre=True)
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of {valid_levels}")
        return v.upper()
    
    @root_validator
    def validate_environment(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Validate environment-specific settings."""
        env = values.get("APP_ENV", "development")
        
        if env == "production":
            # Production validations
            if not values.get("APP_SECRET_KEY") or values["APP_SECRET_KEY"] == "":
                raise ValueError("APP_SECRET_KEY must be set in production")
            
            if not values.get("ENCRYPTION_KEY") or values["ENCRYPTION_KEY"] == "":
                raise ValueError("ENCRYPTION_KEY must be set in production")
            
            if not values.get("TELEGRAM_BOT_TOKEN") or values["TELEGRAM_BOT_TOKEN"] == "":
                raise ValueError("TELEGRAM_BOT_TOKEN must be set in production")
        
        # Development defaults
        if env == "development":
            values["APP_DEBUG"] = True
            values["DEVELOPMENT_MODE"] = True
            values["AUTO_RELOAD"] = True
            
        # Test defaults
        if env == "test":
            values["TEST_MODE"] = True
            values["DATABASE_ECHO"] = False
            
            # Use test database if provided
            if values.get("DATABASE_TEST_URL"):
                values["DATABASE_URL"] = values["DATABASE_TEST_URL"]
            
            # Use test Redis if provided
            if values.get("TEST_REDIS_URL"):
                values["REDIS_URL"] = values["TEST_REDIS_URL"]
        
        return values
    
    @validator("DATABASE_URL", pre=True)
    def validate_database_url(cls, v: Optional[str]) -> Optional[str]:
        """Validate and format database URL."""
        if v is None or v == "":
            return None
        
        # Ensure asyncpg driver is used
        if not v.startswith("postgresql+asyncpg://"):
            if v.startswith("postgresql://"):
                v = v.replace("postgresql://", "postgresql+asyncpg://")
            elif v.startswith("postgres://"):
                v = v.replace("postgres://", "postgresql+asyncpg://")
            else:
                v = f"postgresql+asyncpg://{v}"
        
        return v
    
    # Properties for computed values
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.APP_ENV == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.APP_ENV == "production"
    
    @property
    def is_testing(self) -> bool:
        """Check if running in test environment."""
        return self.APP_ENV == "test" or self.TEST_MODE
    
    @property
    def database_url_decrypted(self) -> str:
        """Get decrypted database URL."""
        return self.DATABASE_URL
    
    @property
    def telegram_bot_token_decrypted(self) -> str:
        """Get decrypted Telegram bot token."""
        return self.TELEGRAM_BOT_TOKEN.get_secret_value()
    
    @property
    def amadeus_api_key_decrypted(self) -> Optional[str]:
        """Get decrypted Amadeus API key."""
        return self.AMADEUS_API_KEY.get_secret_value() if self.AMADEUS_API_KEY else None
    
    @property
    def encryption_key_decrypted(self) -> str:
        """Get decrypted encryption key."""
        return self.ENCRYPTION_KEY.get_secret_value()
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        validate_assignment = True
        
        @classmethod
        def customise_sources(
            cls,
            init_settings,
            env_settings,
            file_secret_settings,
        ):
            """Customize settings loading order."""
            return (
                init_settings,
                env_settings,
                file_secret_settings,
            )


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Returns:
        Settings: Application settings instance
    """
    return Settings()


# Global settings instance
settings = get_settings()
