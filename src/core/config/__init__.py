"""
Configuration module for Travel Platform.

This module handles all configuration management, including environment variables,
secrets encryption/decryption, and validation.
"""

from src.core.config.settings import settings
from src.core.config.secrets import SecretsManager
from src.core.config.validators import (
    validate_email,
    validate_phone,
    validate_password,
    validate_url,
    validate_currency,
    validate_language,
    ValidationError as ConfigValidationError,
)
from src.core.config.constants import (
    AppConstants,
    DatabaseConstants,
    SecurityConstants,
    ApiConstants,
    CacheConstants,
)

__all__ = [
    "settings",
    "SecretsManager",
    "validate_email",
    "validate_phone",
    "validate_password",
    "validate_url",
    "validate_currency",
    "validate_language",
    "ConfigValidationError",
    "AppConstants",
    "DatabaseConstants",
    "SecurityConstants",
    "ApiConstants",
    "CacheConstants",
]
