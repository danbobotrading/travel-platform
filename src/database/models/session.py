"""
Session model for Travel Platform.

This module defines the session model for user authentication sessions.
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    Index,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from src.database.models.base import Base, TimestampMixin
from src.core.config.settings import settings


class Session(Base, TimestampMixin):
    """Session model for user authentication sessions."""
    
    __tablename__ = "sessions"
    
    # Session identification
    session_token: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="Session token (JWT or random string)"
    )
    
    # Relationships
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User associated with this session"
    )
    
    # Session details
    session_type: Mapped[str] = mapped_column(
        String(50),
        default="web",
        nullable=False,
        comment="Session type: web, mobile, api, telegram"
    )
    
    device_info: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        default=dict,
        nullable=False,
        comment="Device information (browser, OS, etc.)"
    )
    
    ip_address: Mapped[str] = mapped_column(
        String(45),
        nullable=False,
        comment="IP address of session origin"
    )
    
    user_agent: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="User agent string"
    )
    
    location: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Geolocation information"
    )
    
    # Authentication details
    auth_method: Mapped[str] = mapped_column(
        String(50),
        default="password",
        nullable=False,
        comment="Authentication method"
    )
    
    mfa_used: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether MFA was used"
    )
    
    mfa_method: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="MFA method used (totp, sms, etc.)"
    )
    
    # Session state
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        comment="Whether session is active"
    )
    
    last_activity: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
        comment="Last activity timestamp"
    )
    
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment="Session expiration timestamp"
    )
    
    revoked_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="When session was revoked"
    )
    
    revocation_reason: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Reason for revocation"
    )
    
    # Security
    is_compromised: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether session is compromised"
    )
    
    security_alerts: Mapped[list] = mapped_column(
        JSONB,
        default=list,
        nullable=False,
        comment="Security alerts for this session"
    )
    
    # Refresh token (if applicable)
    refresh_token: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Refresh token for this session"
    )
    
    refresh_token_expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Refresh token expiration"
    )
    
    # Metadata
    metadata_: Mapped[Dict[str, Any]] = mapped_column(
        "metadata",
        JSONB,
        default=dict,
        nullable=False,
        comment="Additional session metadata"
    )
    
    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        backref="sessions",
        foreign_keys=[user_id]
    )
    
    # Indexes
    __table_args__ = (
        # Composite indexes
        Index("idx_sessions_user_active", "user_id", "is_active"),
        Index("idx_sessions_expiry", "expires_at", "is_active"),
        
        # Partial indexes
        Index(
            "idx_sessions_active_recent",
            "user_id",
            "last_activity",
            postgresql_where=text("is_active = true AND expires_at > NOW()")
        ),
        
        # For cleanup of expired sessions
        Index(
            "idx_sessions_expired",
            "expires_at",
            postgresql_where=text("is_active = true")
        ),
    )
    
    def __init__(self, **kwargs):
        """Initialize session with default expiration."""
        super().__init__(**kwargs)
        
        # Set default expiration if not provided
        if "expires_at" not in kwargs:
            self.expires_at = datetime.now() + timedelta(
                seconds=settings.REDIS_SESSION_TTL
            )
    
    def is_expired(self) -> bool:
        """Check if session is expired."""
        return datetime.now() > self.expires_at
    
    def is_valid(self) -> bool:
        """Check if session is valid (active and not expired)."""
        return self.is_active and not self.is_expired() and not self.is_compromised
    
    def update_last_activity(self) -> None:
        """Update last activity timestamp."""
        self.last_activity = datetime.now()
        
        # Optionally extend session on activity
        if settings.SESSION_EXTEND_ON_ACTIVITY:
            self.expires_at = datetime.now() + timedelta(
                seconds=settings.REDIS_SESSION_TTL
            )
    
    def revoke(self, reason: Optional[str] = None) -> None:
        """Revoke the session."""
        self.is_active = False
        self.revoked_at = datetime.now()
        self.revocation_reason = reason
    
    def mark_as_compromised(self, alert: str) -> None:
        """Mark session as compromised."""
        self.is_compromised = True
        self.security_alerts.append({
            "timestamp": datetime.now().isoformat(),
            "alert": alert,
            "action": "session_compromised"
        })
        self.revoke("Security compromise detected")
    
    def get_remaining_ttl(self) -> int:
        """Get remaining time to live in seconds."""
        if not self.is_active or self.is_expired():
            return 0
        
        remaining = (self.expires_at - datetime.now()).total_seconds()
        return max(0, int(remaining))
    
    def to_dict(self, include_token: bool = False) -> Dict[str, Any]:
        """Convert session to dictionary."""
        data = {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "session_type": self.session_type,
            "device_info": self.device_info,
            "ip_address": self.ip_address,
            "auth_method": self.auth_method,
            "is_active": self.is_active,
            "last_activity": self.last_activity.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "is_valid": self.is_valid(),
            "remaining_ttl": self.get_remaining_ttl(),
        }
        
        if include_token:
            data["session_token"] = self.session_token
        
        return data


# Export model
__all__ = ["Session"]
