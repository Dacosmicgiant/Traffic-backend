import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def debug_registration():
    """Debug registration with detailed error info"""
    print("🔍 Debugging registration...")
    
    user_data = {
        "email": "debuguser2@example.com",  # Use different email
        "full_name": "Debug User Two",
        "password": "testpassword123"
    }
    
    print(f"Sending data: {json.dumps(user_data, indent=2)}")
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        try:
            response_json = response.json()
            print(f"Response JSON: {json.dumps(response_json, indent=2)}")
        except:
            print(f"Response Text: {response.text}")
            
        if response.status_code == 201:
            print("✅ Registration successful!")
        else:
            print("❌ Registration failed!")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    debug_registration()