# Elven Personal Assistant

Elven is a voice-activated AI personal assistant built in Python. It supports natural conversation, task management, weather info, and more, using state-of-the-art AI and APIs.

## ✨ Features
- **Voice Activation**: Wake-word detection ("terminator")
- **Speech Recognition**: Fast, accurate transcription (Whisper)
- **Natural Language Understanding**: GPT-4o via OpenRouter
- **Text-to-Speech**: Realistic voice responses (ElevenLabs)
- **Todoist Integration**: Add and list tasks by voice
- **Weather Info**: Get current weather for any city
- **Extensible**: LLM-powered intent routing for future features

## 🛠 Requirements
- Python 3.8+
- See `requirements.txt` for Python dependencies
- macOS (for built-in audio playback; can be adapted for other OSes)

## 🔑 Environment Variables
Create a `.env.local` file in the project root with:
```
OPENROUTER_API_KEY=your_openrouter_key
TODOIST_API_TOKEN=your_todoist_token
ELEVENLABS_API_KEY=your_elevenlabs_key
OPENWEATHERMAP_API_KEY=your_openweathermap_key
PORCUPINE_ACCESS_KEY=your_porcupine_key
```

## 🚀 Setup & Usage
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Add your API keys to `.env.local` as above.
3. Run the assistant:
   ```bash
   python elven.py
   ```
4. Say "terminator" to activate, then speak your command.

## 🗣 Example Voice Commands
- "Add a task to buy milk today"
- "Show my tasks"
- "What's the weather in London?"
- "Goodbye" (to end the conversation)

## 📝 Notes
- Audio files (`command.wav`, `output.mp3`) and secrets (`.env.local`) are ignored by git.
- Easily extensible: add new intents and actions in `elven.py`.

---

MIT License 