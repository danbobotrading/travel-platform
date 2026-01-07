"""
Payment models for Travel Platform.

This module defines models for payments, payment methods, and transactions.
"""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any
from enum import Enum as PyEnum

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    Index,
    text,
    CheckConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from src.database.models.base import Base, TimestampMixin
from src.core.config.constants import Currency


class PaymentMethodType(PyEnum):
    """Payment method types."""
    
    CARD = "card"
    BANK_TRANSFER = "bank_transfer"
    MOBILE_MONEY = "mobile_money"
    WALLET = "wallet"
    CASH = "cash"
    VOUCHER = "voucher"


class PaymentStatus(PyEnum):
    """Payment status."""
    
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"
    DISPUTED = "disputed"


class PaymentProvider(PyEnum):
    """Payment providers."""
    
    PAYSTACK = "paystack"
    STRIPE = "stripe"
    FLUTTERWAVE = "flutterwave"
    MPESA = "mpesa"
    INTERNAL = "internal"
    MANUAL = "manual"


class Payment(Base, TimestampMixin):
    """Payment model for financial transactions."""
    
    __tablename__ = "payments"
    
    # Payment identification
    reference: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="Payment reference number"
    )
    
    external_reference: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
        comment="Reference from external payment provider"
    )
    
    # Relationships
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User who made the payment"
    )
    
    payment_method_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("payment_methods.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Payment method used"
    )
    
    # Payment details
    amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        comment="Payment amount"
    )
    
    currency: Mapped[Currency] = mapped_column(
        Enum(Currency, name="currency"),
        nullable=False,
        comment="Payment currency"
    )
    
    fee_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=0,
        nullable=False,
        comment="Transaction fee amount"
    )
    
    net_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        comment="Net amount after fees"
    )
    
    # Status and provider
    status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus, name="payment_status"),
        default=PaymentStatus.PENDING,
        nullable=False,
        index=True,
        comment="Payment status"
    )
    
    provider: Mapped[PaymentProvider] = mapped_column(
        Enum(PaymentProvider, name="payment_provider"),
        nullable=False,
        index=True,
        comment="Payment provider"
    )
    
    provider_response: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        default=dict,
        nullable=False,
        comment="Raw response from payment provider"
    )
    
    # Description and metadata
    description: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="Payment description"
    )
    
    metadata_: Mapped[Dict[str, Any]] = mapped_column(
        "metadata",
        JSONB,
        default=dict,
        nullable=False,
        comment="Additional payment metadata"
    )
    
    # Timestamps
    initiated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="When payment was initiated"
    )
    
    processed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="When payment was processed"
    )
    
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="When payment was completed"
    )
    
    failed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="When payment failed"
    )
    
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="When payment was cancelled"
    )
    
    # Error handling
    error_code: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Error code if payment failed"
    )
    
    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Error message if payment failed"
    )
    
    retry_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Number of retry attempts"
    )
    
    # Refund information
    refunded_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=0,
        nullable=False,
        comment="Amount refunded"
    )
    
    refund_reference: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Refund reference number"
    )
    
    refunded_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="When refund was processed"
    )
    
    # Webhook and verification
    webhook_received: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether webhook was received"
    )
    
    webhook_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether webhook was verified"
    )
    
    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45),
        nullable=True,
        comment="IP address of payment initiator"
    )
    
    user_agent: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="User agent of payment initiator"
    )
    
    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        backref="payments",
        foreign_keys=[user_id]
    )
    
    payment_method: Mapped[Optional["PaymentMethod"]] = relationship(
        "PaymentMethod",
        back_populates="payments",
        foreign_keys=[payment_method_id]
    )
    
    # Indexes
    __table_args__ = (
        # Composite indexes
        Index("idx_payments_user_status", "user_id", "status"),
        Index("idx_payments_provider_status", "provider", "status"),
        Index("idx_payments_date_amount", "initiated_at", "amount"),
        
        # Partial indexes for common queries
        Index(
            "idx_payments_recent_pending",
            "initiated_at",
            postgresql_where=text("status = 'pending' AND initiated_at > NOW() - INTERVAL '24 hours'")
        ),
        
        Index(
            "idx_payments_large_amounts",
            "amount",
            postgresql_where=text("amount > 100000")  # For large payments monitoring
        ),
        
        # Check constraints
        CheckConstraint("amount > 0", name="ck_positive_amount"),
        CheckConstraint("fee_amount >= 0", name="ck_non_negative_fee"),
        CheckConstraint("net_amount >= 0", name="ck_non_negative_net"),
        CheckConstraint("retry_count >= 0", name="ck_non_negative_retry"),
        CheckConstraint("refunded_amount >= 0", name="ck_non_negative_refunded"),
        CheckConstraint("refunded_amount <= amount", name="ck_refund_within_amount"),
        
        # Ensure net amount calculation
        CheckConstraint("net_amount = amount - fee_amount", name="ck_net_amount_calc"),
    )
    
    def is_successful(self) -> bool:
        """Check if payment was successful."""
        return self.status == PaymentStatus.COMPLETED
    
    def is_failed(self) -> bool:
        """Check if payment failed."""
        return self.status in [PaymentStatus.FAILED, PaymentStatus.CANCELLED]
    
    def is_refundable(self) -> bool:
        """Check if payment can be refunded."""
        return (
            self.status == PaymentStatus.COMPLETED
            and self.refunded_amount < self.amount
            and (self.completed_at is None or (datetime.now() - self.completed_at).days <= 180)
        )
    
    def mark_as_processing(self) -> None:
        """Mark payment as processing."""
        self.status = PaymentStatus.PROCESSING
        self.processed_at = datetime.now()
    
    def mark_as_completed(self, provider_data: Dict[str, Any]) -> None:
        """Mark payment as completed."""
        self.status = PaymentStatus.COMPLETED
        self.completed_at = datetime.now()
        self.provider_response.update(provider_data)
    
    def mark_as_failed(self, error_code: str, error_message: str) -> None:
        """Mark payment as failed."""
        self.status = PaymentStatus.FAILED
        self.failed_at = datetime.now()
        self.error_code = error_code
        self.error_message = error_message
        self.retry_count += 1


class PaymentMethod(Base, TimestampMixin):
    """Payment method model for storing user payment methods."""
    
    __tablename__ = "payment_methods"
    
    # Relationships
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User who owns this payment method"
    )
    
    # Payment method details
    type: Mapped[PaymentMethodType] = mapped_column(
        Enum(PaymentMethodType, name="payment_method_type"),
        nullable=False,
        index=True,
        comment="Payment method type"
    )
    
    provider: Mapped[PaymentProvider] = mapped_column(
        Enum(PaymentProvider, name="payment_provider"),
        nullable=False,
        index=True,
        comment="Payment provider"
    )
    
    # Card details (if applicable)
    card_last_four: Mapped[Optional[str]] = mapped_column(
        String(4),
        nullable=True,
        comment="Last 4 digits of card"
    )
    
    card_brand: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="Card brand (Visa, MasterCard, etc.)"
    )
    
    card_exp_month: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Card expiration month"
    )
    
    card_exp_year: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Card expiration year"
    )
    
    # Bank transfer details
    bank_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Bank name"
    )
    
    bank_account_last_four: Mapped[Optional[str]] = mapped_column(
        String(4),
        nullable=True,
        comment="Last 4 digits of bank account"
    )
    
    bank_account_type: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="Bank account type (savings, checking)"
    )
    
    # Mobile money details
    mobile_network: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Mobile network (MTN, Airtel, etc.)"
    )
    
    mobile_number: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="Mobile money number"
    )
    
    # Provider-specific identifiers
    provider_customer_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Customer ID at payment provider"
    )
    
    provider_payment_method_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Payment method ID at payment provider"
    )
    
    # Security
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether payment method is verified"
    )
    
    is_default: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether this is default payment method"
    )
    
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        comment="Whether payment method is active"
    )
    
    verification_attempts: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Number of verification attempts"
    )
    
    verified_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="When payment method was verified"
    )
    
    # Metadata
    metadata_: Mapped[Dict[str, Any]] = mapped_column(
        "metadata",
        JSONB,
        default=dict,
        nullable=False,
        comment="Additional payment method metadata"
    )
    
    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        backref="payment_methods",
        foreign_keys=[user_id]
    )
    
    payments: Mapped[list["Payment"]] = relationship(
        "Payment",
        back_populates="payment_method",
        cascade="all, delete-orphan"
    )
    
    # Indexes
    __table_args__ = (
        # Composite index
        Index("idx_payment_methods_user_type", "user_id", "type"),
        
        # Ensure only one default per user
        UniqueConstraint(
            "user_id",
            "is_default",
            name="uq_one_default_per_user",
            postgresql_where=text("is_default = true")
        ),
        
        # Check constraints
        CheckConstraint(
            "card_exp_month >= 1 AND card_exp_month <= 12",
            name="ck_valid_exp_month"
        ),
        CheckConstraint(
            "card_exp_year >= 2024 AND card_exp_year <= 2100",
            name="ck_valid_exp_year"
        ),
        CheckConstraint(
            "verification_attempts >= 0",
            name="ck_non_negative_verification_attempts"
        ),
    )
    
    def get_display_name(self) -> str:
        """Get display name for payment method."""
        if self.type == PaymentMethodType.CARD and self.card_brand and self.card_last_four:
            return f"{self.card_brand} •••• {self.card_last_four}"
        elif self.type == PaymentMethodType.MOBILE_MONEY and self.mobile_network and self.mobile_number:
            return f"{self.mobile_network} {self.mobile_number[-4:]}"
        elif self.type == PaymentMethodType.BANK_TRANSFER and self.bank_name and self.bank_account_last_four:
            return f"{self.bank_name} •••• {self.bank_account_last_four}"
        else:
            return self.type.value.replace("_", " ").title()
    
    def is_expired(self) -> bool:
        """Check if card is expired."""
        if not self.card_exp_month or not self.card_exp_year:
            return False
        
        from datetime import date
        today = date.today()
        return (
            self.card_exp_year < today.year
            or (self.card_exp_year == today.year and self.card_exp_month < today.month)
        )
    
    def mark_as_default(self) -> None:
        """Mark this payment method as default."""
        # This should be handled at application level to ensure only one default
        self.is_default = True
    
    def verify(self) -> None:
        """Mark payment method as verified."""
        self.is_verified = True
        self.verified_at = datetime.now()
        self.verification_attempts = 0


# Export models
__all__ = [
    "Payment",
    "PaymentMethod",
    "PaymentMethodType",
    "PaymentStatus",
    "PaymentProvider",
]
