# Module 1: Config

| Field | Value |
|:---|:---|
| **Complexity** | S |
| **Estimated Files** | ~1 (`config.py`) |
| **Key Risks** | None — foundational module, no external dependencies |

## Requirements

- Centralized configuration via environment variables with sane defaults.
- AI provider registry: map provider name → API client constructor + model defaults.
- All config values accessible as class attributes (pattern from TTB `Config` class).
- Colab runtime detection.

## UI Structure

No UI. Configuration module only.

## Data & API

### Config Class Fields

| Field | Type | Default | Env Var |
|:---|:---|:---|:---|
| `TELEGRAM_BOT_TOKEN` | `str` | — | `TELEGRAM_BOT_TOKEN` |
| `TELEGRAM_CHAT_ID` | `int` | — | `TELEGRAM_CHAT_ID` |
| `AI_PROVIDER` | `str` | `gemini` | `AI_PROVIDER` |
| `AI_API_KEY` | `str` | — | `AI_API_KEY` |
| `AI_MODEL` | `str` | (per-provider default) | `AI_MODEL` |
| `WHISPER_MODEL` | `str` | `large-v2` | `WHISPER_MODEL` |
| `SPEED_FACTOR` | `float` | `1.25` | `SPEED_FACTOR` |
| `MAX_SEGMENTS` | `int` | `5` | `MAX_SEGMENTS` |
| `MIN_SEGMENT_DURATION` | `int` | `15` | `MIN_SEGMENT_DURATION` |
| `MAX_SEGMENT_DURATION` | `int` | `60` | `MAX_SEGMENT_DURATION` |
| `SUBTITLE_FONT_SIZE` | `int` | `24` | `SUBTITLE_FONT_SIZE` |
| `OUTPUT_FOLDER` | `str` | `video_clipper` | `OUTPUT_FOLDER` |
| `ENABLE_IDLE_MONITOR` | `bool` | `True` | `ENABLE_IDLE_MONITOR` |
| `IDLE_SHUTDOWN_MINUTES` | `int` | `10` | `IDLE_SHUTDOWN_MINUTES` |
| `BOT_FILESIZE_LIMIT` | `int` | `50` | `BOT_FILESIZE_LIMIT` |

### AI Provider Registry

```python
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
```

## Technical Implementation

### `config.py`
```python
import os
import time

INIT_START = float(os.getenv('INIT_START', time.time()))

# Core Secrets
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
if TELEGRAM_CHAT_ID:
    TELEGRAM_CHAT_ID = int(TELEGRAM_CHAT_ID)

class Config:
    # AI Provider
    AI_PROVIDER = os.getenv('AI_PROVIDER', 'gemini')
    AI_API_KEY = os.environ.get('AI_API_KEY')
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
```

### Key Design Decision
- AI_MODEL defaults to empty string. If empty, the AI Selector module resolves it from `AI_PROVIDER_DEFAULTS[provider]["model"]`.
- This keeps config simple while allowing per-provider intelligence.

## Testing

| # | Test | Command / Check | Pass/Fail |
|:---|:---|:---|:---|
| T1-1 | Config loads without error | `from config import Config` succeeds | Binary |
| T1-2 | Defaults are sane | `Config.SPEED_FACTOR == 1.25` | Binary |
| T1-3 | Env override works | Set `SPEED_FACTOR=1.5` → `Config.SPEED_FACTOR == 1.5` | Binary |
| T1-4 | Colab detection works | `IS_COLAB` is `True` in Colab, `False` locally | Binary |
