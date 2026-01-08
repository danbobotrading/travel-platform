#!/usr/bin/env python3
"""
Main entry point to run the Telegram bot
"""

import asyncio
import logging
from src.bot import TravelBot
from src.utils.logger import setup_logging

async def main():
    """Run the travel bot"""
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Check for bot token
    from src.core.config import settings
    
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables")
        print("❌ ERROR: TELEGRAM_BOT_TOKEN not set!")
        print("Add to .env file: TELEGRAM_BOT_TOKEN=your_token_here")
        return
    
    # Create and run bot
    bot = TravelBot()
    logger.info("Starting TravelBot for African travel...")
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())
