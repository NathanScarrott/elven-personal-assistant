import os
from dotenv import load_dotenv
import pvporcupine
import pyaudio
import struct
import wave
import whisper
import time
import subprocess
import requests
from openai import OpenAI
import warnings
import re

warnings.filterwarnings("ignore", category=UserWarning)

# Load environment variables from .env.local
load_dotenv('.env.local')

# Placeholder imports for each module (to be implemented)
# import porcupine
# import whisper
# import openai
# import requests
# import smtplib

# Load API keys and tokens
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
TODOIST_API_TOKEN = os.getenv('TODOIST_API_TOKEN')
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
GMAIL_USER = os.getenv('GMAIL_USER')
GMAIL_PASSWORD = os.getenv('GMAIL_PASSWORD')
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = os.getenv('SMTP_PORT')
GOOGLE_CALENDAR_API_KEY = os.getenv('GOOGLE_CALENDAR_API_KEY')
NOTION_API_KEY = os.getenv('NOTION_API_KEY')
OPENWEATHERMAP_API_KEY = os.getenv('OPENWEATHERMAP_API_KEY')
GOOGLE_SEARCH_API_KEY = os.getenv('GOOGLE_SEARCH_API_KEY')
PORCUPINE_ACCESS_KEY = os.getenv('PORCUPINE_ACCESS_KEY')
PHI2_API_URL = os.getenv('PHI2_API_URL', 'http://localhost:8000')

STOP_PHRASES = ["goodbye"]

INTENT_MODEL = "google/gemini-2.5-flash-preview"
RESPONSE_MODEL = "google/gemini-2.5-flash-preview"

def record_audio(filename="command.wav", sample_rate=16000, silence_threshold=500, silence_duration=2.0):
    print("Recording... Speak now!")
    pa = pyaudio.PyAudio()
    stream = pa.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=sample_rate,
                    input=True,
                    frames_per_buffer=1024)
    frames = []
    print("(Waiting for you to start speaking...)")
    # Wait for user to start speaking
    while True:
        data = stream.read(1024, exception_on_overflow=False)
        audio_data = struct.unpack(str(len(data)//2) + 'h', data)
        energy = max(abs(sample) for sample in audio_data)
        if energy > silence_threshold:
            frames.append(data)
            print("Speech detected. Recording...")
            break
    # Now record until 2 seconds of silence
    silent_chunks = 0
    required_silent_chunks = int((sample_rate / 1024) * silence_duration)
    while True:
        data = stream.read(1024, exception_on_overflow=False)
        frames.append(data)
        audio_data = struct.unpack(str(len(data)//2) + 'h', data)
        energy = max(abs(sample) for sample in audio_data)
        if energy < silence_threshold:
            silent_chunks += 1
        else:
            silent_chunks = 0
        if silent_chunks > required_silent_chunks:
            print("Silence detected. Stopping recording.")
            break
    stream.stop_stream()
    stream.close()
    pa.terminate()
    wf = wave.open(filename, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(pa.get_sample_size(pyaudio.paInt16))
    wf.setframerate(sample_rate)
    wf.writeframes(b''.join(frames))
    wf.close()
    print(f"Audio recorded to {filename}")
    return filename

def transcribe_audio(path):
    print("Transcribing audio...")
    model = whisper.load_model("small")
    result = model.transcribe(path, language="en")
    print("Transcription:", result["text"])
    return result["text"]

def listen_for_wake_word():
    print("Listening for wake word ('terminator')...")
    porcupine = pvporcupine.create(access_key=PORCUPINE_ACCESS_KEY, keywords=["terminator"])
    pa = pyaudio.PyAudio()
    audio_stream = pa.open(
        rate=porcupine.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine.frame_length
    )
    try:
        while True:
            pcm = audio_stream.read(porcupine.frame_length, exception_on_overflow=False)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
            result = porcupine.process(pcm)
            if result >= 0:
                print("Wake word detected!")
                break
    finally:
        audio_stream.stop_stream()
        audio_stream.close()
        pa.terminate()
        porcupine.delete()

def speak_mac(text):
    # Use macOS 'say' command for TTS
    subprocess.run(["say", text])

def speak_elevenlabs(text, voice_id=None):
    api_key = ELEVENLABS_API_KEY
    if not api_key:
        print("[WARN] ELEVENLABS_API_KEY not set. Falling back to macOS say.")
        speak_mac(text)
        return
    if not voice_id:
        # Default to Beezle Wheezelby
        voice_id = "BBfN7Spa3cqLPH1xAS22"
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json"
    }
    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1"
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        with open("output.mp3", "wb") as f:
            f.write(response.content)
        # Play the audio on macOS
        subprocess.run(["afplay", "output.mp3"])
    else:
        print(f"[ERROR] ElevenLabs API error: {response.status_code} {response.text}")
        speak_mac(text)

def ask_gpt_openrouter(prompt):
    api_key = OPENROUTER_API_KEY
    if not api_key:
        print("[ERROR] OPENROUTER_API_KEY not set.")
        return "I'm sorry, I can't process your request right now."
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )
    system_prompt = (
        "You are Elven, a wise, helpful, and friendly AI assistant with a touch of fantasy. "
        "You speak concisely, with a gentle and encouraging tone, as if you are a trusted magical guide. "
        "Keep your answers short and to the point within 25 words. "
        "Do not include any Markdown, asterisks, or model names in your response. "
        "Do not mention you are an AI or language model. Speak as Elven only."
    )
    print(f"[Main Response] Using model: {RESPONSE_MODEL}")
    completion = client.chat.completions.create(
        model=RESPONSE_MODEL,
        max_tokens=40,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
    )
    return completion.choices[0].message.content

def add_todoist_task(task, token=TODOIST_API_TOKEN):
    # Extract due date if present
    due_phrases = ["today", "tomorrow", "tonight", "this week", "next week", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    due_string = None
    for phrase in due_phrases:
        if phrase in task.lower():
            due_string = phrase
            # Remove the due phrase from the task content
            task = re.sub(rf"\b{phrase}\b", "", task, flags=re.IGNORECASE).strip()
            break
    headers = {"Authorization": f"Bearer {token}"}
    data = {"content": task}
    if due_string:
        data["due_string"] = due_string
    response = requests.post(
        "https://api.todoist.com/rest/v2/tasks", headers=headers, json=data
    )
    if response.status_code == 200 or response.status_code == 204:
        if due_string:
            return f"Task added: {task} (due {due_string})"
        else:
            return f"Task added: {task}"
    else:
        return f"Failed to add task: {response.text}"

def list_todoist_tasks(token=TODOIST_API_TOKEN):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        "https://api.todoist.com/rest/v2/tasks", headers=headers
    )
    if response.status_code == 200:
        tasks = response.json()
        if not tasks:
            return "You have no tasks."
        return "Your tasks are: " + ", ".join(task["content"] for task in tasks)
    else:
        return f"Failed to fetch tasks: {response.text}"

def get_weather(city, api_key=OPENWEATHERMAP_API_KEY):
    if not api_key:
        return "Weather API key not set."
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        temp = data['main']['temp']
        desc = data['weather'][0]['description']
        return f"The weather in {city} is {desc} with a temperature of {temp}°C."
    else:
        return f"Could not fetch weather for {city}."

def classify_intent_and_entities(transcription):
    """
    Classify intent and extract entities using local FastAPI endpoint with Phi-2 model.
    
    Args:
        transcription (str): The transcribed user speech
        
    Returns:
        dict: Intent classification with format:
              {"intent": str, "task": str|None, "due": str|None, "location": str|None}
    """
    api_url = PHI2_API_URL
    if not api_url:
        print("[ERROR] PHI2_API_URL not set. Falling back to null intent.")
        return {"intent": "null", "task": None, "due": None, "location": None}
    
    # Prepare the request
    endpoint = f"{api_url.rstrip('/')}/api/convert"
    payload = {"text": transcription}
    
    try:
        print(f"[Intent Extraction] Calling local API: {endpoint}")
        response = requests.post(
            endpoint,
            json=payload,
            timeout=30,  # 30-second timeout
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code != 200:
            print(f"[ERROR] API returned status {response.status_code}: {response.text}")
            return {"intent": "null", "task": None, "due": None, "location": None}
        
        # Parse the response
        try:
            api_response = response.json()
            print(f"[DEBUG] Raw API Response: {api_response}")
        except ValueError as e:
            print(f"[ERROR] Failed to parse JSON response: {e}")
            return {"intent": "null", "task": None, "due": None, "location": None}
        
        # Handle different response formats
        if "structured_data" in api_response:
            # Format from actual Phi-2 API
            structured_data = api_response["structured_data"]
            api_intent = structured_data.get("intent", "").lower()
            task = structured_data.get("task")
            location = structured_data.get("location")
            schedule = structured_data.get("schedule") or structured_data.get("datetime")
        else:
            # Format from mock API
            api_intent = api_response.get("intent", "").lower()
            task = api_response.get("task")
            location = api_response.get("location") 
            schedule = api_response.get("due_date")
        
        # Use model's intent directly (no mapping needed)
        result = {
            "intent": api_intent,  # Use your model's intent directly
            "task": None,
            "due": None,
            "location": None
        }
        
        if api_intent == "add_task":
            # Extract task and due date
            result["task"] = task
            result["due"] = schedule
            
        elif api_intent == "get_weather":
            # Extract location
            result["location"] = location
            
        elif api_intent == "send_email":
            # Could extract recipient, subject, body in the future
            pass
        
        print(f"[Intent Extraction] Result: {result}")
        return result
        
    except requests.exceptions.Timeout:
        print("[ERROR] API request timed out (30 seconds)")
        return {"intent": "null", "task": None, "due": None, "location": None}
    
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] Could not connect to API at {endpoint}")
        return {"intent": "null", "task": None, "due": None, "location": None}
    
    except Exception as e:
        print(f"[ERROR] Unexpected error calling API: {e}")
        return {"intent": "null", "task": None, "due": None, "location": None}

def main():
    print("🎤 Elven Personal Assistant starting up...")
    print("📝 No wake word needed - press Enter to record each command")
    print("💬 Say 'goodbye' or 'quit' to exit")
    print("=" * 50)
    
    while True:
        # Wait for user to press Enter
        try:
            input("\n🔴 Press Enter to start recording (or Ctrl+C to quit)...")
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
            
        print("🎙️  Recording... Speak now!")
        audio_path = record_audio()
        
        print("🔄 Transcribing audio...")
        transcription = transcribe_audio(audio_path)
        
        # Check for exit commands
        if any(phrase in transcription.lower() for phrase in STOP_PHRASES + ["quit", "exit"]):
            print("Conversation ended by user.")
            speak_elevenlabs("Goodbye.")
            break
            
        print(f"📝 You said: '{transcription}'")
        
        # LLM-based intent and entity extraction
        print("🧠 Processing with Phi-2...")
        intent_data = classify_intent_and_entities(transcription)
        intent = intent_data.get("intent")
        task = intent_data.get("task")
        due = intent_data.get("due")
        location = intent_data.get("location")
        
        # Change this part in main():
        if intent == "add_task" and task:  # ← Changed from "todoist_add" 
            result = add_todoist_task(task if not due else f"{task} {due}", token=TODOIST_API_TOKEN)
            print(f"✅ {result}")
            speak_elevenlabs(result)
            
        elif intent == "get_weather" and location:  # ← Changed from "weather"
            result = get_weather(location)
            print(f"🌤️  {result}")
            speak_elevenlabs(result)
            
        elif intent == "send_email":  # ← Handle this appropriately
            print("📧 Email functionality not implemented yet")
            speak_elevenlabs("Email functionality is not available yet.")
            
        else:
            # General conversation
            gpt_response = ask_gpt_openrouter(transcription)
            print(f"🤖 AI Response: {gpt_response}")
            speak_elevenlabs(gpt_response)
            
            if any(phrase in gpt_response.lower() for phrase in STOP_PHRASES):
                print("Conversation ended by assistant.")
                break

if __name__ == "__main__":
    main() 