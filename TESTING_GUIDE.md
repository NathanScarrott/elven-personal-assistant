# 🎤 Elven Voice Assistant - Testing Guide

## Prerequisites Checklist

### ✅ 1. Dependencies Installed
```bash
# Install system dependencies (macOS)
brew install portaudio

# Install Python dependencies
pip3 install -r requirements.txt
pip3 install fastapi uvicorn
```

### ✅ 2. Environment Setup
Create `.env.local` file:
```bash
echo "PHI2_API_URL=http://localhost:8000" > .env.local
```

Add your API keys to `.env.local`:
```env
PHI2_API_URL=http://localhost:8000
PORCUPINE_ACCESS_KEY=your_porcupine_key_here
ELEVENLABS_API_KEY=your_elevenlabs_key_here
TODOIST_API_TOKEN=your_todoist_token_here
OPENWEATHERMAP_API_KEY=your_openweathermap_key_here
```

## 🧪 Testing Methods

### Method 1: Quick API Test (Recommended for Development)

**Step 1: Start Mock FastAPI Server**
```bash
# Terminal 1: Start the mock server
python3 mock_phi2_server.py
```

**Step 2: Test Intent Classification**
```bash
# Terminal 2: Run the test script
python3 test_intent_api.py
```

**Step 3: Manual API Test**
```bash
# Test the API directly
curl -X POST http://localhost:8000/api/convert \
  -H "Content-Type: application/json" \
  -d '{"text": "Add buy milk to my todo list"}'
```

### Method 2: Full Voice Assistant Test

**Prerequisites:**
- Microphone access
- Porcupine access key
- Your actual FastAPI server running

**Step 1: Start Your FastAPI Server**
```bash
# Start your actual Phi-2 FastAPI server on localhost:8000
# (Replace this with your actual server startup command)
python3 your_phi2_server.py
```

**Step 2: Run Voice Assistant**
```bash
python3 elven.py
```

**Step 3: Voice Interaction Flow**
1. Say "terminator" (wake word)
2. Wait for recording prompt
3. Speak your command:
   - "Add buy milk to my todo list"
   - "What's the weather in London?"
   - "List my tasks"
   - "How are you?"
4. Listen to response
5. Say "goodbye" to exit

## 🎯 Test Cases

### Intent Classification Tests

| Input | Expected Intent | Expected Entities |
|-------|----------------|-------------------|
| "Add buy milk to my todo list" | `todoist_add` | `task: "buy milk"` |
| "Add call mom tomorrow" | `todoist_add` | `task: "call mom", due: "tomorrow"` |
| "What's the weather in London?" | `weather` | `location: "London"` |
| "List my tasks" | `todoist_list` | - |
| "Show me my todos" | `todoist_list` | - |
| "How are you?" | `null` | - |
| "Send email to John" | `null` | - |

### API Response Format Test

**Your FastAPI should return:**
```json
{
  "intent": "add_task",
  "task": "buy milk",
  "due_date": null,
  "location": null
}
```

**Voice Assistant expects:**
```json
{
  "intent": "todoist_add",
  "task": "buy milk", 
  "due": null,
  "location": null
}
```

## 🐛 Troubleshooting

### Common Issues

**1. "Cannot connect to API"**
- ✅ Check if FastAPI server is running: `curl http://localhost:8000/`
- ✅ Verify PHI2_API_URL in .env.local
- ✅ Check firewall/port access

**2. "PyAudio/PortAudio errors"**
- ✅ Install PortAudio: `brew install portaudio`
- ✅ Reinstall PyAudio: `pip3 install --force-reinstall pyaudio`

**3. "Porcupine wake word not working"**
- ✅ Check PORCUPINE_ACCESS_KEY in .env.local
- ✅ Verify microphone permissions
- ✅ Speak clearly: "terminator"

**4. "Whisper model download"**
- ✅ First run downloads ~244MB model
- ✅ Wait for download to complete
- ✅ Check internet connection

**5. "Intent mapping issues"**
- ✅ Check server logs for request/response
- ✅ Verify API response format matches expected schema
- ✅ Test with mock server first

### Debug Commands

```bash
# Test API connection
curl http://localhost:8000/

# Test intent endpoint
curl -X POST http://localhost:8000/api/convert \
  -H "Content-Type: application/json" \
  -d '{"text": "test message"}'

# Check environment variables
python3 -c "from elven import PHI2_API_URL; print('API URL:', PHI2_API_URL)"

# Test imports
python3 -c "import elven; print('All imports successful')"
```

## 📊 Expected Behavior

### Successful Test Flow

1. **API Connection**: ✅ Server responds on localhost:8000
2. **Intent Classification**: ✅ Returns proper JSON format
3. **Intent Mapping**: ✅ Converts API response to voice assistant format
4. **Action Execution**: ✅ Todoist/Weather actions work
5. **Text-to-Speech**: ✅ Responses are spoken
6. **Error Handling**: ✅ Graceful fallbacks on API failures

### Performance Expectations

- **API Response Time**: < 2 seconds
- **Total Processing**: < 5 seconds from speech to response
- **Memory Usage**: ~500MB (Whisper model)
- **Error Recovery**: Automatic fallback to "null" intent

## 🚀 Production Deployment

### Replace Mock Server

1. Stop mock server
2. Start your actual Phi-2 FastAPI server
3. Update PHI2_API_URL if different port/host
4. Test with real model responses

### Performance Optimization

- Use Whisper "tiny" model for faster transcription
- Implement API response caching
- Add retry logic for API failures
- Monitor API response times

## 📝 API Contract

Your FastAPI must implement:

**Endpoint**: `POST /api/convert`

**Request**:
```json
{
  "text": "user speech transcription"
}
```

**Response**:
```json
{
  "intent": "add_task|list_tasks|get_weather|conversation",
  "task": "task description (for add_task)",
  "due_date": "due date (for add_task)", 
  "location": "location (for get_weather)"
}
```

**Error Handling**: Return HTTP 500 on errors, voice assistant will fallback to "null" intent.

---

**Happy Testing! 🎉**

If you encounter issues, check the logs and verify each component works independently before testing the full system. 