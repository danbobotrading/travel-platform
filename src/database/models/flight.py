"""
Flight models for Travel Platform.

This module defines models for flights, flight searches, and flight bookings.
"""

import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Any
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
from src.core.config.constants import FlightClass, Currency


class FlightStatus(PyEnum):
    """Flight status."""
    
    SCHEDULED = "scheduled"
    ON_TIME = "on_time"
    DELAYED = "delayed"
    CANCELLED = "cancelled"
    DEPARTED = "departed"
    ARRIVED = "arrived"
    DIVERTED = "diverted"


class BookingStatus(PyEnum):
    """Flight booking status."""
    
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    NO_SHOW = "no_show"
    COMPLETED = "completed"


class Flight(Base, TimestampMixin):
    """Flight model for flight information."""
    
    __tablename__ = "flights"
    
    # Flight identification
    flight_number: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        index=True,
        comment="Flight number (e.g., BA123)"
    )
    
    airline_code: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        index=True,
        comment="Airline IATA code (e.g., BA)"
    )
    
    airline_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Airline name"
    )
    
    # Route information
    departure_airport: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        index=True,
        comment="Departure airport IATA code"
    )
    
    departure_city: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Departure city name"
    )
    
    departure_country: Mapped[str] = mapped_column(
        String(2),
        nullable=False,
        comment="Departure country code (ISO 3166-1 alpha-2)"
    )
    
    arrival_airport: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        index=True,
        comment="Arrival airport IATA code"
    )
    
    arrival_city: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Arrival city name"
    )
    
    arrival_country: Mapped[str] = mapped_column(
        String(2),
        nullable=False,
        comment="Arrival country code (ISO 3166-1 alpha-2)"
    )
    
    # Schedule information
    departure_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment="Scheduled departure time"
    )
    
    arrival_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment="Scheduled arrival time"
    )
    
    duration: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Flight duration in minutes"
    )
    
    # Flight details
    aircraft_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Aircraft type (e.g., Boeing 737-800)"
    )
    
    aircraft_registration: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="Aircraft registration number"
    )
    
    distance: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Flight distance in kilometers"
    )
    
    stops: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Number of stops"
    )
    
    stop_details: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSONB,
        default=list,
        nullable=False,
        comment="Details about stops (airport, duration, etc.)"
    )
    
    # Pricing and availability
    base_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        comment="Base price in preferred currency"
    )
    
    currency: Mapped[Currency] = mapped_column(
        Enum(Currency, name="currency"),
        default=Currency.NGN,
        nullable=False,
        comment="Price currency"
    )
    
    available_seats: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Number of available seats"
    )
    
    total_seats: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Total number of seats"
    )
    
    # Class-specific pricing
    economy_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        comment="Economy class price"
    )
    
    premium_economy_price: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2),
        nullable=True,
        comment="Premium economy class price"
    )
    
    business_price: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2),
        nullable=True,
        comment="Business class price"
    )
    
    first_class_price: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2),
        nullable=True,
        comment="First class price"
    )
    
    # Status and metadata
    status: Mapped[FlightStatus] = mapped_column(
        Enum(FlightStatus, name="flight_status"),
        default=FlightStatus.SCHEDULED,
        nullable=False,
        index=True,
        comment="Current flight status"
    )
    
    check_in_opens: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="When check-in opens"
    )
    
    check_in_closes: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="When check-in closes"
    )
    
    baggage_allowance: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        default=lambda: {
            "cabin": {"weight": 7, "unit": "kg"},
            "checked": {"weight": 23, "unit": "kg"},
        },
        nullable=False,
        comment="Baggage allowance information"
    )
    
    amenities: Mapped[List[str]] = mapped_column(
        JSONB,
        default=list,
        nullable=False,
        comment="Flight amenities (wifi, meals, entertainment, etc.)"
    )
    
    metadata_: Mapped[Dict[str, Any]] = mapped_column(
        "metadata",
        JSONB,
        default=dict,
        nullable=False,
        comment="Additional flight metadata"
    )
    
    # Relationships
    bookings: Mapped[List["FlightBooking"]] = relationship(
        "FlightBooking",
        back_populates="flight",
        cascade="all, delete-orphan"
    )
    
    # Indexes
    __table_args__ = (
        # Composite indexes for common queries
        Index("idx_flights_route_date", "departure_airport", "arrival_airport", "departure_time"),
        Index("idx_flights_airline_date", "airline_code", "departure_time"),
        
        # Partial index for active flights
        Index(
            "idx_flights_active_future",
            "departure_time",
            postgresql_where=text(
                "departure_time > NOW() AND status NOT IN ('cancelled', 'arrived')"
            )
        ),
        
        # Check constraints
        CheckConstraint("departure_time < arrival_time", name="ck_departure_before_arrival"),
        CheckConstraint("available_seats >= 0", name="ck_non_negative_seats"),
        CheckConstraint("available_seats <= total_seats", name="ck_seats_within_total"),
        CheckConstraint("duration > 0", name="ck_positive_duration"),
        
        # Unique constraint
        UniqueConstraint(
            "flight_number",
            "departure_time",
            "airline_code",
            name="uq_flight_schedule"
        ),
    )
    
    def get_price_for_class(self, flight_class: FlightClass) -> Decimal:
        """Get price for specific flight class."""
        prices = {
            FlightClass.ECONOMY: self.economy_price,
            FlightClass.PREMIUM_ECONOMY: self.premium_economy_price,
            FlightClass.BUSINESS: self.business_price,
            FlightClass.FIRST: self.first_class_price,
        }
        
        price = prices.get(flight_class)
        if price is None:
            raise ValueError(f"Class {flight_class} not available on this flight")
        
        return price
    
    def is_available(self) -> bool:
        """Check if flight is available for booking."""
        now = datetime.now()
        return (
            self.available_seats > 0
            and self.departure_time > now
            and self.status in [FlightStatus.SCHEDULED, FlightStatus.ON_TIME]
        )
    
    def reserve_seat(self) -> bool:
        """Reserve a seat on the flight."""
        if self.available_seats > 0:
            self.available_seats -= 1
            return True
        return False
    
    def release_seat(self) -> None:
        """Release a reserved seat."""
        if self.available_seats < self.total_seats:
            self.available_seats += 1


class FlightSearch(Base, TimestampMixin):
    """Flight search model for tracking user searches."""
    
    __tablename__ = "flight_searches"
    
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
    
    departure_airport: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        comment="Departure airport code"
    )
    
    arrival_airport: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        comment="Arrival airport code"
    )
    
    departure_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment="Departure date"
    )
    
    return_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Return date (for round trips)"
    )
    
    trip_type: Mapped[str] = mapped_column(
        String(20),
        default="one_way",
        nullable=False,
        comment="Trip type: one_way, round_trip, multi_city"
    )
    
    passengers: Mapped[Dict[str, int]] = mapped_column(
        JSONB,
        default=lambda: {"adults": 1, "children": 0, "infants": 0},
        nullable=False,
        comment="Passenger count by type"
    )
    
    flight_class: Mapped[FlightClass] = mapped_column(
        Enum(FlightClass, name="flight_class"),
        default=FlightClass.ECONOMY,
        nullable=False,
        comment="Requested flight class"
    )
    
    # Search results and metadata
    total_results: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Total number of flight results"
    )
    
    min_price: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2),
        nullable=True,
        comment="Minimum price found"
    )
    
    max_price: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2),
        nullable=True,
        comment="Maximum price found"
    )
    
    currency: Mapped[Currency] = mapped_column(
        Enum(Currency, name="currency"),
        default=Currency.NGN,
        nullable=False,
        comment="Price currency"
    )
    
    search_filters: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        default=dict,
        nullable=False,
        comment="Applied search filters"
    )
    
    # User interaction
    result_clicked: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether user clicked on a result"
    )
    
    booking_initiated: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether user started booking from this search"
    )
    
    booking_completed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether booking was completed"
    )
    
    # Performance and analytics
    response_time_ms: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Search response time in milliseconds"
    )
    
    api_provider: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="API provider used for search"
    )
    
    metadata_: Mapped[Dict[str, Any]] = mapped_column(
        "metadata",
        JSONB,
        default=dict,
        nullable=False,
        comment="Additional search metadata"
    )
    
    # Relationships
    user: Mapped[Optional["User"]] = relationship(
        "User",
        backref="flight_searches",
        foreign_keys=[user_id]
    )
    
    # Indexes
    __table_args__ = (
        # Composite index for analytics
        Index("idx_flight_searches_route_date", "departure_airport", "arrival_airport", "departure_date"),
        Index("idx_flight_searches_user_date", "user_id", "created_at"),
        
        # Partial index for popular searches
        Index(
            "idx_flight_searches_popular",
            "departure_airport",
            "arrival_airport",
            postgresql_where=text("created_at > NOW() - INTERVAL '7 days'")
        ),
    )
    
    def get_total_passengers(self) -> int:
        """Get total number of passengers."""
        return sum(self.passengers.values())
    
    def is_round_trip(self) -> bool:
        """Check if search is for round trip."""
        return self.trip_type == "round_trip" and self.return_date is not None


class FlightBooking(Base, TimestampMixin):
    """Flight booking model."""
    
    __tablename__ = "flight_bookings"
    
    # Booking identification
    booking_reference: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
        index=True,
        comment="Unique booking reference code"
    )
    
    pnr: Mapped[Optional[str]] = mapped_column(
        String(10),
        unique=True,
        nullable=True,
        index=True,
        comment="Passenger Name Record from airline"
    )
    
    # Relationships
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User who made the booking"
    )
    
    flight_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("flights.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="Booked flight"
    )
    
    # Passenger information
    passengers: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=False,
        comment="Passenger details (name, dob, passport, etc.)"
    )
    
    contact_info: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        comment="Contact information for booking"
    )
    
    # Booking details
    flight_class: Mapped[FlightClass] = mapped_column(
        Enum(FlightClass, name="flight_class"),
        nullable=False,
        comment="Booked flight class"
    )
    
    seat_preferences: Mapped[List[str]] = mapped_column(
        JSONB,
        default=list,
        nullable=False,
        comment="Seat preferences (window, aisle, etc.)"
    )
    
    special_requests: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Special requests or notes"
    )
    
    # Pricing and payment
    base_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        comment="Flight base price"
    )
    
    taxes_fees: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        comment="Taxes and fees"
    )
    
    service_fee: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        comment="Platform service fee"
    )
    
    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        comment="Total booking amount"
    )
    
    currency: Mapped[Currency] = mapped_column(
        Enum(Currency, name="currency"),
        nullable=False,
        comment="Booking currency"
    )
    
    paid_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=0,
        nullable=False,
        comment="Amount already paid"
    )
    
    # Status
    status: Mapped[BookingStatus] = mapped_column(
        Enum(BookingStatus, name="booking_status"),
        default=BookingStatus.PENDING,
        nullable=False,
        index=True,
        comment="Booking status"
    )
    
    confirmation_sent: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether confirmation was sent"
    )
    
    confirmation_sent_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="When confirmation was sent"
    )
    
    # Cancellation and changes
    cancellation_reason: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Reason for cancellation"
    )
    
    cancellation_fee: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=0,
        nullable=False,
        comment="Cancellation fee if applicable"
    )
    
    refund_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=0,
        nullable=False,
        comment="Amount to be refunded"
    )
    
    can_be_changed: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Whether booking can be changed"
    )
    
    can_be_cancelled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="Whether booking can be cancelled"
    )
    
    # Timestamps
    booked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="When booking was made"
    )
    
    confirmed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="When booking was confirmed by airline"
    )
    
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="When booking was cancelled"
    )
    
    # External references
    external_booking_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Booking ID from external system/airline"
    )
    
    metadata_: Mapped[Dict[str, Any]] = mapped_column(
        "metadata",
        JSONB,
        default=dict,
        nullable=False,
        comment="Additional booking metadata"
    )
    
    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        backref="flight_bookings",
        foreign_keys=[user_id]
    )
    
    flight: Mapped["Flight"] = relationship(
        "Flight",
        back_populates="bookings",
        foreign_keys=[flight_id]
    )
    
    # Indexes
    __table_args__ = (
        # Composite indexes
        Index("idx_flight_bookings_user_status", "user_id", "status"),
        Index("idx_flight_bookings_flight_date", "flight_id", "booked_at"),
        
        # Partial indexes for common queries
        Index(
            "idx_flight_bookings_active",
            "user_id",
            postgresql_where=text("status IN ('pending', 'confirmed')")
        ),
        
        Index(
            "idx_flight_bookings_recent",
            "booked_at",
            postgresql_where=text("booked_at > NOW() - INTERVAL '30 days'")
        ),
        
        # Check constraints
        CheckConstraint("total_amount >= 0", name="ck_non_negative_total"),
        CheckConstraint("paid_amount >= 0", name="ck_non_negative_paid"),
        CheckConstraint("paid_amount <= total_amount", name="ck_paid_within_total"),
        CheckConstraint("refund_amount >= 0", name="ck_non_negative_refund"),
        CheckConstraint("cancellation_fee >= 0", name="ck_non_negative_cancel_fee"),
    )
    
    def get_balance_due(self) -> Decimal:
        """Get remaining balance to pay."""
        return self.total_amount - self.paid_amount
    
    def is_fully_paid(self) -> bool:
        """Check if booking is fully paid."""
        return self.paid_amount >= self.total_amount
    
    def can_check_in(self) -> bool:
        """Check if booking can check in."""
        if not self.flight:
            return False
        
        now = datetime.now()
        return (
            self.status == BookingStatus.CONFIRMED
            and self.flight.check_in_opens
            and self.flight.check_in_closes
            and self.flight.check_in_opens <= now <= self.flight.check_in_closes
        )
    
    def cancel(self, reason: str, fee: Decimal = 0) -> None:
        """Cancel the booking."""
        self.status = BookingStatus.CANCELLED
        self.cancellation_reason = reason
        self.cancellation_fee = fee
        self.refund_amount = self.paid_amount - fee
        self.cancelled_at = datetime.now()
        
        # Release the seat
        if self.flight:
            self.flight.release_seat()


# Export models
__all__ = [
    "Flight",
    "FlightSearch",
    "FlightBooking",
    "FlightStatus",
    "BookingStatus",
]
