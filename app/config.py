from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Uses Pydantic for automatic validation and parsing.
    """
    
    # Database config
    mongodb_url: str
    database_name: str = "indian_traffic_ai"
    
    # Gemini API config
    gemini_api_key: str
    
    # Application config
    debug: bool = True
    app_name: str = "Indian Traffic Law AI Assistant"
    
    # API config
    api_v1_prefix: str = "/api/v1"
    
    class Config:
        # tells Pydantic to read from .env
        
        env_file = ".env"
        env_file_encoding = "utf-8"
        
# Creating a global settings instance which can be imported elsewhere 
settings = Settings()