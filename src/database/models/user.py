"""
User model for Travel Platform.

This module defines the User model with authentication, profile,
and preference information.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, List
from enum import Enum as PyEnum

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Index,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from src.database.models.base import Base, TimestampMixin, SoftDeleteMixin
from src.core.config.constants import UserRole, Currency, Language


class UserStatus(PyEnum):
    """User account status."""
    
    PENDING = "pending"  # Email not verified
    ACTIVE = "active"  # Account active
    SUSPENDED = "suspended"  # Temporarily suspended
    BANNED = "banned"  # Permanently banned
    INACTIVE = "inactive"  # Not used for long time


class VerificationStatus(PyEnum):
    """User verification status."""
    
    UNVERIFIED = "unverified"  # Not verified
    EMAIL_VERIFIED = "email_verified"  # Email verified
    PHONE_VERIFIED = "phone_verified"  # Phone verified
    KYC_PENDING = "kyc_pending"  # KYC submitted
    KYC_VERIFIED = "kyc_verified"  # KYC approved
    FULLY_VERIFIED = "fully_verified"  # All verifications done


class User(Base, TimestampMixin, SoftDeleteMixin):
    """User model for authentication and profile information."""
    
    __tablename__ = "users"
    
    # Telegram-specific fields
    telegram_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        unique=True,
        index=True,
        nullable=True,
        comment="Telegram user ID"
    )
    
    telegram_username: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True,
        index=True,
        comment="Telegram username without @"
    )
    
    telegram_chat_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        index=True,
        comment="Telegram chat ID for messaging"
    )
    
    # Authentication fields
    email: Mapped[Optional[str]] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=True,
        comment="User email address (nullable for Telegram-only users)"
    )
    
    phone_number: Mapped[Optional[str]] = mapped_column(
        String(20),
        unique=True,
        index=True,
        nullable=True,
        comment="User phone number in E.164 format"
    )
    
    phone_country_code: Mapped[Optional[str]] = mapped_column(
        String(5),
        nullable=True,
        comment="Phone country code (e.g., +234)"
    )
    
    password_hash: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="BCrypt password hash (nullable for Telegram-only users)"
    )
    
    # Profile information
    first_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="User first name"
    )
    
    last_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="User last name"
    )
    
    full_name: Mapped[Optional[str]] = mapped_column(
        String(201),  # first + last + space
        nullable=True,
        comment="Full name (first + last)"
    )
    
    date_of_birth: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="User date of birth"
    )
    
    profile_picture_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="URL to profile picture"
    )
    
    bio: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="User bio/description"
    )
    
    # Account status and permissions
    status: Mapped[UserStatus] = mapped_column(
        Enum(UserStatus, name="user_status"),
        default=UserStatus.PENDING,
        nullable=False,
        index=True,
        comment="User account status"
    )
    
    verification_status: Mapped[VerificationStatus] = mapped_column(
        Enum(VerificationStatus, name="verification_status"),
        default=VerificationStatus.UNVERIFIED,
        nullable=False,
        index=True,
        comment="User verification level"
    )
    
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role"),
        default=UserRole.USER,
        nullable=False,
        index=True,
        comment="User role/permissions"
    )
    
    is_email_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Email verification status"
    )
    
    is_phone_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Phone verification status"
    )
    
    email_verified_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp when email was verified"
    )
    
    phone_verified_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp when phone was verified"
    )
    
    # Preferences
    preferred_language: Mapped[Language] = mapped_column(
        Enum(Language, name="language"),
        default=Language.EN,
        nullable=False,
        comment="User preferred language"
    )
    
    preferred_currency: Mapped[Currency] = mapped_column(
        Enum(Currency, name="currency"),
        default=Currency.NGN,
        nullable=False,
        comment="User preferred currency"
    )
    
    timezone: Mapped[str] = mapped_column(
        String(50),
        default="Africa/Lagos",
        nullable=False,
        comment="User timezone"
    )
    
    notification_preferences: Mapped[dict] = mapped_column(
        JSONB,
        default=lambda: {
            "email": True,
            "telegram": True,
            "push": True,
            "flight_alerts": True,
            "price_drops": True,
            "booking_confirmation": True,
        },
        nullable=False,
        comment="User notification preferences"
    )
    
    # Security and tracking
    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Last login timestamp"
    )
    
    last_login_ip: Mapped[Optional[str]] = mapped_column(
        String(45),  # IPv6 max length
        nullable=True,
        comment="Last login IP address"
    )
    
    login_attempts: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Failed login attempts"
    )
    
    locked_until: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Account lock expiration"
    )
    
    two_factor_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="2FA enabled status"
    )
    
    two_factor_secret: Mapped[Optional[str]] = mapped_column(
        String(32),
        nullable=True,
        comment="2FA secret key"
    )
    
    # Referral system
    referral_code: Mapped[Optional[str]] = mapped_column(
        String(20),
        unique=True,
        index=True,
        nullable=True,
        comment="User referral code"
    )
    
    referred_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="User who referred this user"
    )
    
    referral_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Number of successful referrals"
    )
    
    # Metadata
    metadata_: Mapped[dict] = mapped_column(
        "metadata",
        JSONB,
        default=dict,
        nullable=False,
        comment="Additional user metadata"
    )
    
    # Relationships
    referred_users: Mapped[List["User"]] = relationship(
        "User",
        back_populates="referrer",
        foreign_keys=[referred_by],
        cascade="all, delete-orphan"
    )
    
    referrer: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="referred_users",
        foreign_keys=[referred_by],
        remote_side=[id]
    )
    
    # Indexes
    __table_args__ = (
        # Composite index for common queries
        Index("idx_users_email_phone", "email", "phone_number"),
        Index("idx_users_status_role", "status", "role"),
        Index("idx_users_created_active", "created_at", "is_active"),
        
        # Partial indexes for performance
        Index(
            "idx_users_active_telegram",
            "telegram_id",
            postgresql_where=text("is_active = true AND telegram_id IS NOT NULL")
        ),
        
        # Unique constraint for Telegram username (case-insensitive)
        UniqueConstraint(
            "telegram_username",
            name="uq_users_telegram_username_lower",
            postgresql_where=text("telegram_username IS NOT NULL"),
            postgresql_ops={"telegram_username": "text_pattern_ops"}
        ),
    )
    
    def __init__(self, **kwargs):
        """Initialize user with computed fields."""
        super().__init__(**kwargs)
        
        # Compute full name
        if self.first_name and self.last_name:
            self.full_name = f"{self.first_name} {self.last_name}"
        elif self.first_name:
            self.full_name = self.first_name
        elif self.last_name:
            self.full_name = self.last_name
    
    def update_last_login(self, ip_address: str) -> None:
        """Update last login information."""
        self.last_login_at = datetime.now(timezone.utc)
        self.last_login_ip = ip_address
        self.login_attempts = 0  # Reset on successful login
    
    def increment_login_attempts(self) -> None:
        """Increment failed login attempts."""
        self.login_attempts += 1
        
        # Lock account after 5 failed attempts for 30 minutes
        if self.login_attempts >= 5:
            self.locked_until = datetime.now(timezone.utc) + timedelta(minutes=30)
    
    def is_locked(self) -> bool:
        """Check if account is locked."""
        if not self.locked_until:
            return False
        return datetime.now(timezone.utc) < self.locked_until
    
    def verify_email(self) -> None:
        """Mark email as verified."""
        self.is_email_verified = True
        self.email_verified_at = datetime.now(timezone.utc)
        
        # Update verification status
        if self.is_phone_verified:
            self.verification_status = VerificationStatus.FULLY_VERIFIED
        else:
            self.verification_status = VerificationStatus.EMAIL_VERIFIED
    
    def verify_phone(self) -> None:
        """Mark phone as verified."""
        self.is_phone_verified = True
        self.phone_verified_at = datetime.now(timezone.utc)
        
        # Update verification status
        if self.is_email_verified:
            self.verification_status = VerificationStatus.FULLY_VERIFIED
        else:
            self.verification_status = VerificationStatus.PHONE_VERIFIED
    
    def can_book_flights(self) -> bool:
        """Check if user can book flights."""
        return (
            self.is_active
            and self.status == UserStatus.ACTIVE
            and self.verification_status in [
                VerificationStatus.EMAIL_VERIFIED,
                VerificationStatus.PHONE_VERIFIED,
                VerificationStatus.FULLY_VERIFIED,
            ]
            and not self.is_locked()
        )
    
    def get_display_name(self) -> str:
        """Get user display name."""
        if self.full_name:
            return self.full_name
        elif self.telegram_username:
            return f"@{self.telegram_username}"
        elif self.email:
            return self.email.split('@')[0]
        else:
            return f"User {self.id.hex[:8]}"


# Export models
__all__ = [
    "User",
    "UserStatus",
    "VerificationStatus",
]
