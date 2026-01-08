"""
Booking management endpoints.
"""

from fastapi import APIRouter, Depends
from typing import List

from src.api.dependencies import get_current_user
from src.travel_platform.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.get("/")
async def get_bookings(
    current_user: dict = Depends(get_current_user),
) -> List[dict]:
    """Get user's bookings."""
    logger.info("get_bookings", user=current_user)
    
    return [
        {
            "id": "1",
            "type": "flight",
            "status": "confirmed",
            "date": "2024-01-15"
        }
    ]


@router.post("/")
async def create_booking(
    current_user: dict = Depends(get_current_user),
):
    """Create a new booking."""
    logger.info("create_booking", user=current_user)
    
    return {
        "message": "Booking created (simulated)",
        "booking_id": "new_123"
    }
