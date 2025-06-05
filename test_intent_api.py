#!/usr/bin/env python3
"""
Test script for the intent classification API integration.
Tests the classify_intent_and_entities function with various inputs.
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')

# Import the function from elven.py
from elven import classify_intent_and_entities, PHI2_API_URL

def test_intent_classification():
    """Test the intent classification with sample phrases."""
    
    print("🧪 Testing Intent Classification API Integration")
    print(f"📡 API URL: {PHI2_API_URL}")
    print("=" * 60)
    
    # Test phrases
    test_cases = [
        "Add buy milk to my todo list",
        "What's the weather in London?",
        "List my tasks",
        "Show me my todos",
        "How are you today?",
        "Send an email to John",
        "Add call mom tomorrow to my tasks",
        "What's the weather like in New York?"
    ]
    
    for i, phrase in enumerate(test_cases, 1):
        print(f"\n🔤 Test {i}: '{phrase}'")
        print("-" * 40)
        
        try:
            result = classify_intent_and_entities(phrase)
            print(f"✅ Result: {result}")
            
            # Analyze result
            intent = result.get('intent')
            if intent == 'todoist_add':
                task = result.get('task')
                due = result.get('due')
                print(f"   📝 Task: {task}")
                if due:
                    print(f"   📅 Due: {due}")
            elif intent == 'weather':
                location = result.get('location')
                print(f"   🌤️  Location: {location}")
            elif intent == 'todoist_list':
                print(f"   📋 List tasks requested")
            elif intent == 'null':
                print(f"   💬 General conversation")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 Test completed!")

def test_api_connection():
    """Test if the FastAPI endpoint is reachable."""
    import requests
    
    print("🔗 Testing API Connection")
    print("-" * 30)
    
    try:
        api_url = PHI2_API_URL or "http://localhost:8000"
        endpoint = f"{api_url.rstrip('/')}/api/convert"
        
        # Simple connection test
        response = requests.get(f"{api_url.rstrip('/')}/", timeout=5)
        print(f"✅ API is reachable at {api_url}")
        print(f"   Status: {response.status_code}")
        
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to API at {api_url}")
        print("   Make sure your FastAPI server is running!")
        return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🎤 Elven Voice Assistant - Intent API Test")
    print("=" * 50)
    
    # Test API connection first
    if test_api_connection():
        print("\n")
        test_intent_classification()
    else:
        print("\n💡 To start your FastAPI server:")
        print("   1. Make sure your Phi-2 FastAPI is running on localhost:8000")
        print("   2. Test endpoint: http://localhost:8000/api/convert")
        print("   3. Expected request: {\"text\": \"your text here\"}")
        sys.exit(1) 