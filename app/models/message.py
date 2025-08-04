from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime
from bson import ObjectId

from app.models.conversation import PyObjectId


class MessageBase(BaseModel):
    """Base message model with common fields"""
    role: Literal["user", "assistant"] = Field(..., description="Who sent the message")
    content: str = Field(..., min_length=1, description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class MessageCreate(MessageBase):
    """Model for creating a new message"""
    conversation_id: str = Field(..., description="ID of the conversation this message belongs to")


class MessageInDB(MessageBase):
    """Model representing message as stored in database"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    conversation_id: str = Field(..., description="Reference to conversation")
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class MessageResponse(BaseModel):
    """Model for API responses containing message data"""
    id: str
    role: str
    content: str
    timestamp: datetime
    conversation_id: str
    
    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    """Model for incoming chat requests"""
    message: str = Field(..., min_length=1, max_length=1000)
    conversation_id: Optional[str] = Field(default=None)


class ChatResponse(BaseModel):
    """Model for chat API responses"""
    response: str
    conversation_id: str
    message_id: str