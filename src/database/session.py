"""
Database session management for Travel Platform.

This module provides async session management with dependency injection
for FastAPI and proper cleanup.
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.connection import Database


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session for dependency injection.
    
    Yields:
        AsyncSession: Database session
    
    Usage:
        @app.get("/items")
        async def read_items(session: AsyncSession = Depends(get_session)):
            result = await session.execute(select(Item))
            return result.scalars().all()
    """
    async with Database.get_session() as session:
        yield session


# Export types
__all__ = [
    "get_session",
    "AsyncSession",
]
