import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_user_registration():
    """Test user registration"""
    print("👤 Testing user registration...")
    
    user_data = {
        "email": "testuser@example.com",
        "full_name": "Test User",
        "password": "securepassword123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 201:
        result = response.json()
        print(f"✅ Registration successful!")
        print(f"User: {result['user']['full_name']} ({result['user']['email']})")
        print(f"Token: {result['access_token'][:30]}...")
        return result['access_token']
    else:
        print(f"❌ Registration failed: {response.json()}")
        return None

def test_user_login():
    """Test user login"""
    print("\n🔐 Testing user login...")
    
    login_data = {
        "email": "testuser@example.com",
        "password": "securepassword123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Login successful!")
        print(f"User: {result['user']['full_name']}")
        print(f"Token: {result['access_token'][:30]}...")
        return result['access_token']
    else:
        print(f"❌ Login failed: {response.json()}")
        return None

def test_protected_endpoint(token):
    """Test accessing protected endpoint"""
    print("\n🛡️ Testing protected endpoint...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Protected endpoint access successful!")
        print(f"Current user: {result['full_name']} ({result['email']})")
        return result
    else:
        print(f"❌ Protected endpoint failed: {response.json()}")
        return None

def test_invalid_token():
    """Test with invalid token"""
    print("\n🚫 Testing invalid token...")
    
    headers = {"Authorization": "Bearer invalid_token_here"}
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 401:
        print("✅ Invalid token properly rejected!")
    else:
        print(f"❌ Expected 401, got {response.status_code}")

def test_duplicate_registration():
    """Test registering with same email twice"""
    print("\n🔄 Testing duplicate email registration...")
    
    user_data = {
        "email": "testuser@example.com",  # Same email as before
        "full_name": "Another User",
        "password": "anotherpassword"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 400:
        print("✅ Duplicate email properly rejected!")
        print(f"Error: {response.json()['detail']}")
    else:
        print(f"❌ Expected 400, got {response.status_code}")

def run_auth_tests():
    """Run all authentication tests"""
    print("🚀 Starting Authentication Tests\n")
    
    # Test 1: Register new user
    token = test_user_registration()
    
    if token:
        # Test 2: Login with same user
        login_token = test_user_login()
        
        # Test 3: Access protected endpoint
        if login_token:
            test_protected_endpoint(login_token)
        
        # Test 4: Test invalid token
        test_invalid_token()
        
        # Test 5: Test duplicate registration
        test_duplicate_registration()
    
    print("\n✅ All authentication tests completed!")

if __name__ == "__main__":
    run_auth_tests()