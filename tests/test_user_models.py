# since we are in another directory, we need to add the parent directory to the path

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# test_user_models.py
from app.models.user import UserCreate, UserLogin

# Test user creation model
user_data = UserCreate(
    email="test@example.com",
    full_name="Test User",
    password="securepassword123"
)
print(f"User model created: {user_data.email}")

# Test login model  
login_data = UserLogin(
    email="test@example.com",
    password="securepassword123"
)
print(f"Login model created: {login_data.email}")