"""
Type definitions for Travel Platform.
"""
from typing import TypedDict, Optional, List, Dict, Any, Union
from datetime import datetime, date
from decimal import Decimal
from enum import Enum


# Enums
class TravelClass(str, Enum):
    """Travel class types."""
    ECONOMY = "E"
    PREMIUM_ECONOMY = "PE"
    BUSINESS = "B"
    FIRST = "F"


class TripType(str, Enum):
    """Trip types."""
    ONEWAY = "oneway"
    ROUND = "round"
    MULTICITY = "multicity"


class BookingStatus(str, Enum):
    """Booking statuses."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class PaymentStatus(str, Enum):
    """Payment statuses."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class Currency(str, Enum):
    """Currency codes."""
    ZAR = "ZAR"  # South African Rand
    NGN = "NGN"  # Nigerian Naira
    KES = "KES"  # Kenyan Shilling
    GHS = "GHS"  # Ghanaian Cedi
    USD = "USD"  # US Dollar
    EUR = "EUR"  # Euro
    GBP = "GBP"  # British Pound


# Type definitions for API requests/responses
class SearchRequest(TypedDict, total=False):
    """Flight/hotel search request."""
    origin: str
    destination: str
    departure_date: str
    return_date: Optional[str]
    adults: int
    children: int
    infants: int
    travel_class: TravelClass
    trip_type: TripType
    currency: Currency


class FlightSegment(TypedDict, total=False):
    """Flight segment details."""
    departure_airport: str
    arrival_airport: str
    departure_time: str
    arrival_time: str
    duration: int  # minutes
    airline: str
    flight_number: str
    aircraft: Optional[str]
    travel_class: TravelClass


class FlightOption(TypedDict, total=False):
    """Flight search result."""
    id: str
    price: Decimal
    currency: Currency
    segments: List[FlightSegment]
    total_duration: int  # minutes
    stops: int
    baggage_allowance: Dict[str, Any]
    fare_rules: Dict[str, Any]


class HotelSearchRequest(TypedDict, total=False):
    """Hotel search request."""
    location: str
    check_in: str
    check_out: str
    guests: int
    rooms: int
    currency: Currency


class HotelRoom(TypedDict, total=False):
    """Hotel room details."""
    type: str
    capacity: int
    beds: List[str]
    amenities: List[str]
    price_per_night: Decimal


class HotelOption(TypedDict, total=False):
    """Hotel search result."""
    id: str
    name: str
    location: str
    rating: float
    price_per_night: Decimal
    total_price: Decimal
    currency: Currency
    rooms: List[HotelRoom]
    amenities: List[str]
    images: List[str]


class UserProfile(TypedDict, total=False):
    """User profile data."""
    user_id: str
    telegram_id: Optional[int]
    username: Optional[str]
    first_name: str
    last_name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    country: Optional[str]
    language: str
    currency_preference: Currency
    is_active: bool
    created_at: datetime
    updated_at: datetime


class BookingRequest(TypedDict, total=False):
    """Booking request."""
    user_id: str
    option_id: str
    option_type: str  # 'flight' or 'hotel'
    passengers: List[Dict[str, Any]]
    contact_info: Dict[str, Any]
    payment_method: str
    special_requests: Optional[str]


class BookingDetails(TypedDict, total=False):
    """Booking details."""
    booking_id: str
    user_id: str
    status: BookingStatus
    option_type: str
    option_details: Dict[str, Any]
    total_price: Decimal
    currency: Currency
    payment_status: PaymentStatus
    passengers: List[Dict[str, Any]]
    contact_info: Dict[str, Any]
    booking_reference: Optional[str]
    created_at: datetime
    updated_at: datetime


class PaymentRequest(TypedDict, total=False):
    """Payment request."""
    booking_id: str
    amount: Decimal
    currency: Currency
    payment_method: str
    payment_details: Dict[str, Any]
    return_url: Optional[str]
    cancel_url: Optional[str]


class PaymentResponse(TypedDict, total=False):
    """Payment response."""
    payment_id: str
    status: PaymentStatus
    amount_paid: Decimal
    currency: Currency
    payment_method: str
    transaction_id: Optional[str]
    payment_url: Optional[str]  # For redirect payments
    paid_at: Optional[datetime]
    failure_reason: Optional[str]


class CacheConfig(TypedDict, total=False):
    """Cache configuration."""
    enabled: bool
    ttl: int
    prefix: str
    redis_url: str


class LogConfig(TypedDict, total=False):
    """Logging configuration."""
    level: str
    format: str
    file: Optional[str]


class ApiResponse(TypedDict, total=False):
    """Standard API response."""
    success: bool
    data: Optional[Any]
    error: Optional[str]
    error_code: Optional[str]
    message: Optional[str]
    timestamp: datetime
    request_id: Optional[str]


class PaginatedResponse(TypedDict, total=False):
    """Paginated API response."""
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool


# Custom types
Email = str
PhoneNumber = str
IATACode = str
CountryCode = str
CurrencyCode = str
UUID = str
Timestamp = Union[int, float]
JSON = Union[Dict[str, Any], List[Any], str, int, float, bool, None]


# Type aliases for common patterns
SearchResults = Union[List[FlightOption], List[HotelOption]]
BookingOptions = Union[FlightOption, HotelOption]
PriceRange = Tuple[Decimal, Decimal]
DateRange = Tuple[date, date]
GeoPoint = Tuple[float, float]  # (latitude, longitude)


# Utility functions for type validation
def is_valid_iata(code: str) -> bool:
    """Check if string is a valid IATA code."""
    return isinstance(code, str) and len(code) == 3 and code.isalpha()


def is_valid_country_code(code: str) -> bool:
    """Check if string is a valid country code."""
    return isinstance(code, str) and len(code) == 2 and code.isalpha()


def is_valid_currency_code(code: str) -> bool:
    """Check if string is a valid currency code."""
    return isinstance(code, str) and len(code) == 3 and code.isalpha()


def is_valid_email(email: str) -> bool:
    """Basic email validation."""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


# Type conversion utilities
def convert_to_decimal(value: Union[str, int, float, Decimal]) -> Decimal:
    """Safely convert value to Decimal."""
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def convert_to_date(value: Union[str, date, datetime]) -> date:
    """Safely convert value to date."""
    if isinstance(value, date):
        return value
    elif isinstance(value, datetime):
        return value.date()
    else:
        return datetime.strptime(value, '%Y-%m-%d').date()


def serialize_for_json(obj: Any) -> Any:
    """Serialize object for JSON response."""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, Enum):
        return obj.value
    elif hasattr(obj, 'to_dict'):
        return obj.to_dict()
    elif isinstance(obj, dict):
        return {k: serialize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [serialize_for_json(item) for item in obj]
    else:
        return obj


# Test function
def test_types():
    """Test type definitions and utilities."""
    print("Testing Type Definitions...")
    print("=" * 50)
    
    # Test enum
    print(f"1. TravelClass enum: {TravelClass.ECONOMY.value} = {TravelClass.ECONOMY}")
    
    # Test typed dict
    search_request: SearchRequest = {
        "origin": "JNB",
        "destination": "CPT",
        "departure_date": "2024-01-15",
        "adults": 2,
        "travel_class": TravelClass.ECONOMY
    }
    print(f"2. SearchRequest: {search_request['origin']} → {search_request['destination']}")
    
    # Test validation functions
    print(f"3. IATA validation:")
    print(f"   JNB: {is_valid_iata('JNB')}")
    print(f"   ABC123: {is_valid_iata('ABC123')}")
    
    print(f"4. Email validation:")
    print(f"   test@example.com: {is_valid_email('test@example.com')}")
    print(f"   invalid-email: {is_valid_email('invalid-email')}")
    
    # Test conversion
    dec_value = convert_to_decimal("123.45")
    print(f"5. Decimal conversion: {dec_value} ({type(dec_value).__name__})")
    
    date_value = convert_to_date("2024-01-15")
    print(f"6. Date conversion: {date_value} ({type(date_value).__name__})")
    
    # Test serialization
    test_data = {
        "amount": Decimal("123.45"),
        "date": date(2024, 1, 15),
        "class": TravelClass.BUSINESS
    }
    serialized = serialize_for_json(test_data)
    print(f"7. JSON serialization: {serialized}")
    
    print("\n" + "=" * 50)
    print("✅ Type definitions test complete!")
