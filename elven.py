import os
from dotenv import load_dotenv
import pvporcupine
import pyaudio
import struct

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


def listen_for_wake_word():
    print("Listening for wake word ('hey assistant')...")
    porcupine = pvporcupine.create(keywords=["hey assistant"])
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

def main():
    print("Elven Personal Assistant starting up...")
    listen_for_wake_word()
    # TODO: Listen for activation and record audio
    # TODO: Transcribe audio using Whisper
    # TODO: Process command with GPT-4 (OpenRouter)
    # TODO: Execute actions (Todoist, Email, etc.)
    # TODO: Respond with TTS (Eleven Labs)
    pass

if __name__ == "__main__":
    main() 