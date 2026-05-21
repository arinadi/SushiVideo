# Module 0: Setup

| Field | Value |
|:---|:---|
| **Complexity** | S |
| **Estimated Files** | ~3 (`runner.py`, `start.py`, `requirements.txt`) |
| **Key Risks** | RC-2 (Whisper model download fails on slow connection) |

## Requirements

- One-cell Colab bootstrap that clones repo, installs dependencies, and launches the bot.
- Hardware detection (GPU availability via `nvidia-smi`).
- Environment initialization: secrets loading, `INIT_START` timestamp, working directories.
- No CPU fallback — if no GPU detected, halt with error message.

## UI Structure

No UI. This module is infrastructure only.

**Colab Cell:**
```python
# @title 🍣 Start SushiVideo
import os
from google.colab import userdata

# 1. Load Secrets
for key in ['SV_TELEGRAM_BOT_TOKEN', 'SV_TELEGRAM_CHAT_ID', 'SV_AI_API_KEY']:
    try:
        val = userdata.get(key)
        if val: os.environ[key.replace('SV_', '')] = str(val) # Map SV_ back to standard internally if needed, or keep SV_

    except: pass

# Optional secrets
for key in ['AI_PROVIDER', 'AI_MODEL', 'GITHUB_TOKEN']:
    try:
        val = userdata.get(key)
        if val: os.environ[key] = str(val)
    except: pass

# 2. Launch
!curl -s https://raw.githubusercontent.com/{REPO}/main/runner.py -o runner.py && python runner.py
```

## Data & API

**Environment Variables Set:**
| Variable | Source | Required |
|:---|:---|:---|
| `SV_TELEGRAM_BOT_TOKEN` | Colab Secrets | ✅ |
| `SV_TELEGRAM_CHAT_ID` | Colab Secrets | ✅ |
| `SV_AI_API_KEY` | Colab Secrets | ✅ |
| `AI_PROVIDER` | Colab Secrets | ❌ (default: `gemini`) |
| `AI_MODEL` | Colab Secrets | ❌ (default: `gemini-2.5-flash`) |
| `INIT_START` | Set by `runner.py` | Auto |

**Directories Created:**
- `uploads/` — temporary video storage
- `transcripts/` — SRT files
- `video_clipper/` — final output clips

## Technical Implementation

### `runner.py` (Pattern from TTB)
1. Record `INIT_START` timestamp.
2. Clone or update repo via git.
3. Install core dependencies: `pip install -r requirements.txt -q`
4. Launch `start.py`.

### `start.py` (Pattern from TTB, modified)
1. Check GPU via `nvidia-smi`.
2. If no GPU → print error and exit (no CPU fallback).
3. Set `TRANSCRIPTION_MODE=WHISPER` (always — no Gemini transcription).
4. Launch `main.py` via subprocess.

### `requirements.txt`
```
python-telegram-bot>=21.0
yt-dlp
ffmpeg-python
faster-whisper>=1.1.0
google-genai>=1.0.0
gradio>=4.0.0
nest_asyncio
```

## Testing

| # | Test | Command / Check | Pass/Fail |
|:---|:---|:---|:---|
| T0-1 | GPU detected | `nvidia-smi` returns 0 | Binary |
| T0-2 | Dependencies installed | `python -c "import telegram, yt_dlp, faster_whisper, genai, gradio"` | Binary |
| T0-3 | Secrets loaded | `os.environ.get('SV_TELEGRAM_BOT_TOKEN')` is not None | Binary |
| T0-4 | Directories created | `os.path.isdir('uploads')` and `os.path.isdir('video_clipper')` | Binary |
