"""
Currency conversion utilities for Travel Platform.
"""

import json
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Optional, Union
from datetime import datetime, timedelta

from src.travel_platform.utils.logger import get_logger
from src.travel_platform.utils.cache import async_cache

logger = get_logger(__name__)


class CurrencyConverter:
    """Simple currency converter with fallback rates."""
    
    # Fallback rates (ZAR as base)
    RATES = {
        'ZAR': 1.0,      # Base
        'NGN': 45.50,    # 1 ZAR = ~45.50 NGN
        'KES': 7.20,     # 1 ZAR = ~7.20 KES  
        'GHS': 0.42,     # 1 ZAR = ~0.42 GHS
        'USD': 0.054,    # 1 ZAR = ~0.054 USD
        'EUR': 0.049,    # 1 ZAR = ~0.049 EUR
    }
    
    @async_cache(ttl=3600)
    async def get_rate(self, from_currency: str, to_currency: str) -> float:
        """Get exchange rate with caching."""
        from_curr = from_currency.upper()
        to_curr = to_currency.upper()
        
        if from_curr not in self.RATES or to_curr not in self.RATES:
            raise ValueError(f"Unsupported currency: {from_curr} or {to_curr}")
        
        if from_curr == to_curr:
            return 1.0
        
        # Convert via ZAR base
        from_rate = self.RATES[from_curr]
        to_rate = self.RATES[to_curr]
        
        return to_rate / from_rate
    
    async def convert(self, amount: Union[float, str], from_currency: str, to_currency: str) -> Decimal:
        """Convert currency amount."""
        rate = await self.get_rate(from_currency, to_currency)
        
        if isinstance(amount, str):
            amount_decimal = Decimal(amount)
        else:
            amount_decimal = Decimal(str(amount))
        
        converted = amount_decimal * Decimal(str(rate))
        
        # Round to 2 decimal places
        return converted.quantize(Decimal('1.00'), rounding=ROUND_HALF_UP)


# Global instance
_converter = CurrencyConverter()


async def convert_currency(amount: Union[float, str], from_currency: str, to_currency: str) -> Decimal:
    """Convert currency."""
    return await _converter.convert(amount, from_currency, to_currency)


def format_currency(amount: Union[float, str, Decimal], currency: str = 'ZAR') -> str:
    """Format currency amount."""
    symbols = {
        'ZAR': 'R', 'NGN': '₦', 'KES': 'KSh', 
        'GHS': 'GH₵', 'USD': '$', 'EUR': '€'
    }
    
    if isinstance(amount, str):
        amount_decimal = Decimal(amount)
    elif isinstance(amount, float):
        amount_decimal = Decimal(str(amount))
    else:
        amount_decimal = amount
    
    symbol = symbols.get(currency.upper(), currency)
    
    # Round and format
    formatted = amount_decimal.quantize(Decimal('1.00'), rounding=ROUND_HALF_UP)
    
    return f"{symbol}{formatted}"
