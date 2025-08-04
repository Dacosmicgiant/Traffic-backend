from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.message import MessageCreate, MessageInDB, MessageResponse
from typing import List, Optional
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)


class MessageService:
    """
    Service class for message database operations.
    Handles storing and retrieving messages for conversations.
    """
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.db = database
        self.messages_collection = database.messages

    async def create_message(self, message_data: MessageCreate) -> MessageResponse:
        """
        Create a new message in the database.
        
        Args:
            message_data: Message details from API request
            
        Returns:
            Created message with generated ID
        """
        try:
            # Convert Pydantic model to dict for MongoDB
            message_dict = message_data.model_dump()
            
            # Insert into database
            result = await self.messages_collection.insert_one(message_dict)
            
            # Fetch the created message
            created_message = await self.messages_collection.find_one(
                {"_id": result.inserted_id}
            )
            
            # Convert to response model
            return self._convert_to_response(created_message)
            
        except Exception as e:
            logger.error(f"Error creating message: {e}")
            raise

    async def get_conversation_messages(self, conversation_id: str) -> List[MessageResponse]:
        """
        Get all messages for a specific conversation, ordered by timestamp.
        
        Args:
            conversation_id: MongoDB ObjectId as string
            
        Returns:
            List of messages ordered by timestamp (oldest first)
        """
        try:
            cursor = self.messages_collection.find(
                {"conversation_id": conversation_id}
            ).sort("timestamp", 1)  # Oldest first for conversation flow
            
            messages = []
            async for message in cursor:
                messages.append(self._convert_to_response(message))
                
            return messages
            
        except Exception as e:
            logger.error(f"Error getting messages for conversation {conversation_id}: {e}")
            return []

    async def get_conversation_history_for_ai(self, conversation_id: str) -> List[dict]:
        """
        Get conversation history formatted for AI service consumption.
        Returns simple format: [{"role": "user", "content": "..."}, ...]
        
        Args:
            conversation_id: MongoDB ObjectId as string
            
        Returns:
            List of message dictionaries for AI context
        """
        try:
            cursor = self.messages_collection.find(
                {"conversation_id": conversation_id},
                {"role": 1, "content": 1, "_id": 0}  # Only get role and content
            ).sort("timestamp", 1)
            
            history = []
            async for message in cursor:
                history.append({
                    "role": message["role"],
                    "content": message["content"]
                })
                
            return history
            
        except Exception as e:
            logger.error(f"Error getting conversation history for AI: {e}")
            return []

    async def delete_conversation_messages(self, conversation_id: str) -> int:
        """
        Delete all messages for a conversation.
        Useful for cleanup operations.
        
        Args:
            conversation_id: MongoDB ObjectId as string
            
        Returns:
            Number of messages deleted
        """
        try:
            result = await self.messages_collection.delete_many(
                {"conversation_id": conversation_id}
            )
            
            logger.info(f"Deleted {result.deleted_count} messages for conversation {conversation_id}")
            return result.deleted_count
            
        except Exception as e:
            logger.error(f"Error deleting messages for conversation {conversation_id}: {e}")
            return 0

    def _convert_to_response(self, message_dict: dict) -> MessageResponse:
        """
        Convert MongoDB document to Pydantic response model.
        
        Args:
            message_dict: Raw MongoDB document
            
        Returns:
            Pydantic MessageResponse model
        """
        return MessageResponse(
            id=str(message_dict["_id"]),
            role=message_dict["role"],
            content=message_dict["content"],
            timestamp=message_dict["timestamp"],
            conversation_id=message_dict["conversation_id"]
        )