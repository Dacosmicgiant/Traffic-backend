from pydantic import BaseModel, Field, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema
from typing import Optional, Any
from datetime import datetime
from bson import ObjectId


class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic v2 models"""
    
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: Any
    ) -> core_schema.CoreSchema:
        """
        Return a Pydantic CoreSchema that validates the ObjectId type.
        """
        return core_schema.no_info_wrap_validator_function(
            cls.validate,
            core_schema.str_schema(),
            serialization=core_schema.to_string_ser_schema(),
        )

    @classmethod
    def validate(cls, value):
        """Validate that the value is a valid ObjectId"""
        if isinstance(value, ObjectId):
            return value
        if isinstance(value, str) and ObjectId.is_valid(value):
            return ObjectId(value)
        raise ValueError("Invalid ObjectId")

    @classmethod
    def __get_pydantic_json_schema__(
        cls, schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        """Return JSON schema for ObjectId (appears as string in API docs)"""
        return {"type": "string", "format": "objectid"}


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