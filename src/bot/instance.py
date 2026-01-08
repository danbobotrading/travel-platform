"""
Telegram bot instance management.
"""

from typing import Optional
import asyncio
from telegram import Bot
from telegram.ext import Application, ApplicationBuilder

from src.bot.config import get_bot_config
from src.travel_platform.utils.logger import get_logger

logger = get_logger(__name__)


class BotManager:
    """Manage Telegram bot instance."""
    
    _instance: Optional['BotManager'] = None
    _application: Optional[Application] = None
    _bot: Optional[Bot] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BotManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.config = get_bot_config()
        self._initialized = True
    
    async def initialize(self) -> Application:
        """Initialize bot application."""
        if self._application is None:
            try:
                logger.info("initializing_bot", token_length=len(self.config.token))
                
                # Create application
                self._application = (
                    ApplicationBuilder()
                    .token(self.config.token)
                    .connection_pool_size(8)
                    .connect_timeout(30.0)
                    .read_timeout(30.0)
                    .write_timeout(30.0)
                    .pool_timeout(30.0)
                    .get_updates_read_timeout(30.0)
                    .get_updates_write_timeout(30.0)
                    .get_updates_connect_timeout(30.0)
                    .get_updates_pool_timeout(30.0)
                    .build()
                )
                
                self._bot = self._application.bot
                
                logger.info("bot_initialized", username=self._bot.username if self._bot.username else "unknown")
                
            except Exception as e:
                logger.error("bot_initialization_failed", error=str(e))
                raise
        
        return self._application
    
    async def shutdown(self):
        """Shutdown bot application."""
        if self._application:
            try:
                await self._application.shutdown()
                await self._application.stop()
                logger.info("bot_shutdown_complete")
            except Exception as e:
                logger.error("bot_shutdown_failed", error=str(e))
            finally:
                self._application = None
                self._bot = None
    
    def get_application(self) -> Optional[Application]:
        """Get bot application instance."""
        return self._application
    
    def get_bot(self) -> Optional[Bot]:
        """Get bot instance."""
        return self._bot
    
    async def set_webhook(self) -> bool:
        """Set webhook for bot."""
        if not self.config.webhook_url:
            logger.warning("webhook_url_not_set")
            return False
        
        try:
            await self._bot.set_webhook(
                url=self.config.webhook_url,
                secret_token=self.config.webhook_secret,
                max_connections=40,
                allowed_updates=["message", "callback_query", "inline_query"]
            )
            
            logger.info("webhook_set", url=self.config.webhook_url)
            return True
            
        except Exception as e:
            logger.error("webhook_set_failed", error=str(e))
            return False
    
    async def delete_webhook(self) -> bool:
        """Delete webhook for bot."""
        try:
            await self._bot.delete_webhook(drop_pending_updates=True)
            logger.info("webhook_deleted")
            return True
        except Exception as e:
            logger.error("webhook_delete_failed", error=str(e))
            return False


# Global bot manager instance
bot_manager = BotManager()


async def get_bot_manager() -> BotManager:
    """Get bot manager instance."""
    return bot_manager


async def initialize_bot() -> Application:
    """Initialize bot and return application."""
    return await bot_manager.initialize()
