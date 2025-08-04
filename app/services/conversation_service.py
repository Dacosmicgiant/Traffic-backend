from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.conversation import ConversationCreate, ConversationInDB, ConversationResponse
from app.models.message import MessageInDB
from typing import List, Optional
from bson import ObjectId
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


class ConversationService:
    """
    Service class for conversation database operations.
    Keeps all conversation logic in one place.
    """
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.db = database
        self.conversations_collection = database.conversations
        self.messages_collection = database.messages

    async def create_conversation(self, conversation_data: ConversationCreate) -> ConversationResponse:
        """
        Create a new conversation in the database.
        
        Args:
            conversation_data: Conversation details from API request
            
        Returns:
            Created conversation with generated ID
        """
        try:
            # Convert Pydantic model to dict for MongoDB
            conversation_dict = conversation_data.model_dump()
            conversation_dict["message_count"] = 0
            
            # Insert into database
            result = await self.conversations_collection.insert_one(conversation_dict)
            
            # Fetch the created conversation
            created_conversation = await self.conversations_collection.find_one(
                {"_id": result.inserted_id}
            )
            
            # Convert to response model
            return self._convert_to_response(created_conversation)
            
        except Exception as e:
            logger.error(f"Error creating conversation: {e}")
            raise

    async def get_conversation(self, conversation_id: str) -> Optional[ConversationResponse]:
        """
        Get a specific conversation by ID.
        
        Args:
            conversation_id: MongoDB ObjectId as string
            
        Returns:
            Conversation data or None if not found
        """
        try:
            if not ObjectId.is_valid(conversation_id):
                return None
                
            conversation = await self.conversations_collection.find_one(
                {"_id": ObjectId(conversation_id)}
            )
            
            if conversation:
                return self._convert_to_response(conversation)
            return None
            
        except Exception as e:
            logger.error(f"Error getting conversation {conversation_id}: {e}")
            return None

    async def get_all_conversations(self, user_id: str = "default_user") -> List[ConversationResponse]:
        """
        Get all conversations for a user, sorted by most recent first.
        
        Args:
            user_id: User identifier (default for now)
            
        Returns:
            List of conversations sorted by updated_at descending
        """
        try:
            cursor = self.conversations_collection.find(
                {"user_id": user_id}
            ).sort("updated_at", -1)  # Most recent first
            
            conversations = []
            async for conversation in cursor:
                conversations.append(self._convert_to_response(conversation))
                
            return conversations
            
        except Exception as e:
            logger.error(f"Error getting conversations for user {user_id}: {e}")
            return []

    async def update_conversation_timestamp(self, conversation_id: str) -> bool:
        """
        Update the conversation's updated_at timestamp.
        Called when new messages are added.
        
        Args:
            conversation_id: MongoDB ObjectId as string
            
        Returns:
            True if updated successfully, False otherwise
        """
        try:
            if not ObjectId.is_valid(conversation_id):
                return False
                
            result = await self.conversations_collection.update_one(
                {"_id": ObjectId(conversation_id)},
                {
                    "$set": {"updated_at": datetime.now(timezone.utc)},
                    "$inc": {"message_count": 1}  # Increment message count
                }
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error updating conversation {conversation_id}: {e}")
            return False

    def _convert_to_response(self, conversation_dict: dict) -> ConversationResponse:
        """
        Convert MongoDB document to Pydantic response model.
        
        Args:
            conversation_dict: Raw MongoDB document
            
        Returns:
            Pydantic ConversationResponse model
        """
        return ConversationResponse(
            id=str(conversation_dict["_id"]),
            title=conversation_dict["title"],
            user_id=conversation_dict["user_id"],
            created_at=conversation_dict["created_at"],
            updated_at=conversation_dict["updated_at"],
            message_count=conversation_dict.get("message_count", 0)
        )