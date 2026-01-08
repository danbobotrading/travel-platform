"""
User API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from src.api.dependencies import get_current_user
from src.travel_platform.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/users", tags=["users"])


@router.get("/")
async def get_users():
    """Get all users (placeholder)."""
    return {"message": "Users endpoint - to be implemented"}


@router.get("/me")
async def get_current_user_info(
    current_user: dict = Depends(get_current_user)
):
    """Get current user info."""
    return {
        "message": "User info endpoint",
        "user": current_user
    }
