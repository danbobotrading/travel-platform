"""
Conversation handlers for guided search flow
"""

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ContextTypes, 
    ConversationHandler, 
    MessageHandler, 
    filters,
    CommandHandler
)
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Conversation states
DEPARTURE, ARRIVAL, DATE, PASSENGERS, CONFIRM = range(5)

# African airports with city names
AFRICAN_AIRPORTS = {
    "JNB": "Johannesburg, South Africa",
    "CPT": "Cape Town, South Africa",
    "LAG": "Lagos, Nigeria",
    "ABV": "Abuja, Nigeria",
    "NBO": "Nairobi, Kenya",
    "ACC": "Accra, Ghana",
    "CAI": "Cairo, Egypt",
    "ADD": "Addis Ababa, Ethiopia",
    "DAR": "Dar es Salaam, Tanzania",
    "KGL": "Kigali, Rwanda",
    "EBB": "Entebbe, Uganda"
}

async def start_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start flight search conversation"""
    await update.message.reply_text(
        "✈️ *Flight Search Started*\n\n"
        "Please enter departure airport code (e.g., JNB):",
        parse_mode="Markdown"
    )
    return DEPARTURE

async def get_departure(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get departure airport"""
    dep_code = update.message.text.upper().strip()
    
    if dep_code not in AFRICAN_AIRPORTS:
        await update.message.reply_text(
            "❌ *Invalid airport code*\n\n"
            "Please enter a valid African airport code:\n"
            "• JNB - Johannesburg\n"
            "• LAG - Lagos\n"
            "• NBO - Nairobi\n"
            "• ACC - Accra\n"
            "• CAI - Cairo",
            parse_mode="Markdown"
        )
        return DEPARTURE
    
    context.user_data['departure'] = dep_code
    await update.message.reply_text(
        f"✅ Departure: {dep_code} ({AFRICAN_AIRPORTS[dep_code]})\n\n"
        "Now enter arrival airport code:",
        parse_mode="Markdown"
    )
    return ARRIVAL

async def get_arrival(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get arrival airport"""
    arr_code = update.message.text.upper().strip()
    
    if arr_code not in AFRICAN_AIRPORTS:
        await update.message.reply_text(
            "❌ *Invalid airport code*\n\n"
            "Please enter a valid African airport code.",
            parse_mode="Markdown"
        )
        return ARRIVAL
    
    if arr_code == context.user_data.get('departure'):
        await update.message.reply_text(
            "❌ *Same airport*\n\n"
            "Departure and arrival cannot be the same.\n"
            "Please enter a different arrival airport:",
            parse_mode="Markdown"
        )
        return ARRIVAL
    
    context.user_data['arrival'] = arr_code
    await update.message.reply_text(
        f"✅ Route: {context.user_data['departure']} → {arr_code}\n\n"
        "Enter travel date (YYYY-MM-DD, e.g., 2024-12-25):",
        parse_mode="Markdown"
    )
    return DATE

async def get_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get travel date"""
    date_str = update.message.text.strip()
    
    try:
        travel_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        today = datetime.now().date()
        
        if travel_date < today:
            await update.message.reply_text(
                "❌ *Date in past*\n\n"
                "Travel date cannot be in the past.\n"
                "Please enter a future date:",
                parse_mode="Markdown"
            )
            return DATE
        
        context.user_data['date'] = date_str
        await update.message.reply_text(
            f"✅ Date: {date_str}\n\n"
            "Enter number of passengers (1-9):",
            parse_mode="Markdown"
        )
        return PASSENGERS
        
    except ValueError:
        await update.message.reply_text(
            "❌ *Invalid date format*\n\n"
            "Please use YYYY-MM-DD format (e.g., 2024-12-25):",
            parse_mode="Markdown"
        )
        return DATE

async def get_passengers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get number of passengers"""
    try:
        passengers = int(update.message.text.strip())
        
        if not 1 <= passengers <= 9:
            await update.message.reply_text(
                "❌ *Invalid number*\n\n"
                "Please enter between 1-9 passengers:",
                parse_mode="Markdown"
            )
            return PASSENGERS
        
        context.user_data['passengers'] = passengers
        
        # Show summary
        summary = f"""✅ *Search Summary*

*Route:* {context.user_data['departure']} → {context.user_data['arrival']}
*Date:* {context.user_data['date']}
*Passengers:* {passengers}

Search for flights now?"""
        
        keyboard = [["Yes", "No"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        
        await update.message.reply_text(
            summary,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        return CONFIRM
        
    except ValueError:
        await update.message.reply_text(
            "❌ *Invalid number*\n\n"
            "Please enter a number between 1-9:",
            parse_mode="Markdown"
        )
        return PASSENGERS

async def confirm_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Confirm and execute search"""
    response = update.message.text.lower()
    
    if response == "yes":
        await update.message.reply_text(
            "🔍 *Searching for flights...*\n\n"
            "Checking multiple providers for the best deals...",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardRemove()
        )
        
        # TODO: Call actual search engine
        await update.message.reply_text(
            "✅ *Search Complete!*\n\n"
            "Implement search engine integration here.\n"
            "Use your FlightSearchEngine from Section 7.",
            parse_mode="Markdown"
        )
        
    else:
        await update.message.reply_text(
            "❌ Search cancelled.",
            reply_markup=ReplyKeyboardRemove()
        )
    
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel the conversation"""
    await update.message.reply_text(
        "❌ Search cancelled.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

def create_flight_search_handler():
    """Create conversation handler for flight search"""
    return ConversationHandler(
        entry_points=[CommandHandler("flights", start_search)],
        states={
            DEPARTURE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_departure)],
            ARRIVAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_arrival)],
            DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_date)],
            PASSENGERS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_passengers)],
            CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_search)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
