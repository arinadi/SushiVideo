import os
import time

INIT_START = float(os.getenv('INIT_START', time.time()))

# Core Secrets
TELEGRAM_BOT_TOKEN = os.environ.get('SV_TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('SV_TELEGRAM_CHAT_ID')
if TELEGRAM_CHAT_ID:
    TELEGRAM_CHAT_ID = int(TELEGRAM_CHAT_ID)

AI_PROVIDER_DEFAULTS = {
    "gemini": {
        "model": "gemini-2.5-flash",
        "fallback_model": "gemini-2.0-flash",
        "client_class": "google.genai.Client",
    },
    "openai": {
        "model": "gpt-4o-mini",
        "fallback_model": "gpt-4o",
        "client_class": "openai.OpenAI",
    },
    "anthropic": {
        "model": "claude-sonnet-4-20250514",
        "fallback_model": "claude-haiku-4-20250514",
        "client_class": "anthropic.Anthropic",
    },
}

class Config:
    # AI Provider
    AI_PROVIDER = os.getenv('AI_PROVIDER', 'gemini')
    AI_API_KEY = os.environ.get('SV_AI_API_KEY')
    AI_MODEL = os.getenv('AI_MODEL', '')  # Empty = use provider default
    
    # Whisper
    WHISPER_MODEL = os.getenv('WHISPER_MODEL', 'large-v2')
    
    # Video Processing
    SPEED_FACTOR = float(os.getenv('SPEED_FACTOR', 1.25))
    MAX_SEGMENTS = int(os.getenv('MAX_SEGMENTS', 5))
    MIN_SEGMENT_DURATION = int(os.getenv('MIN_SEGMENT_DURATION', 15))
    MAX_SEGMENT_DURATION = int(os.getenv('MAX_SEGMENT_DURATION', 60))
    SUBTITLE_FONT_SIZE = int(os.getenv('SUBTITLE_FONT_SIZE', 24))
    OUTPUT_FOLDER = os.getenv('OUTPUT_FOLDER', 'video_clipper')
    
    # System
    ENABLE_IDLE_MONITOR = os.getenv('ENABLE_IDLE_MONITOR', 'True').lower() == 'true'
    IDLE_SHUTDOWN_MINUTES = int(os.getenv('IDLE_SHUTDOWN_MINUTES', 10))
    BOT_FILESIZE_LIMIT = int(os.getenv('BOT_FILESIZE_LIMIT', 50))

# Colab Detection
try:
    from google.colab import runtime
    IS_COLAB = True
except ImportError:
    IS_COLAB = False
