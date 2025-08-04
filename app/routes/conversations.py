from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.services.database import get_database
from app.services.conversation_service import ConversationService
from app.services.message_service import MessageService
from app.models.conversation import ConversationCreate, ConversationResponse
from app.models.message import MessageResponse
from typing import List
import logging

logger = logging.getLogger(__name__)

# Create router instance
router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.post("/", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    conversation: ConversationCreate,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Create a new conversation.
    
    - **title**: Title for the conversation (required)
    - **user_id**: User identifier (optional, defaults to 'default_user')
    """
    try:
        conversation_service = ConversationService(db)
        new_conversation = await conversation_service.create_conversation(conversation)
        
        logger.info(f"Created new conversation: {new_conversation.id}")
        return new_conversation
        
    except Exception as e:
        logger.error(f"Failed to create conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create conversation"
        )


@router.get("/", response_model=List[ConversationResponse])
async def get_conversations(
    user_id: str = "default_user",
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get all conversations for a user.
    
    - **user_id**: User identifier (defaults to 'default_user')
    
    Returns conversations sorted by most recent first.
    """
    try:
        conversation_service = ConversationService(db)
        conversations = await conversation_service.get_all_conversations(user_id)
        
        logger.info(f"Retrieved {len(conversations)} conversations for user {user_id}")
        return conversations
        
    except Exception as e:
        logger.error(f"Failed to get conversations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversations"
        )


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get a specific conversation by ID.
    
    - **conversation_id**: MongoDB ObjectId of the conversation
    """
    try:
        conversation_service = ConversationService(db)
        conversation = await conversation_service.get_conversation(conversation_id)
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation {conversation_id} not found"
            )
            
        logger.info(f"Retrieved conversation: {conversation_id}")
        return conversation
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        logger.error(f"Failed to get conversation {conversation_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversation"
        )


@router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(
    conversation_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get all messages for a specific conversation.
    
    - **conversation_id**: MongoDB ObjectId of the conversation
    
    Returns messages ordered chronologically (oldest first).
    """
    try:
        # First verify conversation exists
        conversation_service = ConversationService(db)
        conversation = await conversation_service.get_conversation(conversation_id)
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation {conversation_id} not found"
            )
        
        # Get messages
        message_service = MessageService(db)
        messages = await message_service.get_conversation_messages(conversation_id)
        
        logger.info(f"Retrieved {len(messages)} messages for conversation {conversation_id}")
        return messages
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        logger.error(f"Failed to get messages for conversation {conversation_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve messages"
        )


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Delete a conversation and all its messages.
    
    - **conversation_id**: MongoDB ObjectId of the conversation
    """
    try:
        # Verify conversation exists
        conversation_service = ConversationService(db)
        conversation = await conversation_service.get_conversation(conversation_id)
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation {conversation_id} not found"
            )
        
        # Delete all messages first
        message_service = MessageService(db)
        deleted_messages = await message_service.delete_conversation_messages(conversation_id)
        
        # Delete the conversation
        from bson import ObjectId
        result = await conversation_service.conversations_collection.delete_one(
            {"_id": ObjectId(conversation_id)}
        )
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete conversation"
            )
        
        logger.info(f"Deleted conversation {conversation_id} and {deleted_messages} messages")
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        logger.error(f"Failed to delete conversation {conversation_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete conversation"
        )