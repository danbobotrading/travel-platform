"""
Travel Platform - Enterprise Telegram travel search & booking bot.

This package contains the core application logic for the Travel Platform,
including the API, Telegram bot, database models, and service integrations.
"""

__version__ = "1.0.0"
__author__ = "Travel Platform Team"
__email__ = "dev@travelplatform.com"
__description__ = "Enterprise Telegram travel search & booking bot for African users"

# Package metadata
PACKAGE_NAME = "travel_platform"
API_VERSION = "v1"
SUPPORTED_LANGUAGES = ["en", "fr", "ar", "sw", "pt", "ha"]
SUPPORTED_CURRENCIES = ["NGN", "GHS", "KES", "ZAR", "USD", "EUR", "GBP"]

# Import key modules for easier access
try:
    from src.core.config import settings
    from src.core.logging import logger
    from src.database.connection import Database
    from src.utils.cache import redis_client
except ImportError:
    # Allow imports even if dependencies aren't fully initialized yet
    pass

__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "__description__",
    "PACKAGE_NAME",
    "API_VERSION",
    "SUPPORTED_LANGUAGES",
    "SUPPORTED_CURRENCIES",
    "settings",
    "logger",
    "Database",
    "redis_client",
]
