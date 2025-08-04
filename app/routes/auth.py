from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.services.database import get_database
from app.services.user_service import UserService
from app.services.auth_service import AuthService
from app.services.dependencies import get_current_active_user
from app.models.user import UserCreate, UserLogin, UserResponse, Token
import logging

logger = logging.getLogger(__name__)

# Create router instance
router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Register a new user account.
    
    - **email**: Valid email address (must be unique)
    - **full_name**: User's full name (2-100 characters)
    - **password**: Password (minimum 6 characters)
    
    Returns JWT token for immediate login after registration.
    """
    try:
        user_service = UserService(db)
        
        # Create the user (this checks for email duplicates)
        new_user = await user_service.create_user(user_data)
        
        # Get the full user data for token creation
        user_in_db = await user_service.get_user_by_email(user_data.email)
        
        # Create access token
        access_token = AuthService.create_token_for_user(user_in_db)
        
        logger.info(f"New user registered: {user_data.email}")
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user=new_user
        )
        
    except ValueError as e:
        # Handle duplicate email error
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error during user registration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again."
        )


@router.post("/login", response_model=Token)
async def login_user(
    login_data: UserLogin,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Login with email and password.
    
    - **email**: Your registered email address
    - **password**: Your account password
    
    Returns JWT token for accessing protected endpoints.
    """
    try:
        user_service = UserService(db)
        
        # Get user from database
        user = await user_service.get_user_by_email(login_data.email)
        
        # Authenticate user
        if not AuthService.authenticate_user(user, login_data.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Update user activity
        await user_service.update_user_activity(str(user.id))
        
        # Create access token
        access_token = AuthService.create_token_for_user(user)
        
        # Convert user to response format
        user_response = await user_service.get_user_by_id(str(user.id))
        
        logger.info(f"User logged in: {login_data.email}")
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user=user_response
        )
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        logger.error(f"Error during user login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed. Please try again."
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Get current authenticated user's information.
    
    Requires valid JWT token in Authorization header.
    """
    return current_user


@router.post("/logout")
async def logout_user(
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    Logout current user.
    
    Note: Since we're using stateless JWT tokens, this just confirms
    the user is authenticated. In a production system, you might
    want to implement token blacklisting.
    """
    logger.info(f"User logged out: {current_user.email}")
    return {"message": "Successfully logged out"}