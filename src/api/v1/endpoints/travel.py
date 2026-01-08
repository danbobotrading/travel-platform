"""
Travel search endpoints.
"""

from fastapi import APIRouter, Depends, Query
from datetime import date
from typing import Optional

from src.api.dependencies import get_current_user
from src.travel_platform.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/travel", tags=["travel"])


@router.get("/search/flights")
async def search_flights(
    current_user: dict = Depends(get_current_user),
    origin: str = Query(..., description="Origin airport code"),
    destination: str = Query(..., description="Destination airport code"),
    departure_date: date = Query(..., description="Departure date"),
    return_date: Optional[date] = Query(None, description="Return date"),
    adults: int = Query(1, ge=1, le=9, description="Number of adults"),
):
    """Search for flights."""
    logger.info("flight_search", user=current_user, origin=origin, destination=destination)
    
    return {
        "message": "Flight search will be implemented",
        "search": {
            "origin": origin,
            "destination": destination,
            "departure_date": departure_date.isoformat(),
            "return_date": return_date.isoformat() if return_date else None,
            "adults": adults
        }
    }


@router.get("/search/hotels")
async def search_hotels(
    current_user: dict = Depends(get_current_user),
    location: str = Query(..., description="City or location"),
    check_in: date = Query(..., description="Check-in date"),
    check_out: date = Query(..., description="Check-out date"),
    guests: int = Query(1, ge=1, le=10, description="Number of guests"),
):
    """Search for hotels."""
    logger.info("hotel_search", user=current_user, location=location)
    
    return {
        "message": "Hotel search will be implemented",
        "search": {
            "location": location,
            "check_in": check_in.isoformat(),
            "check_out": check_out.isoformat(),
            "guests": guests
        }
    }
