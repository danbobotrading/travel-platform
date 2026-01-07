"""
Database module for Travel Platform.

This module handles all database operations, including connection management,
models, repositories, and migrations.
"""

from src.database.connection import Database, get_database
from src.database.models.base import Base
from src.database.models.user import User
from src.database.models.flight import Flight, FlightSearch, FlightBooking
from src.database.models.hotel import Hotel, HotelSearch, HotelBooking
from src.database.models.payment import Payment, PaymentMethod
from src.database.models.session import Session
from src.database.session import AsyncSession, get_session
from src.database.redis_client import RedisClient, get_redis
from src.database.migrations import run_migrations, create_migration

__all__ = [
    # Database connection
    "Database",
    "get_database",
    
    # Base and models
    "Base",
    "User",
    "Flight",
    "FlightSearch",
    "FlightBooking",
    "Hotel",
    "HotelSearch",
    "HotelBooking",
    "Payment",
    "PaymentMethod",
    "Session",
    
    # Session management
    "AsyncSession",
    "get_session",
    
    # Redis
    "RedisClient",
    "get_redis",
    
    # Migrations
    "run_migrations",
    "create_migration",
]
