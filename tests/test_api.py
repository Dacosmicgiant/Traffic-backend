# since we are in another directory, we need to add the parent directory to the path

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import requests
import json
import asyncio

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("🏥 Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")

def test_create_conversation():
    """Test creating a conversation"""
    print("💬 Testing conversation creation...")
    data = {"title": "Test Conversation About Traffic Laws"}
    response = requests.post(f"{BASE_URL}/api/v1/conversations/", json=data)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Created conversation: {result['id']}")
    print(f"Title: {result['title']}\n")
    return result['id']

def test_ask_question(conversation_id=None):
    """Test asking a question"""
    print("🤖 Testing AI question...")
    data = {
        "message": "What documents do I need for a driving license in India?",
        "conversation_id": conversation_id
    }
    response = requests.post(f"{BASE_URL}/api/v1/chat/ask", json=data)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"AI Response: {result['response'][:100]}...")
    print(f"Conversation ID: {result['conversation_id']}\n")
    return result['conversation_id']

def test_get_conversations():
    """Test getting all conversations"""
    print("📋 Testing get all conversations...")
    response = requests.get(f"{BASE_URL}/api/v1/conversations/")
    print(f"Status: {response.status_code}")
    conversations = response.json()
    print(f"Found {len(conversations)} conversations")
    for conv in conversations:
        print(f"  - {conv['title']} (Messages: {conv['message_count']})")
    print()

def test_get_messages(conversation_id):
    """Test getting messages from a conversation"""
    print("💭 Testing get conversation messages...")
    response = requests.get(f"{BASE_URL}/api/v1/conversations/{conversation_id}/messages")
    print(f"Status: {response.status_code}")
    messages = response.json()
    print(f"Found {len(messages)} messages:")
    for msg in messages:
        print(f"  {msg['role']}: {msg['content'][:50]}...")
    print()

def run_all_tests():
    """Run all tests in sequence"""
    print("🚀 Starting API Tests\n")
    
    # Test 1: Health check
    test_health()
    
    # Test 2: Create conversation
    conv_id = test_create_conversation()
    
    # Test 3: Ask question in new conversation
    conv_id2 = test_ask_question()
    
    # Test 4: Ask another question in existing conversation
    test_ask_question(conv_id2)
    
    # Test 5: Get all conversations
    test_get_conversations()
    
    # Test 6: Get messages from conversation
    test_get_messages(conv_id2)
    
    print("✅ All tests completed!")

if __name__ == "__main__":
    run_all_tests()