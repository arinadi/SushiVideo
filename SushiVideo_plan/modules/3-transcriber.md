# Module 3: Transcriber

| Field | Value |
|:---|:---|
| **Complexity** | L |
| **Estimated Files** | ~1 (`transcriber.py`) |
| **Key Risks** | RC-2 (Whisper model OOM on long videos or unhandled text encoding) |

## Requirements

- Resolve transcript source in priority order: 
  1. User-provided SRT (highest priority)
  2. YouTube auto-generated SRT (if available)
  3. Whisper generated transcript (lowest priority, runs locally on GPU)
- Normalize all input subtitle formats to standard SRT format.
- Run Faster-Whisper with VAD (Voice Activity Detection) enabled to filter out silence.
- Return `TranscriptData` dataclass.

## UI Structure

No direct UI. Called by main orchestrator.

**Status messages sent during processing:**
```
🔪 Slicing audio track...
🤖 Transcribing video with Whisper (this may take a few minutes)...
✅ Transcript ready (Source: {source})
```

## Data & API

### Output: `TranscriptData` Dataclass
```python
from dataclasses import dataclass

@dataclass
class TranscriptData:
    source: str           # 'user_srt', 'youtube_auto', 'whisper_generated'
    srt_content: str      # Raw SRT string content
    transcript_text: str  # Plain text transcript without timestamps
    language: str         # Detected or specified language (e.g., 'en', 'id')
```

## Technical Implementation

### `transcriber.py`

```python
import os
import asyncio
from faster_whisper import WhisperModel
import utils # formatting helpers

_whisper_model = None

async def init_whisper(model_size: str = "large-v2"):
    """Initialize Whisper model in background."""
    global _whisper_model
    if not _whisper_model:
        # TTB pattern: Use float16 for CUDA
        _whisper_model = await asyncio.to_thread(
            WhisperModel, model_size, device="cuda", compute_type="float16"
        )

async def get_transcript(video_meta: VideoMeta, user_srt_path: str | None = None) -> TranscriptData:
    """Resolve transcript based on priority."""
    
    # Priority 1: User SRT
    if user_srt_path and os.path.exists(user_srt_path):
        return await _process_existing_srt(user_srt_path, 'user_srt')
        
    # Priority 2: YouTube Auto-Sub
    if video_meta.has_youtube_subs and video_meta.subtitle_path:
        return await _process_existing_srt(video_meta.subtitle_path, 'youtube_auto')
        
    # Priority 3: Whisper Generation
    return await _generate_whisper_transcript(video_meta.local_path)

async def _process_existing_srt(srt_path: str, source: str) -> TranscriptData:
    """Read SRT and extract plain text."""
    with open(srt_path, 'r', encoding='utf-8') as f:
        srt_content = f.read()
    
    # Extract plain text from SRT format using simple regex/parsing
    plain_text = utils.srt_to_plaintext(srt_content)
    
    return TranscriptData(
        source=source,
        srt_content=srt_content,
        transcript_text=plain_text,
        language="unknown" # Could parse from yt-dlp filename if needed
    )

async def _generate_whisper_transcript(video_path: str) -> TranscriptData:
    """Run faster-whisper on local video file."""
    global _whisper_model
    if not _whisper_model:
        await init_whisper()
        
    segments_generator, info = await asyncio.to_thread(
        _whisper_model.transcribe, 
        video_path,
        beam_size=5,
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=500)
    )
    
    # Convert generator to list to force execution
    segments = list(segments_generator)
    
    # Format to SRT and plain text
    srt_content = utils.segments_to_srt(segments)
    plain_text = "\n".join([s.text.strip() for s in segments])
    
    return TranscriptData(
        source='whisper_generated',
        srt_content=srt_content,
        transcript_text=plain_text,
        language=info.language
    )
```

## Testing

| # | Test | Command / Check | Pass/Fail |
|:---|:---|:---|:---|
| T3-1 | User SRT priority | Passes user SRT → source is `user_srt` | Binary |
| T3-2 | YT SRT fallback | Passes video with YT subs → source is `youtube_auto` | Binary |
| T3-3 | Whisper transcription | Passes raw video → source is `whisper_generated` | Binary |
| T3-4 | SRT formatting | Generated SRT matches standard format `00:00:01,000 --> 00:00:05,000` | Binary |
| T3-5 | Plaintext extraction | Removes timestamps and sequence numbers from SRT | Binary |
