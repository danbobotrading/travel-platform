"""
Webhook handler for Telegram bot integrated with FastAPI.
"""

from typing import Dict, Any
from fastapi import APIRouter, Request, Depends, HTTPException
from telegram import Update

from src.bot.instance import bot_manager
from src.api.dependencies import get_telegram_webhook_secret
from src.travel_platform.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post("/webhook")
async def webhook_endpoint(
    request: Request,
    secret: str = Depends(get_telegram_webhook_secret),
) -> Dict[str, Any]:
    """
    Handle Telegram webhook updates.
    
    This endpoint receives updates from Telegram and processes them.
    """
    try:
        # Get update from request
        update_data = await request.json()
        update = Update.de_json(update_data, bot_manager.get_bot())
        
        # Process update
        application = bot_manager.get_application()
        if application:
            await application.process_update(update)
            logger.info("webhook_update_processed", update_id=update.update_id)
        else:
            logger.error("bot_application_not_initialized")
            raise HTTPException(status_code=503, detail="Bot not initialized")
        
        return {"status": "ok", "update_id": update.update_id}
        
    except Exception as e:
        logger.error("webhook_processing_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/webhook")
async def webhook_info() -> Dict[str, Any]:
    """Get webhook information."""
    bot = bot_manager.get_bot()
    if not bot:
        return {"status": "bot_not_initialized"}
    
    try:
        webhook_info = await bot.get_webhook_info()
        return {
            "status": "ok",
            "webhook_info": {
                "url": webhook_info.url,
                "has_custom_certificate": webhook_info.has_custom_certificate,
                "pending_update_count": webhook_info.pending_update_count,
                "ip_address": webhook_info.ip_address,
                "last_error_date": webhook_info.last_error_date,
                "last_error_message": webhook_info.last_error_message,
                "last_synchronization_error_date": webhook_info.last_synchronization_error_date,
                "max_connections": webhook_info.max_connections,
                "allowed_updates": webhook_info.allowed_updates,
            }
        }
    except Exception as e:
        logger.error("webhook_info_failed", error=str(e))
        return {"status": "error", "error": str(e)}


@router.post("/webhook/set")
async def set_webhook() -> Dict[str, Any]:
    """Set webhook for bot."""
    try:
        success = await bot_manager.set_webhook()
        return {"status": "ok" if success else "failed", "action": "set_webhook"}
    except Exception as e:
        logger.error("set_webhook_failed", error=str(e))
        return {"status": "error", "error": str(e)}


@router.post("/webhook/delete")
async def delete_webhook() -> Dict[str, Any]:
    """Delete webhook for bot."""
    try:
        success = await bot_manager.delete_webhook()
        return {"status": "ok" if success else "failed", "action": "delete_webhook"}
    except Exception as e:
        logger.error("delete_webhook_failed", error=str(e))
        return {"status": "error", "error": str(e)}
