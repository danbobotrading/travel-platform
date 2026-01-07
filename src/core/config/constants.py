"""
Constants for Travel Platform.

This module defines all application constants, including enums,
configuration values, and static data for the travel platform.
"""

from enum import Enum, IntEnum
from typing import Dict, List, Tuple


class AppConstants:
    """Application-level constants."""
    
    # Application metadata
    APP_NAME = "Travel Platform"
    APP_VERSION = "1.0.0"
    APP_DESCRIPTION = "Enterprise Telegram travel search & booking bot for African users"
    
    # Supported languages (ISO 639-1 codes)
    SUPPORTED_LANGUAGES = ["en", "fr", "ar", "sw", "pt", "ha"]
    
    # Supported currencies (ISO 4217 codes)
    SUPPORTED_CURRENCIES = ["NGN", "GHS", "KES", "ZAR", "USD", "EUR", "GBP"]
    
    # African countries focus (ISO 3166-1 alpha-2 codes)
    AFRICAN_COUNTRIES = [
        "NG",  # Nigeria
        "GH",  # Ghana
        "KE",  # Kenya
        "ZA",  # South Africa
        "EG",  # Egypt
        "MA",  # Morocco
        "TN",  # Tunisia
        "DZ",  # Algeria
        "CI",  # Côte d'Ivoire
        "SN",  # Senegal
        "CM",  # Cameroon
        "UG",  # Uganda
        "TZ",  # Tanzania
        "ET",  # Ethiopia
        "RW",  # Rwanda
        "BW",  # Botswana
        "NA",  # Namibia
        "ZM",  # Zambia
        "ZW",  # Zimbabwe
        "MW",  # Malawi
        "MZ",  # Mozambique
        "AO",  # Angola
        "CD",  # DR Congo
        "GA",  # Gabon
        "CG",  # Republic of the Congo
        "GN",  # Guinea
        "ML",  # Mali
        "BF",  # Burkina Faso
        "NE",  # Niger
        "TD",  # Chad
        "SD",  # Sudan
        "ER",  # Eritrea
        "DJ",  # Djibouti
        "SO",  # Somalia
        "BI",  # Burundi
        "SS",  # South Sudan
        "LR",  # Liberia
        "SL",  # Sierra Leone
        "GM",  # Gambia
        "GW",  # Guinea-Bissau
        "MR",  # Mauritania
        "ST",  # São Tomé and Príncipe
        "SC",  # Seychelles
        "CV",  # Cape Verde
        "KM",  # Comoros
        "MU",  # Mauritius
    ]
    
    # Major African airports (IATA codes)
    MAJOR_AIRPORTS = {
        "NG": ["LOS", "ABV", "PHC", "KAN", "ENU", "QOW"],
        "GH": ["ACC", "KMS", "TKD"],
        "KE": ["NBO", "MBA"],
        "ZA": ["JNB", "CPT", "DUR", "GRJ"],
        "EG": ["CAI", "HRG", "LXR"],
        "MA": ["CMN", "RAK", "FEZ"],
        "TN": ["TUN", "DJE", "SFA"],
        "DZ": ["ALG", "ORN", "AAE"],
    }
    
    # Timezone constants
    DEFAULT_TIMEZONE = "Africa/Lagos"
    SUPPORTED_TIMEZONES = [
        "Africa/Lagos",     # West Africa Time (Nigeria)
        "Africa/Accra",     # Ghana
        "Africa/Nairobi",   # East Africa Time (Kenya)
        "Africa/Johannesburg",  # South Africa
        "Africa/Cairo",     # Egypt
        "Africa/Casablanca",# Morocco
        "Africa/Tunis",     # Tunisia
        "Africa/Algiers",   # Algeria
    ]
    
    # File upload limits (in bytes)
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    ALLOWED_DOCUMENT_TYPES = ["application/pdf", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
    
    # Pagination defaults
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100
    DEFAULT_PAGE_NUMBER = 1


class DatabaseConstants:
    """Database-related constants."""
    
    # Table names
    USERS_TABLE = "users"
    FLIGHTS_TABLE = "flights"
    HOTELS_TABLE = "hotels"
    BOOKINGS_TABLE = "bookings"
    PAYMENTS_TABLE = "payments"
    SESSIONS_TABLE = "sessions"
    
    # Index names
    USERS_EMAIL_IDX = "idx_users_email"
    USERS_PHONE_IDX = "idx_users_phone"
    FLIGHTS_ROUTE_IDX = "idx_flights_route"
    BOOKINGS_USER_IDX = "idx_bookings_user_id"
    
    # Connection pool defaults
    DEFAULT_POOL_SIZE = 20
    MAX_POOL_OVERFLOW = 40
    POOL_TIMEOUT = 30
    POOL_RECYCLE = 3600
    
    # Migration settings
    MIGRATION_TABLE = "alembic_version"
    MIGRATION_CONTEXT = "src.database:migration_context"


class SecurityConstants:
    """Security-related constants."""
    
    # JWT settings
    JWT_ALGORITHM = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS = 7
    JWT_ISSUER = "travel-platform"
    
    # Password hashing
    PASSWORD_HASH_ALGORITHM = "bcrypt"
    PASSWORD_SALT_LENGTH = 16
    PASSWORD_HASH_ROUNDS = 12
    
    # Encryption
    ENCRYPTION_ALGORITHM = "fernet"
    ENCRYPTION_KEY_LENGTH = 32
    ENCRYPTION_SALT = "travel_platform_salt_2024"
    ENCRYPTION_ITERATIONS = 100000
    
    # Rate limiting
    RATE_LIMIT_REQUESTS = 100
    RATE_LIMIT_PERIOD = 60  # seconds
    RATE_LIMIT_STRATEGY = "fixed-window"
    
    # CORS
    ALLOWED_ORIGINS = ["http://localhost:3000", "http://localhost:8000"]
    ALLOWED_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    ALLOWED_HEADERS = ["*"]
    ALLOW_CREDENTIALS = True
    
    # Session
    SESSION_COOKIE_NAME = "travel_session"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = "lax"
    SESSION_TIMEOUT = 86400  # 24 hours


class ApiConstants:
    """API-related constants."""
    
    # API versions
    CURRENT_API_VERSION = "v1"
    API_PREFIX = "/api"
    
    # Response formats
    DEFAULT_RESPONSE_FORMAT = "json"
    SUPPORTED_RESPONSE_FORMATS = ["json", "xml"]
    
    # Pagination
    PAGE_QUERY_PARAM = "page"
    SIZE_QUERY_PARAM = "size"
    SORT_QUERY_PARAM = "sort"
    FILTER_QUERY_PARAM = "filter"
    
    # Rate limiting headers
    RATE_LIMIT_LIMIT_HEADER = "X-RateLimit-Limit"
    RATE_LIMIT_REMAINING_HEADER = "X-RateLimit-Remaining"
    RATE_LIMIT_RESET_HEADER = "X-RateLimit-Reset"
    
    # Request IDs
    REQUEST_ID_HEADER = "X-Request-ID"
    
    # Cache control
    CACHE_CONTROL_HEADER = "Cache-Control"
    DEFAULT_CACHE_CONTROL = "no-cache"
    PUBLIC_CACHE_CONTROL = "public, max-age=300"


class CacheConstants:
    """Cache-related constants."""
    
    # Redis settings
    REDIS_DEFAULT_DB = 0
    REDIS_SESSION_DB = 1
    REDIS_CACHE_DB = 2
    REDIS_QUEUE_DB = 3
    
    # Cache keys prefixes
    USER_CACHE_PREFIX = "user:"
    FLIGHT_CACHE_PREFIX = "flight:"
    HOTEL_CACHE_PREFIX = "hotel:"
    SESSION_CACHE_PREFIX = "session:"
    RATE_LIMIT_PREFIX = "rate_limit:"
    
    # Cache TTLs (in seconds)
    USER_CACHE_TTL = 3600  # 1 hour
    FLIGHT_CACHE_TTL = 300  # 5 minutes
    HOTEL_CACHE_TTL = 600  # 10 minutes
    SESSION_CACHE_TTL = 86400  # 24 hours
    RATE_LIMIT_TTL = 60  # 1 minute
    
    # Cache strategies
    CACHE_STRATEGY_WRITE_THROUGH = "write_through"
    CACHE_STRATEGY_WRITE_BACK = "write_back"
    CACHE_STRATEGY_CACHE_ASIDE = "cache_aside"
    
    # Cache invalidation patterns
    INVALIDATION_PATTERN_ALL = "all"
    INVALIDATION_PATTERN_SINGLE = "single"
    INVALIDATION_PATTERN_PATTERN = "pattern"


class UserRole(Enum):
    """User role enumeration."""
    
    GUEST = "guest"
    USER = "user"
    AGENT = "agent"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"
    
    @classmethod
    def get_hierarchy(cls, role: str) -> int:
        """Get hierarchy level of a role (higher number = more privileges)."""
        hierarchy = {
            cls.GUEST.value: 0,
            cls.USER.value: 1,
            cls.AGENT.value: 2,
            cls.ADMIN.value: 3,
            cls.SUPER_ADMIN.value: 4,
        }
        return hierarchy.get(role, 0)
    
    @classmethod
    def can_perform(cls, user_role: str, required_role: str) -> bool:
        """Check if user role can perform action requiring required_role."""
        return cls.get_hierarchy(user_role) >= cls.get_hierarchy(required_role)


class BookingStatus(Enum):
    """Booking status enumeration."""
    
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    REFUNDED = "refunded"
    FAILED = "failed"
    
    @classmethod
    def is_active(cls, status: str) -> bool:
        """Check if booking status is active."""
        active_statuses = [cls.PENDING.value, cls.CONFIRMED.value]
        return status in active_statuses
    
    @classmethod
    def is_completed(cls, status: str) -> bool:
        """Check if booking status is completed."""
        return status == cls.COMPLETED.value
    
    @classmethod
    def is_cancellable(cls, status: str) -> bool:
        """Check if booking can be cancelled."""
        cancellable_statuses = [cls.PENDING.value, cls.CONFIRMED.value]
        return status in cancellable_statuses


class PaymentStatus(Enum):
    """Payment status enumeration."""
    
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"
    CANCELLED = "cancelled"
    
    @classmethod
    def is_successful(cls, status: str) -> bool:
        """Check if payment was successful."""
        successful_statuses = [cls.COMPLETED.value]
        return status in successful_statuses
    
    @classmethod
    def is_failed(cls, status: str) -> bool:
        """Check if payment failed."""
        failed_statuses = [cls.FAILED.value, cls.CANCELLED.value]
        return status in failed_statuses
    
    @classmethod
    def is_pending(cls, status: str) -> bool:
        """Check if payment is pending."""
        pending_statuses = [cls.PENDING.value, cls.PROCESSING.value]
        return status in pending_statuses


class FlightClass(Enum):
    """Flight class enumeration."""
    
    ECONOMY = "economy"
    PREMIUM_ECONOMY = "premium_economy"
    BUSINESS = "business"
    FIRST = "first"
    
    @classmethod
    def get_price_multiplier(cls, flight_class: str) -> float:
        """Get price multiplier for flight class."""
        multipliers = {
            cls.ECONOMY.value: 1.0,
            cls.PREMIUM_ECONOMY.value: 1.5,
            cls.BUSINESS.value: 2.5,
            cls.FIRST.value: 4.0,
        }
        return multipliers.get(flight_class, 1.0)


class Currency(Enum):
    """Currency enumeration with metadata."""
    
    NGN = ("Nigerian Naira", "₦", "NG")
    GHS = ("Ghanaian Cedi", "₵", "GH")
    KES = ("Kenyan Shilling", "KSh", "KE")
    ZAR = ("South African Rand", "R", "ZA")
    USD = ("US Dollar", "$", "US")
    EUR = ("Euro", "€", "EU")
    GBP = ("British Pound", "£", "GB")
    
    def __init__(self, full_name: str, symbol: str, country_code: str):
        self.full_name = full_name
        self.symbol = symbol
        self.country_code = country_code
    
    @classmethod
    def get_by_country(cls, country_code: str) -> str:
        """Get default currency for a country."""
        country_currencies = {
            "NG": cls.NGN.value,
            "GH": cls.GHS.value,
            "KE": cls.KES.value,
            "ZA": cls.ZAR.value,
            "US": cls.USD.value,
            "GB": cls.GBP.value,
        }
        
        # Default to USD for other countries
        return country_currencies.get(country_code.upper(), cls.USD.value)
    
    @classmethod
    def get_symbol(cls, currency_code: str) -> str:
        """Get currency symbol."""
        for currency in cls:
            if currency.value == currency_code:
                return currency.symbol
        return currency_code


class Language(Enum):
    """Language enumeration with metadata."""
    
    EN = ("English", "en", "🇬🇧")
    FR = ("French", "fr", "🇫🇷")
    AR = ("Arabic", "ar", "🇸🇦")
    SW = ("Swahili", "sw", "🇹🇿")
    PT = ("Portuguese", "pt", "🇵🇹")
    HA = ("Hausa", "ha", "🇳🇬")
    
    def __init__(self, full_name: str, code: str, flag: str):
        self.full_name = full_name
        self.code = code
        self.flag = flag
    
    @classmethod
    def get_by_country(cls, country_code: str) -> List[str]:
        """Get default languages for a country."""
        country_languages = {
            "NG": [cls.EN.value, cls.HA.value],
            "GH": [cls.EN.value],
            "KE": [cls.EN.value, cls.SW.value],
            "ZA": [cls.EN.value],
            "EG": [cls.AR.value],
            "MA": [cls.AR.value, cls.FR.value],
            "TN": [cls.AR.value, cls.FR.value],
            "DZ": [cls.AR.value, cls.FR.value],
        }
        return country_languages.get(country_code.upper(), [cls.EN.value])
    
    @classmethod
    def get_flag(cls, language_code: str) -> str:
        """Get flag emoji for language."""
        for language in cls:
            if language.value == language_code:
                return language.flag
        return "🏳️"


class ErrorCodes:
    """Error code constants."""
    
    # Validation errors (1000-1999)
    VALIDATION_ERROR = 1000
    INVALID_EMAIL = 1001
    INVALID_PHONE = 1002
    INVALID_PASSWORD = 1003
    INVALID_URL = 1004
    INVALID_CURRENCY = 1005
    INVALID_LANGUAGE = 1006
    INVALID_COUNTRY = 1007
    INVALID_DATE = 1008
    INVALID_AIRPORT = 1009
    
    # Authentication errors (2000-2999)
    AUTHENTICATION_FAILED = 2000
    INVALID_TOKEN = 2001
    EXPIRED_TOKEN = 2002
    INVALID_CREDENTIALS = 2003
    ACCOUNT_LOCKED = 2004
    ACCOUNT_DISABLED = 2005
    INSUFFICIENT_PERMISSIONS = 2006
    
    # Resource errors (3000-3999)
    NOT_FOUND = 3000
    ALREADY_EXISTS = 3001
    CONFLICT = 3002
    LIMIT_EXCEEDED = 3003
    INSUFFICIENT_FUNDS = 3004
    OUT_OF_STOCK = 3005
    
    # System errors (4000-4999)
    INTERNAL_ERROR = 4000
    SERVICE_UNAVAILABLE = 4001
    DATABASE_ERROR = 4002
    NETWORK_ERROR = 4003
    EXTERNAL_API_ERROR = 4004
    DECRYPTION_ERROR = 4005
    ENCRYPTION_ERROR = 4006
    
    # Business logic errors (5000-5999)
    BOOKING_ERROR = 5000
    PAYMENT_ERROR = 5001
    FLIGHT_UNAVAILABLE = 5002
    HOTEL_UNAVAILABLE = 5003
    PRICE_CHANGED = 5004
    POLICY_VIOLATION = 5005
    
    # Rate limiting (6000-6999)
    RATE_LIMIT_EXCEEDED = 6000


# Export constants for easy access
__all__ = [
    "AppConstants",
    "DatabaseConstants",
    "SecurityConstants",
    "ApiConstants",
    "CacheConstants",
    "UserRole",
    "BookingStatus",
    "PaymentStatus",
    "FlightClass",
    "Currency",
    "Language",
    "ErrorCodes",
]
