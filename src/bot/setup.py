"""
Bot setup and initialization.
"""

from src.bot.instance import initialize_bot, bot_manager
from src.bot.handlers.commands import register_commands
from src.bot.handlers.messages import register_message_handlers
from src.travel_platform.utils.logger import get_logger

logger = get_logger(__name__)


async def setup_bot():
    """Setup and initialize the bot."""
    try:
        # Initialize bot application
        application = await initialize_bot()
        
        # Register handlers
        register_commands(application)
        register_message_handlers(application)
        
        # Store config in bot data
        application.bot_data['config'] = {
            'admin_ids': bot_manager.config.admin_ids
        }
        
        logger.info("bot_setup_complete")
        return application
        
    except Exception as e:
        logger.error("bot_setup_failed", error=str(e))
        raise


async def start_polling():
    """Start bot with polling (for development)."""
    try:
        application = await setup_bot()
        
        logger.info("starting_bot_polling")
        
        # Start polling
        await application.initialize()
        await application.start()
        await application.updater.start_polling(
            allowed_updates=["message", "callback_query", "inline_query"]
        )
        
        logger.info("bot_polling_started")
        return application
        
    except Exception as e:
        logger.error("bot_polling_start_failed", error=str(e))
        raise


async def stop_bot():
    """Stop the bot."""
    await bot_manager.shutdown()
    logger.info("bot_stopped")
