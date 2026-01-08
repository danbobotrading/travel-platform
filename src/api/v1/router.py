"""
Main API router for Travel Platform v1.
"""

from fastapi import APIRouter

from src.api.v1.endpoints import users, auth, travel, bookings

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(users.router)
api_router.include_router(auth.router)
api_router.include_router(travel.router)
api_router.include_router(bookings.router)
