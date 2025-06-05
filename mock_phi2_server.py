#!/usr/bin/env python3
"""
Mock FastAPI server for testing the Elven Voice Assistant integration.
This simulates the expected responses from a Phi-2 intent classification API.
"""

from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import re

app = FastAPI(title="Mock Phi-2 Intent Classification API")

class TextRequest(BaseModel):
    text: str

class IntentResponse(BaseModel):
    intent: str
    task: str = None
    due_date: str = None
    location: str = None

def classify_mock_intent(text: str) -> IntentResponse:
    """
    Mock intent classification logic.
    This simulates what a real Phi-2 model might return.
    """
    text_lower = text.lower()
    
    # Task-related keywords
    task_keywords = ["add", "create", "todo", "task", "remind", "remember"]
    list_keywords = ["list", "show", "what", "tasks", "todos"]
    weather_keywords = ["weather", "temperature", "rain", "sunny", "cloudy"]
    
    # Check for task addition
    if any(keyword in text_lower for keyword in task_keywords):
        # Extract task content
        task_match = re.search(r'(?:add|create|todo|task|remind|remember)\s+(.+?)(?:\s+to\s+|$)', text_lower)
        task = task_match.group(1).strip() if task_match else text.strip()
        
        # Extract due date
        due_date = None
        due_patterns = ["today", "tomorrow", "tonight", "this week", "next week", 
                       "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        for pattern in due_patterns:
            if pattern in text_lower:
                due_date = pattern
                # Remove due date from task
                task = re.sub(rf'\b{pattern}\b', '', task, flags=re.IGNORECASE).strip()
                break
        
        return IntentResponse(
            intent="add_task",
            task=task,
            due_date=due_date
        )
    
    # Check for task listing
    elif any(keyword in text_lower for keyword in list_keywords) and ("task" in text_lower or "todo" in text_lower):
        return IntentResponse(intent="list_tasks")
    
    # Check for weather
    elif any(keyword in text_lower for keyword in weather_keywords):
        # Extract location
        location_match = re.search(r'(?:in|for)\s+([A-Za-z\s]+?)(?:\?|$)', text)
        location = location_match.group(1).strip() if location_match else None
        
        return IntentResponse(
            intent="get_weather",
            location=location
        )
    
    # Default to conversation
    else:
        return IntentResponse(intent="conversation")

@app.get("/")
def root():
    return {"message": "Mock Phi-2 Intent Classification API", "status": "running"}

@app.post("/api/convert", response_model=IntentResponse)
def convert_text(request: TextRequest):
    """
    Convert text to intent classification.
    This endpoint simulates the expected Phi-2 API behavior.
    """
    print(f"📝 Processing: '{request.text}'")
    
    response = classify_mock_intent(request.text)
    
    print(f"🤖 Response: {response.dict()}")
    
    return response

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "mock-phi2-api"}

if __name__ == "__main__":
    print("🚀 Starting Mock Phi-2 FastAPI Server")
    print("📡 Server will run on: http://localhost:8000")
    print("🔗 API endpoint: http://localhost:8000/api/convert")
    print("📋 Test endpoint: http://localhost:8000/")
    print("\n💡 To test manually:")
    print("curl -X POST http://localhost:8000/api/convert \\")
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"text": "Add buy milk to my todo list"}\'')
    print("\nPress Ctrl+C to stop the server\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000) 