from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from app.models.user import UserInDB, TokenData
import logging

logger = logging.getLogger(__name__)

# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration
SECRET_KEY = "your-super-secret-key-change-this-in-production"  # In production, use environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class AuthService:
    """
    Service class for authentication operations.
    Handles password hashing, JWT tokens, and user verification.
    """
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a plain password using bcrypt.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password string
        """
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain password against its hash.
        
        Args:
            plain_password: Plain text password from user
            hashed_password: Stored hash from database
            
        Returns:
            True if password matches, False otherwise
        """
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Create a JWT access token.
        
        Args:
            data: Data to encode in the token (user_id, email, etc.)
            expires_delta: Optional custom expiration time
            
        Returns:
            JWT token string
        """
        to_encode = data.copy()
        
        # Set expiration time
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        
        # Create and return JWT token
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> TokenData:
        """
        Verify and decode a JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            TokenData with user information
            
        Raises:
            HTTPException: If token is invalid or expired
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            # Decode the JWT token
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            
            # Extract user information
            email: str = payload.get("sub")
            user_id: str = payload.get("user_id")
            
            if email is None or user_id is None:
                logger.warning("Token missing required fields")
                raise credentials_exception
                
            token_data = TokenData(email=email, user_id=user_id)
            return token_data
            
        except JWTError as e:
            logger.warning(f"JWT verification failed: {e}")
            raise credentials_exception
    
    @staticmethod
    def authenticate_user(user: UserInDB, password: str) -> bool:
        """
        Authenticate a user by verifying their password.
        
        Args:
            user: User object from database
            password: Plain text password from login request
            
        Returns:
            True if authentication successful, False otherwise
        """
        if not user:
            return False
        if not AuthService.verify_password(password, user.hashed_password):
            return False
        return True
    
    @staticmethod
    def create_token_for_user(user: UserInDB) -> str:
        """
        Create an access token for a specific user.
        
        Args:
            user: User object from database
            
        Returns:
            JWT access token string
        """
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = AuthService.create_access_token(
            data={"sub": user.email, "user_id": str(user.id)},
            expires_delta=access_token_expires
        )
        return access_token