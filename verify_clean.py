"""
Clean test of Section 1-6 completed components.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

print("=" * 60)
print("POST-CLEANUP VERIFICATION")
print("=" * 60)

tests = []
total_score = 0

# Test 1: Core Structure
print("\n1. PROJECT STRUCTURE CHECK")
print("-" * 40)

required_dirs = ["src", "src/core", "src/database", "src/utils"]
required_files = [
    "src/core/config/settings.py",
    "src/core/exceptions.py", 
    "src/core/types.py",
    "src/utils/__init__.py",
    "src/utils/logger.py",
    "src/utils/currency_simple.py",
    "src/utils/date_helpers.py",
    "src/utils/cache.py",
    "src/utils/validators.py",
    "src/utils/security.py",
    ".env",
    "requirements.txt",
    "docker-compose.yml"
]

dir_score = 0
for dir_path in required_dirs:
    if os.path.exists(dir_path):
        print(f"   ✅ {dir_path}")
        dir_score += 1
    else:
        print(f"   ❌ {dir_path}")

file_score = 0
for file_path in required_files:
    if os.path.exists(file_path):
        print(f"   ✅ {file_path}")
        file_score += 1
    else:
        print(f"   ❌ {file_path}")

structure_score = (dir_score + file_score) / (len(required_dirs) + len(required_files)) * 100
print(f"\n   Structure Score: {structure_score:.0f}%")
total_score += structure_score * 0.3  # 30% weight

# Test 2: Core Imports
print("\n2. CORE IMPORTS CHECK")
print("-" * 40)

import_tests = [
    ("Settings", "from src.core.config.settings import settings"),
    ("Logger", "from src.utils.logger import logger"),
    ("Currency", "from src.utils.currency_simple import CurrencyConverter"),
    ("Date Helpers", "from src.utils.date_helpers import TravelDateHelper"),
    ("Validators", "from src.utils.validators import TravelValidators"),
    ("Security", "from src.utils.security import SecurityUtils"),
    ("Cache", "from src.utils.cache import RedisCache"),
    ("Exceptions", "from src.core.exceptions import TravelPlatformError"),
    ("Types", "from src.core.types import TravelClass, Currency")
]

import_score = 0
for test_name, import_stmt in import_tests:
    try:
        exec(import_stmt)
        print(f"   ✅ {test_name}")
        import_score += 1
    except Exception as e:
        print(f"   ❌ {test_name}: {type(e).__name__}")

import_percent = (import_score / len(import_tests)) * 100
print(f"\n   Imports Score: {import_percent:.0f}%")
total_score += import_percent * 0.4  # 40% weight

# Test 3: Functionality
print("\n3. BASIC FUNCTIONALITY CHECK")
print("-" * 40)

func_score = 0
func_tests = 0

try:
    # Logger test
    from src.utils.logger import logger
    logger.info("cleanup_test", component="verification", status="running")
    print(f"   ✅ Logger functional")
    func_score += 1
except:
    print(f"   ❌ Logger not functional")

func_tests += 1

try:
    # Currency test
    from src.utils.currency_simple import converter
    currencies = converter.get_african_currencies()
    if len(currencies) >= 4:
        print(f"   ✅ Currency: {len(currencies)} African currencies")
        func_score += 1
    else:
        print(f"   ⚠️  Currency: Only {len(currencies)} currencies")
except:
    print(f"   ❌ Currency not functional")

func_tests += 1

try:
    # Date helpers test
    from src.utils.date_helpers import TravelDateHelper
    from datetime import date
    today = date.today()
    formatted = TravelDateHelper.format_travel_date(today, "ZA")
    if formatted:
        print(f"   ✅ Date Helpers: Formatting works")
        func_score += 1
except:
    print(f"   ❌ Date Helpers not functional")

func_tests += 1

try:
    # Validators test
    from src.utils.validators import TravelValidators
    valid, msg = TravelValidators.validate_email_address("test@example.com")
    if valid:
        print(f"   ✅ Validators: Email validation works")
        func_score += 1
except:
    print(f"   ❌ Validators not functional")

func_tests += 1

func_percent = (func_score / func_tests) * 100
print(f"\n   Functionality Score: {func_percent:.0f}%")
total_score += func_percent * 0.3  # 30% weight

# Final Score
print("\n" + "=" * 60)
print("FINAL VERIFICATION RESULTS")
print("=" * 60)

print(f"\nBREAKDOWN:")
print(f"  Structure:    {structure_score:.0f}% (30% weight)")
print(f"  Imports:      {import_percent:.0f}% (40% weight)")
print(f"  Functionality: {func_percent:.0f}% (30% weight)")

print(f"\nOVERALL SCORE: {total_score:.0f}%")

if total_score >= 80:
    print("\n🎉 STATUS: READY FOR SECTION 7")
    print("Project is clean and functional.")
elif total_score >= 60:
    print("\n⚠️  STATUS: NEEDS MINOR FIXES")
    print("Some issues but can proceed.")
else:
    print("\n❌ STATUS: NEEDS MAJOR FIXES")
    print("Significant issues found.")

print("\n" + "=" * 60)
