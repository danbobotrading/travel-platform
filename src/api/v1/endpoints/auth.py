"""
Authentication API endpoints.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login")
async def login():
    """Login endpoint (placeholder)."""
    return {"message": "Login endpoint - to be implemented"}
