"""
Core module for Travel Platform.

This module contains the fundamental building blocks of the application,
including configuration management, security, exceptions, and utilities.
"""

from src.core.config import settings
from src.core.security import SecurityManager
from src.core.exceptions import (
    TravelPlatformException,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    ConflictError,
    RateLimitError,
    ServiceUnavailableError,
)
from src.core.dependencies import get_database, get_current_user
from src.core.logging import logger
from src.core.constants import (
    UserRole,
    BookingStatus,
    PaymentStatus,
    FlightClass,
    Currency,
    Country,
    Language,
)

__all__ = [
    "settings",
    "SecurityManager",
    "TravelPlatformException",
    "ValidationError",
    "AuthenticationError",
    "AuthorizationError",
    "NotFoundError",
    "ConflictError",
    "RateLimitError",
    "ServiceUnavailableError",
    "get_database",
    "get_current_user",
    "logger",
    "UserRole",
    "BookingStatus",
    "PaymentStatus",
    "FlightClass",
    "Currency",
    "Country",
    "Language",
]
