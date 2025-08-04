from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.services.database import get_database
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.models.user import UserResponse
from typing import Optional

# HTTP Bearer token scheme for FastAPI
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncIOMotorDatabase = Depends(get_database)
) -> UserResponse:
    """
    FastAPI dependency to get the current authenticated user.
    
    This function:
    1. Extracts the JWT token from the Authorization header
    2. Verifies the token
    3. Fetches the user from database
    4. Returns the user information
    
    Args:
        credentials: JWT token from Authorization header
        db: Database connection
        
    Returns:
        Current user information
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    
    # Verify the JWT token
    token_data = AuthService.verify_token(credentials.credentials)
    
    # Get user from database
    user_service = UserService(db)
    user = await user_service.get_user_by_id(token_data.user_id)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def get_current_active_user(
    current_user: UserResponse = Depends(get_current_user)
) -> UserResponse:
    """
    FastAPI dependency to get current active user.
    This is just an alias for clarity.
    
    Args:
        current_user: User from get_current_user dependency
        
    Returns:
        Active user information
    """
    return current_user


def get_user_service(db: AsyncIOMotorDatabase = Depends(get_database)) -> UserService:
    """
    FastAPI dependency to provide UserService instance.
    
    Args:
        db: Database connection
        
    Returns:
        UserService instance
    """
    return UserService(db)