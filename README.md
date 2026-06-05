# ROCK - Private AI Desktop Assistant

ROCK is a highly intelligent, 100% locally hosted AI operating system companion built in Python. Designed for secure, offline workflows, it acts as a proactive desktop assistant capable of hardware monitoring, app launching, real-time web querying, and complex conversational reasoning. 

## Key Features
- **Local Neural Engine:** Powered by Qwen2.5 (7B) via Ollama, ensuring zero cloud dependency and strict data privacy.
- **Voice Biometric Security:** Utilizes PyTorch and SpeechBrain (ECAPA-TDNN embeddings) to extract vocal features, locking activation strictly to the authorized user's voice print.
- **Asynchronous Audio Pipeline:** Combines Picovoice Porcupine (Wake word), OpenAI Whisper (STT), and pyttsx3 (TTS) for a seamless, hands-free voice interaction experience.
- **Intent Routing:** Automatically routes general queries to the local LLM while intercepting specific commands to execute OS-level operations (e.g., launching IDEs, monitoring CPU/RAM/Battery).
- **Secure Web Fallback:** Intercepts factual queries to perform secure, strict-safe searches via DuckDuckGo, feeding real-time data into the LLM for summarization.

## Technology Stack
- **Language:** Python
- **LLM Backend:** Ollama (Qwen2.5-coder:7b)
- **Audio Processing:** PyAudio, torchaudio, SpeechRecognition
- **Speech Models:** OpenAI Whisper (Local STT), SpeechBrain (Speaker Verification), pyttsx3 (TTS)
- **System Automation:** psutil, subprocess, os
- **Web API:** DuckDuckGo-search

## Setup Instructions
1. Clone this repository.
2. Ensure you have **Ollama** installed and running on your system with the model pulled: `ollama pull qwen2.5-coder:7b`.
3. Create a Python virtual environment and activate it.
4. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   *(Note: Installing PyAudio requires Microsoft C++ Build Tools on newer Python versions. Python 3.12 is recommended for pre-compiled binaries).*
5. Run the voice enrollment script to record your biometric lock:
   ```bash
   python setup_voice.py
   ```
6. Start the assistant:
   ```bash
   python main.py
   ```
