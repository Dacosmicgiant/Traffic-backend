from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import settings
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class DatabaseService:
    """
    Handles MongoDB connection and provides database instance.
    Uses singleton pattern to ensure single connection.
    """
    
    client: Optional[AsyncIOMotorClient] = None
    database: Optional[AsyncIOMotorDatabase] = None

    @classmethod
    async def connect_to_mongo(cls):
        """Create database connection"""
        try:
            logger.info("Connecting to MongoDB...")
            cls.client = AsyncIOMotorClient(settings.mongodb_url)
            cls.database = cls.client[settings.database_name]
            
            # Test the connection
            await cls.client.admin.command('ping')
            logger.info("Successfully connected to MongoDB!")
            
        except Exception as e:
            logger.error(f"Error connecting to MongoDB: {e}")
            raise

    @classmethod
    async def close_mongo_connection(cls):
        """Close database connection"""
        if cls.client:
            cls.client.close()
            logger.info("MongoDB connection closed")

    @classmethod
    def get_database(cls) -> AsyncIOMotorDatabase:
        """Get database instance"""
        if cls.database is None:
            raise RuntimeError("Database not initialized. Call connect_to_mongo() first.")
        return cls.database


# Dependency function for FastAPI
async def get_database() -> AsyncIOMotorDatabase:
    """FastAPI dependency to inject database instance"""
    return DatabaseService.get_database()