"""
Telegram bot configuration for Travel Platform.
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass

from src.bot.env_loader import get_bot_token, get_admin_ids
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
    """Get bot configuration from environment."""
    token = get_bot_token()
    
    if not token:
        logger.warning("bot_token_not_found", source="environment")
    
    return BotConfig(
        token=token,
        api_url="https://api.telegram.org/bot",
        webhook_url=None,  # Will be set when webhook configured
        webhook_secret=None,
        admin_ids=get_admin_ids()
    )
