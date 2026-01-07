"""
Validators for Travel Platform.

This module provides validation functions for various data types,
including emails, phone numbers, passwords, URLs, currencies, and languages.
"""

import re
import phonenumbers
from typing import Any, Dict, List, Optional, Tuple, Union
from urllib.parse import urlparse

import pycountry
from email_validator import validate_email as validate_email_lib, EmailNotValidError
from pydantic import BaseModel, Field, validator

from src.core.exceptions import ValidationError
from src.core.logging import logger


class ValidationErrorDetail(BaseModel):
    """Detailed validation error information."""
    
    field: str = Field(..., description="Field that failed validation")
    value: Any = Field(..., description="Invalid value")
    error: str = Field(..., description="Error message")
    constraint: Optional[str] = Field(None, description="Constraint that was violated")


class ValidationResult(BaseModel):
    """Result of validation operation."""
    
    is_valid: bool = Field(..., description="Whether validation passed")
    errors: List[ValidationErrorDetail] = Field(default_factory=list, description="Validation errors")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")
    
    def add_error(self, field: str, value: Any, error: str, constraint: Optional[str] = None) -> None:
        """Add a validation error."""
        self.errors.append(ValidationErrorDetail(
            field=field,
            value=value,
            error=error,
            constraint=constraint
        ))
        self.is_valid = False
    
    def add_warning(self, warning: str) -> None:
        """Add a validation warning."""
        self.warnings.append(warning)
    
    def raise_if_invalid(self, message: str = "Validation failed") -> None:
        """Raise ValidationError if validation failed."""
        if not self.is_valid:
            raise ValidationError(
                message=message,
                details=[error.dict() for error in self.errors]
            )


def validate_email(email: str, check_deliverability: bool = False) -> Tuple[bool, Optional[str]]:
    """
    Validate email address format and optionally check deliverability.
    
    Args:
        email: Email address to validate
        check_deliverability: Whether to check if domain accepts email
    
    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    try:
        # Validate email using email-validator
        email_info = validate_email_lib(
            email,
            check_deliverability=check_deliverability
        )
        
        # Additional checks for common issues
        normalized_email = email_info.normalized
        
        # Check for disposable email domains
        disposable_domains = [
            "tempmail.com", "mailinator.com", "10minutemail.com",
            "guerrillamail.com", "yopmail.com", "trashmail.com"
        ]
        
        domain = normalized_email.split('@')[1].lower()
        if any(disposable in domain for disposable in disposable_domains):
            return False, "Disposable email addresses are not allowed"
        
        return True, None
        
    except EmailNotValidError as e:
        return False, str(e)
    except Exception as e:
        logger.error(f"Unexpected error during email validation: {e}")
        return False, "Invalid email address"


def validate_phone(phone_number: str, country_code: str = "NG") -> Tuple[bool, Optional[str]]:
    """
    Validate phone number format for a specific country.
    
    Args:
        phone_number: Phone number to validate
        country_code: ISO 3166-1 alpha-2 country code
    
    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    try:
        # Parse phone number
        parsed_number = phonenumbers.parse(phone_number, country_code)
        
        # Check if number is valid
        if not phonenumbers.is_valid_number(parsed_number):
            return False, "Invalid phone number"
        
        # Check if number is possible
        if not phonenumbers.is_possible_number(parsed_number):
            return False, "Impossible phone number"
        
        # Format in E.164 format
        formatted = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
        
        # Additional African country specific checks
        if country_code.upper() == "NG":
            # Nigerian numbers should start with +234
            if not formatted.startswith("+234"):
                return False, "Nigerian numbers must start with +234"
            
            # Nigerian numbers are 13 digits total (+234 followed by 10 digits)
            if len(formatted) != 13:
                return False, "Nigerian numbers must be 13 digits including country code"
        
        elif country_code.upper() == "GH":
            # Ghanaian numbers should start with +233
            if not formatted.startswith("+233"):
                return False, "Ghanaian numbers must start with +233"
        
        elif country_code.upper() == "KE":
            # Kenyan numbers should start with +254
            if not formatted.startswith("+254"):
                return False, "Kenyan numbers must start with +254"
        
        return True, None
        
    except phonenumbers.NumberParseException as e:
        return False, f"Failed to parse phone number: {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error during phone validation: {e}")
        return False, "Invalid phone number"


def validate_password(password: str) -> ValidationResult:
    """
    Validate password strength.
    
    Requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    
    Args:
        password: Password to validate
    
    Returns:
        ValidationResult: Detailed validation result
    """
    result = ValidationResult(is_valid=True)
    
    # Check minimum length
    if len(password) < 8:
        result.add_error(
            field="password",
            value=password,
            error="Password must be at least 8 characters long",
            constraint="min_length=8"
        )
    
    # Check for uppercase letters
    if not re.search(r"[A-Z]", password):
        result.add_error(
            field="password",
            value="[REDACTED]",
            error="Password must contain at least one uppercase letter",
            constraint="has_uppercase"
        )
    
    # Check for lowercase letters
    if not re.search(r"[a-z]", password):
        result.add_error(
            field="password",
            value="[REDACTED]",
            error="Password must contain at least one lowercase letter",
            constraint="has_lowercase"
        )
    
    # Check for digits
    if not re.search(r"\d", password):
        result.add_error(
            field="password",
            value="[REDACTED]",
            error="Password must contain at least one digit",
            constraint="has_digit"
        )
    
    # Check for special characters
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        result.add_error(
            field="password",
            value="[REDACTED]",
            error="Password must contain at least one special character",
            constraint="has_special"
        )
    
    # Check for common weak passwords
    weak_passwords = [
        "password", "12345678", "qwertyui", "admin123",
        "welcome1", "password1", "abcdefgh", "11111111"
    ]
    
    if password.lower() in weak_passwords:
        result.add_error(
            field="password",
            value="[REDACTED]",
            error="Password is too common or weak",
            constraint="not_common"
        )
    
    # Check for sequential characters
    if re.search(r"(.)\1{2,}", password):
        result.add_warning("Password contains repeated characters")
    
    # Check for sequential numbers/letters
    sequential_patterns = [
        "0123456789", "1234567890", "abcdefgh", "qwertyui",
        "asdfghjk", "zxcvbnm", "987654321", "0987654321"
    ]
    
    for pattern in sequential_patterns:
        if pattern in password.lower():
            result.add_warning("Password contains sequential characters")
            break
    
    return result


def validate_url(url: str, allowed_schemes: Optional[List[str]] = None) -> Tuple[bool, Optional[str]]:
    """
    Validate URL format and scheme.
    
    Args:
        url: URL to validate
        allowed_schemes: List of allowed URL schemes (default: ['http', 'https'])
    
    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    if allowed_schemes is None:
        allowed_schemes = ["http", "https"]
    
    try:
        # Parse URL
        parsed = urlparse(url)
        
        # Check scheme
        if parsed.scheme not in allowed_schemes:
            return False, f"URL scheme must be one of: {', '.join(allowed_schemes)}"
        
        # Check netloc (domain)
        if not parsed.netloc:
            return False, "URL must have a domain"
        
        # Check for basic domain format
        if not re.match(r"^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", parsed.netloc):
            return False, "Invalid domain format"
        
        # Additional security checks
        # Prevent potential SSRF attacks
        local_netlocs = ["localhost", "127.0.0.1", "0.0.0.0", "::1"]
        if parsed.netloc.split(':')[0] in local_netlocs:
            return False, "Localhost URLs are not allowed"
        
        # Check for suspicious patterns
        suspicious_patterns = [
            r"@",  # Userinfo in URL
            r"//{2,}",  # Multiple slashes
            r"\.\.",  # Directory traversal
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, url):
                return False, "Suspicious URL pattern detected"
        
        return True, None
        
    except Exception as e:
        logger.error(f"Unexpected error during URL validation: {e}")
        return False, "Invalid URL format"


def validate_currency(currency_code: str) -> Tuple[bool, Optional[str]]:
    """
    Validate currency code (ISO 4217).
    
    Args:
        currency_code: Currency code to validate
    
    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    try:
        # Check if it's a valid ISO 4217 currency
        currency = pycountry.currencies.get(alpha_3=currency_code.upper())
        
        if not currency:
            return False, f"Invalid currency code: {currency_code}"
        
        # Additional checks for supported currencies
        supported_currencies = ["NGN", "GHS", "KES", "ZAR", "USD", "EUR", "GBP"]
        
        if currency_code.upper() not in supported_currencies:
            return False, f"Currency not supported: {currency_code}. Supported: {', '.join(supported_currencies)}"
        
        return True, None
        
    except Exception as e:
        logger.error(f"Unexpected error during currency validation: {e}")
        return False, "Invalid currency code"


def validate_language(language_code: str) -> Tuple[bool, Optional[str]]:
    """
    Validate language code (ISO 639-1).
    
    Args:
        language_code: Language code to validate
    
    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    try:
        # Check if it's a valid ISO 639-1 language
        language = pycountry.languages.get(alpha_2=language_code.lower())
        
        if not language:
            # Try alpha_3
            language = pycountry.languages.get(alpha_3=language_code.lower())
        
        if not language:
            return False, f"Invalid language code: {language_code}"
        
        # Additional checks for supported languages
        supported_languages = ["en", "fr", "ar", "sw", "pt", "ha"]
        
        if language_code.lower() not in supported_languages:
            return False, f"Language not supported: {language_code}. Supported: {', '.join(supported_languages)}"
        
        return True, None
        
    except Exception as e:
        logger.error(f"Unexpected error during language validation: {e}")
        return False, "Invalid language code"


def validate_country(country_code: str) -> Tuple[bool, Optional[str]]:
    """
    Validate country code (ISO 3166-1 alpha-2).
    
    Args:
        country_code: Country code to validate
    
    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    try:
        country = pycountry.countries.get(alpha_2=country_code.upper())
        
        if not country:
            return False, f"Invalid country code: {country_code}"
        
        # Focus on African countries
        african_countries = [
            "NG", "GH", "KE", "ZA", "EG", "MA", "TN", "DZ",
            "CI", "SN", "CM", "UG", "TZ", "ET", "RW", "BW",
            "NA", "ZM", "ZW", "MW", "MZ", "AO", "CD", "GA",
            "CG", "GN", "ML", "BF", "NE", "TD", "SD", "ER",
            "DJ", "SO", "BI", "RW", "SS", "LR", "SL", "GM",
            "GW", "MR", "ST", "SC", "CV", "KM", "MU", "RE",
            "YT", "SH", "IO", "TF", "EH"
        ]
        
        if country_code.upper() not in african_countries:
            return False, f"Non-African country: {country_code}. This platform focuses on African countries."
        
        return True, None
        
    except Exception as e:
        logger.error(f"Unexpected error during country validation: {e}")
        return False, "Invalid country code"


def validate_airport_code(airport_code: str) -> Tuple[bool, Optional[str]]:
    """
    Validate airport IATA code.
    
    Args:
        airport_code: Airport IATA code to validate
    
    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    # Basic format check (3 uppercase letters)
    if not re.match(r"^[A-Z]{3}$", airport_code):
        return False, "Airport code must be 3 uppercase letters"
    
    # List of major African airports
    african_airports = [
        "LOS", "ABV", "ACC", "KAN", "PHC", "QUO", "ENU", "CBQ",
        "IBA", "ILR", "JOS", "KAD", "MDI", "MIU", "MXJ", "PHC",
        "QOW", "QRW", "TIN", "YOL", "ADD", "BJL", "BKO", "BZV",
        "CIP", "CMN", "CPT", "DAR", "DKR", "DLA", "EBB", "FIH",
        "JNB", "KGL", "KRT", "LAD", "LUN", "MPM", "NBO", "NDJ",
        "NIM", "OUA", "ROB", "TUN", "WDH", "WVB"
    ]
    
    if airport_code not in african_airports:
        return False, f"Unsupported airport: {airport_code}"
    
    return True, None


def validate_date_range(start_date: str, end_date: str) -> Tuple[bool, Optional[str]]:
    """
    Validate date range (end date must be after start date).
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    
    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    try:
        from datetime import datetime
        
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        if end <= start:
            return False, "End date must be after start date"
        
        # Maximum range: 1 year
        max_range = 365
        if (end - start).days > max_range:
            return False, f"Date range cannot exceed {max_range} days"
        
        return True, None
        
    except ValueError as e:
        return False, f"Invalid date format: {str(e)}. Use YYYY-MM-DD."
    except Exception as e:
        logger.error(f"Unexpected error during date range validation: {e}")
        return False, "Invalid date range"


class ValidatorRegistry:
    """Registry for custom validators."""
    
    def __init__(self):
        self._validators: Dict[str, callable] = {}
        self._register_builtin_validators()
    
    def _register_builtin_validators(self) -> None:
        """Register built-in validators."""
        self.register("email", validate_email)
        self.register("phone", validate_phone)
        self.register("password", validate_password)
        self.register("url", validate_url)
        self.register("currency", validate_currency)
        self.register("language", validate_language)
        self.register("country", validate_country)
        self.register("airport_code", validate_airport_code)
        self.register("date_range", validate_date_range)
    
    def register(self, name: str, validator_func: callable) -> None:
        """
        Register a custom validator.
        
        Args:
            name: Validator name
            validator_func: Validator function
        
        Raises:
            ValueError: If validator with same name already exists
        """
        if name in self._validators:
            raise ValueError(f"Validator '{name}' already registered")
        self._validators[name] = validator_func
    
    def get(self, name: str) -> Optional[callable]:
        """
        Get validator by name.
        
        Args:
            name: Validator name
        
        Returns:
            Optional[callable]: Validator function or None if not found
        """
        return self._validators.get(name)
    
    def validate(self, name: str, *args, **kwargs) -> Any:
        """
        Execute validator by name.
        
        Args:
            name: Validator name
            *args: Validator arguments
            **kwargs: Validator keyword arguments
        
        Returns:
            Any: Validator result
        
        Raises:
            KeyError: If validator not found
        """
        validator_func = self.get(name)
        if not validator_func:
            raise KeyError(f"Validator '{name}' not found")
        return validator_func(*args, **kwargs)
    
    def list_validators(self) -> List[str]:
        """
        List all registered validators.
        
        Returns:
            List[str]: List of validator names
        """
        return list(self._validators.keys())


# Global validator registry instance
validator_registry = ValidatorRegistry()
