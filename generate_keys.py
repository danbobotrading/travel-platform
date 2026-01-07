# generate_keys.py
import secrets
import base64

print("🔐 Generating Secure Keys for Travel Platform")
print("=" * 50)

# Generate a secure secret key (for JWT, sessions, etc.)
secret_key = secrets.token_urlsafe(32)
print(f"\n1. APP_SECRET_KEY (for JWT/sessions):")
print(f"   {secret_key}")

# Generate a 32-character encryption key (must be exactly 32 chars)
encryption_key = secrets.token_urlsafe(32)
print(f"\n2. ENCRYPTION_KEY (32 chars for Fernet encryption):")
print(f"   {encryption_key}")
print(f"   Length: {len(encryption_key)} characters")

# Generate a random database password
db_password = secrets.token_urlsafe(16)
print(f"\n3. Database Password (suggested):")
print(f"   {db_password}")

# Generate Telegram bot token placeholder
print(f"\n4. TELEGRAM_BOT_TOKEN (get from @BotFather):")
print(f"   Get this from Telegram: https://t.me/BotFather")

print("\n" + "=" * 50)
print("📝 Copy these values to your .env file")

# Create a sample .env content
env_content = f"""# ============ APPLICATION ============
APP_NAME="Travel Platform"
APP_ENV=development
APP_DEBUG=true
APP_VERSION=1.0.0
APP_SECRET_KEY={secret_key}
APP_URL=http://localhost:8000

# ============ DATABASE ============
DATABASE_URL=postgresql+asyncpg://travel_user:{db_password}@localhost:5432/travel_platform
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=40
DATABASE_POOL_TIMEOUT=30
DATABASE_ECHO=true

# ============ REDIS ============
REDIS_URL=redis://localhost:6379/0
REDIS_CACHE_TTL=3600
REDIS_SESSION_TTL=86400
REDIS_MAX_CONNECTIONS=50

# ============ TELEGRAM ============
TELEGRAM_BOT_TOKEN=your-telegram-bot-token-here
TELEGRAM_API_URL=https://api.telegram.org/bot
TELEGRAM_ADMIN_IDS=123456789

# ============ SECURITY ============
ENCRYPTION_KEY={encryption_key}
JWT_SECRET_KEY={secret_key}
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
"""

print(f"\n📄 Sample .env content has been generated.")
print("💡 Save this as '.env' in your project root")
