"""
Date and time helpers for Travel Platform.
Focus on African travel patterns, weekends, and holidays.
"""
import re
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple, Union
from dateutil.relativedelta import relativedelta
import pytz
from enum import Enum


class DayOfWeek(Enum):
    """Days of the week."""
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


class AfricanTimezone(Enum):
    """Major African timezones."""
    # Southern Africa
    SOUTH_AFRICA = "Africa/Johannesburg"
    NAMIBIA = "Africa/Windhoek"
    MOZAMBIQUE = "Africa/Maputo"
    ZIMBABWE = "Africa/Harare"
    ZAMBIA = "Africa/Lusaka"
    
    # East Africa
    KENYA = "Africa/Nairobi"
    TANZANIA = "Africa/Dar_es_Salaam"
    UGANDA = "Africa/Kampala"
    RWANDA = "Africa/Kigali"
    ETHIOPIA = "Africa/Addis_Ababa"
    
    # West Africa
    NIGERIA = "Africa/Lagos"
    GHANA = "Africa/Accra"
    SENEGAL = "Africa/Dakar"
    IVORY_COAST = "Africa/Abidjan"
    
    # North Africa
    EGYPT = "Africa/Cairo"
    MOROCCO = "Africa/Casablanca"
    TUNISIA = "Africa/Tunis"
    ALGERIA = "Africa/Algiers"


class TravelDateHelper:
    """Helper for travel-related date operations in Africa."""
    
    # African public holidays (common across multiple countries)
    # Note: Some holidays are based on lunar calendar and vary each year
    COMMON_HOLIDAYS = {
        "01-01": "New Year's Day",
        "05-01": "Workers' Day",
        "12-25": "Christmas Day",
        "12-26": "Boxing Day",
    }
    
    # Country-specific major holidays (fixed dates)
    COUNTRY_HOLIDAYS = {
        "ZA": {  # South Africa
            "03-21": "Human Rights Day",
            "04-27": "Freedom Day",
            "05-01": "Workers' Day",
            "06-16": "Youth Day",
            "08-09": "National Women's Day",
            "09-24": "Heritage Day",
            "12-16": "Day of Reconciliation",
        },
        "NG": {  # Nigeria
            "01-01": "New Year's Day",
            "05-01": "Workers' Day",
            "05-27": "Children's Day",
            "06-12": "Democracy Day",
            "10-01": "Independence Day",
            "12-25": "Christmas Day",
            "12-26": "Boxing Day",
        },
        "KE": {  # Kenya
            "01-01": "New Year's Day",
            "05-01": "Labour Day",
            "06-01": "Madaraka Day",
            "10-10": "Mashujaa Day",
            "10-20": "Kenyatta Day",
            "12-12": "Jamhuri Day",
            "12-25": "Christmas Day",
            "12-26": "Boxing Day",
        },
        "GH": {  # Ghana
            "01-01": "New Year's Day",
            "03-06": "Independence Day",
            "05-01": "Workers' Day",
            "07-01": "Republic Day",
            "12-25": "Christmas Day",
            "12-26": "Boxing Day",
        },
    }
    
    # Peak travel seasons in Africa (approximate)
    PEAK_SEASONS = {
        "summer": {
            "name": "Summer Holidays",
            "months": [11, 12, 1],  # Nov, Dec, Jan
            "description": "Major holiday season with high travel demand"
        },
        "easter": {
            "name": "Easter Period",
            "months": [3, 4],  # March, April
            "description": "Easter holidays and school breaks"
        },
        "winter": {
            "name": "Winter Breaks",
            "months": [6, 7],  # June, July
            "description": "Mid-year school holidays"
        }
    }
    
    @staticmethod
    def get_african_timezone(country_code: str = "ZA") -> pytz.timezone:
        """Get timezone for African country."""
        timezone_map = {
            "ZA": AfricanTimezone.SOUTH_AFRICA.value,
            "NG": AfricanTimezone.NIGERIA.value,
            "KE": AfricanTimezone.KENYA.value,
            "GH": AfricanTimezone.GHANA.value,
            "EG": AfricanTimezone.EGYPT.value,
            "MA": AfricanTimezone.MOROCCO.value,
            "TZ": AfricanTimezone.TANZANIA.value,
            "ET": AfricanTimezone.ETHIOPIA.value,
            "UG": AfricanTimezone.UGANDA.value,
            "RW": AfricanTimezone.RWANDA.value,
        }
        
        tz_name = timezone_map.get(country_code.upper(), AfricanTimezone.SOUTH_AFRICA.value)
        return pytz.timezone(tz_name)
    
    @staticmethod
    def now_in_africa(country_code: str = "ZA") -> datetime:
        """Get current datetime in African timezone."""
        tz = TravelDateHelper.get_african_timezone(country_code)
        return datetime.now(tz)
    
    @staticmethod
    def is_weekend(target_date: Union[date, datetime]) -> bool:
        """Check if date is weekend (Friday afternoon to Sunday)."""
        if isinstance(target_date, datetime):
            day_of_week = target_date.weekday()
            # In many African countries, weekend starts Friday afternoon
            is_friday_afternoon = (day_of_week == 4 and target_date.hour >= 12)
            return day_of_week >= 5 or is_friday_afternoon
        else:
            return target_date.weekday() >= 5
    
    @staticmethod
    def is_public_holiday(target_date: Union[date, datetime], country_code: str = "ZA") -> bool:
        """Check if date is a public holiday in the specified country."""
        if isinstance(target_date, datetime):
            check_date = target_date.date()
        else:
            check_date = target_date
        
        date_str = check_date.strftime("%m-%d")
        
        # Check common holidays
        if date_str in TravelDateHelper.COMMON_HOLIDAYS:
            return True
        
        # Check country-specific holidays
        country_holidays = TravelDateHelper.COUNTRY_HOLIDAYS.get(country_code.upper(), {})
        if date_str in country_holidays:
            return True
        
        return False
    
    @staticmethod
    def is_peak_travel_season(target_date: Union[date, datetime]) -> bool:
        """Check if date falls within peak travel season."""
        if isinstance(target_date, datetime):
            month = target_date.month
        else:
            month = target_date.month
        
        for season in TravelDateHelper.PEAK_SEASONS.values():
            if month in season["months"]:
                return True
        
        return False
    
    @staticmethod
    def calculate_travel_periods(
        start_date: Union[date, datetime],
        end_date: Union[date, datetime],
        country_code: str = "ZA"
    ) -> Dict[str, int]:
        """Calculate various travel period metrics."""
        if isinstance(start_date, datetime):
            start_date = start_date.date()
        if isinstance(end_date, datetime):
            end_date = end_date.date()
        
        total_days = (end_date - start_date).days + 1
        weekdays = 0
        weekends = 0
        holidays = 0
        peak_days = 0
        
        current_date = start_date
        while current_date <= end_date:
            if TravelDateHelper.is_weekend(current_date):
                weekends += 1
            else:
                weekdays += 1
            
            if TravelDateHelper.is_public_holiday(current_date, country_code):
                holidays += 1
            
            if TravelDateHelper.is_peak_travel_season(current_date):
                peak_days += 1
            
            current_date += timedelta(days=1)
        
        return {
            "total_days": total_days,
            "weekdays": weekdays,
            "weekends": weekends,
            "holidays": holidays,
            "peak_days": peak_days,
            "business_days": weekdays - holidays,
        }
    
    @staticmethod
    def suggest_travel_dates(
        desired_departure: date,
        trip_duration: int,
        country_code: str = "ZA",
        avoid_weekends: bool = True,
        avoid_holidays: bool = True,
        max_adjustment_days: int = 7
    ) -> Dict[str, date]:
        """Suggest optimal travel dates considering weekends and holidays."""
        best_departure = desired_departure
        best_score = float('inf')
        
        # Try different departure dates within adjustment window
        for adjustment in range(-max_adjustment_days, max_adjustment_days + 1):
            test_departure = desired_departure + timedelta(days=adjustment)
            test_return = test_departure + timedelta(days=trip_duration - 1)
            
            # Calculate penalty score
            penalty = 0
            
            if avoid_weekends and TravelDateHelper.is_weekend(test_departure):
                penalty += 5
            
            if avoid_holidays and TravelDateHelper.is_public_holiday(test_departure, country_code):
                penalty += 10
            
            if avoid_holidays and TravelDateHelper.is_public_holiday(test_return, country_code):
                penalty += 10
            
            # Add adjustment penalty (prefer closer to desired date)
            penalty += abs(adjustment) * 0.5
            
            # Check middle of trip for weekends/holidays
            current = test_departure
            while current <= test_return:
                if avoid_weekends and TravelDateHelper.is_weekend(current):
                    penalty += 1
                if avoid_holidays and TravelDateHelper.is_public_holiday(current, country_code):
                    penalty += 2
                current += timedelta(days=1)
            
            if penalty < best_score:
                best_score = penalty
                best_departure = test_departure
        
        best_return = best_departure + timedelta(days=trip_duration - 1)
        
        return {
            "departure_date": best_departure,
            "return_date": best_return,
            "adjustment_days": (best_departure - desired_departure).days,
            "score": best_score,
        }
    
    @staticmethod
    def format_travel_date(
        date_obj: Union[date, datetime],
        country_code: str = "ZA",
        include_time: bool = False
    ) -> str:
        """Format date for display in local format."""
        # Common African date formats
        formats = {
            "ZA": "%d/%m/%Y",  # South Africa: DD/MM/YYYY
            "NG": "%d/%m/%Y",  # Nigeria: DD/MM/YYYY
            "KE": "%d/%m/%Y",  # Kenya: DD/MM/YYYY
            "GH": "%d/%m/%Y",  # Ghana: DD/MM/YYYY
            "EG": "%d/%m/%Y",  # Egypt: DD/MM/YYYY
            "MA": "%d/%m/%Y",  # Morocco: DD/MM/YYYY
        }
        
        date_format = formats.get(country_code.upper(), "%Y-%m-%d")
        
        if include_time and isinstance(date_obj, datetime):
            date_format += " %H:%M"
        
        if isinstance(date_obj, datetime):
            return date_obj.strftime(date_format)
        else:
            return date_obj.strftime(date_format)
    
    @staticmethod
    def parse_travel_date(
        date_str: str,
        country_code: str = "ZA"
    ) -> date:
        """Parse date string in local format."""
        # Try common formats
        formats = [
            "%d/%m/%Y",  # DD/MM/YYYY
            "%Y-%m-%d",  # YYYY-MM-DD
            "%d-%m-%Y",  # DD-MM-YYYY
            "%m/%d/%Y",  # MM/DD/YYYY (American)
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        
        raise ValueError(f"Could not parse date: {date_str}")
    
    @staticmethod
    def get_next_business_day(
        from_date: Union[date, datetime],
        country_code: str = "ZA"
    ) -> date:
        """Get the next business day (not weekend or holiday)."""
        if isinstance(from_date, datetime):
            current = from_date.date()
        else:
            current = from_date
        
        while True:
            current += timedelta(days=1)
            if (not TravelDateHelper.is_weekend(current) and 
                not TravelDateHelper.is_public_holiday(current, country_code)):
                return current
    
    @staticmethod
    def get_peak_season_info(target_date: Union[date, datetime]) -> Optional[Dict]:
        """Get peak season information for a date."""
        if isinstance(target_date, datetime):
            month = target_date.month
        else:
            month = target_date.month
        
        for season_name, season_info in TravelDateHelper.PEAK_SEASONS.items():
            if month in season_info["months"]:
                return {
                    "name": season_info["name"],
                    "description": season_info["description"],
                    "season": season_name,
                }
        
        return None


# Convenience functions
def is_travel_date_optimal(
    date_obj: Union[date, datetime],
    country_code: str = "ZA"
) -> bool:
    """Check if a date is optimal for travel (not weekend, holiday, or peak)."""
    return (not TravelDateHelper.is_weekend(date_obj) and
            not TravelDateHelper.is_public_holiday(date_obj, country_code) and
            not TravelDateHelper.is_peak_travel_season(date_obj))


def calculate_trip_price_multiplier(
    start_date: date,
    end_date: date,
    country_code: str = "ZA"
) -> float:
    """Calculate price multiplier based on travel dates."""
    periods = TravelDateHelper.calculate_travel_periods(start_date, end_date, country_code)
    
    base_multiplier = 1.0
    
    # Weekend surcharge
    if periods["weekends"] > 0:
        base_multiplier += periods["weekends"] * 0.1
    
    # Holiday surcharge
    if periods["holidays"] > 0:
        base_multiplier += periods["holidays"] * 0.2
    
    # Peak season surcharge
    if periods["peak_days"] > 0:
        base_multiplier += periods["peak_days"] * 0.15
    
    return round(base_multiplier, 2)


def get_african_timezones() -> List[Dict[str, str]]:
    """Get list of all African timezones."""
    return [
        {"code": tz.name, "value": tz.value, "name": tz.name.replace("_", " ").title()}
        for tz in AfricanTimezone
    ]


# Test function
def test_date_helpers():
    """Test the date helpers."""
    print("Testing Travel Date Helpers...")
    print("=" * 50)
    
    today = date.today()
    tomorrow = today + timedelta(days=1)
    
    print(f"Today: {TravelDateHelper.format_travel_date(today, 'ZA')}")
    print(f"Is weekend: {TravelDateHelper.is_weekend(today)}")
    print(f"Is public holiday (ZA): {TravelDateHelper.is_public_holiday(today, 'ZA')}")
    print(f"Is peak season: {TravelDateHelper.is_peak_travel_season(today)}")
    
    print(f"\nNow in Johannesburg: {TravelDateHelper.now_in_africa('ZA')}")
    print(f"Now in Lagos: {TravelDateHelper.now_in_africa('NG')}")
    print(f"Now in Nairobi: {TravelDateHelper.now_in_africa('KE')}")
    
    # Test travel period calculation
    start_date = today
    end_date = today + timedelta(days=10)
    periods = TravelDateHelper.calculate_travel_periods(start_date, end_date, 'ZA')
    print(f"\nTravel period {start_date} to {end_date}:")
    for key, value in periods.items():
        print(f"  {key}: {value}")
    
    # Test date suggestion
    suggestion = TravelDateHelper.suggest_travel_dates(
        desired_departure=today,
        trip_duration=7,
        country_code='ZA',
        avoid_weekends=True,
        avoid_holidays=True
    )
    print(f"\nSuggested travel dates:")
    print(f"  Depart: {suggestion['departure_date']}")
    print(f"  Return: {suggestion['return_date']}")
    print(f"  Adjustment: {suggestion['adjustment_days']} days")
    
    # Test price multiplier
    multiplier = calculate_trip_price_multiplier(start_date, end_date, 'ZA')
    print(f"\nPrice multiplier: {multiplier}x")
    
    print("\n" + "=" * 50)
    print("✅ Date helpers test completed!")


if __name__ == "__main__":
    test_date_helpers()
