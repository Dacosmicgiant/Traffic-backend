from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime, timezone
from bson import ObjectId
from app.models.conversation import PyObjectId  # Import from conversation.py

class UserBase(BaseModel):
    """Base user model with common fields"""
    email: EmailStr = Field(..., description="User's email address")
    full_name: str = Field(..., min_length=2, max_length=100)
    is_active: bool = Field(default=True)


class UserCreate(UserBase):
    """Model for user registration"""
    password: str = Field(..., min_length=6, max_length=100)


class UserLogin(BaseModel):
    """Model for user login"""
    email: EmailStr
    password: str


class UserInDB(UserBase):
    """Model representing user as stored in database"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    hashed_password: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class UserResponse(BaseModel):
    """Model for API responses containing user data"""
    id: str
    email: str
    full_name: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """JWT token response model"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenData(BaseModel):
    """Token payload data"""
    email: Optional[str] = None
    user_id: Optional[str] = None