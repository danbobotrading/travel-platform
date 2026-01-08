"""
Currency conversion utilities for Travel Platform.
Focus on African currencies with ZAR as base currency.
"""
import asyncio
import json
from typing import Dict, Optional, Any, Union
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timedelta
from functools import lru_cache
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

try:
    from src.core.config.settings import settings
    from src.utils.logger import logger
except ImportError:
    # Fallback for direct execution
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Create mock settings
    class MockSettings:
        CURRENCY_API_URL = "https://api.exchangerate-api.com/v4/latest/ZAR"
        CURRENCY_API_KEY = None
    
    settings = MockSettings()


class CurrencyConverter:
    """Currency conversion with caching for African currencies."""
    
    # African currencies with their symbols and names
    AFRICAN_CURRENCIES = {
        'ZAR': {'name': 'South African Rand', 'symbol': 'R'},
        'NGN': {'name': 'Nigerian Naira', 'symbol': '₦'},
        'KES': {'name': 'Kenyan Shilling', 'symbol': 'KSh'},
        'GHS': {'name': 'Ghanaian Cedi', 'symbol': 'GH₵'},
        'ETB': {'name': 'Ethiopian Birr', 'symbol': 'Br'},
        'EGP': {'name': 'Egyptian Pound', 'symbol': 'E£'},
        'MAD': {'name': 'Moroccan Dirham', 'symbol': 'DH'},
        'TZS': {'name': 'Tanzanian Shilling', 'symbol': 'TSh'},
        'UGX': {'name': 'Ugandan Shilling', 'symbol': 'USh'},
        'RWF': {'name': 'Rwandan Franc', 'symbol': 'FRw'},
    }
    
    # Fallback exchange rates (updated periodically)
    FALLBACK_RATES = {
        'ZAR': 1.0,
        'NGN': 80.5,   # 1 ZAR = 80.5 NGN
        'KES': 7.2,    # 1 ZAR = 7.2 KES
        'GHS': 0.35,   # 1 ZAR = 0.35 GHS
        'ETB': 3.8,    # 1 ZAR = 3.8 ETB
        'EGP': 1.7,    # 1 ZAR = 1.7 EGP
        'MAD': 0.6,    # 1 ZAR = 0.6 MAD
        'TZS': 165.0,  # 1 ZAR = 165 TZS
        'UGX': 240.0,  # 1 ZAR = 240 UGX
        'RWF': 70.0,   # 1 ZAR = 70 RWF
        'USD': 0.054,  # 1 ZAR = 0.054 USD
        'EUR': 0.049,  # 1 ZAR = 0.049 EUR
        'GBP': 0.042,  # 1 ZAR = 0.042 GBP
    }
    
    def __init__(self):
        self._rates: Dict[str, float] = {}
        self._last_updated: Optional[datetime] = None
        self._cache_ttl = 3600  # 1 hour
        self._http_client: Optional[httpx.AsyncClient] = None
    
    async def _get_http_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(
                timeout=30.0,
                headers={'User-Agent': 'TravelPlatform/1.0'}
            )
        return self._http_client
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def _fetch_exchange_rates(self) -> Dict[str, float]:
        """Fetch exchange rates from API."""
        api_url = getattr(settings, 'CURRENCY_API_URL', None)
        api_key = getattr(settings, 'CURRENCY_API_KEY', None)
        
        if not api_url:
            print("⚠️ Currency API not configured, using fallback rates")
            return self.FALLBACK_RATES.copy()
        
        try:
            client = await self._get_http_client()
            response = await client.get(api_url)
            response.raise_for_status()
            
            data = response.json()
            rates = data.get('rates', {})
            
            # Ensure ZAR is base (rate = 1)
            if 'ZAR' in rates:
                zar_rate = rates['ZAR']
                normalized_rates = {
                    currency: rate / zar_rate
                    for currency, rate in rates.items()
                }
                normalized_rates['ZAR'] = 1.0
                
                # Add any missing African currencies from fallback
                for currency in self.AFRICAN_CURRENCIES:
                    if currency not in normalized_rates and currency in self.FALLBACK_RATES:
                        normalized_rates[currency] = self.FALLBACK_RATES[currency]
                
                print(f"✅ Fetched {len(normalized_rates)} currency rates from API")
                return normalized_rates
            else:
                print("⚠️ API response doesn't contain ZAR, using fallback rates")
                return self.FALLBACK_RATES.copy()
                
        except Exception as e:
            print(f"⚠️ Failed to fetch currency rates: {e}, using fallback")
            return self.FALLBACK_RATES.copy()
    
    async def get_rates(self, force_refresh: bool = False) -> Dict[str, float]:
        """Get exchange rates with caching."""
        now = datetime.utcnow()
        
        if (force_refresh or 
            not self._rates or 
            not self._last_updated or 
            (now - self._last_updated).total_seconds() > self._cache_ttl):
            
            self._rates = await self._fetch_exchange_rates()
            self._last_updated = now
        
        return self._rates.copy()
    
    async def convert(
        self, 
        amount: Union[float, Decimal, int], 
        from_currency: str, 
        to_currency: str,
        decimal_places: int = 2
    ) -> Decimal:
        """Convert amount from one currency to another."""
        # Normalize currency codes
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()
        
        # Get rates
        rates = await self.get_rates()
        
        # Check if currencies are supported
        if from_currency not in rates:
            raise ValueError(f"Unsupported source currency: {from_currency}")
        if to_currency not in rates:
            raise ValueError(f"Unsupported target currency: {to_currency}")
        
        # Convert amount to Decimal for precision
        if not isinstance(amount, Decimal):
            amount = Decimal(str(amount))
        
        # Perform conversion
        from_rate = Decimal(str(rates[from_currency]))
        to_rate = Decimal(str(rates[to_currency]))
        
        # Convert via ZAR (base currency)
        if from_currency != 'ZAR':
            zar_amount = amount / from_rate
        else:
            zar_amount = amount
        
        if to_currency != 'ZAR':
            result = zar_amount * to_rate
        else:
            result = zar_amount
        
        # Round to specified decimal places
        result = result.quantize(
            Decimal('1.' + '0' * decimal_places),
            rounding=ROUND_HALF_UP
        )
        
        return result
    
    async def format_amount(
        self, 
        amount: Union[float, Decimal, int], 
        currency: str
    ) -> str:
        """Format amount with currency symbol."""
        currency = currency.upper()
        
        if currency in self.AFRICAN_CURRENCIES:
            currency_info = self.AFRICAN_CURRENCIES[currency]
            symbol = currency_info['symbol']
            
            # Format based on currency
            if currency in ['ZAR', 'NGN', 'KES', 'GHS', 'ETB', 'EGP', 'TZS', 'UGX', 'RWF']:
                # Use comma as thousand separator for African currencies
                if isinstance(amount, (int, float)):
                    amount_str = f"{amount:,.2f}"
                else:
                    amount_str = f"{amount:,.2f}"
            else:
                amount_str = f"{amount:.2f}"
            
            return f"{symbol} {amount_str}"
        else:
            # Generic format for other currencies
            return f"{currency} {amount:.2f}"
    
    def get_african_currencies(self) -> Dict[str, Dict[str, str]]:
        """Get list of supported African currencies."""
        return self.AFRICAN_CURRENCIES.copy()
    
    async def get_exchange_rate(self, from_currency: str, to_currency: str) -> Decimal:
        """Get direct exchange rate between two currencies."""
        rates = await self.get_rates()
        
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()
        
        if from_currency not in rates or to_currency not in rates:
            raise ValueError(f"Unsupported currency pair: {from_currency}/{to_currency}")
        
        from_rate = Decimal(str(rates[from_currency]))
        to_rate = Decimal(str(rates[to_currency]))
        
        return (to_rate / from_rate).quantize(Decimal('0.00001'))
    
    async def close(self):
        """Clean up resources."""
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None


# Global converter instance
_converter: Optional[CurrencyConverter] = None


async def get_converter() -> CurrencyConverter:
    """Get or create currency converter instance."""
    global _converter
    if _converter is None:
        _converter = CurrencyConverter()
    return _converter


async def convert_currency(
    amount: Union[float, Decimal, int], 
    from_currency: str, 
    to_currency: str,
    decimal_places: int = 2
) -> Decimal:
    """Convert currency (convenience function)."""
    converter = await get_converter()
    return await converter.convert(amount, from_currency, to_currency, decimal_places)


async def format_currency(
    amount: Union[float, Decimal, int], 
    currency: str
) -> str:
    """Format currency amount (convenience function)."""
    converter = await get_converter()
    return await converter.format_amount(amount, currency)


async def cleanup_currency_converter():
    """Cleanup currency converter resources."""
    global _converter
    if _converter:
        await _converter.close()
        _converter = None


# Test function
async def main():
    """Test the currency converter."""
    converter = await get_converter()
    
    print("African Currencies:")
    for code, info in converter.get_african_currencies().items():
        print(f"  {code}: {info['name']} ({info['symbol']})")
    
    print("\nExchange Rates (ZAR based):")
    rates = await converter.get_rates()
    for currency in ['ZAR', 'NGN', 'KES', 'GHS', 'USD']:
        if currency in rates:
            print(f"  1 ZAR = {rates[currency]:.4f} {currency}")
    
    print("\nSample Conversions (1000 ZAR):")
    conversions = [('ZAR', 'NGN'), ('ZAR', 'KES'), ('ZAR', 'GHS'), ('ZAR', 'USD')]
    for from_curr, to_curr in conversions:
        try:
            result = await convert_currency(1000, from_curr, to_curr)
            formatted = await format_currency(result, to_curr)
            print(f"  1000 {from_curr} = {formatted}")
        except Exception as e:
            print(f"  ❌ {from_curr} to {to_curr}: {e}")
    
    await cleanup_currency_converter()


if __name__ == "__main__":
    asyncio.run(main())
