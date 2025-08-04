# since we are in another directory, we need to add the parent directory to the path

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
from app.services.ai_service import get_ai_service

async def test_ai_service():
    ai_service = get_ai_service()
    
    # Test with empty conversation history
    response = await ai_service.generate_response(
        "What is the speed limit on highways in India?", 
        []
    )
    print(f"AI Response: {response}")

# Run the test
if __name__ == "__main__":
    asyncio.run(test_ai_service())