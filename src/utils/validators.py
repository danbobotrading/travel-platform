"""
Data validation utilities for Travel Platform.
Includes validators for travel-related data.
"""
import re
import phonenumbers
from typing import Any, Dict, List, Optional, Tuple, Union
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from email_validator import validate_email, EmailNotValidError
import pytz

from .logger import logger


class TravelValidators:
    """Validators for travel platform data."""
    
    # African country codes
    AFRICAN_COUNTRIES = {
        'ZA': 'South Africa',
        'NG': 'Nigeria', 
        'KE': 'Kenya',
        'GH': 'Ghana',
        'EG': 'Egypt',
        'MA': 'Morocco',
        'TZ': 'Tanzania',
        'ET': 'Ethiopia',
        'UG': 'Uganda',
        'RW': 'Rwandafrican_countries',
    }
    
    # IATA airport codes for major African airports
    AFRICAN_AIRPORTS = {
        'JNB': 'Johannesburg',
        'CPT': 'Cape Town',
        'DUR': 'Durban',
        'LOS': 'Lagos',
        'ABV': 'Abuja',
        'NBO': 'Nairobi',
        'ACC': 'Accra',
        'CAI': 'Cairo',
        'CMN': 'Casablanca',
        'DAR': 'Dar es Salaam',
        'ADD': 'Addis Ababa',
        'EBB': 'Entebbe',
        'KGL': 'Kigali',
    }
    
    @staticmethod
    def validate_email_address(email: str) -> Tuple[bool, str]:
        """Validate email address."""
        try:
            # Validate and normalize email
            email_info = validate_email(email, check_deliverability=False)
            normalized = email_info.normalized
            return True, normalized
        except EmailNotValidError as e:
            return False, str(e)
    
    @staticmethod
    def validate_phone_number(
        phone: str, 
        country_code: str = 'ZA'
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """Validate phone number for African countries."""
        try:
            # Map country codes to phone regions
            region_map = {
                'ZA': 'ZA',  # South Africa
                'NG': 'NG',  # Nigeria
                'KE': 'KE',  # Kenya
                'GH': 'GH',  # Ghana
                'EG': 'EG',  # Egypt
                'MA': 'MA',  # Morocco
            }
            
            region = region_map.get(country_code.upper(), 'ZZ')  # ZZ = international
            
            parsed = phonenumbers.parse(phone, region)
            
            if not phonenumbers.is_valid_number(parsed):
                return False, "Invalid phone number", None
            
            # Format in international format
            formatted = phonenumbers.format_number(
                parsed, 
                phonenumbers.PhoneNumberFormat.INTERNATIONAL
            )
            
            # Extract national number
            national = phonenumbers.format_number(
                parsed,
                phonenumbers.PhoneNumberFormat.NATIONAL
            )
            
            return True, formatted, national
            
        except phonenumbers.NumberParseException as e:
            return False, f"Phone parse error: {e}", None
        except Exception as e:
            return False, f"Validation error: {e}", None
    
    @staticmethod
    def validate_iata_code(code: str, code_type: str = 'airport') -> Tuple[bool, str]:
        """
        Validate IATA airport or airline code.
        
        Args:
            code: IATA code (3 letters)
            code_type: 'airport' or 'airline'
        """
        if not isinstance(code, str):
            return False, "Code must be a string"
        
        code = code.strip().upper()
        
        if len(code) != 3:
            return False, "IATA code must be 3 characters"
        
        if not code.isalpha():
            return False, "IATA code must contain only letters"
        
        if code_type == 'airport':
            if code in TravelValidators.AFRICAN_AIRPORTS:
                return True, TravelValidators.AFRICAN_AIRPORTS[code]
            else:
                # Allow non-African airports too
                return True, "Valid IATA airport code"
        
        elif code_type == 'airline':
            # Basic airline code validation
            return True, "Valid IATA airline code"
        
        return False, f"Unknown code type: {code_type}"
    
    @staticmethod
    def validate_date_range(
        start_date: Union[str, date, datetime],
        end_date: Union[str, date, datetime],
        min_days: int = 1,
        max_days: int = 365
    ) -> Tuple[bool, Optional[str], Optional[int]]:
        """Validate travel date range."""
        try:
            # Parse dates if they're strings
            if isinstance(start_date, str):
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            elif isinstance(start_date, datetime):
                start_date = start_date.date()
            
            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            elif isinstance(end_date, datetime):
                end_date = end_date.date()
            
            # Check if dates are valid
            if not isinstance(start_date, date) or not isinstance(end_date, date):
                return False, "Invalid date format", None
            
            # Check if start date is in the past
            if start_date < date.today():
                return False, "Start date cannot be in the past", None
            
            # Check if end date is after start date
            if end_date <= start_date:
                return False, "End date must be after start date", None
            
            # Calculate duration
            duration = (end_date - start_date).days + 1
            
            # Check duration limits
            if duration < min_days:
                return False, f"Minimum trip duration is {min_days} days", None
            
            if duration > max_days:
                return False, f"Maximum trip duration is {max_days} days", None
            
            return True, None, duration
            
        except ValueError as e:
            return False, f"Date format error: {e}", None
        except Exception as e:
            return False, f"Validation error: {e}", None
    
    @staticmethod
    def validate_passenger_count(
        adults: int = 1,
        children: int = 0,
        infants: int = 0,
        max_passengers: int = 9
    ) -> Tuple[bool, Optional[str], Optional[int]]:
        """Validate passenger counts."""
        # Check minimum values
        if adults < 1:
            return False, "At least one adult is required", None
        
        if children < 0:
            return False, "Children count cannot be negative", None
        
        if infants < 0:
            return False, "Infants count cannot be negative", None
        
        # Check maximum infants per adult
        if infants > adults:
            return False, "Maximum one infant per adult", None
        
        # Check total passengers
        total = adults + children + infants
        
        if total > max_passengers:
            return False, f"Maximum {max_passengers} passengers allowed", None
        
        return True, None, total
    
    @staticmethod
    def validate_currency_amount(
        amount: Union[str, int, float, Decimal],
        min_amount: Union[int, float, Decimal] = 0,
        max_amount: Union[int, float, Decimal] = 1000000
    ) -> Tuple[bool, Optional[str], Optional[Decimal]]:
        """Validate currency amount."""
        try:
            # Convert to Decimal for precise validation
            if not isinstance(amount, Decimal):
                amount_dec = Decimal(str(amount))
            else:
                amount_dec = amount
            
            # Check minimum
            if amount_dec < Decimal(str(min_amount)):
                return False, f"Amount must be at least {min_amount}", None
            
            # Check maximum
            if amount_dec > Decimal(str(max_amount)):
                return False, f"Amount cannot exceed {max_amount}", None
            
            # Check decimal places (max 2 for currency)
            if abs(amount_dec.as_tuple().exponent) > 2:
                return False, "Amount cannot have more than 2 decimal places", None
            
            return True, None, amount_dec
            
        except InvalidOperation:
            return False, "Invalid amount format", None
        except Exception as e:
            return False, f"Validation error: {e}", None
    
    @staticmethod
    def validate_country_code(code: str) -> Tuple[bool, Optional[str]]:
        """Validate country code (ISO 3166-1 alpha-2)."""
        if not isinstance(code, str):
            return False, "Country code must be a string"
        
        code = code.strip().upper()
        
        if len(code) != 2:
            return False, "Country code must be 2 letters"
        
        if not code.isalpha():
            return False, "Country code must contain only letters"
        
        # Check if it's an African country
        if code in TravelValidators.AFRICAN_COUNTRIES:
            return True, TravelValidators.AFRICAN_COUNTRIES[code]
        else:
            # Allow non-African countries too
            return True, "Valid country code"
    
    @staticmethod
    def validate_travel_class(class_code: str) -> Tuple[bool, Optional[str]]:
        """Validate travel class code."""
        valid_classes = {
            'E': 'Economy',
            'PE': 'Premium Economy',
            'B': 'Business',
            'F': 'First'
        }
        
        class_code = class_code.upper()
        
        if class_code in valid_classes:
            return True, valid_classes[class_code]
        else:
            valid_options = ', '.join(valid_classes.keys())
            return False, f"Invalid class. Valid options: {valid_options}"
    
    @staticmethod
    def validate_search_params(params: Dict[str, Any]) -> Tuple[bool, List[str], Dict[str, Any]]:
        """Validate flight/hotel search parameters."""
        errors = []
        validated = {}
        
        # Required fields
        required = ['origin', 'destination', 'departure_date']
        for field in required:
            if field not in params:
                errors.append(f"Missing required field: {field}")
        
        if errors:
            return False, errors, {}
        
        # Validate origin
        origin_valid, origin_msg = TravelValidators.validate_iata_code(params['origin'])
        if not origin_valid:
            errors.append(f"Invalid origin: {origin_msg}")
        else:
            validated['origin'] = params['origin'].upper()
        
        # Validate destination
        dest_valid, dest_msg = TravelValidators.validate_iata_code(params['destination'])
        if not dest_valid:
            errors.append(f"Invalid destination: {dest_msg}")
        else:
            validated['destination'] = params['destination'].upper()
        
        # Validate dates
        departure = params.get('departure_date')
        return_date = params.get('return_date')
        
        if return_date:
            # Round trip
            date_valid, date_msg, duration = TravelValidators.validate_date_range(
                departure, return_date, min_days=1, max_days=365
            )
            if not date_valid:
                errors.append(f"Invalid dates: {date_msg}")
            else:
                validated['departure_date'] = departure
                validated['return_date'] = return_date
                validated['trip_type'] = 'round'
                validated['duration'] = duration
        else:
            # One way
            try:
                dep_date = datetime.strptime(departure, '%Y-%m-%d').date()
                if dep_date < date.today():
                    errors.append("Departure date cannot be in the past")
                else:
                    validated['departure_date'] = departure
                    validated['trip_type'] = 'oneway'
            except ValueError:
                errors.append("Invalid departure date format. Use YYYY-MM-DD")
        
        # Validate passengers
        adults = params.get('adults', 1)
        children = params.get('children', 0)
        infants = params.get('infants', 0)
        
        pax_valid, pax_msg, total = TravelValidators.validate_passenger_count(
            adults, children, infants
        )
        if not pax_valid:
            errors.append(f"Invalid passengers: {pax_msg}")
        else:
            validated['adults'] = adults
            validated['children'] = children
            validated['infants'] = infants
            validated['total_passengers'] = total
        
        # Validate class if provided
        if 'class' in params:
            class_valid, class_msg = TravelValidators.validate_travel_class(params['class'])
            if not class_valid:
                errors.append(f"Invalid class: {class_msg}")
            else:
                validated['class'] = params['class'].upper()
        
        return len(errors) == 0, errors, validated


# Convenience functions
def validate_search_request(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate search request and return standardized response.
    
    Returns:
        Dict with keys: valid, errors, validated_params
    """
    valid, errors, validated = TravelValidators.validate_search_params(params)
    
    return {
        'valid': valid,
        'errors': errors,
        'validated_params': validated if valid else {},
        'timestamp': datetime.utcnow().isoformat()
    }


def validate_user_registration(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate user registration data."""
    errors = []
    validated = {}
    
    # Validate email
    if 'email' in data:
        email_valid, email_msg = TravelValidators.validate_email_address(data['email'])
        if not email_valid:
            errors.append(f"Invalid email: {email_msg}")
        else:
            validated['email'] = email_msg  # normalized email
    
    # Validate phone
    if 'phone' in data:
        country = data.get('country', 'ZA')
        phone_valid, phone_msg, phone_national = TravelValidators.validate_phone_number(
            data['phone'], country
        )
        if not phone_valid:
            errors.append(f"Invalid phone: {phone_msg}")
        else:
            validated['phone'] = phone_msg
            validated['phone_national'] = phone_national
    
    # Validate name
    if 'first_name' in data:
        first_name = data['first_name'].strip()
        if len(first_name) < 2:
            errors.append("First name must be at least 2 characters")
        else:
            validated['first_name'] = first_name
    
    if 'last_name' in data:
        last_name = data['last_name'].strip()
        if len(last_name) < 2:
            errors.append("Last name must be at least 2 characters")
        else:
            validated['last_name'] = last_name
    
    # Validate country
    if 'country' in data:
        country_valid, country_name = TravelValidators.validate_country_code(data['country'])
        if not country_valid:
            errors.append(f"Invalid country: {country_name}")
        else:
            validated['country'] = data['country'].upper()
            validated['country_name'] = country_name
    
    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'validated_data': validated,
        'timestamp': datetime.utcnow().isoformat()
    }


# Test function
def test_validators():
    """Test validation utilities."""
    print("Testing Travel Validators...")
    print("=" * 50)
    
    # Test email validation
    email_valid, email_norm = TravelValidators.validate_email_address("test@example.com")
    print(f"1. Email validation: {'✅' if email_valid else '❌'} {email_norm}")
    
    # Test phone validation
    phone_valid, phone_intl, phone_national = TravelValidators.validate_phone_number(
        "+27123456789", "ZA"
    )
    print(f"2. Phone validation (ZA): {'✅' if phone_valid else '❌'} {phone_intl}")
    
    # Test IATA code validation
    iata_valid, iata_name = TravelValidators.validate_iata_code("JNB")
    print(f"3. IATA code (JNB): {'✅' if iata_valid else '❌'} {iata_name}")
    
    # Test date range validation
    today = date.today()
    future = date(today.year, today.month, today.day + 7)
    date_valid, date_msg, duration = TravelValidators.validate_date_range(
        today.isoformat(), future.isoformat()
    )
    print(f"4. Date range ({duration} days): {'✅' if date_valid else '❌'} {date_msg or 'Valid'}")
    
    # Test passenger validation
    pax_valid, pax_msg, total = TravelValidators.validate_passenger_count(2, 1, 1)
    print(f"5. Passengers (2A,1C,1I): {'✅' if pax_valid else '❌'} Total: {total}")
    
    # Test search params validation
    search_params = {
        'origin': 'JNB',
        'destination': 'CPT',
        'departure_date': future.isoformat(),
        'adults': 2,
        'class': 'E'
    }
    search_valid, search_errors, search_validated = TravelValidators.validate_search_params(search_params)
    print(f"6. Search params: {'✅' if search_valid else '❌'}")
    if search_errors:
        print(f"   Errors: {search_errors}")
    
    print("\n" + "=" * 50)
    print("✅ Validators test complete!")


if __name__ == "__main__":
    test_validators()
