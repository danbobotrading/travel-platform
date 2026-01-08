"""
Basic command handlers for the travel bot
"""

from telegram import Update
from telegram.ext import ContextTypes
import logging

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    
    welcome_msg = f"""🎉 Welcome {user.first_name} to TravelBot Africa!

🌍 *Your African Travel Companion*
Search flights across Africa with local currency support.

*Available Commands:*
/flights - Search for flights
/settings - Set preferences (currency, language)
/help - Show help information

*Supported African Currencies:*
• 🇿🇦 South Africa - ZAR (R)
• 🇳🇬 Nigeria - NGN (₦)
• 🇰🇪 Kenya - KES (KSh)
• 🇬🇭 Ghana - GHS (₵)

Start with /flights to find your next adventure!"""
    
    await update.message.reply_text(welcome_msg, parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = """🆘 *TravelBot Help*

*Search Flights:*
• Use /flights for step-by-step search
• Or use quick search: `JNB to LAG 2024-12-25`

*Supported African Airports:*
• JNB - Johannesburg, South Africa
• LAG - Lagos, Nigeria
• NBO - Nairobi, Kenya
• ACC - Accra, Ghana
• CAI - Cairo, Egypt
• ADD - Addis Ababa, Ethiopia
• DAR - Dar es Salaam, Tanzania

*Settings:*
Use /settings to:
• Set preferred currency
• Save frequent routes
• Set travel preferences

*Need Help?*
Contact support: @travelbot_support"""
    
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def search_flights(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /flights command - start search flow"""
    await update.message.reply_text(
        "✈️ *Flight Search*\n\n"
        "Let's find your perfect flight!\n"
        "Please enter your departure airport code (e.g., JNB):",
        parse_mode="Markdown"
    )
    # This will trigger the conversation flow
    return "DEPARTURE"

async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /settings command"""
    settings_text = """⚙️ *Settings*

*Current Preferences:*
• Currency: ZAR (Rand)
• Timezone: Africa/Johannesburg
• Language: English

*Available Options:*
1. Change currency (ZAR, NGN, KES, GHS)
2. Set timezone
3. Save frequent routes
4. Notification preferences

Reply with the number to change a setting."""
    
    await update.message.reply_text(settings_text, parse_mode="Markdown")
