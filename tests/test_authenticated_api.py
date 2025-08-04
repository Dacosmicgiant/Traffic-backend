import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def register_and_login():
    """Register a new user and get auth token"""
    print("👤 Registering new user...")
    
    user_data = {
        "email": "chatuser@example.com",
        "full_name": "Chat Test User",
        "password": "securepassword123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
    if response.status_code == 201:
        result = response.json()
        print(f"✅ User registered: {result['user']['full_name']}")
        return result['access_token']
    elif response.status_code == 400 and "Email already registered" in response.json().get('detail', ''):
        # User exists, try login
        print("User already exists, trying login...")
        login_data = {
            "email": user_data["email"],
            "password": user_data["password"]
        }
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ User logged in: {result['user']['full_name']}")
            return result['access_token']
    
    print(f"❌ Authentication failed: {response.json()}")
    return None

def test_authenticated_chat(token):
    """Test chat functionality with authentication"""
    print("\n🤖 Testing authenticated chat...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Ask first question (creates new conversation)
    chat_data = {
        "message": "What is the penalty for not wearing a helmet while riding a motorcycle in India?"
    }
    
    response = requests.post(f"{BASE_URL}/chat/ask", json=chat_data, headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Chat successful!")
        print(f"AI Response: {result['response'][:100]}...")
        print(f"Conversation ID: {result['conversation_id']}")
        return result['conversation_id']
    else:
        print(f"❌ Chat failed: {response.json()}")
        return None

def test_continue_conversation(token, conversation_id):
    """Test continuing an existing conversation"""
    print("\n💬 Testing conversation continuation...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Ask follow-up question
    chat_data = {
        "message": "What about the penalty for riding without a license?",
        "conversation_id": conversation_id
    }
    
    response = requests.post(f"{BASE_URL}/chat/ask", json=chat_data, headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Conversation continuation successful!")
        print(f"AI Response: {result['response'][:100]}...")
    else:
        print(f"❌ Conversation continuation failed: {response.json()}")

def test_get_authenticated_conversations(token):
    """Test getting user's conversations"""
    print("\n📋 Testing authenticated conversation list...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/conversations/", headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        conversations = response.json()
        print(f"✅ Found {len(conversations)} conversations")
        for conv in conversations:
            print(f"  - {conv['title']} (Messages: {conv['message_count']})")
    else:
        print(f"❌ Failed to get conversations: {response.json()}")

def test_unauthenticated_access():
    """Test that endpoints properly reject unauthenticated requests"""
    print("\n🚫 Testing unauthenticated access...")
    
    # Try chat without token
    chat_data = {"message": "Test message"}
    response = requests.post(f"{BASE_URL}/chat/ask", json=chat_data)
    print(f"Chat without token - Status: {response.status_code}")
    
    if response.status_code == 401:
        print("✅ Unauthenticated chat properly rejected!")
    
    # Try get conversations without token
    response = requests.get(f"{BASE_URL}/conversations/")
    print(f"Conversations without token - Status: {response.status_code}")
    
    if response.status_code == 401:
        print("✅ Unauthenticated conversations properly rejected!")

def run_authenticated_tests():
    """Run all authenticated API tests"""
    print("🚀 Starting Authenticated API Tests\n")
    
    # Get authentication token
    token = register_and_login()
    
    if token:
        # Test authenticated chat
        conversation_id = test_authenticated_chat(token)
        
        if conversation_id:
            # Test conversation continuation
            test_continue_conversation(token, conversation_id)
        
        # Test getting conversations
        test_get_authenticated_conversations(token)
    
    # Test unauthenticated access
    test_unauthenticated_access()
    
    print("\n✅ All authenticated tests completed!")

if __name__ == "__main__":
    run_authenticated_tests()