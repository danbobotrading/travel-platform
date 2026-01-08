"""
Message handlers for Telegram bot.
"""

from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from telegram.constants import ParseMode

from src.travel_platform.utils.logger import get_logger

logger = get_logger(__name__)


async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular text messages."""
    user = update.effective_user
    text = update.message.text
    
    logger.info("text_message", user_id=user.id, text_length=len(text))
    
    # Check for conversion requests
    if any(keyword in text.lower() for keyword in ['convert', 'to', 'zar', 'ngn', 'kes', 'ghs', 'usd']):
        # This is a currency conversion request
        response = (
            "💰 *Currency Conversion*\n\n"
            "I see you want to convert currency!\n\n"
            "Please use the format:\n"
            "`/convert [amount] [from] to [to]`\n\n"
            "Example: `/convert 1000 ZAR to NGN`\n\n"
            "Supported currencies: ZAR, NGN, KES, GHS, USD, EUR"
        )
    elif any(keyword in text.lower() for keyword in ['flight', 'fly', 'airplane', 'ticket']):
        # Flight related query
        response = (
            "✈️ *Flight Search*\n\n"
            "I can help you search for flights!\n\n"
            "Use `/search` to start a flight search, "
            "or tell me:\n"
            "• Where are you flying from?\n"
            "• Where are you flying to?\n"
            "• When are you traveling?"
        )
    elif any(keyword in text.lower() for keyword in ['hotel', 'stay', 'accommodation', 'room']):
        # Hotel related query
        response = (
            "🏨 *Hotel Search*\n\n"
            "I can help you find hotels!\n\n"
            "Use `/search` to start a hotel search, "
            "or tell me:\n"
            "• Which city/location?\n"
            "• Check-in and check-out dates?\n"
            "• How many guests?"
        )
    else:
        # Generic response
        response = (
            "🤖 *Travel Assistant*\n\n"
            "I'm here to help with your travel needs!\n\n"
            "You can:\n"
            "• Use `/search` to find flights/hotels\n"
            "• Use `/currency` for currency conversion\n"
            "• Use `/bookings` to view your bookings\n"
            "• Use `/help` for all commands"
        )
    
    await update.message.reply_text(
        response,
        parse_mode=ParseMode.MARKDOWN
    )


async def handle_unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle unknown commands."""
    user = update.effective_user
    
    logger.info("unknown_command", user_id=user.id)
    
    await update.message.reply_text(
        "🤔 I don't recognize that command.\n\n"
        "Use /help to see available commands."
    )


def register_message_handlers(application):
    """Register all message handlers."""
    # Handle text messages
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_text_message
    ))
    
    # Handle unknown commands
    application.add_handler(MessageHandler(
        filters.COMMAND,
        handle_unknown_command
    ))
    
    logger.info("message_handlers_registered")
