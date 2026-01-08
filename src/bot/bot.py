"""
Main Travel Bot for African travel search
"""

from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, filters
from telegram.ext import CallbackQueryHandler
import logging

from src.core.config import settings
from .handlers import commands, conversations

logger = logging.getLogger(__name__)

class TravelBot:
    def __init__(self):
        self.token = settings.TELEGRAM_BOT_TOKEN
        self.app = None
        
    def setup_handlers(self):
        """Register all command and conversation handlers"""
        
        # Basic commands
        self.app.add_handler(CommandHandler("start", commands.start))
        self.app.add_handler(CommandHandler("help", commands.help_command))
        self.app.add_handler(CommandHandler("flights", commands.search_flights))
        self.app.add_handler(CommandHandler("settings", commands.settings))
        
        # Flight search conversation
        self.app.add_handler(conversations.create_flight_search_handler())
        
        # Error handler
        self.app.add_error_handler(self.error_handler)
        
    async def error_handler(self, update, context):
        """Handle errors gracefully"""
        logger.error(f"Exception while handling update: {context.error}")
        
    async def run(self):
        """Run the bot with polling"""
        self.app = Application.builder().token(self.token).build()
        self.setup_handlers()
        
        logger.info("Bot is starting...")
        await self.app.initialize()
        await self.app.start()
        await self.app.updater.start_polling()
        
        logger.info("Bot is running. Press Ctrl+C to stop.")
        
        # Keep running
        await self.app.updater.idle()
