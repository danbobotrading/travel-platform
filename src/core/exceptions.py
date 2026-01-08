"""
Custom exceptions for Travel Platform.
"""
from typing import Optional, Any, Dict


class TravelPlatformError(Exception):
    """Base exception for Travel Platform."""
    
    def __init__(
        self, 
        message: str = "An error occurred",
        code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 500
    ):
        self.message = message
        self.code = code
        self.details = details or {}
        self.status_code = status_code
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses."""
        return {
            "error": True,
            "code": self.code,
            "message": self.message,
            "details": self.details,
            "status_code": self.status_code
        }


# Database exceptions
class DatabaseError(TravelPlatformError):
    """Database-related errors."""
    
    def __init__(self, message: str = "Database error", details: Optional[Dict] = None):
        super().__init__(message, "DATABASE_ERROR", details, 500)


class RecordNotFoundError(DatabaseError):
    """Record not found in database."""
    
    def __init__(self, model: str = "record", identifier: Any = None):
        message = f"{model} not found"
        if identifier:
            message += f" with identifier: {identifier}"
        super().__init__(message, "RECORD_NOT_FOUND", {"model": model, "identifier": identifier}, 404)


class DuplicateRecordError(DatabaseError):
    """Duplicate record error."""
    
    def __init__(self, model: str = "record", field: str = None, value: Any = None):
        message = f"Duplicate {model}"
        if field and value:
            message += f" with {field}={value}"
        super().__init__(message, "DUPLICATE_RECORD", {"model": model, "field": field, "value": value}, 409)


# Validation exceptions
class ValidationError(TravelPlatformError):
    """Validation errors."""
    
    def __init__(self, message: str = "Validation failed", errors: Optional[list] = None):
        super().__init__(message, "VALIDATION_ERROR", {"errors": errors or []}, 400)


class InvalidInputError(ValidationError):
    """Invalid input data."""
    
    def __init__(self, field: str = None, message: str = "Invalid input"):
        if field:
            message = f"Invalid {field}: {message}"
        super().__init__(message, "INVALID_INPUT", {"field": field}, 400)


class MissingFieldError(ValidationError):
    """Required field missing."""
    
    def __init__(self, field: str):
        message = f"Missing required field: {field}"
        super().__init__(message, "MISSING_FIELD", {"field": field}, 400)


# Authentication & Authorization exceptions
class AuthenticationError(TravelPlatformError):
    """Authentication errors."""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, "AUTHENTICATION_ERROR", {}, 401)


class InvalidCredentialsError(AuthenticationError):
    """Invalid credentials error."""
    
    def __init__(self, message: str = "Invalid credentials"):
        super().__init__(message, "INVALID_CREDENTIALS", {}, 401)


class TokenExpiredError(AuthenticationError):
    """Token expired error."""
    
    def __init__(self, message: str = "Token has expired"):
        super().__init__(message, "TOKEN_EXPIRED", {}, 401)


class InvalidTokenError(AuthenticationError):
    """Invalid token error."""
    
    def __init__(self, message: str = "Invalid token"):
        super().__init__(message, "INVALID_TOKEN", {}, 401)


class AuthorizationError(TravelPlatformError):
    """Authorization errors."""
    
    def __init__(self, message: str = "Not authorized"):
        super().__init__(message, "AUTHORIZATION_ERROR", {}, 403)


class InsufficientPermissionsError(AuthorizationError):
    """Insufficient permissions error."""
    
    def __init__(self, required_permission: str = None):
        message = "Insufficient permissions"
        if required_permission:
            message += f": {required_permission}"
        super().__init__(message, "INSUFFICIENT_PERMISSIONS", {"required_permission": required_permission}, 403)


# Business logic exceptions
class BusinessLogicError(TravelPlatformError):
    """Business logic errors."""
    
    def __init__(self, message: str = "Business rule violation"):
        super().__init__(message, "BUSINESS_LOGIC_ERROR", {}, 400)


class PaymentError(BusinessLogicError):
    """Payment processing errors."""
    
    def __init__(self, message: str = "Payment failed", details: Optional[Dict] = None):
        super().__init__(message, "PAYMENT_ERROR", details, 400)


class InsufficientFundsError(PaymentError):
    """Insufficient funds error."""
    
    def __init__(self, message: str = "Insufficient funds"):
        super().__init__(message, "INSUFFICIENT_FUNDS", {}, 400)


class BookingError(BusinessLogicError):
    """Booking-related errors."""
    
    def __init__(self, message: str = "Booking failed", details: Optional[Dict] = None):
        super().__init__(message, "BOOKING_ERROR", details, 400)


class NoAvailabilityError(BookingError):
    """No availability error."""
    
    def __init__(self, resource: str = "resource", date: str = None):
        message = f"No {resource} available"
        if date:
            message += f" for {date}"
        super().__init__(message, "NO_AVAILABILITY", {"resource": resource, "date": date}, 400)


# External service exceptions
class ExternalServiceError(TravelPlatformError):
    """External service errors."""
    
    def __init__(self, service: str = "external", message: str = "Service error", details: Optional[Dict] = None):
        full_message = f"{service} service error: {message}"
        super().__init__(full_message, "EXTERNAL_SERVICE_ERROR", details, 502)


class APIRateLimitError(ExternalServiceError):
    """API rate limit error."""
    
    def __init__(self, service: str = "API", retry_after: int = None):
        message = f"{service} rate limit exceeded"
        details = {"retry_after": retry_after} if retry_after else {}
        super().__init__(service, message, details, 429)


class ServiceTimeoutError(ExternalServiceError):
    """Service timeout error."""
    
    def __init__(self, service: str = "external", timeout: int = None):
        message = f"{service} service timeout"
        details = {"timeout": timeout} if timeout else {}
        super().__init__(service, message, details, 504)


# Cache exceptions
class CacheError(TravelPlatformError):
    """Cache-related errors."""
    
    def __init__(self, message: str = "Cache error"):
        super().__init__(message, "CACHE_ERROR", {}, 500)


class CacheMissError(CacheError):
    """Cache miss error."""
    
    def __init__(self, key: str = None):
        message = "Cache miss"
        if key:
            message += f" for key: {key}"
        super().__init__(message, "CACHE_MISS", {"key": key}, 404)


# Utility functions
def handle_exception(error: Exception) -> TravelPlatformError:
    """Convert generic exceptions to TravelPlatformError."""
    if isinstance(error, TravelPlatformError):
        return error
    
    # Convert common exceptions
    if isinstance(error, ValueError):
        return ValidationError(str(error))
    elif isinstance(error, KeyError):
        return MissingFieldError(str(error))
    elif isinstance(error, PermissionError):
        return AuthorizationError(str(error))
    elif isinstance(error, TimeoutError):
        return ServiceTimeoutError("operation", details={"error": str(error)})
    
    # Generic error
    return TravelPlatformError(
        message=str(error) or "An unexpected error occurred",
        details={"original_error": type(error).__name__}
    )


def error_response(error: TravelPlatformError) -> Dict[str, Any]:
    """Create standardized error response."""
    return error.to_dict()


# Test function
def test_exceptions():
    """Test custom exceptions."""
    print("Testing Custom Exceptions...")
    print("=" * 50)
    
    # Test base exception
    try:
        raise TravelPlatformError("Test error", "TEST_ERROR", {"test": True}, 400)
    except TravelPlatformError as e:
        print(f"1. Base exception: ✅ Code: {e.code}, Status: {e.status_code}")
    
    # Test validation error
    try:
        raise ValidationError("Invalid data", ["field1 is required", "field2 must be email"])
    except ValidationError as e:
        print(f"2. Validation error: ✅ {len(e.details['errors'])} errors")
    
    # Test authentication error
    try:
        raise InvalidCredentialsError("Wrong password")
    except InvalidCredentialsError as e:
        print(f"3. Auth error: ✅ {e.message}")
    
    # Test business logic error
    try:
        raise NoAvailabilityError("hotel", "2024-01-15")
    except NoAvailabilityError as e:
        print(f"4. Business error: ✅ {e.message}")
    
    # Test conversion
    try:
        raise ValueError("Test value error")
    except ValueError as e:
        converted = handle_exception(e)
        print(f"5. Exception conversion: ✅ {type(converted).__name__}")
    
    print("\n" + "=" * 50)
    print("✅ Exceptions test complete!")
