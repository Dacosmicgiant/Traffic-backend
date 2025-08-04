from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from bson import ObjectId


class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic models"""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class ConversationBase(BaseModel):
    """Base conversation model with common fields"""
    title: str = Field(..., min_length=1, max_length=200)
    user_id: Optional[str] = Field(default="default_user")  # For future user system
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ConversationCreate(ConversationBase):
    """Model for creating a new conversation"""
    pass


class ConversationInDB(ConversationBase):
    """Model representing conversation as stored in database"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    message_count: int = Field(default=0)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class ConversationResponse(BaseModel):
    """Model for API responses containing conversation data"""
    id: str
    title: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    message_count: int
    
    class Config:
        from_attributes = True