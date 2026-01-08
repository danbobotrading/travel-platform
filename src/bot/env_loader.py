"""
Simple environment loader for bot configuration.
"""

import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

def get_env_var(name: str, default: str = '') -> str:
    """Get environment variable."""
    return os.environ.get(name, default)

def get_bot_token() -> str:
    """Get bot token from environment."""
    return get_env_var('TELEGRAM_BOT_TOKEN')

def get_admin_ids() -> list:
    """Get admin IDs from environment."""
    ids_str = get_env_var('TELEGRAM_ADMIN_IDS', '')
    if ids_str:
        try:
            return [int(id.strip()) for id in ids_str.split(',')]
        except ValueError:
            return []
    return []
