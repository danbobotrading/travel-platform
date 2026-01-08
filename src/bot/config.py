"""
Telegram bot configuration for Travel Platform.
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass

from src.core.config.settings import settings
from src.travel_platform.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class BotConfig:
    """Bot configuration."""
    token: str
    api_url: str = "https://api.telegram.org/bot"
    webhook_url: Optional[str] = None
    webhook_secret: Optional[str] = None
    admin_ids: list = None
    
    def __post_init__(self):
        if self.admin_ids is None:
            self.admin_ids = []


def get_bot_config() -> BotConfig:
    """Get bot configuration from settings."""
    try:
        token = settings.TELEGRAM_BOT_TOKEN.get_secret_value()
    except AttributeError:
        token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
        if hasattr(token, 'get_secret_value'):
            token = token.get_secret_value()
    
    webhook_url = getattr(settings, 'TELEGRAM_WEBHOOK_URL', None)
    webhook_secret = None
    if hasattr(settings, 'TELEGRAM_WEBHOOK_SECRET'):
        secret = settings.TELEGRAM_WEBHOOK_SECRET
        if secret and hasattr(secret, 'get_secret_value'):
            webhook_secret = secret.get_secret_value()
    
    admin_ids = getattr(settings, 'TELEGRAM_ADMIN_IDS', [])
    
    return BotConfig(
        token=token,
        api_url=getattr(settings, 'TELEGRAM_API_URL', 'https://api.telegram.org/bot'),
        webhook_url=webhook_url,
        webhook_secret=webhook_secret,
        admin_ids=admin_ids
    )
