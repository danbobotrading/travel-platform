"""
Hotel models for Travel Platform.

This module defines models for hotels, hotel searches, and hotel bookings.
"""

import uuid
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Dict, Any
from enum import Enum as PyEnum

from sqlalchemy import (
    Boolean,
    Date,
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


class HotelCategory(PyEnum):
    """Hotel category/star rating."""
    
    BUDGET = "budget"  # 1-2 stars
    ECONOMY = "economy"  # 3 stars
    COMFORT = "comfort"  # 4 stars
    LUXURY = "luxury"  # 5 stars
    BOUTIQUE = "boutique"  # Boutique/specialty
    RESORT = "resort"  # Resort
    APARTMENT = "apartment"  # Apartment/rental


class RoomType(PyEnum):
    """Hotel room types."""
    
    STANDARD = "standard"
    DELUXE = "deluxe"
    SUITE = "suite"
    FAMILY = "family"
    EXECUTIVE = "executive"
    PRESIDENTIAL = "presidential"
    STUDIO = "studio"
    VILLA = "villa"


class HotelBookingStatus(PyEnum):
    """Hotel booking status."""
    
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    CHECKED_IN = "checked_in"
    CHECKED_OUT = "checked_out"
    NO_SHOW = "no_show"
    REFUNDED = "refunded"


class Hotel(Base, TimestampMixin):
    """Hotel model for hotel information."""
    
    __tablename__ = "hotels"
    
    # Hotel identification
    external_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        unique=True,
        nullable=True,
        index=True,
        comment="External hotel ID from provider"
    )
    
    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True,
        comment="Hotel name"
    )
    
    chain_code: Mapped[Optional[str]] = mapped_column(
        String(10),
        nullable=True,
        index=True,
        comment="Hotel chain code"
    )
    
    chain_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Hotel chain name"
    )
    
    # Location information
    address: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="Full address"
    )
    
    city: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="City name"
    )
    
    state: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="State/province"
    )
    
    country: Mapped[str] = mapped_column(
        String(2),
        nullable=False,
        index=True,
        comment="Country code (ISO 3166-1 alpha-2)"
    )
    
    postal_code: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="Postal/ZIP code"
    )
    
    latitude: Mapped[Decimal] = mapped_column(
        Numeric(9, 6),
        nullable=False,
        comment="Latitude coordinate"
    )
    
    longitude: Mapped[Decimal] = mapped_column(
        Numeric(9, 6),
        nullable=False,
        comment="Longitude coordinate"
    )
    
    timezone: Mapped[str] = mapped_column(
        String(50),
        default="Africa/Lagos",
        nullable=False,
        comment="Hotel timezone"
    )
    
    # Hotel details
    category: Mapped[HotelCategory] = mapped_column(
        Enum(HotelCategory, name="hotel_category"),
        nullable=False,
        index=True,
        comment="Hotel category/star rating"
    )
    
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Hotel description"
    )
    
    amenities: Mapped[List[str]] = mapped_column(
        JSONB,
        default=list,
        nullable=False,
        comment="Hotel amenities list"
    )
    
    check_in_time: Mapped[str] = mapped_column(
        String(10),
        default="14:00",
        nullable=False,
        comment="Standard check-in time (HH:MM)"
    )
    
    check_out_time: Mapped[str] = mapped_column(
        String(10),
        default="12:00",
        nullable=False,
        comment="Standard check-out time (HH:MM)"
    )
    
    min_check_in_age: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Minimum age for check-in"
    )
    
    # Contact information
    phone: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="Hotel phone number"
    )
    
    email: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Hotel email"
    )
    
    website: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="Hotel website"
    )
    
    # Rating and reviews
    star_rating: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(2, 1),
        nullable=True,
        comment="Star rating (1.0 to 5.0)"
    )
    
    guest_rating: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(3, 2),
        nullable=True,
        comment="Guest rating (0.0 to 10.0)"
    )
    
    review_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Number of reviews"
    )
    
    # Media
    image_urls: Mapped[List[str]] = mapped_column(
        JSONB,
        default=list,
        nullable=False,
        comment="Hotel image URLs"
    )
    
    # Policies
    cancellation_policy: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        default=lambda: {
            "free_cancellation_until": None,
            "cancellation_fee": 0,
            "non_refundable": False,
        },
        nullable=False,
        comment="Cancellation policy details"
    )
    
    pet_policy: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Pet policy"
    )
    
    extra_bed_policy: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Extra bed policy"
    )
    
    # Room information
    total_rooms: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Total number of rooms"
    )
    
    room_types: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSONB,
        default=list,
        nullable=False,
        comment="Available room types with details"
    )
    
    # Pricing
    currency: Mapped[Currency] = mapped_column(
        Enum(Currency, name="currency"),
        default=Currency.NGN,
        nullable=False,
        comment="Default currency for pricing"
    )
    
    min_price_per_night: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        comment="Minimum price per night"
    )
    
    max_price_per_night: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        comment="Maximum price per night"
    )
    
    # Status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        comment="Whether hotel is active"
    )
    
    metadata_: Mapped[Dict[str, Any]] = mapped_column(
        "metadata",
        JSONB,
        default=dict,
        nullable=False,
        comment="Additional hotel metadata"
    )
    
    # Relationships
    bookings: Mapped[List["HotelBooking"]] = relationship(
        "HotelBooking",
        back_populates="hotel",
        cascade="all, delete-orphan"
    )
    
    # Indexes
    __table_args__ = (
        # Composite indexes
        Index("idx_hotels_location", "country", "city"),
        Index("idx_hotels_geo", "latitude", "longitude"),
        
        # GiST index for geographic searches
        Index(
            "idx_hotels_location_gist",
            text("(point(longitude, latitude))"),
            postgresql_using="gist"
        ),
        
        # Partial index for active hotels
        Index(
            "idx_hotels_active",
            "city",
            "category",
            postgresql_where=text("is_active = true")
        ),
        
        # Check constraints
        CheckConstraint("star_rating >= 1 AND star_rating <= 5", name="ck_star_rating_range"),
        CheckConstraint("guest_rating >= 0 AND guest_rating <= 10", name="ck_guest_rating_range"),
        CheckConstraint("min_price_per_night >= 0", name="ck_non_negative_min_price"),
        CheckConstraint("max_price_per_night >= min_price_per_night", name="ck_max_gte_min_price"),
        
        # Unique constraint for location
        UniqueConstraint(
            "name",
            "city",
            "country",
            name="uq_hotel_location"
        ),
    )
    
    def is_available(self, check_in: date, check_out: date) -> bool:
        """Check if hotel has availability for dates."""
        # This would typically check room inventory
        # For now, assume available if hotel is active
        return self.is_active
    
    def get_location_point(self) -> tuple:
        """Get geographic point (latitude, longitude)."""
        return (float(self.latitude), float(self.longitude))


class HotelSearch(Base, TimestampMixin):
    """Hotel search model for tracking user searches."""
    
    __tablename__ = "hotel_searches"
    
    # Search parameters
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        comment="User who performed the search"
    )
    
    session_id: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
        comment="Session identifier for anonymous users"
    )
    
    # Location
    city: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="Search city"
    )
    
    country: Mapped[str] = mapped_column(
        String(2),
        nullable=False,
        index=True,
        comment="Search country code"
    )
    
    latitude: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(9, 6),
        nullable=True,
        comment="Search latitude"
    )
    
    longitude: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(9, 6),
        nullable=True,
        comment="Search longitude"
    )
    
    radius_km: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Search radius in kilometers"
    )
    
    # Dates
    check_in: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
        comment="Check-in date"
    )
    
    check_out: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
        comment="Check-out date"
    )
    
    # Guests
    adults: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
        comment="Number of adults"
    )
    
    children: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Number of children"
    )
    
    rooms: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
        comment="Number of rooms"
    )
    
    # Preferences
    min_star_rating: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(2, 1),
        nullable=True,
        comment="Minimum star rating"
    )
    
    max_price_per_night: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2),
        nullable=True,
        comment="Maximum price per night"
    )
    
    currency: Mapped[Currency] = mapped_column(
        Enum(Currency, name="currency"),
        default=Currency.NGN,
        nullable=False,
        comment="Price currency"
    )
    
    amenities: Mapped[List[str]] = mapped_column(
        JSONB,
        default=list,
        nullable=False,
        comment="Requested amenities"
    )
    
    hotel_categories: Mapped[List[str]] = mapped_column(
        JSONB,
        default=list,
        nullable=False,
        comment="Requested hotel categories"
    )
    
    # Search results and
