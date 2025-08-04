from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.services.database import get_database
from app.services.conversation_service import ConversationService
from app.services.message_service import MessageService
from app.services.dependencies import get_current_active_user  # Add this import
from app.models.conversation import ConversationCreate, ConversationResponse
from app.models.message import MessageResponse
from app.models.user import UserResponse  # Add this import
from typing import List
import logging

logger = logging.getLogger(__name__)

# Create router instance
router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.post("/", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    conversation: ConversationCreate,
    current_user: UserResponse = Depends(get_current_active_user),  # Add authentication
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Create a new conversation for the authenticated user.
    
    - **title**: Title for the conversation (required)
    
    Requires authentication: Include JWT token in Authorization header.
    """
    try:
        conversation_service = ConversationService(db)
        
        # Override user_id with authenticated user's ID
        conversation_data = ConversationCreate(
            title=conversation.title,
            user_id=current_user.id  # Use authenticated user's ID
        )
        
        new_conversation = await conversation_service.create_conversation(conversation_data)
        
        logger.info(f"Created new conversation: {new_conversation.id} for user: {current_user.email}")
        return new_conversation
        
    except Exception as e:
        logger.error(f"Failed to create conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create conversation"
        )


@router.get("/", response_model=List[ConversationResponse])
async def get_conversations(
    current_user: UserResponse = Depends(get_current_active_user),  # Add authentication
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get all conversations for the authenticated user.
    
    Returns conversations sorted by most recent first.
    Requires authentication: Include JWT token in Authorization header.
    """
    try:
        conversation_service = ConversationService(db)
        conversations = await conversation_service.get_all_conversations(current_user.id)  # Use authenticated user's ID
        
        logger.info(f"Retrieved {len(conversations)} conversations for user {current_user.email}")
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
    current_user: UserResponse = Depends(get_current_active_user),  # Add authentication
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get a specific conversation by ID (only if it belongs to the authenticated user).
    
    - **conversation_id**: MongoDB ObjectId of the conversation
    
    Requires authentication: Include JWT token in Authorization header.
    """
    try:
        conversation_service = ConversationService(db)
        conversation = await conversation_service.get_conversation(conversation_id)
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation {conversation_id} not found"
            )
        
        # Check if conversation belongs to current user
        if conversation.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: This conversation doesn't belong to you"
            )
            
        logger.info(f"Retrieved conversation: {conversation_id} for user: {current_user.email}")
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
    current_user: UserResponse = Depends(get_current_active_user),  # Add authentication
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get all messages for a specific conversation (only if it belongs to the authenticated user).
    
    - **conversation_id**: MongoDB ObjectId of the conversation
    
    Returns messages ordered chronologically (oldest first).
    Requires authentication: Include JWT token in Authorization header.
    """
    try:
        # First verify conversation exists and belongs to user
        conversation_service = ConversationService(db)
        conversation = await conversation_service.get_conversation(conversation_id)
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation {conversation_id} not found"
            )
        
        # Check ownership
        if conversation.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: This conversation doesn't belong to you"
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
    current_user: UserResponse = Depends(get_current_active_user),  # Add authentication
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Delete a conversation and all its messages (only if it belongs to the authenticated user).
    
    - **conversation_id**: MongoDB ObjectId of the conversation
    
    Requires authentication: Include JWT token in Authorization header.
    """
    try:
        # Verify conversation exists and belongs to user
        conversation_service = ConversationService(db)
        conversation = await conversation_service.get_conversation(conversation_id)
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation {conversation_id} not found"
            )
        
        # Check ownership
        if conversation.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: This conversation doesn't belong to you"
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
        
        logger.info(f"Deleted conversation {conversation_id} and {deleted_messages} messages for user {current_user.email}")
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        logger.error(f"Failed to delete conversation {conversation_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete conversation"
        )