# since we are in another directory, we need to add the parent directory to the path

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.auth_service import AuthService

# Test password hashing
password = "mySecurePassword123"
hashed = AuthService.hash_password(password)
print(f"Original: {password}")
print(f"Hashed: {hashed}")

# Test password verification
is_valid = AuthService.verify_password(password, hashed)
print(f"Password verification: {is_valid}")

# Test JWT token creation
token_data = {"sub": "user@example.com", "user_id": "123456"}
token = AuthService.create_access_token(token_data)
print(f"JWT Token: {token[:50]}...")

# Test token verification
try:
    verified_data = AuthService.verify_token(token)
    print(f"Token verified successfully: {verified_data.email}")
except Exception as e:
    print(f"Token verification failed: {e}")