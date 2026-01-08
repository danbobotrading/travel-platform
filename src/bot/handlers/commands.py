"""
Command handlers for Telegram bot.
"""

from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from telegram.constants import ParseMode

from src.travel_platform.utils.logger import get_logger

logger = get_logger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    user = update.effective_user
    chat = update.effective_chat
    
    logger.info("start_command", user_id=user.id, username=user.username)
    
    welcome_message = (
        "👋 *Welcome to Travel Platform!*\n\n"
        "I can help you search and book travel arrangements across Africa. "
        "Here's what I can do:\n\n"
        "• ✈️ Search for flights\n"
        "• 🏨 Find hotels\n"
        "• 💰 Check currency rates\n"
        "• 📅 Plan your itinerary\n\n"
        "Use /help to see all available commands."
    )
    
    await update.message.reply_text(
        welcome_message,
        parse_mode=ParseMode.MARKDOWN
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    user = update.effective_user
    
    logger.info("help_command", user_id=user.id)
    
    help_message = (
        "📋 *Available Commands:*\n\n"
        "*/start* - Welcome message\n"
        "*/help* - This help message\n"
        "*/search* - Search for flights or hotels\n"
        "*/bookings* - View your bookings\n"
        "*/currency* - Convert currency\n"
        "*/settings* - Update your preferences\n\n"
        "💰 *Currency Support:*\n"
        "• ZAR (South African Rand)\n"
        "• NGN (Nigerian Naira)\n"
        "• KES (Kenyan Shilling)\n"
        "• GHS (Ghanaian Cedi)\n"
        "• USD (US Dollar)\n\n"
        "🌍 *African Focus:*\n"
        "Specializing in African destinations and travel needs."
    )
    
    await update.message.reply_text(
        help_message,
        parse_mode=ParseMode.MARKDOWN
    )


async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /search command."""
    user = update.effective_user
    
    logger.info("search_command", user_id=user.id)
    
    search_message = (
        "🔍 *Search Options:*\n\n"
        "I can help you search for:\n\n"
        "1. ✈️ *Flights* - Search for flights\n"
        "2. 🏨 *Hotels* - Find accommodation\n"
        "3. 🚗 *Car Rentals* - Rent a vehicle\n\n"
        "Please tell me what you'd like to search for, "
        "or use the buttons when they're available."
    )
    
    await update.message.reply_text(
        search_message,
        parse_mode=ParseMode.MARKDOWN
    )


async def bookings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /bookings command."""
    user = update.effective_user
    
    logger.info("bookings_command", user_id=user.id)
    
    # TODO: Fetch actual bookings from database
    bookings_message = (
        "📋 *Your Bookings*\n\n"
        "You don't have any bookings yet.\n\n"
        "Use /search to find and book flights or hotels."
    )
    
    await update.message.reply_text(
        bookings_message,
        parse_mode=ParseMode.MARKDOWN
    )


async def currency_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /currency command."""
    user = update.effective_user
    
    logger.info("currency_command", user_id=user.id)
    
    currency_message = (
        "💰 *Currency Converter*\n\n"
        "I can convert between African currencies:\n\n"
        "• 🇿🇦 ZAR - South African Rand\n"
        "• 🇳🇬 NGN - Nigerian Naira\n"
        "• 🇰🇪 KES - Kenyan Shilling\n"
        "• 🇬🇭 GHS - Ghanaian Cedi\n"
        "• 🇺🇸 USD - US Dollar\n"
        "• 🇪🇺 EUR - Euro\n\n"
        "Format: `/convert 100 USD to ZAR`\n"
        "Example: `/convert 1000 ZAR to NGN`"
    )
    
    await update.message.reply_text(
        currency_message,
        parse_mode=ParseMode.MARKDOWN
    )


async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /settings command."""
    user = update.effective_user
    
    logger.info("settings_command", user_id=user.id)
    
    settings_message = (
        "⚙️ *Your Settings*\n\n"
        "Current preferences:\n"
        "• Currency: ZAR (South African Rand)\n"
        "• Language: English\n"
        "• Notifications: Enabled\n\n"
        "Use these commands to update:\n"
        "• `/setcurrency ZAR` - Change currency\n"
        "• `/setlanguage en` - Change language\n"
        "• `/notifications on` - Toggle notifications"
    )
    
    await update.message.reply_text(
        settings_message,
        parse_mode=ParseMode.MARKDOWN
    )


async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /admin command (admin only)."""
    user = update.effective_user
    config = context.bot_data.get('config', {})
    admin_ids = config.get('admin_ids', [])
    
    if user.id not in admin_ids:
        await update.message.reply_text("⛔ Admin access required.")
        return
    
    logger.info("admin_command", user_id=user.id)
    
    admin_message = (
        "👑 *Admin Panel*\n\n"
        "Available admin commands:\n\n"
        "• `/stats` - View bot statistics\n"
        "• `/users` - List all users\n"
        "• `/broadcast` - Send message to all users\n"
        "• `/maintenance` - Toggle maintenance mode"
    )
    
    await update.message.reply_text(
        admin_message,
        parse_mode=ParseMode.MARKDOWN
    )


def register_commands(application):
    """Register all command handlers."""
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("search", search_command))
    application.add_handler(CommandHandler("bookings", bookings_command))
    application.add_handler(CommandHandler("currency", currency_command))
    application.add_handler(CommandHandler("settings", settings_command))
    application.add_handler(CommandHandler("admin", admin_command))
    
    logger.info("commands_registered")
