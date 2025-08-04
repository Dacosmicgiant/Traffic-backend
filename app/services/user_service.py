from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.user import UserCreate, UserInDB, UserResponse
from app.services.auth_service import AuthService
from typing import Optional
from bson import ObjectId

import logging

logger = logging.getLogger(__name__)


class UserService:
    """
    Service class for user database operations.
    Handles user registration, retrieval, and management.
    """
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.db = database
        self.users_collection = database.users

    async def create_user(self, user_data: UserCreate) -> UserResponse:
        """
        Create a new user account.
        
        Args:
            user_data: User registration data
            
        Returns:
            Created user information (without password)
            
        Raises:
            ValueError: If email already exists
        """
        try:
            # Check if user already exists
            existing_user = await self.get_user_by_email(user_data.email)
            if existing_user:
                raise ValueError("Email already registered")
            
            # Hash the password
            hashed_password = AuthService.hash_password(user_data.password)
            
            # Prepare user document for database
            user_dict = user_data.model_dump(exclude={"password"})
            user_dict["hashed_password"] = hashed_password
            user_dict["created_at"] = datetime.now(timezone.utc)
            user_dict["updated_at"] = datetime.now(timezone.utc)
            
            # Insert into database
            result = await self.users_collection.insert_one(user_dict)
            
            # Fetch the created user
            created_user = await self.users_collection.find_one(
                {"_id": result.inserted_id}
            )
            
            # Convert to response model (excludes sensitive data)
            return self._convert_to_response(created_user)
            
        except ValueError:
            raise  # Re-raise validation errors
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise

    async def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        """
        Get user by email address.
        
        Args:
            email: User's email address
            
        Returns:
            User data including hashed password, or None if not found
        """
        try:
            user_doc = await self.users_collection.find_one({"email": email})
            if user_doc:
                return self._convert_to_db_model(user_doc)
            return None
            
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {e}")
            return None

    async def get_user_by_id(self, user_id: str) -> Optional[UserResponse]:
        """
        Get user by their ID.
        
        Args:
            user_id: MongoDB ObjectId as string
            
        Returns:
            User data (without sensitive information), or None if not found
        """
        try:
            if not ObjectId.is_valid(user_id):
                return None
                
            user_doc = await self.users_collection.find_one(
                {"_id": ObjectId(user_id)}
            )
            
            if user_doc:
                return self._convert_to_response(user_doc)
            return None
            
        except Exception as e:
            logger.error(f"Error getting user by ID {user_id}: {e}")
            return None

    async def update_user_activity(self, user_id: str) -> bool:
        """
        Update user's last activity timestamp.
        Called when user performs actions.
        
        Args:
            user_id: MongoDB ObjectId as string
            
        Returns:
            True if updated successfully, False otherwise
        """
        try:
            if not ObjectId.is_valid(user_id):
                return False
                
            result = await self.users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"updated_at": datetime.now(timezone.utc)}}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error updating user activity {user_id}: {e}")
            return False

    def _convert_to_db_model(self, user_dict: dict) -> UserInDB:
        """
        Convert MongoDB document to UserInDB model.
        Includes sensitive data like hashed_password.
        
        Args:
            user_dict: Raw MongoDB document
            
        Returns:
            UserInDB Pydantic model
        """
        return UserInDB(
            id=user_dict["_id"],
            email=user_dict["email"],
            full_name=user_dict["full_name"],
            hashed_password=user_dict["hashed_password"],
            is_active=user_dict.get("is_active", True),
            created_at=user_dict.get("created_at"),
            updated_at=user_dict.get("updated_at")
        )

    def _convert_to_response(self, user_dict: dict) -> UserResponse:
        """
        Convert MongoDB document to UserResponse model.
        Excludes sensitive data like passwords.
        
        Args:
            user_dict: Raw MongoDB document
            
        Returns:
            UserResponse Pydantic model
        """
        return UserResponse(
            id=str(user_dict["_id"]),
            email=user_dict["email"],
            full_name=user_dict["full_name"],
            is_active=user_dict.get("is_active", True),
            created_at=user_dict.get("created_at")
        )