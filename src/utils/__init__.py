"""
Utilities module for Travel Platform.
"""
from .logger import (
    logger,
    get_logger,
    TravelPlatformLogger,
    log_request,
    log_response,
    log_error,
    log_user_action
)

from .currency_simple import (
    SimpleCurrencyConverter as CurrencyConverter,
    converter
)

from .date_helpers import (
    TravelDateHelper,
    calculate_trip_price_multiplier,
    get_african_timezones,
    is_travel_date_optimal
)

from .cache import (
    RedisCache,
    get_cache,
    cached,
    invalidate_cache,
    CacheManager,
    cleanup_cache
)

from .validators import (
    TravelValidators,
    validate_search_request,
    validate_user_registration
)

from .security import (
    SecurityUtils,
    SecurityMiddleware,
    generate_secure_password,
    hash_api_key,
    verify_api_key
)

__all__ = [
    # Logger
    'logger',
    'get_logger',
    'TravelPlatformLogger',
    'log_request',
    'log_response',
    'log_error',
    'log_user_action',
    
    # Currency
    'CurrencyConverter',
    'converter',
    
    # Date helpers
    'TravelDateHelper',
    'calculate_trip_price_multiplier',
    'get_african_timezones',
    'is_travel_date_optimal',
    
    # Cache
    'RedisCache',
    'get_cache',
    'cached',
    'invalidate_cache',
    'CacheManager',
    'cleanup_cache',
    
    # Validators
    'TravelValidators',
    'validate_search_request',
    'validate_user_registration',
    
    # Security
    'SecurityUtils',
    'SecurityMiddleware',
    'generate_secure_password',
    'hash_api_key',
    'verify_api_key',
]
