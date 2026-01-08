"""
Pydantic schemas for User models.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from uuid import UUID


class UserBase(BaseModel):
    """Base user schema."""
    telegram_id: int = Field(..., description="Telegram user ID")
    username: Optional[str] = Field(None, description="Telegram username")
    first_name: str = Field(..., description="First name")
    email: Optional[EmailStr] = Field(None, description="Email address")


class UserCreate(UserBase):
    """Schema for creating a new user."""
    pass


class UserUpdate(BaseModel):
    """Schema for updating user information."""
    username: Optional[str] = None
    first_name: Optional[str] = None
    email: Optional[EmailStr] = None


class UserInDB(UserBase):
    """User schema as stored in database."""
    id: UUID = Field(..., description="User UUID")
    is_active: bool = Field(..., description="Whether user is active")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True


class UserPublic(UserInDB):
    """Public user schema."""
    pass


class UserListResponse(BaseModel):
    """Response schema for user list."""
    users: List[UserPublic]
    total: int
    page: int
    page_size: int
