"""
Database connection management for Travel Platform.

This module provides async database connection management using SQLAlchemy 2.0
with connection pooling, health checks, and error handling.
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from sqlalchemy.pool import AsyncAdaptedQueuePool, NullPool

from src.core.config.settings import settings
from src.core.logging import logger
from src.core.exceptions import DatabaseError, ServiceUnavailableError

class Database:
    """Database connection manager for async PostgreSQL connections."""
    
    _engine: Optional[AsyncEngine] = None
    _session_factory: Optional[async_sessionmaker[AsyncSession]] = None
    _is_connected: bool = False
    
    @classmethod
    async def connect(cls) -> None:
        """Establish database connection and create engine."""
        if cls._is_connected:
            logger.debug("Database already connected")
            return
        
        try:
            # Create async engine with connection pooling
            cls._engine = create_async_engine(
                str(settings.database_url_decrypted),
                echo=settings.DATABASE_ECHO,
                echo_pool=settings.DATABASE_ECHO,
                poolclass=AsyncAdaptedQueuePool,
                pool_size=settings.DATABASE_POOL_SIZE,
                max_overflow=settings.DATABASE_MAX_OVERFLOW,
                pool_timeout=settings.DATABASE_POOL_TIMEOUT,
                pool_recycle=3600,  # Recycle connections every hour
                pool_pre_ping=True,  # Verify connections before using
                future=True,  # Use SQLAlchemy 2.0 style
                connect_args={
                    "command_timeout": 60,
                    "server_settings": {
                        "application_name": "travel_platform",
                        "jit": "off",  # Disable JIT for better performance
                    }
                }
            )
            
            # Create session factory
            cls._session_factory = async_sessionmaker(
                cls._engine,
                class_=AsyncSession,
                expire_on_commit=False,
                autoflush=False,
                autocommit=False,
            )
            
            # Test connection
            async with cls._engine.connect() as conn:
                await conn.execute("SELECT 1")
            
            cls._is_connected = True
            logger.info("✅ Database connection established successfully")
            
        except OperationalError as e:
            logger.error(f"Database connection failed: {e}")
            raise ServiceUnavailableError(
                message="Database service unavailable",
                details=f"Could not connect to database: {str(e)}"
            )
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemy error during connection: {e}")
            raise DatabaseError(
                message="Database configuration error",
                details=f"SQLAlchemy error: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Unexpected error during database connection: {e}")
            raise DatabaseError(
                message="Database connection failed",
                details=f"Unexpected error: {str(e)}"
            )
    
    @classmethod
    async def disconnect(cls) -> None:
        """Close database connection and dispose engine."""
        if cls._engine:
            await cls._engine.dispose()
            cls._engine = None
            cls._session_factory = None
            cls._is_connected = False
            logger.info("Database connection closed")
    
    @classmethod
    def get_session_factory(cls) -> async_sessionmaker[AsyncSession]:
        """Get the session factory."""
        if not cls._session_factory:
            raise DatabaseError(
                message="Database not connected",
                details="Call Database.connect() first"
            )
        return cls._session_factory
    
    @classmethod
    @asynccontextmanager
    async def get_session(cls) -> AsyncGenerator[AsyncSession, None]:
        """Get a database session with automatic cleanup."""
        if not cls._session_factory:
            raise DatabaseError(
                message="Database not connected",
                details="Call Database.connect() first"
            )
        
        session: AsyncSession = cls._session_factory()
        try:
            yield session
            await session.commit()
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise DatabaseError(
                message="Database operation failed",
                details=f"Session error: {str(e)}"
            )
        except Exception as e:
            await session.rollback()
            logger.error(f"Unexpected error in database session: {e}")
            raise DatabaseError(
                message="Database operation failed",
                details=f"Unexpected error: {str(e)}"
            )
        finally:
            await session.close()
    
    @classmethod
    async def health_check(cls) -> dict:
        """Perform health check on database connection."""
        try:
            if not cls._engine:
                return {
                    "status": "unhealthy",
                    "error": "Database engine not initialized",
                    "timestamp": asyncio.get_event_loop().time()
                }
            
            async with cls._engine.connect() as conn:
                # Execute simple query
                result = await conn.execute("SELECT 1 as health_check, version() as version")
                row = result.fetchone()
                
                # Get connection info
                connection_info = await conn.get_raw_connection()
                
                return {
                    "status": "healthy",
                    "database": {
                        "version": row.version if row else "unknown",
                        "connection": {
                            "transaction_status": connection_info.info.transaction_status,
                            "backend_pid": connection_info.info.backend_pid,
                        }
                    },
                    "pool": {
                        "checked_out": cls._engine.pool.checkedout(),
                        "checked_in": cls._engine.pool.checkedin(),
                        "overflow": cls._engine.pool.overflow(),
                    },
                    "timestamp": asyncio.get_event_loop().time()
                }
                
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": asyncio.get_event_loop().time()
            }
    
    @classmethod
    def is_connected(cls) -> bool:
        """Check if database is connected."""
        return cls._is_connected
    
    @classmethod
    async def execute_raw_sql(cls, sql: str, parameters: Optional[dict] = None) -> list:
        """Execute raw SQL query."""
        async with cls.get_session() as session:
            result = await session.execute(sql, parameters or {})
            return result.fetchall()
    
    @classmethod
    async def create_tables(cls) -> None:
        """Create all tables (for testing/development)."""
        from src.database.models.base import Base
        
        async with cls._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created")


# Dependency for FastAPI
async def get_database() -> Database:
    """Get database instance for dependency injection."""
    return Database
