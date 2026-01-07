"""
Base database model for Travel Platform.

This module defines the base class for all SQLAlchemy models with common
fields, methods, and configuration.
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import DateTime, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func

from src.core.config.constants import AppConstants


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    
    # Custom type annotations
    type_annotation_map = {
        uuid.UUID: UUID(as_uuid=True),
        datetime: DateTime(timezone=True),
    }
    
    @declared_attr.directive
    def __tablename__(cls) -> str:
        """Generate table name from class name."""
        # Convert CamelCase to snake_case
        name = cls.__name__
        snake_case = ''.join(
            ['_' + c.lower() if c.isupper() else c for c in name]
        ).lstrip('_')
        return snake_case + 's'  # Pluralize
    
    # Common fields for all models
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
        index=True,
        comment="Primary key identifier"
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
        comment="Timestamp when record was created"
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        index=True,
        comment="Timestamp when record was last updated"
    )
    
    is_active: Mapped[bool] = mapped_column(
        default=True,
        nullable=False,
        index=True,
        comment="Soft delete flag"
    )
    
    def __repr__(self) -> str:
        """String representation of the model."""
        return f"<{self.__class__.__name__}(id={self.id})>"
    
    def to_dict(self, exclude: Optional[list] = None) -> dict:
        """
        Convert model to dictionary.
        
        Args:
            exclude: List of field names to exclude
        
        Returns:
            dict: Dictionary representation of the model
        """
        exclude = exclude or []
        result = {}
        
        for column in self.__table__.columns:
            if column.name in exclude:
                continue
            value = getattr(self, column.name)
            
            # Handle special types
            if isinstance(value, datetime):
                value = value.isoformat()
            elif isinstance(value, uuid.UUID):
                value = str(value)
            
            result[column.name] = value
        
        return result
    
    @classmethod
    def get_table_name(cls) -> str:
        """Get the table name for this model."""
        return cls.__tablename__
    
    @classmethod
    def get_primary_key(cls) -> str:
        """Get the primary key column name."""
        return 'id'
    
    @classmethod
    def get_columns(cls) -> list:
        """Get all column names."""
        return [column.name for column in cls.__table__.columns]


class TimestampMixin:
    """Mixin for adding timestamp fields."""
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )


class SoftDeleteMixin:
    """Mixin for soft delete functionality."""
    
    is_active: Mapped[bool] = mapped_column(
        default=True,
        nullable=False,
        index=True
    )
    
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )
    
    def soft_delete(self) -> None:
        """Soft delete the record."""
        self.is_active = False
        self.deleted_at = datetime.now(timezone.utc)


class AuditMixin:
    """Mixin for audit fields (created_by, updated_by)."""
    
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        index=True,
        comment="User who created the record"
    )
    
    updated_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        index=True,
        comment="User who last updated the record"
    )


# Export base classes
__all__ = [
    "Base",
    "TimestampMixin",
    "SoftDeleteMixin",
    "AuditMixin",
]
