# 🍣 SushiVideo

> **"Cut the best piece. Serve it in one bite."**

SushiVideo is a powerful, zero-cost, and highly portable AI video clipper. It transforms long-form YouTube videos into viral-ready, portrait short clips (TikTok, Reels, Shorts) with hardcoded subtitles—**all running 100% free on Google Colab's GPU infrastructure.**

Forget expensive SaaS subscriptions or the need for a beefy local PC. SushiVideo acts as your personal AI sushi chef, carefully analyzing transcripts and slicing the perfect cuts, ready for social media.

## ✨ Why SushiVideo?

- **💸 Zero Cost:** Stop paying $20-$50/month for automated clipping tools.
- **🚀 Ridiculously Fast:** Leverages Google Colab's server-grade internet to download massive videos in seconds.
- **🧠 Intelligent AI Selection:** Uses top-tier AI models (Gemini by default, swappable to OpenAI or Claude) to find the most engaging hooks and viral moments.
- **📱 True Automation:** Automated FFmpeg editing reformats landscape videos to 9:16 portrait (fit-center with blurred background), adjusts speed to 1.25x for better retention, and burns in high-quality subtitles.
- **🤖 Dual Interface:** Control everything via a slick Telegram Bot or a Gradio Web UI for large direct file uploads.

## 🛠️ Tech Stack
- **Core:** Python 3.10+
- **Transcription:** Faster-Whisper (runs locally on GPU, no API limits)
- **AI Engine:** Google Gemini (via `google-genai`), provider-agnostic.
- **Video Processing:** FFmpeg + `yt-dlp`
- **Interfaces:** `python-telegram-bot` & Gradio

## 🚀 Quick Start (Colab)

Run SushiVideo instantly in your browser with zero local setup.

1. Create a new Google Colab notebook.
2. Change runtime to **T4 GPU**.
3. Add your API keys to Colab Secrets:
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
   - `AI_API_KEY` (Gemini API Key)
4. Paste and run the following cell:

```python
# @title 🍣 Start SushiVideo
import os
from google.colab import userdata

# 1. Load Secrets
for key in ['TELEGRAM_BOT_TOKEN', 'TELEGRAM_CHAT_ID', 'AI_API_KEY']:
    try:
        val = userdata.get(key)
        if val: os.environ[key] = str(val)
    except: pass

# 2. Launch
!curl -s https://raw.githubusercontent.com/arinadi/SushiVideo/main/runner.py -o runner.py && python runner.py
```

## 🏗️ Architecture

SushiVideo is built on the **EDNA Methodology**, featuring a robust data pipeline architecture with async threading, idle monitoring (to save Colab GPU credits), and a job queue system to handle heavy rendering tasks securely.

Read the full blueprints in the `SushiVideo_plan/` directory.

---
*Built for solo creators who want to dominate short-form content without breaking the bank.*
