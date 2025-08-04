# since we are in another directory, we need to add the parent directory to the path

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.config import settings

print(f"App Name: {settings.app_name}")
print(f"Debug Mode: {settings.debug}")
print(f"MongoDB URL: {settings.mongodb_url}")
print(f"Database Name: {settings.database_name}")
print(f"Gemini API Key: {settings.gemini_api_key}")