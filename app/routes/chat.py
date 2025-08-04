from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.services.database import get_database
from app.services.ai_service import AIServiceInterface, get_ai_service
from app.services.conversation_service import ConversationService
from app.services.message_service import MessageService
from app.models.message import ChatRequest, ChatResponse, MessageCreate
from app.models.conversation import ConversationCreate
import logging

logger = logging.getLogger(__name__)

# Create router instance
router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/ask", response_model=ChatResponse)
async def ask_question(
    request: ChatRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
    ai_service: AIServiceInterface = Depends(get_ai_service)
):
    """
    Ask a question about Indian traffic laws.
    
    This is the main endpoint for AI interactions.
    
    - **message**: Your question about Indian traffic laws
    - **conversation_id**: (Optional) Continue an existing conversation
    
    If no conversation_id is provided, a new conversation will be created.
    """
    try:
        conversation_service = ConversationService(db)
        message_service = MessageService(db)
        
        # Step 1: Handle conversation creation or validation
        if request.conversation_id:
            # Validate existing conversation
            conversation = await conversation_service.get_conversation(request.conversation_id)
            if not conversation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Conversation {request.conversation_id} not found"
                )
            conversation_id = request.conversation_id
        else:
            # Create new conversation with auto-generated title
            title = _generate_conversation_title(request.message)
            new_conversation = await conversation_service.create_conversation(
                ConversationCreate(title=title)
            )
            conversation_id = new_conversation.id
        
        # Step 2: Save user message to database
        user_message = await message_service.create_message(
            MessageCreate(
                role="user",
                content=request.message,
                conversation_id=conversation_id
            )
        )
        
        # Step 3: Get conversation history for AI context
        conversation_history = await message_service.get_conversation_history_for_ai(conversation_id)
        
        # Step 4: Generate AI response
        ai_response = await ai_service.generate_response(
            message=request.message,
            conversation_history=conversation_history[:-1]  # Exclude the message we just added
        )
        
        # Step 5: Save AI response to database
        assistant_message = await message_service.create_message(
            MessageCreate(
                role="assistant",
                content=ai_response,
                conversation_id=conversation_id
            )
        )
        
        # Step 6: Update conversation timestamp
        await conversation_service.update_conversation_timestamp(conversation_id)
        
        # Step 7: Return response
        logger.info(f"Processed question in conversation {conversation_id}")
        return ChatResponse(
            response=ai_response,
            conversation_id=conversation_id,
            message_id=assistant_message.id
        )
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process your question. Please try again."
        )


def _generate_conversation_title(message: str) -> str:
    """
    Generate a conversation title based on the first message.
    Keeps it simple and readable.
    
    Args:
        message: The user's first message
        
    Returns:
        Generated title (max 50 characters)
    """
    # Take first 50 characters and clean up
    title = message.strip()[:50]
    
    # If we cut off mid-word, remove the incomplete word
    if len(message) > 50:
        words = title.split()
        if len(words) > 1:
            title = " ".join(words[:-1]) + "..."
    
    return title if title else "New Traffic Law Question"