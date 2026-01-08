"""
Simplified currency converter for testing.
"""
from typing import Dict, Optional
from datetime import datetime


class SimpleCurrencyConverter:
    """Simple currency converter without network dependencies."""
    
    AFRICAN_CURRENCIES = {
        'ZAR': {'name': 'South African Rand', 'symbol': 'R'},
        'NGN': {'name': 'Nigerian Naira', 'symbol': '₦'},
        'KES': {'name': 'Kenyan Shilling', 'symbol': 'KSh'},
        'GHS': {'name': 'Ghanaian Cedi', 'symbol': 'GH₵'},
    }
    
    FALLBACK_RATES = {
        'ZAR': 1.0,
        'NGN': 80.5,
        'KES': 7.2,
        'GHS': 0.35,
        'USD': 0.054,
    }
    
    def __init__(self):
        self._rates = self.FALLBACK_RATES.copy()
    
    def get_african_currencies(self) -> Dict:
        return self.AFRICAN_CURRENCIES.copy()
    
    def get_rates(self) -> Dict:
        return self._rates.copy()
    
    def format_amount(self, amount: float, currency: str) -> str:
        currency = currency.upper()
        if currency in self.AFRICAN_CURRENCIES:
            symbol = self.AFRICAN_CURRENCIES[currency]['symbol']
            return f"{symbol} {amount:,.2f}"
        return f"{currency} {amount:.2f}"


# Create instance for testing
converter = SimpleCurrencyConverter()

if __name__ == "__main__":
    print("Simple Currency Converter Test")
    print("=" * 40)
    
    currencies = converter.get_african_currencies()
    print(f"Available currencies: {len(currencies)}")
    for code, info in currencies.items():
        print(f"  {code}: {info['name']}")
    
    rates = converter.get_rates()
    print(f"\nExchange rates:")
    for currency in ['ZAR', 'NGN', 'KES', 'GHS', 'USD']:
        if currency in rates:
            print(f"  1 ZAR = {rates[currency]} {currency}")
    
    print(f"\nFormatting examples:")
    print(f"  R 1500.75 = {converter.format_amount(1500.75, 'ZAR')}")
    print(f"  ₦ 50000 = {converter.format_amount(50000, 'NGN')}")
    
    print("\n✅ Simple currency converter working!")
